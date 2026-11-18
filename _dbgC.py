# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = r"G:\vektor-lab(1)\vektor-lab"
sys.path.insert(0, ROOT)
import sympy as sp
import mathlab
from test_benchmark import conv

# L22 debug
plain = conv(r"\lim_{x\to 0}\frac{1}{x}\int_0^x e^{t^2}\,dt", uneval=True)
print("L01 conv:", plain[:120])
opd = json.loads(plain[12:])
expr = mathlab._build_op(opd)
print("built:", repr(expr)[:120])
print("args:", [repr(a)[:60] for a in expr.args])
a0 = expr.args[0].doit()
print("args[0].doit:", repr(a0)[:100])
res = sp.Limit(a0, expr.args[1], expr.args[2]).doit()
print("limit:", res)

# C05 debug
plain2 = conv(r"\sum_{k=1}^{4}\int_0^1 x^k\,dx", uneval=True)
opd2 = json.loads(plain2[12:])
print("C05 opd:", json.dumps(opd2)[:150])
inner = opd2["body"]
print("inner body:", inner.get("body") if isinstance(inner, dict) else inner)
e = mathlab._expr_int(inner["body"] if isinstance(inner, dict) else inner,
                      assume_int=("k",))
print("inner expr:", e, "| free_symbols:", [(s.name, s.assumptions0) for s in e.free_symbols])
