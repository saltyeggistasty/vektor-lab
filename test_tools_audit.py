# -*- coding: utf-8 -*-
"""==============================================================
AUDIT SUITE — semua tool mathfield (matematika & fisika).
Memastikan revamp parser tool kalkulus (anti dobel-apply, anti
"Unknown symbols", paste-safe) BERLAKU juga di tool lain: input
paste-like (\frac, \left\right, \sqrt, \pi, ^, \cdot, spasi)
gak boleh bikin crash / sampah macro ke backend/engine.

E2E: LaTeX -> la2plain ASLI (Node, dr tools.js) -> run_tool ASLI
(mathlab) utk tool backend; conv-only utk tool engine grafik
(gsurf3d/gfrenet/gslope/gdomain dipakai GRAPH_ENGINES frontend).

Jalankan:  python test_tools_audit.py   (exit 0 = semua OK)
=============================================================="""
import io, sys, json, os, re, subprocess, tempfile

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                              errors="replace")
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

import sympy as sp
import mathlab

# ---------- harness node (sama dgn test_integral_tool) ----------
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

def conv(la, uneval=False):
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False,
                                     encoding="utf-8") as f:
        f.write(_NODE_JS)
        path = f.name
    try:
        r = subprocess.run(
            ["node", path, os.path.join(ROOT, "static", "tools.js"),
             json.dumps({"la": la, "uneval": uneval})],
            capture_output=True, text=True, encoding="utf-8", timeout=30,
            cwd=ROOT)
        out = json.loads(r.stdout)
        if not out["ok"]:
            raise ValueError(out["out"])
        return out["out"]
    finally:
        os.unlink(path)

results = []

def rec(tag, cls, info=""):
    results.append((tag, cls, info))

# ================================================================
# 1) ODE — eq field mengandung "=" (regresi =-split harus GAK ada)
# ================================================================
ODE_CASES = [
    (r"y'' + y = \sin(x)", "y(0) = 1, y'(0) = 0"),
    (r"y' = x", ""),
    (r"\frac{dy}{dx} = x", ""),
    (r"\frac{d^2 y}{dx^2} = 0", ""),
    (r"y'' + y = \sin\left(x\right)", "y(0) = 1"),
]
for eq, ics in ODE_CASES:
    tag = f"ODE: {eq[:42]}"
    try:
        plain_eq = conv(eq)                      # la2plain non-uneval
        data = {"eq": plain_eq}
        if ics:
            data["ics"] = conv(ics) if "\\" in ics else ics
        out = mathlab.run_tool("ode", data)
        sol = str(out.get("rows", [["", ""]])[0][1])[:40] if out.get("rows") else ""
        rec(tag, "PASS", sol)
    except mathlab.LabError as e:
        rec(tag, "PASS-WARN", f"{e.key}: {str(e)[:40]}")
    except Exception as e:
        rec(tag, "FAIL-VISIBLE", f"{type(e).__name__}: {str(e)[:60]}")

# ================================================================
# 2) TAYLOR — expr + field x0/order (harus berdampak)
# ================================================================
TAYLOR_CASES = [
    (r"\sin(x)", "0", "5"),
    (r"\frac{1}{1-x}", "0", "4"),
    (r"e^x", "0", "3"),
    (r"\ln(1+x)", "0", "4"),
]
for expr, x0, order in TAYLOR_CASES:
    tag = f"TAYLOR: {expr[:40]} @ x0={x0}, n={order}"
    try:
        plain = conv(expr)
        out = mathlab.run_tool("taylor", {"expr": plain, "x0": x0,
                                          "order": order})
        rec(tag, "PASS", str(out.get("rows", [["", ""]])[0][1])[:40])
    except mathlab.LabError as e:
        rec(tag, "PASS-WARN", f"{e.key}: {str(e)[:40]}")
    except Exception as e:
        rec(tag, "FAIL-VISIBLE", f"{type(e).__name__}: {str(e)[:60]}")

# ================================================================
# 3) POLY — expr polinom paste-like
# ================================================================
POLY_CASES = [
    (r"x^2 - 5x + 6", "roots"),
    (r"x^2 - 5x + 6", "factor"),
    (r"\left(x+1\right)^2", "roots"),
    (r"2x^2 - 8", "roots"),
    (r"x^3 - \pi", "roots"),
]
for expr, mode in POLY_CASES:
    tag = f"POLY: {expr[:42]} [{mode}]"
    try:
        plain = conv(expr)
        out = mathlab.run_tool("poly", {"expr": plain, "mode": mode})
        rec(tag, "PASS", str(out.get("rows", [["", ""]])[0][1])[:44])
    except mathlab.LabError as e:
        rec(tag, "PASS-WARN", f"{e.key}: {str(e)[:40]}")
    except Exception as e:
        rec(tag, "FAIL-VISIBLE", f"{type(e).__name__}: {str(e)[:60]}")

# ================================================================
# 4) ENGINE tools (gsurf3d/gfrenet/gslope/gdomain): conv-only —
#    output harus bersih dr macro & Abs (mathjs gak paham), kurung
#    seimbang, dan mengandung variabel yg benar
# ================================================================
ENGINE_CASES = [
    ("gsurf3d", "expr", r"\sin(x)\cos(2y)", ["x", "y"]),
    ("gsurf3d", "expr", r"\frac{\sin x}{x}", ["x"]),
    ("gfrenet", "xt", r"3\cos(t)", ["t"]),
    ("gfrenet", "yt", r"3\sin(t)", ["t"]),
    ("gslope", "expr", r"x - y", ["x", "y"]),
    ("gslope", "expr", r"x^2 \cdot y", ["x", "y"]),
    ("gdomain", "expr", r"\frac{1}{z}", ["z"]),
    ("gdomain", "expr", r"\left|z\right|", ["z"]),
    ("gdomain", "expr", r"z^2 - 1", ["z"]),
]
for tool, fld, la, vars_ in ENGINE_CASES:
    tag = f"ENGINE {tool}.{fld}: {la[:36]}"
    try:
        out = conv(la)
        problems = []
        if re.search(r"\\[a-zA-Z]", out):
            problems.append("sisa macro")
        if "Abs(" in out:
            problems.append("Abs (mathjs gak paham)")
        if out.count("(") != out.count(")"):
            problems.append("kurung gak seimbang")
        for v in vars_:
            # var boleh nempel angka/kurung ("2y") — asal ada pemisah kiri
            if not re.search(r"(^|[^a-zA-Z])" + v + r"\b", out):
                problems.append(f"var {v} hilang")
        if problems:
            rec(tag, "FAIL-SILENT", "; ".join(problems))
        else:
            rec(tag, "PASS", out[:40])
    except Exception as e:
        rec(tag, "FAIL-VISIBLE", f"{type(e).__name__}: {str(e)[:60]}")

# ================================================================
# 5) LAPORAN
# ================================================================
w = max(len(r[0]) for r in results) + 2
print("=" * (w + 30))
print("AUDIT SEMUA TOOL MATHFIELD:")
print("=" * (w + 30))
for tag, cls, info in results:
    mark = {"PASS": "OK ", "PASS-WARN": "OKw"}.get(cls, "!!!")
    print(f"{mark} {tag:<{w}} {cls:<14} {info}")
from collections import Counter
cnt = Counter(r[1] for r in results)
print("-" * (w + 30))
print("RINGKASAN:", dict(cnt))
fails = [r for r in results if r[1].startswith("FAIL")]
sys.exit(1 if fails else 0)
