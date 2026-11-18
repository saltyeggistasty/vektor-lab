# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = r"G:\vektor-lab(1)\vektor-lab"
sys.path.insert(0, ROOT)
import mathlab
e = mathlab._expr_int("ij", assume_int=("i", "j"))
print("expr:", e)
for s in e.free_symbols:
    print("  sym:", s, {kk: vv for kk, vv in s.assumptions0.items()
                        if kk in ("integer", "positive")})
