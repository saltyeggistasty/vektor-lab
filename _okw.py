# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
out = open(r"G:\vektor-lab(1)\vektor-lab\_bench_out.txt",
           encoding="utf-8", errors="replace").read()
for ln in out.splitlines():
    if ln.startswith("OKw"):
        print(ln[:120])
