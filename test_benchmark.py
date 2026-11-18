# -*- coding: utf-8 -*-
"""==============================================================
BENCHMARK — Integrals & Limits (bug_reports2.md deliverable).
Semua kasus report: L01-23, D01-16, S01-22, I01-12, DI01-24,
C01-08 (nested), P01-28 (fn powers), V01-07 (varian K1).
E2E: LaTeX -> la2plain ASLI (Node/tools.js) -> mathlab.run_tool ASLI.
Tiap kasus dijalankan di NATIVE mode + AUTO mode (rule 7).
Klasifikasi: PASS / PASS-FORMAT / PASS-WARN / FAIL-VISIBLE /
FAIL-SILENT / TIMEOUT. Format checks F01-F09 (section 11.3).

Jalankan:  python test_benchmark.py [filter]
=============================================================="""
import io, sys, json, os, re, subprocess, tempfile, time, random
from concurrent.futures import ThreadPoolExecutor

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                              errors="replace")
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

import sympy as sp
import mathlab

x, y, t, n, k, i, j = sp.symbols("x y t n k i j")
NS = {"x": x, "y": y, "t": t, "n": n, "k": k, "i": i, "j": j,
      "E": sp.E, "pi": sp.pi, "oo": sp.oo, "Abs": sp.Abs}

random.seed(7)

# ----------------------------------------------------------------
# harness: konversi frontend ASLI (node) + backend ASLI
# ----------------------------------------------------------------
_NODE_JS = r"""
const fs = require("fs");
const src = fs.readFileSync(process.argv[2], "utf8");
const start = src.indexOf("function readGroup");
const end = src.indexOf("const TOOLS");
if (start < 0 || end < 0) { console.error("extract fail"); process.exit(2); }
eval(src.slice(start, end));
const inp = JSON.parse(process.argv[3]);
try {
  console.log(JSON.stringify({ ok: true,
    out: la2plain(inp.la, { unevaluated: !!inp.uneval }) }));
} catch (e) {
  console.log(JSON.stringify({ ok: false, out: String(e) }));
}
"""

def conv(la, uneval=True):
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False,
                                     encoding="utf-8") as f:
        f.write(_NODE_JS)
        path = f.name
    try:
        r = subprocess.run(
            ["node", path, os.path.join(ROOT, "static", "tools.js"),
             json.dumps({"la": la, "uneval": uneval})],
            capture_output=True, text=True, encoding="utf-8", timeout=20,
            cwd=ROOT)
        return json.loads(r.stdout)["out"]
    finally:
        os.unlink(path)

MODE_MAP = {"limit": "lim", "derivative": "diff", "sum": "sum",
            "indefinite": "indef", "definite": "def", "auto": "auto",
            "product": "prod"}

def backend_run(case, mode_key):
    plain = conv(case["latex"], uneval=True)
    data = {"expr": plain, "mode": mode_key}
    if plain.startswith("__NABLA_OP__"):
        data["op_data"] = json.loads(plain[12:])
        data["expr"] = ""
    data.update({kk: vv for kk, vv in case["fields"].items()})
    t0 = time.time()
    out = mathlab.run_tool("integral", data)
    return out, (time.time() - t0) * 1000

# ----------------------------------------------------------------
# comparator (report section 3)
# ----------------------------------------------------------------
def _numeric_equal(f, g, lo=0.3, hi=2.5, kk=6, tol=1e-6):
    try:
        for _ in range(kk):
            p = random.uniform(lo, hi)
            d = (f - g).subs(x, p)
            if abs(complex(sp.N(d))) > tol:
                return False
        return True
    except Exception:
        return False

def matches(expected, plain):
    exp = sp.sympify(expected, locals=NS)
    got = sp.sympify(str(plain).replace("+ C", "").replace("+C", ""),
                     locals=NS)
    if sp.simplify(got - exp) == 0:
        return True
    try:
        if abs(sp.N(got) - sp.N(exp)) < 1e-9:
            return True
    except (TypeError, ValueError):
        pass
    return _numeric_equal(got, exp)

# ----------------------------------------------------------------
# CASES (report sections 4-10)
# ----------------------------------------------------------------
def T(cid, mode, latex, expected, kind="exact", tier=1, **fields):
    return {"id": cid, "mode": mode, "latex": latex, "expected": expected,
            "kind": kind, "tier": tier, "fields": fields}

