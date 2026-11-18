# -*- coding: utf-8 -*-
"""==============================================================
TEST SUITE — tool "Integrals & Limits" (bug_reports.md deliverable)
E2E sungguhan: LaTeX -> la2plain (frontend ASLI, diekstrak dr
tools.js via Node) -> mathlab.tool_integral (backend ASLI).

Jalankan:  python test_integral_tool.py
Output: tabel hasil + ringkasan klasifikasi. Exit code 0 kalau
gak ada FAIL*.
=============================================================="""
import io, sys, json, os, subprocess, tempfile

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                              errors="replace")
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

import sympy as sp
import mathlab

# ----------------------------------------------------------------
# 1) HARNESS: ekstrak fungsi konversi LaTeX ASLI dari static/tools.js
#    (readGroup/grabBody/grabTillPlus/calculus2sympy/la2plain) dan
#    jalankan via Node. cleanLatex (app.js) di-stub 1:1.
# ----------------------------------------------------------------
_NODE_JS = r"""
const fs = require("fs");
const src = fs.readFileSync(process.argv[2], "utf8");
const start = src.indexOf("function readGroup");
const end = src.indexOf("const TOOLS");
if (start < 0 || end < 0) { console.error("extract fail"); process.exit(2); }
const code = src.slice(start, end);
/* stub cleanLatex = implementasi persis app.js */
const cleanLatex = (s) => {
  if (!s) return "";
  let res = s;
  const stylePattern =
    /\\(?:bm|boldsymbol|mathbf|textbf|mathit|textit|mathrm|textrm|text|mathsf|mathtt|mathbb|mathcal|mathscr|mathfrak|operatorname)\{([^{}]*)\}/g;
  while (stylePattern.test(res)) res = res.replace(stylePattern, "$1");
  return res
    .replace(/\\(?:boldmath|displaystyle|textstyle|scriptstyle|scriptscriptstyle|bf|it|rm|sf|tt)\b/g, "")
    .replace(/\\,/g, " ").replace(/\\:/g, " ").replace(/\\;/g, " ")
    .trim();
};
eval(code);
const inp = JSON.parse(process.argv[3]);
try {
  console.log(JSON.stringify({ ok: true,
    out: la2plain(inp.la, { unevaluated: !!inp.uneval }) }));
} catch (e) {
  console.log(JSON.stringify({ ok: false, out: String(e) }));
}
"""

def la2plain_frontend(la):
    """Konversi LaTeX -> plain pakai fungsi ASLI tools.js (via Node)."""
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False,
                                     encoding="utf-8") as f:
        f.write(_NODE_JS)
        path = f.name
    try:
        r = subprocess.run(
            ["node", path, os.path.join(ROOT, "static", "tools.js"),
             json.dumps({"la": la, "uneval": True})],
            capture_output=True, text=True, encoding="utf-8", timeout=30,
            cwd=ROOT)
        out = json.loads(r.stdout)
        if not out["ok"]:
            raise ValueError(out["out"])
        return out["out"]
    finally:
        os.unlink(path)

# ----------------------------------------------------------------
# 2) ORACLE: hasil harapan dihitung independen pakai SymPy unevaluated
# ----------------------------------------------------------------
x, y, t, n, k, a, b = sp.symbols("x y t n k a b")
oo = sp.oo

def run_case(la, mode="auto", extra=None):
    """Full pipeline: LaTeX (frontend asli) -> backend asli.
    Return dict hasil atau LabError."""
    plain = la2plain_frontend(la)
    data = {"expr": plain, "mode": mode}
    if plain.startswith("__NABLA_OP__"):
        data["op_data"] = json.loads(plain[12:])
        data["expr"] = ""
    if extra:
        data.update(extra)
    return mathlab.tool_integral(data), plain

def num_eq(v1, v2, tol=1e-9):
    if v1 == v2:
        return True   # oo == oo, zoo == zoo, dsb.
    try:
        return abs(float(sp.N(v1 - v2, 20))) < tol
    except (TypeError, ValueError):
        return False

