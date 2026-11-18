# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = r"G:\vektor-lab(1)\vektor-lab"
sys.path.insert(0, ROOT)
import mathlab
from test_benchmark import conv

plain = conv(r"\sum_{k=1}^{4}\int_0^1 x^k\,dx", uneval=True)
print("conv:", plain[:140])
opd = json.loads(plain[12:])
print("opd:", json.dumps(opd)[:200])
expr = mathlab._build_op(opd)
print("built:", repr(expr)[:140])
for s in expr.free_symbols:
    print("  sym:", s, {kk: vv for kk, vv in s.assumptions0.items()
                        if kk in ("integer", "positive")})
print("doit:", repr(expr.doit())[:120])
out = mathlab.run_tool("integral", {"op_data": opd, "expr": "", "mode": "sum"})
print("run_tool plain:", out.get("plain"))