CASES = []
CASES += [
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
CASES += [
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
 T("D12","derivative",r"\frac{d}{dx}\left(x^3\ln x\right)","4*E**2",xo="e"),
 T("D13","derivative",r"\frac{d}{dx}\int_0^{x^2}e^{-t^2}\,dt","2*x*exp(-x**4)"),
 T("D14","derivative",r"\frac{d}{dx}\int_1^{x}\frac{\sin t}{t}\,dt","sin(x)/x"),
 T("D15","derivative",r"\frac{\partial}{\partial x}\left(x^2y+\sin(xy)\right)","2*x*y+y*cos(x*y)"),
 T("D16","derivative",r"\frac{\partial^2}{\partial x\,\partial y}\left(x^3y^2\right)","6*x**2*y"),
]
CASES += [
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
 T("S17","sum",r"\sum_{k=0}^{20}\left(\frac{1}{k}-\frac{1}{k+1}\right)","Rational(20,21)"),
 T("S18","sum",r"\sum_{k=0}^{10}\binom{10}{k}","1024"),
 T("S19","sum",r"\sum_{i=1}^{5}\sum_{j=1}^{i}j","35",tier=2),
 T("S20","sum",r"\sum_{i=1}^{3}\sum_{j=1}^{3}ij","36",tier=2),
 T("S21","sum",r"\prod_{k=1}^{10}k","3628800"),
 T("S22","sum",r"\prod_{n=2}^{\infty}\left(1-\frac{1}{n^2}\right)","Rational(1,2)",tier=2),
]
CASES += [
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
 T("I12","indefinite",r"\int \frac{x^3+2x}{(x^2+1)^2}\,dx","log(x**2+1)/2-1/(2*(x**2+1))",kind="antiderivative"),
]
CASES += [
 T("DI01","definite",r"\int_0^1 x^2e^x\,dx","E-2"),
 T("DI02","definite",r"\int_0^{\pi}\sin^2x\,dx","pi/2"),
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
 T("DI23","definite",r"\int_0^1\int_0^1 xy\,dx\,dy","Rational(1,4)",tier=2),
 T("DI24","definite",r"\int_0^1\int_0^x y\,dy\,dx","Rational(1,6)",tier=2),
]
CASES += [
 T("C01","definite",r"\int_0^1\frac{d}{dx}\left(x^3e^x\right)dx","E"),
 T("C02","derivative",r"\frac{d}{dx}\left[\int_0^x t^2e^{-t}\,dt\right]","exp(-1)",xo="1"),
 T("C03","indefinite",r"\int \frac{d}{dx}\left(x^3\right)dx","x**3",kind="antiderivative"),
 T("C04","derivative",r"\frac{d}{dx}\int x^2\,dx","x**2"),
 T("C05","sum",r"\sum_{k=1}^{4}\int_0^1 x^k\,dx","Rational(77,60)"),
 T("C06","definite",r"\int_0^1\sum_{n=0}^{3}x^n\,dx","Rational(25,12)"),
 T("C07","limit",r"\lim_{x\to 0}\frac{1}{x^2}\int_0^x\sin t\,dt","Rational(1,2)"),
 T("C08","derivative",r"\frac{d}{dx}\sum_{n=0}^{3}x^n","1+2*x+3*x**2"),
]
CASES += [
 T("P01","indefinite",r"\int \sin^2 x\,dx","x/2-sin(2*x)/4",kind="antiderivative"),
 T("P02","indefinite",r"\int \cos^2 x\,dx","x/2+sin(2*x)/4",kind="antiderivative"),
 T("P03","indefinite",r"\int \tan^2 x\,dx","tan(x)-x",kind="antiderivative"),
 T("P04","indefinite",r"\int \sec^2 x\,dx","tan(x)",kind="antiderivative"),
 T("P05","indefinite",r"\int \sin^2 x\cos x\,dx","sin(x)**3/3",kind="antiderivative"),
 T("P06","indefinite",r"\int \sin^{2}{x}\,dx","x/2-sin(2*x)/4",kind="antiderivative"),
 T("P07","indefinite",r"\int \sin^2(x)\,dx","x/2-sin(2*x)/4",kind="antiderivative"),
 T("P08","indefinite",r"\int \sin^2 2x\,dx","x/2-sin(4*x)/8",kind="antiderivative"),
 T("P09","indefinite",r"\int \ln^2 x\,dx","x*log(x)**2-2*x*log(x)+2*x",kind="antiderivative"),
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
 T("P20","limit",r"\lim_{x\to 0}\frac{\sin^2 x}{x^2}","1"),
 T("P21","limit",r"\lim_{x\to 0}\frac{\tan^2 x}{x^2}","1"),
 T("P22","definite",r"\int_0^{\pi}\cos^2 x\,dx","pi/2"),
 T("P23","definite",r"\int_0^{\pi/2}\sin^2 x\cos^2 x\,dx","pi/16"),
 T("P24","definite",r"\int_0^1\ln^2 x\,dx","2"),
 T("P25","sum",r"\sum_{k=1}^{3}\sin^2\left(\frac{k\pi}{2}\right)","2"),
 T("P26","auto",r"\sin^2\left(\frac{\pi}{6}\right)","Rational(1,4)"),
 T("P27","auto",r"\sin^2 x+\cos^2 x","1"),
 T("P28","auto",r"\sin^{-1}(1)","pi/2"),
]
CASES += [T(f"V{ii:02d}","definite",ss,"pi/2") for ii, ss in enumerate([
 r"\int_0^{\pi}\sin^2x\,dx",
 r"\int_0^{\pi}\sin^2xdx",
 r"\int_0^{\pi}\sin^2 x\ dx",
 r"\int_0^{\pi}\sin^{2}x\,\mathrm{d}x",
 r"\int_0^{\pi}\sin^2\left(x\right)dx",
 r"\int_0^{\pi}\left(\sin x\right)^2dx",
 r"\int_0^\pi \sin^2 x \, dx",
], 1)]

# ----------------------------------------------------------------
# RUN: native mode + auto (rule 7), thread timeout 20s
# ----------------------------------------------------------------
def run_case_safe(case, mode_key):
    t0 = time.time()
    try:
        with ThreadPoolExecutor(max_workers=1) as ex:
            fut = ex.submit(_run_inner, case, mode_key)
            try:
                r = fut.result(timeout=20)
            except TimeoutError:
                return {"cls": "TIMEOUT", "info": ">20s", "ms": 20000}
            r["ms"] = round((time.time() - t0) * 1000)
            return r
    except mathlab.LabError as e:
        return {"cls": "PASS-WARN", "info": f"{e.key}: {str(e)[:44]}", "ms": 0}
    except Exception as e:
        import traceback
        traceback.print_exc()   # FAIL-VISIBLE selalu disertai traceback
        return {"cls": "FAIL-VISIBLE", "info": f"{type(e).__name__}: {str(e)[:60]}",
                "ms": 0}

def _run_inner(case, mode_key):
    out, ms = backend_run(case, mode_key)
    rows = out.get("rows", [])
    sym_row = next((r[1] for r in rows if r[0] in ("sym", "dxn", "sumv",
                     "prodv", "R", "dval")), "")
    num_row = next((r[1] for r in rows if r[0] == "num"), "")
    dval_row = next((r[1] for r in rows if r[0] == "dval"), "")
    plain = out.get("plain", "")
    try:
        if case["kind"] == "diverges":
            ok = (plain in ("oo", "-oo", "zoo", "nan") or
                  "diverge" in plain.lower())
        else:
            # kasus dgn titik evaluasi: bandingkan dval (nilai di titik)
            if case["fields"].get("xo") and dval_row:
                ok = matches(case["expected"], dval_row)
            else:
                ok = matches(case["expected"], plain if plain else sym_row)
            if not ok and num_row:
                try:
                    ok = abs(sp.N(sp.sympify(num_row)) -
                             sp.N(sp.sympify(case["expected"], locals=NS))) < 1e-6
                except Exception:
                    pass
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"cls": "FAIL-VISIBLE", "info": f"check {e}", "latex": sym_row,
                "plain": plain}
    info = plain[:44]
    if ok:
        viol = []
        for pat in (r"\*\*", r"\blog\(", r"\\log(?!_)", r"\bAbs\b", r"\batan\b",
                    r"\boo\b", r"\bzoo\b", r"\bnan\b", r"\\operatorname\{a"):
            if re.search(pat, sym_row):
                viol.append(pat.strip("\\^"))
        return {"cls": "PASS" if not viol else "PASS-FORMAT",
                "info": ("fmt:" + ",".join(viol)) if viol else info,
                "latex": sym_row, "plain": plain}
    return {"cls": "FAIL-SILENT", "info": info, "latex": sym_row, "plain": plain}