def check(actual_plain, expected):
    """actual_plain = str sympy dr backend; expected = sympy expr/angka.
    Numeric utk konstanta; sample-point utk ekspresi ber-symbol.
    "+ C" (konstanta integrasi) di-strip dulu."""
    expected = sp.sympify(expected)
    act = sp.sympify(str(actual_plain).replace("+ C", "").strip() or "0")
    if act.free_symbols or expected.free_symbols:
        common = sorted(act.free_symbols | expected.free_symbols, key=str)
        # nilai BEDA per simbol (dulu semua sama -> x vs y gak kebeda)
        vals = [1.7, -0.9, 2.3, 0.8]
        for base in (0.0, 0.35):
            sub = {s: vals[i % len(vals)] + base for i, s in enumerate(common)}
            if not num_eq(act.subs(sub), expected.subs(sub), 1e-6):
                return False
        return True
    return num_eq(act, expected)

# ----------------------------------------------------------------
# 3) MATRIX TEST (bug_reports.md: canaries + tiap keluarga operator)
#    (laTeX, mode, extra_fields, expected sympy | "ERR:key" | "NUM:x")
# ----------------------------------------------------------------
PI = sp.pi
CASES = [
    # --- canary: 0/1/2x application berbeda semua ---
    (r"\int x^2 dx", "auto", None, x**3/3),
    (r"\frac{d}{dx} x^3", "auto", None, 3*x**2),
    (r"\frac{d}{dx} x^4", "auto", None, 4*x**3),
    (r"\int_0^3 x^2 dx", "auto", None, 9),
    # --- A. Integral ---
    (r"\int x dx", "auto", None, x**2/2),
    (r"\int \frac{1}{x} dx", "auto", None, sp.log(x)),          # ln|x| (documented)
    (r"\int e^x dx", "auto", None, sp.exp(x)),
    (r"\int \sin x dx", "auto", None, -sp.cos(x)),
    (r"\int_1^2 x dx", "auto", None, sp.Rational(3, 2)),
    (r"\int_{-1}^{1} x dx", "auto", None, 0),
    (r"\int_2^1 x dx", "auto", None, sp.Rational(-3, 2)),
    (r"\int_0^0 x dx", "auto", None, 0),
    (r"\int_0^\infty e^{-x} dx", "auto", None, 1),
    (r"\int_{-\infty}^{\infty} e^{-x^2} dx", "auto", None, sp.sqrt(PI)),
    (r"\int_a^b x dx", "auto", None, (b**2 - a**2)/2),
    (r"\int t dt", "auto", None, t**2/2),
    (r"\int xy dx", "auto", None, x**2*y/2),
    (r"\int xdx", "auto", None, x**2/2),
    (r"\int x^2dx", "auto", None, x**3/3),
    (r"\int e^xdx", "auto", None, sp.exp(x)),
    (r"\int \sin xdx", "auto", None, -sp.cos(x)),
    (r"\int x\,dx", "auto", None, x**2/2),
    (r"\int x \mathrm{d}x", "auto", None, x**2/2),
    (r"\int x", "auto", None, "ERR:int_missing_dx"),            # PASS-WARN
    (r"\iint", "auto", None, "ERR:int_unsupported"),            # PASS-WARN
    (r"\int_0^1 \int_0^x y dy dx", "auto", None, "ERR:int_unsupported"),  # deliberate
    # --- B. Derivatives ---
    (r"\frac{d}{dx}(x^3)", "auto", None, 3*x**2),
    (r"\frac{d}{dx}\left(x^3\right)", "auto", None, 3*x**2),
    (r"\frac{d x^3}{dx}", "auto", None, 3*x**2),
    (r"\frac{d^2}{dx^2} x^3", "auto", None, 6*x),
    # mode diff MANUAL: field order n = OVERRIDE orde editor
    (r"\frac{d}{dx} x^3", "diff", {"n": "3", "xo": "2"}, 6),
    (r"\frac{d}{dx} x^3", "diff", {"n": "1"}, 3*x**2),
    (r"\frac{d}{dx} x^3", "diff", {"n": "6"}, 0),
    (r"\frac{d}{dx} x^3", "diff", {"xo": "2"}, "DVAL:12"),
    (r"\frac{d}{dt} t^3", "auto", None, 3*t**2),
    (r"\frac{\partial}{\partial x} x^2 y", "auto", None, 2*x*y),
    (r"\frac{\partial^2}{\partial x \partial y} x^2 y", "auto", None, 2*x),
    (r"\frac{d}{dx}\sin(x^2)", "auto", None, 2*x*sp.cos(x**2)),
    (r"\frac{d}{dx} x e^x", "auto", None, sp.exp(x)*(x + 1)),
    (r"\frac{d}{dx}\frac{x}{x+1}", "auto", None, 1/(x + 1)**2),
    # --- C. Limits ---
    (r"\lim_{x\to 0} \frac{\sin x}{x}", "auto", None, 1),
    (r"\lim_{x\to 2} x^2", "auto", None, 4),
    (r"\lim_{x\to 0} \frac{1-\cos x}{x^2}", "auto", None, sp.Rational(1, 2)),
    (r"\lim_{x\to\infty} \frac{1}{x}", "auto", None, 0),
    (r"\lim_{x\to\infty} \left(1+\frac{1}{x}\right)^x", "auto", None, sp.E),
    (r"\lim_{x\to 0^{+}} \frac{1}{x}", "auto", None, oo),
    (r"\lim_{x\to 0^{-}} \frac{1}{x}", "auto", None, -oo),
    (r"\lim_{x\to 0} \frac{1}{x}", "auto", None, oo),           # documented: right-hand
    (r"\lim_{n\to\infty} \frac{1}{n}", "auto", None, 0),
    (r"\lim\limits_{x\to 0} \frac{\sin x}{x}", "auto", None, 1),
    (r"\lim_{x \rightarrow 0} \frac{\sin x}{x}", "auto", None, 1),
    # --- D. Sums & products ---
    (r"\sum_{x=1}^{5} x^2", "auto", None, 55),
    (r"\sum_{i=1}^{4} i", "auto", None, 10),
    (r"\sum_{k=1}^{4} k", "auto", None, 10),
    (r"\sum_{i=1}^{3} 2^i", "auto", None, 14),
    (r"\sum_{k=1}^{n} k", "auto", None, n*(n + 1)/2),
    (r"\sum_{n=1}^{\infty} \frac{1}{n^2}", "auto", None, PI**2/6),
    (r"\sum_{n=0}^{\infty} \left(\frac{1}{2}\right)^n", "auto", None, 2),
    (r"\sum_{i=3}^{3} i", "auto", None, 3),
    (r"\prod_{i=1}^{5} i", "auto", None, 120),
    (r"\prod_{k=1}^{n} k", "auto", None, sp.factorial(n)),
    # --- E. Exp / log / fungsi ---
    (r"e^{2\ln 4}", "auto", None, 16),
    (r"e^0", "auto", None, 1),
    (r"\ln e", "auto", None, 1),
    (r"\ln 1", "auto", None, 0),
    (r"\log_{2} 8", "auto", None, 3),
    (r"\log_{10} 1000", "auto", None, 3),
    (r"\sqrt[3]{8}", "auto", None, 2),
    (r"5!", "auto", None, 120),
    (r"\binom{5}{2}", "auto", None, 10),
    (r"e^{\ln x}", "auto", None, x),
    # --- F. Plain expression (mode manual tetap jalan) ---
    (r"x+x", "auto", None, 2*x),
    (r"x^2", "diff", {"n": "1"}, 2*x),
    (r"x^2", "indef", None, x**3/3),
    (r"\sin(x)", "def", {"a": "0", "b": "3.14159265358979"}, 2.0),
    # --- Golden tests: baris contoh app (paste utuh) ---
    (r"\displaystyle\int_0^{3}\frac{\sin x}{x}\,dx \approx 1.84865",
     "auto", None, 1.848652),
    (r"\dfrac{d}{dx}\,x^{3} = 3x^{2}", "auto", None, 3*x**2),
    (r"\sum_{x=1}^{5}x^{2} = 55", "auto", None, 55),
    (r"\displaystyle\int x^2\,dx = \tfrac{x^3}{3} + C", "auto", None, x**3/3),
    (r"e^{2\ln 4} = 16", "auto", None, 16),
    (r"\displaystyle\lim_{x\to 0}\frac{\sin x}{x} = 1", "auto", None, 1),
    (r"\left.\dfrac{d}{dx}x^{3}\right|_{x=2} = 12", "auto", None, 12),
    # --- Conflicting bounds: editor MENANG (anti 4.5) ---
    (r"\int_1^2 x dx", "def", {"a": "0", "b": "3"}, sp.Rational(3, 2)),
    (r"\int_1^2 x dx", "def", {"a": "0", "b": "2"}, sp.Rational(3, 2)),
    (r"\int_1^2 x dx", "indef", None, sp.Rational(3, 2)),  # op sendiri, sekali
    # --- Operator di input + mode manual apapun = tetap SEKALI ---
    (r"\int_0^3 x^2 dx", "indef", None, 9),
    (r"\int_0^3 x^2 dx", "diff", {"n": "1"}, 9),
    (r"\int x^2 dx", "def", {"a": "0", "b": "3"}, 9),
    # --- sentinel rusak ---
    (r"\int_", "auto", None, "ERR:int_missing_dx"),
    (r"\sum_{n=}^{(){}", "auto", None, "ERR:int_malformed"),
    # --- paste round-trip & tinkering (bar bisa hilang saat paste) ---
    (r"\dfrac{\mathrm{d}^2}{\mathrm{d}x^2}x\bigm{|}_{x=1}", "auto", None, 0),
    (r"\dfrac{\mathrm{d}^2}{\mathrm{d}x^2}x_{x=1}", "auto", None, 0),
    (r"\dfrac{\mathrm{d}^2}{\mathrm{d}x^2}x^2_{x=1}", "auto", None, 2),
    (r"\dfrac{\mathrm{d}^2}{\mathrm{d}x^2}x{|}_{x=1}", "auto", None, 0),
    (r"\dfrac{\mathrm{d}^2}{\mathrm{d}x^2} x _{x=1}", "auto", None, 0),
    (r"\dfrac{\mathrm{d}^2}{\mathrm{d}x^2}x|_{x=1}", "auto", None, 0),
    (r"\frac{d}{d x} x^{3}", "auto", None, 3*x**2),
    (r"\left. \frac{d}{d x} x^{3} \right|_{x=2}", "auto", None, 12),
    (r"\sum_{n=1}^{5} n^{2}", "auto", None, 55),
    (r"\prod_{n=1}^{5} n", "auto", None, 120),
]

