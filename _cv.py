# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import sympy as sp
x = sp.Symbol("x")
k = sp.Symbol("k", integer=True, positive=True)
I = sp.Integral(x**k, (x, 0, 1))
print("doit     :", I.doit())
print("integrate:", sp.integrate(x**k, (x, 0, 1)))
