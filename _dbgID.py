# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = r"G:\vektor-lab(1)\vektor-lab"
sys.path.insert(0, ROOT)
import sympy as sp
import mathlab
from test_benchmark import conv

plain = conv(r"\sum_{i=1}^{3}\sum_{j=1}^{3}ij", uneval=True)
opd = json.loads(plain[12:])
expr = mathlab._build_op(opd, int_syms=())
print("built:", expr)
for s in expr.free_symbols:
    print("  sym:", s, "assumptions:", {kk: vv for kk, vv in s.assumptions0.items() if kk in ("integer", "positive")})
print("limits:", expr.limits)
for lim in expr.limits:
    print("  lim var:", lim[0], "assumptions:", {kk: vv for kk, vv in lim[0].assumptions0.items() if kk in ("integer", "positive")})
# body function
fn = expr.function
print("function:", fn)
for s in fn.free_symbols:
    print("  fn sym:", s, "assumptions:", {kk: vv for kk, vv in s.assumptions0.items() if kk in ("integer", "positive")})