# ----------------------------------------------------------------
# 4) RUN + klasifikasi
# ----------------------------------------------------------------
results = []
for la, mode, extra, expected in CASES:
    tag = la[:48]
    try:
        data, plain = run_case(la, mode, extra)
    except mathlab.LabError as e:
        if isinstance(expected, str) and expected.startswith("ERR:"):
            ok = e.key == "err." + expected[4:]
            results.append((tag, "PASS-WARN" if ok else "FAIL-WRONG-KEY",
                            f"err={e.key}"))
        else:
            results.append((tag, "FAIL-VISIBLE", f"LabError: {e}"))
        continue
    except Exception as e:
        results.append((tag, "FAIL-VISIBLE", f"{type(e).__name__}: {e}"))
        continue
    if isinstance(expected, str) and expected.startswith("ERR:"):
        results.append((tag, "FAIL-SILENT", f"keluar hasil: {plain[:50]}"))
        continue
    try:
        if isinstance(expected, str) and expected.startswith("DVAL:"):
            dv = [r[1] for r in data["rows"] if r[0] == "dval"]
            okp = bool(dv) and num_eq(sp.N(dv[0]), float(expected[5:]), 1e-9)
        else:
            okp = check(data.get("plain", ""), expected)
    except Exception as e:
        if os.environ.get("TRACE"):
            import traceback; traceback.print_exc()
        okp = False
    # numeric utk golden berupa float murni
    if not okp and isinstance(expected, float):
        numrows = [r[1] for r in data["rows"] if r[0] == "num"]
        okp = numrows and num_eq(sp.N(numrows[0]), expected, 1e-4)
    results.append((tag, "PASS" if okp else "FAIL-SILENT",
                    (data.get("plain") or "")[:44]))

