import vectorcalc as vc
expr = r"\sum_{i=0}^{n} i^2"
try:
    parsed = vc.parse(expr)
    print("Parsed:", parsed)
except Exception as e:
    print("Error:", e)