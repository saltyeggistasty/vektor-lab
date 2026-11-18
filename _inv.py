# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"G:\vektor-lab(1)\vektor-lab")
import sympy as sp
import mathlab

x = sp.Symbol("x")
# 1) C05: asumsi index k pada inner Integral
k = sp.Symbol("k", integer=True, positive=True)
print("C05 integrate:", sp.integrate(x**k, (x, 0, 1)))
inner = sp.Integral(x**k, (x, 0, 1))
print("C05 Sum:", sp.Sum(inner, (k, 1, 4)).doit())

# 2) S20: nested sums
i2 = sp.Symbol("i", integer=True, positive=True)
j2 = sp.Symbol("j", integer=True, positive=True)
s20 = sp.Sum(sp.Sum(i2*j2, (j2, 1, 3)), (i2, 1, 3))
print("S20:", s20.doit())

# 3) L22: Limit(Integral) doit
t = sp.Symbol("t")
L = sp.Limit(sp.Integral(sp.exp(t**2), (t, 0, x))/x, x, 0)
print("L22 raw doit:", L.doit())
print("L22 deep:", L.doit(deep=True))

# 4) I05 matches numeric
import mathlab as m
r = mathlab.run_tool("integral", {"expr": "1/(x**2-1)", "mode": "indef"})
print("I05 plain:", r.get("plain"))