# --- matrix calculator: input mathfield LaTeX NxN ---
try:
    m1 = mathlab.tool_matrix({"matrix":
        r"\begin{pmatrix}1 & 2 \\ 3 & 4\end{pmatrix}", "op": "det"})
    m2 = mathlab.tool_matrix({"matrix":
        r"\begin{bmatrix}1 & 0 & 0 \\ 0 & 1 & 0 \\ 0 & 0 & 1\end{bmatrix}",
        "op": "det"})
    m3 = mathlab.tool_matrix({"matrix":
        r"\begin{pmatrix}\frac{1}{2} & 0 \\ 0 & 4\end{pmatrix}", "op": "det"})
    okm = (m1["rows"][0][1] == "-2" and m2["rows"][0][1] == "1"
           and m3["rows"][0][1] == "2")
    results.append(("MATRIX: pmatrix/bmatrix/frac via mathfield",
                    "PASS" if okm else "FAIL-SILENT",
                    f"{m1['rows'][0][1]}, {m2['rows'][0][1]}, {m3['rows'][0][1]}"))
except Exception as e:
    results.append(("MATRIX: pmatrix via mathfield", "FAIL-VISIBLE", str(e)[:60]))

# --- batas/titik tidak valid (setengah diisi di mathfield) -> pesan bersih ---
try:
    mathlab.tool_integral({"op_data": {"op": "integral", "body": "x", "var": "x",
        "has_bounds": True, "a": "n=", "b": "3"}, "expr": "", "mode": "def"})
    results.append(("BOUND invalid (a='n=')", "FAIL-SILENT", "tidak ditolak"))
