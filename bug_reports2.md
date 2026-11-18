# Benchmark and Fix Report: Integrals & Limits tool (Nabla Workspace)

Companion to the earlier bug report ("calculus operators in the input are
mishandled"). This report (1) gives a full benchmark with expected values to
run against the app, (2) documents a new parser bug, and (3) defines an
output-format standard with fixes.

## 1. Known failures already observed (reproduce these first)

| # | Input (LaTeX) | Observed | Required |
|---|---|---|---|
| K1 | `\int_0^{\pi}\sin^2x\,dx` | Error: "Ekspresi tidak bisa dipahami: unsupported operand type(s) for ** or pow(): 'FunctionClass' and 'Integer'" | `\frac{\pi}{2}` ≈ 1.570796 |
| K2 | `\frac{d}{dx}\left(x^x\right)` | `(x^x)(log(x)+1)` | `x^{x}\left(\ln x + 1\right)`, plain text `x^x (ln(x) + 1)` |
| K3 | `\int x dx` (Indefinite) | `x³/6 + C` (double integration, see earlier report) | `x²/2 + C` |

### K1 root-cause hypotheses (most likely first)
1. The expression is parsed with `sympy.parse_expr` / `sympify` without the
   `function_exponentiation` and `implicit_application` transformations, or the
   preprocessing turns `\sin^2x` into the string `sin**2*x` (or `sin**2x`).
   In SymPy, `sin` on its own is the unapplied function CLASS, so `sin**2`
   raises exactly: unsupported operand type(s) for ** or pow(): 'FunctionClass'
   and 'Integer'. The argument `x` never gets attached to `sin`.
2. A regex converts `\sin` to `sin(` only when a `(` or `{` follows, so
   `\sin^2x` (power, then bare argument) falls through to the class.
3. The parser's name table maps "sin" to the class, and the exponent path never
   applies it to an argument.
Whatever the cause, expect the same failure for every function written with a
power and no parentheses: `\cos^2 x`, `\tan^2 x`, `\sec^3 x`, `\sinh^2 x`,
`\ln^2 x`, `\arcsin^2 x`. The benchmark includes all of these (section 8).

## 2. Rules for the AI (read first)
1. **Reproduce before fixing.** Run the whole benchmark against the current code
   and record actual outputs BEFORE any change.
2. **Never edit an expected value to match the app.** If you believe an expected
   value is wrong, say so in the report and show an independent derivation
   (SymPy `.doit()` on an UNEVALUATED object, plus mpmath numeric check).
3. **Enumerate from the code, not from this list.** Also test every operator,
   function and editor-insert path you find in the code that is not covered here
   and list them in the coverage table.
4. **Classify every result:**
   - PASS: correct value, format rules satisfied
   - PASS-FORMAT: correct value, format rule violated (section 6)
   - PASS-WARN: explicit, accurate "unsupported / diverges / does not exist"
     message instead of a result (allowed only for tier-2 cases, see below)
   - FAIL-VISIBLE: crash, raw Python exception, or misleading error
   - FAIL-SILENT: wrong value with no warning (highest severity)
5. **Tiers.** Tier 1 cases must PASS. Tier 2 are hard cases where an explicit
   "unsupported in this calculator" message is acceptable, but a wrong value
   or a raw exception never is.
6. **Timeout.** 20 s per case. Record the time of every case. A timeout is a
   FAIL-VISIBLE unless the app shows a clean "took too long" message.
7. **Run each case twice:** once in the NATIVE manual mode that matches the
   outermost operator, and once in AUTO mode (if/when implemented). For nested
   cases (section 7) the native mode is the outermost operator.
8. **Also run the mode x input mismatch matrix** from the earlier report using
   inputs from this benchmark. Mismatches must give a correct result or an
   explicit warning, never a silently wrong number.

## 3. Test harness requirements
Add to the JSON response of the compute route (debug fields are fine to keep):
`result_latex`, `result_text`, `result_sympy` (str of the SymPy object),
`mode_used`, `warnings` (list), `numeric_value`, `elapsed_ms`.
Compare using `result_sympy`, never by string-matching the displayed LaTeX.

```python
import random, sympy as sp
from dataclasses import dataclass, field
from sympy import symbols, sympify, simplify, N, Rational, E, pi, oo, zoo, log, Abs

x, y, t, n = symbols("x y t n")
NS = {"x": x, "y": y, "t": t, "n": n, "E": E, "pi": pi, "oo": oo, "Abs": Abs}

@dataclass
class Case:
    id: str
    mode: str                  # limit | derivative | sum | indefinite | definite | auto
    latex: str
    expected: str              # SymPy-parsable, or "diverges"
    kind: str = "exact"        # exact | numeric | antiderivative | diverges
    tier: int = 1
    fields: dict = field(default_factory=dict)   # extra UI fields: point, order, a, b

def T(id, mode, latex, expected, kind="exact", tier=1, **fields):
    return Case(id, mode, latex, expected, kind, tier, fields)

def _numeric_equal(f, g, lo=0.3, hi=2.5, k=6, tol=1e-9):
    pts = [random.uniform(lo, hi) for _ in range(k)]
    return all(abs(complex(N((f - g).subs(x, p)))) < tol for p in pts)

def matches(case, app_sympy_str):
    if case.kind == "diverges":
        return app_sympy_str in ("oo", "-oo", "zoo", "nan") or "diverge" in app_sympy_str.lower()
    exp = sympify(case.expected, locals=NS)
    got = sympify(app_sympy_str.replace("+ C", "").replace("+C", ""), locals=NS)
    if case.kind == "numeric":
        return abs(N(got) - N(exp)) < 1e-6
    if case.kind == "antiderivative":      # compare derivatives; constants may differ
        d = sp.diff(got, x) - sp.diff(exp, x)
        return simplify(d) == 0 or _numeric_equal(sp.diff(got, x), sp.diff(exp, x))
    if simplify(got - exp) == 0:
        return True
    try:                                    # numeric fallback, report as "PASS (numeric only)"
        return abs(N(got) - N(exp)) < 1e-9
    except TypeError:
        return _numeric_equal(got, exp)
```

Also write an independent oracle for every case: build the expected result
from UNEVALUATED SymPy objects (`Integral(...).doit()`, `Limit(...)`,
`Sum(...).doit()`, `Derivative(...).doit()`) and compare it to the hand-written
`expected`. Any disagreement is reported to the user, not silently resolved.

## 4. Benchmark: limits (native mode: limit)
```python
LIMITS = [
 T("L01","limit",r"\lim_{x\to 0}\frac{e^x-1-x-\frac{x^2}{2}}{x^3}","Rational(1,6)"),
 T("L02","limit",r"\lim_{x\to 0}\frac{\sin x-x}{x^3}","-Rational(1,6)"),
 T("L03","limit",r"\lim_{x\to 0}\frac{\tan x-\sin x}{x^3}","Rational(1,2)"),
 T("L04","limit",r"\lim_{x\to 0}\frac{\ln(1+x)-x+\frac{x^2}{2}}{x^3}","Rational(1,3)"),
 T("L05","limit",r"\lim_{x\to 0}\frac{\arctan x-x}{x^3}","-Rational(1,3)"),
 T("L06","limit",r"\lim_{x\to 0}\frac{\sinh x-x}{x^3}","Rational(1,6)"),
 T("L07","limit",r"\lim_{x\to 0}\frac{e^{x^2}-\cos x}{x^2}","Rational(3,2)"),
 T("L08","limit",r"\lim_{x\to 0}\left(\frac{1}{x^2}-\frac{1}{\sin^2 x}\right)","-Rational(1,3)"),
 T("L09","limit",r"\lim_{x\to 0}\frac{(e^x-1-x)(\sin x-x)}{x^5}","-Rational(1,12)"),
 T("L10","limit",r"\lim_{x\to 0}\frac{e^{\sin x}-e^{\tan x}}{\sin x-\tan x}","1"),
 T("L11","limit",r"\lim_{x\to 0}\frac{(1+x)^{1/x}-e}{x}","-E/2"),
 T("L12","limit",r"\lim_{x\to 0}(\cos x)^{1/x^2}","exp(-Rational(1,2))"),
 T("L13","limit",r"\lim_{x\to\infty}\left(1+\frac{3}{x}\right)^{2x}","exp(6)"),
 T("L14","limit",r"\lim_{x\to\infty}\left(\sqrt{x^2+3x}-x\right)","Rational(3,2)"),
 T("L15","limit",r"\lim_{x\to 1}\left(\frac{x}{x-1}-\frac{1}{\ln x}\right)","Rational(1,2)"),
 T("L16","limit",r"\lim_{x\to 0^+}x^x","1"),
 T("L17","limit",r"\lim_{x\to\infty}x^{1/x}","1"),
 T("L18","limit",r"\lim_{x\to\infty}x^2e^{-x}","0"),
 T("L19","limit",r"\lim_{n\to\infty}n\left(\sqrt[n]{2}-1\right)","log(2)"),
 T("L20","limit",r"\lim_{n\to\infty}\frac{1}{n}\sum_{k=1}^{n}\sin\left(\frac{k\pi}{n}\right)","2/pi",tier=2),
 T("L21","limit",r"\lim_{n\to\infty}\sum_{k=1}^{n}\frac{k}{n^2}","Rational(1,2)",tier=2),
 T("L22","limit",r"\lim_{x\to 0}\frac{1}{x}\int_0^x e^{t^2}\,dt","1",tier=2),
 T("L23","limit",r"\lim_{x\to 0}\frac{\int_0^x \sin(t^2)\,dt}{x^3}","Rational(1,3)",tier=2),
]
```

## 5. Benchmark: derivatives (native mode: derivative)
Cases D08 to D11: ALSO run with only the body in the editor and the order set
in the "Derivative order" field. Both routes must give the same answer, and
setting the order in BOTH places with different values must warn.
D12 and C02 use the "Evaluation point" field. If the field rejects `e`, use
2.718281828459045 and compare numerically.
```python
DERIVS = [
 T("D01","derivative",r"\frac{d}{dx}\left(x^x\right)","x**x*(log(x)+1)"),
 T("D02","derivative",r"\frac{d}{dx}\left(\sin(x^2)\,e^{3x}\right)","exp(3*x)*(2*x*cos(x**2)+3*sin(x**2))"),
 T("D03","derivative",r"\frac{d}{dx}\left(\frac{x^3-2x}{x^2+1}\right)","(x**4+5*x**2-2)/(x**2+1)**2"),
 T("D04","derivative",r"\frac{d}{dx}\ln\left(\frac{x^2+1}{\sqrt{x}+1}\right)","2*x/(x**2+1)-1/(2*sqrt(x)*(sqrt(x)+1))"),
 T("D05","derivative",r"\frac{d}{dx}\arctan\left(\frac{x}{\sqrt{1-x^2}}\right)","1/sqrt(1-x**2)"),
 T("D06","derivative",r"\frac{d}{dx}\left(x^2+1\right)^{\sin x}","(x**2+1)**sin(x)*(cos(x)*log(x**2+1)+2*x*sin(x)/(x**2+1))"),
 T("D07","derivative",r"\frac{d}{dx}\sqrt{1+\sin^2 x}","sin(x)*cos(x)/sqrt(1+sin(x)**2)"),
 T("D08","derivative",r"\frac{d^2}{dx^2}\left(x^2e^{-x}\right)","exp(-x)*(x**2-4*x+2)"),
 T("D09","derivative",r"\frac{d^4}{dx^4}\sin(2x)","16*sin(2*x)"),
 T("D10","derivative",r"\frac{d^{10}}{dx^{10}}x^{10}","3628800"),
 T("D11","derivative",r"\frac{d^{11}}{dx^{11}}x^{10}","0"),
 T("D12","derivative",r"\frac{d}{dx}\left(x^3\ln x\right)","4*E**2",point="e"),
 T("D13","derivative",r"\frac{d}{dx}\int_0^{x^2}e^{-t^2}\,dt","2*x*exp(-x**4)"),
 T("D14","derivative",r"\frac{d}{dx}\int_1^{x}\frac{\sin t}{t}\,dt","sin(x)/x"),
 T("D15","derivative",r"\frac{\partial}{\partial x}\left(x^2y+\sin(xy)\right)","2*x*y+y*cos(x*y)"),
 T("D16","derivative",r"\frac{\partial^2}{\partial x\,\partial y}\left(x^3y^2\right)","6*x**2*y"),
]
```

## 6. Benchmark: sums, series, products (native mode: sum)
```python
SUMS = [
 T("S01","sum",r"\sum_{n=1}^{\infty}\frac{1}{n^2}","pi**2/6"),
 T("S02","sum",r"\sum_{n=1}^{\infty}\frac{1}{n^4}","pi**4/90"),
 T("S03","sum",r"\sum_{n=0}^{\infty}\frac{1}{n!}","E"),
 T("S04","sum",r"\sum_{n=0}^{\infty}\frac{2^n}{n!}","exp(2)"),
 T("S05","sum",r"\sum_{n=1}^{\infty}\frac{1}{n(n+1)}","1"),
 T("S06","sum",r"\sum_{n=1}^{\infty}\frac{1}{n(n+2)}","Rational(3,4)"),
 T("S07","sum",r"\sum_{n=1}^{\infty}\frac{1}{4n^2-1}","Rational(1,2)"),
 T("S08","sum",r"\sum_{n=1}^{\infty}\frac{n}{2^n}","2"),
 T("S09","sum",r"\sum_{n=1}^{\infty}\frac{n^2}{2^n}","6"),
 T("S10","sum",r"\sum_{n=1}^{\infty}\frac{1}{n\,2^n}","log(2)"),
 T("S11","sum",r"\sum_{n=1}^{\infty}\frac{(-1)^{n+1}}{n}","log(2)"),
 T("S12","sum",r"\sum_{n=0}^{\infty}\frac{(-1)^n}{2n+1}","pi/4"),
 T("S13","sum",r"\sum_{n=1}^{\infty}\frac{1}{n}","diverges",kind="diverges"),
 T("S14","sum",r"\sum_{k=1}^{100}k^2","338350"),
 T("S15","sum",r"\sum_{k=1}^{n}k^3","n**2*(n+1)**2/4"),
 T("S16","sum",r"\sum_{k=1}^{n}k\,2^k","(n-1)*2**(n+1)+2"),
 T("S17","sum",r"\sum_{k=1}^{20}\left(\frac{1}{k}-\frac{1}{k+1}\right)","Rational(20,21)"),
 T("S18","sum",r"\sum_{k=0}^{10}\binom{10}{k}","1024"),
 T("S19","sum",r"\sum_{i=1}^{5}\sum_{j=1}^{i}j","35"),
 T("S20","sum",r"\sum_{i=1}^{3}\sum_{j=1}^{3}ij","36"),
 T("S21","sum",r"\prod_{k=1}^{10}k","3628800"),
 T("S22","sum",r"\prod_{n=2}^{\infty}\left(1-\frac{1}{n^2}\right)","Rational(1,2)",tier=2),
]
```
Note for S01 to S22: confirm `i`, `k`, `n`, `j` are treated as index
variables and not as the imaginary unit or free symbols.

## 7. Benchmark: indefinite integrals (native mode: indefinite)
The result must end with `+ C`. Compare derivatives (kind `antiderivative`),
since valid antiderivatives differ by form and constant.
```python
INDEF = [
 T("I01","indefinite",r"\int xe^x\,dx","(x-1)*exp(x)",kind="antiderivative"),
 T("I02","indefinite",r"\int x^2\sin x\,dx","-x**2*cos(x)+2*x*sin(x)+2*cos(x)",kind="antiderivative"),
 T("I03","indefinite",r"\int \ln x\,dx","x*log(x)-x",kind="antiderivative"),
 T("I04","indefinite",r"\int \frac{1}{x^2+4x+5}\,dx","atan(x+2)",kind="antiderivative"),
 T("I05","indefinite",r"\int \frac{1}{x^2-1}\,dx","log(Abs((x-1)/(x+1)))/2",kind="antiderivative"),
 T("I06","indefinite",r"\int \sin^3x\cos^2x\,dx","-cos(x)**3/3+cos(x)**5/5",kind="antiderivative"),
 T("I07","indefinite",r"\int \frac{x}{\sqrt{1-x^2}}\,dx","-sqrt(1-x**2)",kind="antiderivative"),
 T("I08","indefinite",r"\int e^x\sin x\,dx","exp(x)*(sin(x)-cos(x))/2",kind="antiderivative"),
 T("I09","indefinite",r"\int \sec^3x\,dx","(sec(x)*tan(x)+log(Abs(sec(x)+tan(x))))/2",kind="antiderivative"),
 T("I10","indefinite",r"\int x\arctan x\,dx","(x**2+1)/2*atan(x)-x/2",kind="antiderivative"),
 T("I11","indefinite",r"\int \frac{1}{1+e^x}\,dx","x-log(1+exp(x))",kind="antiderivative"),
 # CORRECTED: the sign of the second term is minus (earlier draft had plus)
 T("I12","indefinite",r"\int \frac{x^3+2x}{(x^2+1)^2}\,dx","log(x**2+1)/2-1/(2*(x**2+1))",kind="antiderivative"),
]
```

## 8. Benchmark: definite and improper integrals (native mode: definite)
Run each with the bounds typed in the editor and the Lower/Upper fields empty
or locked. Then run a conflict case: same input with different values in the
bound fields. It must use the editor bounds or warn, never silently pick one.
```python
DEFINITE = [
 T("DI01","definite",r"\int_0^1 x^2e^x\,dx","E-2"),
 T("DI02","definite",r"\int_0^{\pi}\sin^2x\,dx","pi/2"),            # KNOWN FAILING (K1)
 T("DI03","definite",r"\int_0^{\pi/2}\sin^5x\,dx","Rational(8,15)"),
 T("DI04","definite",r"\int_0^1 \ln x\,dx","-1"),
 T("DI05","definite",r"\int_1^e (\ln x)^2\,dx","E-2"),
 T("DI06","definite",r"\int_0^{\pi}x\sin x\,dx","pi"),
 T("DI07","definite",r"\int_0^{\pi/4}\tan x\,dx","log(2)/2"),
 T("DI08","definite",r"\int_0^1\sqrt{1-x^2}\,dx","pi/4"),
 T("DI09","definite",r"\int_0^1\frac{x}{1+x^4}\,dx","pi/8"),
 T("DI10","definite",r"\int_{-1}^{1}x^3\cos x\,dx","0"),
 T("DI11","definite",r"\int_0^{2\pi}\left|\sin x\right|\,dx","4"),
 T("DI12","definite",r"\int_0^{\pi/2}\ln(\sin x)\,dx","-pi*log(2)/2",tier=2),
 T("DI13","definite",r"\int_0^{\infty}x^3e^{-x}\,dx","6"),
 T("DI14","definite",r"\int_0^{\infty}e^{-x}\sin x\,dx","Rational(1,2)"),
 T("DI15","definite",r"\int_0^{\infty}x^2e^{-x^2/2}\,dx","sqrt(pi/2)"),
 T("DI16","definite",r"\int_{-\infty}^{\infty}e^{-x^2}\,dx","sqrt(pi)"),
 T("DI17","definite",r"\int_0^{\infty}\frac{1}{1+x^2}\,dx","pi/2"),
 T("DI18","definite",r"\int_0^{\infty}\frac{\sin x}{x}\,dx","pi/2",tier=2),
 T("DI19","definite",r"\int_0^1\frac{1}{\sqrt{x}}\,dx","2"),
 T("DI20","definite",r"\int_0^1\frac{1}{x}\,dx","diverges",kind="diverges"),
 T("DI21","definite",r"\int_0^3\frac{\sin x}{x}\,dx","1.848652",kind="numeric"),
 T("DI22","definite",r"\int_0^1 x^x\,dx","0.7834305",kind="numeric",tier=2),
 T("DI23","definite",r"\int_0^1\int_0^1 xy\,dx\,dy","Rational(1,4)"),
 T("DI24","definite",r"\int_0^1\int_0^x y\,dy\,dx","Rational(1,6)"),
]
```

## 9. Benchmark: nested and combined operations (the double-application killers)
```python
NESTED = [
 T("C01","definite",r"\int_0^1\frac{d}{dx}\left(x^3e^x\right)dx","E"),
 T("C02","derivative",r"\frac{d}{dx}\left[\int_0^x t^2e^{-t}\,dt\right]","exp(-1)",point="1"),
 T("C03","indefinite",r"\int \frac{d}{dx}\left(x^3\right)dx","x**3",kind="antiderivative"),
 T("C04","derivative",r"\frac{d}{dx}\int x^2\,dx","x**2"),
 T("C05","sum",r"\sum_{k=1}^{4}\int_0^1 x^k\,dx","Rational(77,60)"),
 T("C06","definite",r"\int_0^1\sum_{n=0}^{3}x^n\,dx","Rational(25,12)"),
 T("C07","limit",r"\lim_{x\to 0}\frac{1}{x^2}\int_0^x\sin t\,dt","Rational(1,2)"),
 T("C08","derivative",r"\frac{d}{dx}\sum_{n=0}^{3}x^n","1+2*x+3*x**2"),
]
```
Diagnostic: if C03 returns `x^4/4`-like output or C04 returns `2x`, the
operator was applied twice.

## 10. Benchmark: functions with powers (targets bug K1)
```python
FNPOW = [
 # integrals
 T("P01","indefinite",r"\int \sin^2 x\,dx","x/2-sin(2*x)/4",kind="antiderivative"),
 T("P02","indefinite",r"\int \cos^2 x\,dx","x/2+sin(2*x)/4",kind="antiderivative"),
 T("P03","indefinite",r"\int \tan^2 x\,dx","tan(x)-x",kind="antiderivative"),
 T("P04","indefinite",r"\int \sec^2 x\,dx","tan(x)",kind="antiderivative"),
 T("P05","indefinite",r"\int \sin^2 x\cos x\,dx","sin(x)**3/3",kind="antiderivative"),
 T("P06","indefinite",r"\int \sin^{2}{x}\,dx","x/2-sin(2*x)/4",kind="antiderivative"),
 T("P07","indefinite",r"\int \sin^2(x)\,dx","x/2-sin(2*x)/4",kind="antiderivative"),
 T("P08","indefinite",r"\int \sin^2 2x\,dx","x/2-sin(4*x)/8",kind="antiderivative"),
 T("P09","indefinite",r"\int \ln^2 x\,dx","x*log(x)**2-2*x*log(x)+2*x",kind="antiderivative"),
 # derivatives
 T("P10","derivative",r"\frac{d}{dx}\sin^2 x","sin(2*x)"),
 T("P11","derivative",r"\frac{d}{dx}\tan^2 x","2*tan(x)*sec(x)**2"),
 T("P12","derivative",r"\frac{d}{dx}\ln^2 x","2*log(x)/x"),
 T("P13","derivative",r"\frac{d}{dx}\cos^3 x","-3*cos(x)**2*sin(x)"),
 T("P14","derivative",r"\frac{d}{dx}\sinh^2 x","2*sinh(x)*cosh(x)"),
 T("P15","derivative",r"\frac{d}{dx}e^{\sin^2 x}","exp(sin(x)**2)*sin(2*x)"),
 T("P16","derivative",r"\frac{d}{dx}\arcsin^2 x","2*asin(x)/sqrt(1-x**2)"),
 T("P17","derivative",r"\frac{d}{dx}\sin^2\left(x^2\right)","4*x*sin(x**2)*cos(x**2)"),
 T("P18","derivative",r"\frac{d}{dx}\sin 2x","2*cos(2*x)"),
 T("P19","derivative",r"\frac{d}{dx}\left(\sin x\cos x\right)","cos(2*x)"),
 # limits, definite, sums, plain evaluate
 T("P20","limit",r"\lim_{x\to 0}\frac{\sin^2 x}{x^2}","1"),
 T("P21","limit",r"\lim_{x\to 0}\frac{\tan^2 x}{x^2}","1"),
 T("P22","definite",r"\int_0^{\pi}\cos^2 x\,dx","pi/2"),
 T("P23","definite",r"\int_0^{\pi/2}\sin^2 x\cos^2 x\,dx","pi/16"),
 T("P24","definite",r"\int_0^1\ln^2 x\,dx","2"),
 T("P25","sum",r"\sum_{k=1}^{3}\sin^2\left(\frac{k\pi}{2}\right)","2"),
 T("P26","auto",r"\sin^2\left(\frac{\pi}{6}\right)","Rational(1,4)"),
 T("P27","auto",r"\sin^2 x+\cos^2 x","1"),
 # DESIGN DECISION, see section 12 (inverse vs reciprocal): expected assumes inverse
 T("P28","auto",r"\sin^{-1}(1)","pi/2"),
]
# Variants of the failing input K1: ALL must give pi/2. Tests tokenisation and spacing.
VARIANTS = [T(f"V{i:02d}","definite",s,"pi/2") for i,s in enumerate([
 r"\int_0^{\pi}\sin^2x\,dx",
 r"\int_0^{\pi}\sin^2xdx",
 r"\int_0^{\pi}\sin^2 x\ dx",
 r"\int_0^{\pi}\sin^{2}x\,\mathrm{d}x",
 r"\int_0^{\pi}\sin^2\left(x\right)dx",
 r"\int_0^{\pi}\left(\sin x\right)^2dx",
 r"\int_0^\pi \sin^2 x \, dx",
],1)]
```
Property/fuzz test for this bug class: generate `fn^p(arg)` for
fn in {sin, cos, tan, cot, sec, csc, sinh, cosh, tanh, ln, arcsin, arctan},
p in {2, 3, 4}, arg in {`x`, `(x)`, `{x}`, `2x`, `x^2`, `\frac{x}{2}`}. For each,
differentiate and integrate where an oracle exists (derivative always),
compare to SymPy built directly as `fn(arg)**p`. No generated input may
produce a raw exception or the strings "FunctionClass" or "unsupported operand".

## 11. Output-format standard (fixes K2) and checks

### 11.1 Required display rules
| Current | Required |
|---|---|
| `(x^x)(log(x)+1)` | `x^x (ln(x) + 1)` in text, `x^{x}\left(\ln x + 1\right)` in LaTeX |
| `\log{x}` / `log(x)` for natural log | `\ln x` |
| `\operatorname{atan}(x)` / `atan(x)` | `\arctan x` (same for arcsin, arccos, arccot, arcsec, arccsc) |
| `log(x) + C` from ∫1/x | `\ln\left|x\right| + C` |
| `sin(x)**2` | `\sin^{2} x` |
| `oo`, `zoo`, `nan` | `\infty`, "undefined", "does not exist" (never raw) |
| `Abs(x)` | `\left|x\right|` |
| `exp(-x**4)` | `e^{-x^{4}}` |
| `x**(1/2)` | `\sqrt{x}` |
| `I` | `i` |
| redundant parentheses around a single power or symbol, e.g. `(x^x)(...)` | none |

Further rules:
1. Natural log is always `ln`. `log_b` is printed with its base as a subscript.
   (How a bare typed `\log` is interpreted is a documented design decision,
   see section 12.)
2. Put the coefficient and simple factors first, and the parenthesised sum last:
   `2x e^{-x^{4}}`, `x^{x}\left(\ln x+1\right)`, `e^{3x}\left(2x\cos x^{2}+3\sin x^{2}\right)`.
3. Use implicit multiplication; show `\cdot` only between two numbers.
4. Rational results are shown as fractions, plus a decimal in the "Numeric value"
   box (6+ digits) only when the result is a real constant. Blank or "n/a" for
   expressions in x.
5. "+ C" appears only on indefinite integrals.
6. Diverging results show "diverges" (or "does not exist"), and the numeric box
   stays empty.
7. Text output (copy to clipboard) uses `^`, `sqrt(...)`, `ln(...)`, `pi`, `e`
   and `/`, never `**`, `log(`, `Abs(`, `asin(`, `oo`.

### 11.2 Implementation hints (verify against the installed SymPy version)
- `sympy.latex(expr, ln_notation=True, inv_trig_style="full", mul_symbol=None)`
  covers `\ln` and `\arcsin`-style names. Subclass `LatexPrinter` for anything left
  over (Abs of logs, the factor ordering rule, `\sin^{2}` style).
- For indefinite integrals, rewrite `log(u)` to `log(Abs(u))` unless `u` is
  provably positive (declare `x` real, and `(x**2+1).is_positive` becomes True).
- Do not call `simplify()` blindly: it can return worse-looking forms. Build
  candidates `[expr, simplify(expr), trigsimp(expr), factor(expr), together(expr)]`
  and pick the one with the lowest `count_ops`, with a tie-break that prefers
  the factored prefactor form (rule 2).
- Equivalent textbook forms are all acceptable (for example
  `x/2 - sin(2x)/4` and `x/2 - sin(x)cos(x)/2`). Only the format rules above
  are enforced, not a specific equivalent form.

### 11.3 Automated format checks (run on every PASS)
```python
import re
FORBIDDEN_LATEX = [r"\\log\b(?!_)", r"\\operatorname\{a(sin|cos|tan|cot|sec|csc)", r"Abs",
                   r"\*\*", r"\bexp\b", r"\bzoo\b", r"\bnan\b", r"\boo\b",
                   r"Integral|Sum\(|Limit|Derivative|Subs",
                   r"\\left\(\s*[A-Za-z0-9]+\^\{[^}]*\}\s*\\right\)\\left\("]   # (x^x)(...)
FORBIDDEN_TEXT  = [r"\*\*", r"\blog\(", r"\bAbs\(", r"\ba(sin|cos|tan|cot|sec|csc)\(",
                   r"\boo\b", r"\bzoo\b", r"\bnan\b", r"Integral\(|Limit\(|Derivative\("]
def format_violations(latex, text):
    return ([p for p in FORBIDDEN_LATEX if re.search(p, latex)] +
            [p for p in FORBIDDEN_TEXT if re.search(p, text)])
```
Format-specific cases (check the displayed output, in addition to value):
```python
FORMAT = [
 ("F01", r"\frac{d}{dx}\left(x^x\right)",            ["\\ln"],               ["\\log", "(x^x)("]),
 ("F02", r"\int \frac{1}{x}\,dx",                    ["\\ln", "|x|", "C"],   ["log("]),
 ("F03", r"\int \frac{1}{x^2+4x+5}\,dx",             ["\\arctan"],           ["atan"]),
 ("F04", r"\int \sin^2 x\,dx",                       ["\\sin"],              ["**"]),
 ("F05", r"\int_0^{\infty}e^{-x^2}\,dx",             ["\\sqrt{\\pi}"],       ["oo"]),
 ("F06", r"\lim_{x\to\infty}\left(1+\frac{3}{x}\right)^{2x}", ["e^{6}"],     ["exp"]),
 ("F07", r"\frac{d}{dx}\int_0^{x^2}e^{-t^2}\,dt",    ["e^{-x^{4}}"],         ["exp"]),
 ("F08", r"\sum_{n=1}^{\infty}\frac{1}{n}",          ["diverge"],            ["oo"]),
 ("F09", r"\frac{d}{dx}\sqrt{1+\sin^2 x}",           ["\\sqrt{"],            ["**", "\\frac{1}{2}}"]),
]   # (id, input, must_contain, must_not_contain)
```

## 12. Fix for K1: function powers and parser robustness

### 12.1 Preprocessing order (important)
1. Strip presentation-only markup (`\textcolor`, `\mathbf`, `\colorbox`, `\!`, `\,`
   spacing used only for display).
2. Extract the outer operator (`\int`, bounds, differential `dx`/`\mathrm{d}x`/`d x`
   including the no-space form `xdx`, `\frac{d}{dx}`, `\lim`, `\sum`, `\prod`).
   Differentials must be removed BEFORE step 3, otherwise `\sin^2x\,dx`
   leaves `dx` glued to the function argument.
3. **Normalise function powers** on the remaining body (below).
4. Parse the body alone, validate symbols, apply the operation exactly once.

### 12.2 Normalise function powers
Convert `\fn^{p} ARG` and `\fn^p ARG` into `\left(\fn\left(ARG\right)\right)^{p}`
for fn in: sin cos tan cot sec csc, arcsin arccos arctan arccot arcsec arccsc,
sinh cosh tanh coth sech csch, ln, log, exp. Use a small tokenizer or
recursive-descent routine, not a single regex, so nested cases like
`\sin^2\left(\cos^2 x\right)` work.

Argument rule (document it in the UI help):
- `\left(...\right)` or `(...)` or `{...}` is the argument.
- Otherwise the argument is the run of implicit-multiplication factors (numbers,
  variables, powers, fractions, roots) that follows, ending at: another function
  name, `+`, `-`, a relation (`=`, `<`), a comma, a closing delimiter,
  `\cdot`, `\times`, a differential, or the end of input.
  So `\sin 2x` = sin(2x), and `\sin x\cos x` = sin(x)·cos(x).
- If no argument follows (`\sin^2` alone) return a friendly error, not a
  stack trace.

If the parser is SymPy `parse_expr`, add `implicit_multiplication_application`
and `function_exponentiation` to the transformations as a second line of
defence, but do not rely on it alone (verify behaviour with tests P01 to P28).
Also guard against unapplied functions: after parsing, if the result contains
a `FunctionClass` / `UndefinedFunction` object that is not an applied function
(for example the bare name `sin` or `cos`), raise a clean "missing argument for
sin" error instead of attempting arithmetic on it.

## 13. Error-handling fix
- The user must never see raw Python exception text (as in
  "unsupported operand type(s) for ** or pow(): ...").
- Separate three error classes:
  1. User input problem (unbalanced braces, missing differential, unknown
     symbol): friendly, specific message, with the offending part quoted.
  2. Unsupported operation: "This calculator can't evaluate X (reason)".
  3. Internal error (any TypeError/AttributeError/KeyError, or a FunctionClass
     message like K1): log the full traceback and the input server-side, show a
     generic message with an error id, and treat it as a BUG in the test table.
- Language: the app currently mixes Indonesian ("Ekspresi tidak bisa
  dipahami") and English ("Unknown symbols"). Choose one language for all
  messages, or add proper localisation and a language switch. Ask the product
  owner which, and do not mix them.
- Error messages must not claim the user's input is wrong when the cause is an
  internal bug (K1 is valid, standard notation).

## 14. Deliverables
1. The operator and function inventory found in the code (file and line refs).
2. A test file containing every case above, parametrised, plus the fuzz test
   and the format checks.
3. A results table for the CURRENT code (before any fix) with classification,
   elapsed time and, for failures, the actual output.
4. Root-cause statements for K1, K2 and K3 with logged evidence (raw request,
   preprocessed string, parser output, expression before/after each solver call).
5. The fixes, then the same results table after the fixes.
6. Coverage table: every operator, function, mode, field and editor-insert item
   found in the code, with the tests that hit it, or NOT TESTED with a reason.
7. A short list of design decisions made for ambiguous inputs (below).
8. A note on every expected value in this report that the independent oracle
   disagreed with (should be none).

### Design decisions the AI must make visible and document
- `\sin^{-1}x`: inverse function (arcsin) or reciprocal? (Test P28 assumes inverse.
  Show the interpretation in the output, e.g. "interpreted as arcsin".)
- Bare `\log x`: base 10 or natural? Show the base used in the output.
- Two-sided limit that does not exist (`\lim_{x\to 0}\frac{1}{x}`): "does not
  exist", not a bare ∞.
- Reversed sum range (`\sum_{i=5}^{1}`): standard empty-sum 0 vs SymPy's
  convention; document and show a note if different.
- Radians vs degrees (assume radians; say so).
- Conflicting order/bounds/point in the editor and in the fields.

## 15. Acceptance criteria
- Every tier-1 case is PASS with zero format violations.
- Every tier-2 case is PASS or PASS-WARN (explicit "unsupported" message).
- Zero FAIL-SILENT and zero FAIL-VISIBLE.
- K1 variants V01 to V07 and the whole function-power fuzz set pass.
- No raw Python exception text or Python-style syntax (`**`, `log(`, `Abs(`,
  `atan`, `oo`) appears anywhere in the UI.
- No operation is ever applied twice (C01 to C08, plus the earlier report's canaries).
- Every example-usage row in the app also passes as an automated test.