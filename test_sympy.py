import sympy as sp
i = sp.Symbol('i')
n = sp.Symbol('n')
body = i**2
start = 0
end = n
res = sp.summation(body, (i, start, end))
print("Sum of i^2 from 0 to n:", res)
print("Simplified:", sp.simplify(res))