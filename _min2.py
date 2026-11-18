# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import sympy as sp
i = sp.Symbol("i", integer=True, positive=True)
j = sp.Symbol("j", integer=True, positive=True)
s1 = sp.Sum(i*j, (j, 1, 3), (i, 1, 3))
print("multi-limit:", s1, "-> doit:", s1.doit())
s2 = sp.Sum(sp.Sum(i*j, (j, 1, 3)), (i, 1, 3))
print("nested:", s2, "-> doit:", s2.doit())
# L22 minimal
a0 = sp.sqrt(sp.pi)*sp.erfi(x)/2/x if False else None
import sympy
L = sp.Limit(sp.sqrt(sp.pi)*sp.erfi(x)/(2*x), x, 0)
print("L22 direct:", L.doit())
print("L22 limit fn:", sp.limit(sp.sqrt(sp.pi)*sp.erfi(x)/(2*x), x, 0))
# series
print("series:", sp.sqrt(sp.pi)*sp.erfi(x)/(2*x).series(x, 0, 4))
