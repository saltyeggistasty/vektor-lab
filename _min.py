# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import sympy as sp
x = sp.Symbol("x")
k = sp.Symbol("k", integer=True, positive=True)

# L22 minimal
a0 = sp.sqrt(sp.pi)*sp.erfi(x)/2
print("limit erfi/x:", sp.Limit(a0, x, 0).doit())
print("limit erfi/x (limit fn):", sp.limit(a0, x, 0))

# C05 minimal
inner = sp.Integral(x**k, (x, 0, 1))
print("inner doit:", inner.doit())
s = sp.Sum(inner, (k, 1, 4))
print("Sum doit:", s.doit())
s2 = sp.Sum(1/(k+1), (k, 1, 4))
print("Sum 1/(k+1):", s2.doit())
