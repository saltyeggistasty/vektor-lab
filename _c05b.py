# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = r"G:\vektor-lab(1)\vektor-lab"
sys.path.insert(0, ROOT)
import mathlab
from test_benchmark import conv
plain = conv(r"\sum_{k=1}^{4}\int_0^1 x^k\,dx", uneval=True)
opd = json.loads(plain[12:]) if plain.startswith("__NABLA_OP__") else None
print("opd:", json.dumps(opd)[:180] if opd else plain[:80])
out = mathlab.run_tool("integral", {"op_data": opd, "expr": "", "mode": "sum"})
print("C05:", out.get("plain"))
