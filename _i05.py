# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = r"G:\vektor-lab(1)\vektor-lab"
sys.path.insert(0, ROOT)
import mathlab
from test_benchmark import conv

plain = conv(r"\int \frac{1}{x^2-1}\,dx", uneval=True)
print("conv:", plain[:100])
data = {"expr": plain, "mode": "indef"}
if plain.startswith("__NABLA_OP__"):
    data["op_data"] = json.loads(plain[12:])
    data["expr"] = ""
out = mathlab.run_tool("integral", data)
print("plain:", out.get("plain"))
print("rows:", [r[1] for r in out["rows"]])