# ----------------------------------------------------------------
if __name__ == "__main__":
    MAIN_FILTER = sys.argv[1] if len(sys.argv) > 1 else ""
    results = []
    for case in CASES:
        if MAIN_FILTER and MAIN_FILTER.lower() not in case["id"].lower():
            continue
        native = {"limit": "lim", "derivative": "diff", "sum": "sum",
                  "indefinite": "indef", "definite": "def",
                  "auto": "auto"}.get(case["mode"], case["mode"])
        r1 = run_case_safe(case, native)
        results.append((f"{case['id']} [{native}]", r1["cls"], r1["info"]))
        if case["mode"] != "auto":      # rule 7: native + auto
            r2 = run_case_safe(case, "auto")
            results.append((f"{case['id']} [auto]", r2["cls"], r2["info"]))

    w = max(len(r[0]) for r in results) + 2
    print("=" * (w + 30))
    print("BENCHMARK (E2E: conv ASLI + backend ASLI):")
    print("=" * (w + 30))
    for tag, cls, info in results:
        mark = {"PASS": "OK ", "PASS-FORMAT": "OKf", "PASS-WARN": "OKw"}.get(cls, "!!!")
        print(f"{mark} {tag:<{w}} {cls:<14} {info}")
    from collections import Counter
    cnt = Counter(r[1] for r in results)
    print("-" * (w + 30))
    print("RINGKASAN:", dict(cnt))
    bad = [r for r in results if r[1].startswith("FAIL") or r[1] == "TIMEOUT"]
    sys.exit(1 if bad else 0)