except mathlab.LabError as e:
    ok = e.key == "err.bound_invalid"
    results.append(("BOUND invalid (a='n=')",
                    "PASS-WARN" if ok else "FAIL-WRONG-KEY", e.key))
except Exception as e:
    results.append(("BOUND invalid (a='n=')", "FAIL-VISIBLE", str(e)[:60]))

# --- property test anti dobel-apply (report: independent oracle) ---
prop_ok = True
try:
    d1, _ = run_case(r"\int x^2 dx")
    d2, _ = run_case(r"\frac{d}{dx} x^2")
    a1 = sp.sympify(d1["plain"]); a2 = sp.sympify(d2["plain"])
    prop_ok = sp.simplify(sp.diff(a1, x) - x**2) == 0 and sp.simplify(a2 - 2*x) == 0
except Exception as e:
    prop_ok = False
results.append(("PROPERTY: d(indef(f))==f & d/dx x^2==2x",
                "PASS" if prop_ok else "FAIL-SILENT", ""))

# --- tool lain yang share parser: matrix input di tool integral ---
try:
    la2plain_frontend(r"\det\begin{pmatrix}1&2\\3&4\end{pmatrix}")
    mres = mathlab.tool_integral({
        "expr": la2plain_frontend(r"\begin{pmatrix}1&2\\3&4\end{pmatrix}"),
        "mode": "auto"})
    results.append((r"G: \begin{pmatrix} di tool integral", "FAIL-SILENT",
                    "kepaksa hasil?"))
except mathlab.LabError:
    results.append((r"G: \begin{pmatrix} di tool integral", "PASS-WARN",
                    "pesan eksplisit"))
except Exception as e:
    results.append((r"G: \begin{pmatrix} di tool integral", "FAIL-VISIBLE",
                    str(e)[:60]))

# ----------------------------------------------------------------
# 5) LAPORAN
# ----------------------------------------------------------------
w = max(len(r[0]) for r in results) + 2
print("=" * (w + 34))
print("HASIL (frontend ASLI + backend ASLI):")
print("=" * (w + 34))
for tag, cls, info in results:
    mark = {"PASS": "OK ", "PASS-WARN": "OKw"}.get(cls, "!!!")
    print(f"{mark} {tag:<{w}} {cls:<16} {info}")
from collections import Counter
cnt = Counter(r[1] for r in results)
print("-" * (w + 34))
print("RINGKASAN:", dict(cnt))
fails = [r for r in results if r[1].startswith("FAIL")]
sys.exit(1 if fails else 0)
