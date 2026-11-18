# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import sympy as sp
x = sp.Symbol("x")
k = sp.Symbol("k", integer=True, positive=True)
inner = sp.Integral(x**k, (x, 0, 1))
s = sp.Sum(inner, (k, 1, 4))
print("Sum doit:", s.doit())
# alternatif: doit inner dulu, lalu sum
r = sp.Sum(inner.doit(), (k, 1, 4)).doit()
print("inner-dulu:", r)
