# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = r"G:\vektor-lab(1)\vektor-lab"
sys.path.insert(0, ROOT)
import sympy as sp
import mathlab
from test_benchmark import conv

print("_expr_int ij:", mathlab._expr_int("ij"))

# S20 full
plain = conv(r"\sum_{i=1}^{3}\sum_{j=1}^{3}ij", uneval=True)
print("conv:", plain[:150])
opd = json.loads(plain[12:])
print("opd:", json.dumps(opd)[:200])
expr = mathlab._build_op(opd, int_syms=())
print("built:", repr(expr)[:100])
res = expr.doit()
print("doit:", res)
out = mathlab.run_tool("integral", {"op_data": opd, "expr": "", "mode": "sum"})
print("run_tool plain:", out.get("plain"))

# L22 debug
plain2 = conv(r"\lim_{x\to 0}\frac{1}{x}\int_0^x e^{t^2}\,dt", uneval=True)
opd2 = json.loads(plain2[12:])
print("L22 opd:", json.dumps(opd2)[:180])
expr2 = mathlab._build_op(opd2)
print("built:", repr(expr2)[:100])
a0 = expr2.args[0].doit()
print("a0.doit:", a0)
r2 = sp.Limit(a0, expr2.args[1], expr2.args[2]).doit()
print("limit:", r2)
