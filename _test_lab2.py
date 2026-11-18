# Uji referensi gelombang 2 (10 tool baru).
import math
import mathlab as ml

PASS = FAIL = 0

def check(name, got, want, tol=1e-5):
    global PASS, FAIL
    ok = False
    try:
        ok = abs(float(got) - float(want)) <= tol * max(1.0, abs(float(want)))
    except (TypeError, ValueError):
        ok = str(got) == str(want)
    if ok:
        PASS += 1
        print(f"PASS {name}: {got}")
    else:
        FAIL += 1
        print(f"FAIL {name}: got={got} want={want}")

def row(r, key):
    return [x for x in r["rows"] if x[0] == key][0][1]

# complex
r = ml.run_tool("complex", {"mode": "polar", "re": "1", "im": "1"})
check("cplx abs", row(r, "abs"), math.sqrt(2), 1e-4)
check("cplx arg deg", row(r, "arg_deg").split()[0], 45, 1e-6)
r = ml.run_tool("complex", {"mode": "power", "re": "1", "im": "1", "n": "8"})
check("cplx (1+i)^8", row(r, "num").split()[0], 16, 1e-6)
r = ml.run_tool("complex", {"mode": "roots", "re": "8", "im": "0", "n": "3"})
check("cplx root1", row(r, "w1").split()[0], 2, 1e-6)
assert len(r["rows"]) == 3

# taylor
r = ml.run_tool("taylor", {"expr": "exp(x)", "x0": 0, "order": 4})
print("  taylor:", row(r, "poly"))
assert "x**3/6" in row(r, "poly").replace("\\frac{x^{3}}{6}", "x**3/6") or "\\frac{x^{3}}{6}" in row(r, "poly")

# modmath
r = ml.run_tool("modmath", {"mode": "powmod", "a": "2", "b": "10", "n": "1000"})
check("modmath pow", row(r, "res"), 24)
r = ml.run_tool("modmath", {"mode": "invmod", "a": "3", "n": "11"})
check("modmath inv", row(r, "inv"), 4)
r = ml.run_tool("modmath", {"mode": "gcd", "a": "12", "b": "18"})
check("modmath gcd", row(r, "gcd"), 6)
check("modmath lcm", row(r, "lcm"), 36)
r = ml.run_tool("modmath", {"mode": "prime", "n": "97"})
check("modmath prime97", row(r, "prime"), "ya")
r = ml.run_tool("modmath", {"mode": "prime", "n": "360"})
print("  factor 360:", row(r, "factor"))
try:
    ml.run_tool("modmath", {"mode": "invmod", "a": "2", "n": "4"})
    print("FAIL invmod no-inverse should raise")
except ml.LabError:
    print("PASS invmod no-inverse raises")

# entropy
r = ml.run_tool("entropy", {"probs": "0.5, 0.5"})
check("entropy H(0.5,0.5)", row(r, "H").split()[0], 1, 1e-9)
check("entropy Hmax", row(r, "H_max").split()[0], 1, 1e-9)
r = ml.run_tool("entropy", {"probs": "0.125 0.125 0.125 0.125 0.125 0.125 0.125 0.125"})
check("entropy H(8 uniform)", row(r, "H").split()[0], 3, 1e-9)
try:
    ml.run_tool("entropy", {"probs": "0.5, 0.4"})
    print("FAIL entropy sum!=1 should raise")
except ml.LabError:
    print("PASS entropy sum!=1 raises")

# poly
r = ml.run_tool("poly", {"coeffs": "1,-5,6", "mode": "roots"})
print("  roots:", [row(r, "x1"), row(r, "x2")])
check("poly root a", row(r, "x1"), 2, 1e-9)
check("poly root b", row(r, "x2"), 3, 1e-9)
r = ml.run_tool("poly", {"coeffs": "1,-5,6", "mode": "factor"})
print("  factor:", row(r, "R"))
assert "3" in row(r, "R") and "2" in row(r, "R")

# heatexp
r = ml.run_tool("heatexp", {"mode": "heat", "m": "1", "c": "4186", "t1": "20", "t2": "30"})
check("heat Q", row(r, "Q").split()[0], 41860, 1e-6)
check("heat dir", row(r, "dir"), "serap")
r = ml.run_tool("heatexp", {"mode": "expand", "l0": "10", "alpha": "1.2e-5", "dt": "50"})
check("expand dL", row(r, "dL").split()[0], 0.006, 1e-9)
r = ml.run_tool("heatexp", {"mode": "latent", "m": "0.5", "latent": "334000"})
check("latent Q", row(r, "Q").split()[0], 167000, 1e-9)

# schwartz
r = ml.run_tool("schwartz", {"msun": "1"})
check("schwartz rs (1 Msun)", row(r, "rs").split()[0], 2953.9, 1e-3)
r = ml.run_tool("schwartz", {"msun": "1", "r": "5907.8"})
check("schwartz dil@2rs", row(r, "dil"), 0.7071068, 1e-3)
check("schwartz vesc@2rs", row(r, "vesc").split()[0], 2.9979e8 / math.sqrt(2), 1e-3)
try:
    ml.run_tool("schwartz", {"msun": "1", "r": "100"})
    print("FAIL schwartz r<rs should raise")
except ml.LabError:
    print("PASS schwartz r<rs raises")

# optics
r = ml.run_tool("optics", {"mode": "snell", "n1": "1", "n2": "1.5", "th1": "30"})
check("optics snell th2", row(r, "th2").split()[0], 19.4712, 1e-4)
r = ml.run_tool("optics", {"mode": "snell", "n1": "1.5", "n2": "1", "th1": "45"})
check("optics TIR", row(r, "tir"), "ya")
r = ml.run_tool("optics", {"mode": "lens", "f": "0.1", "do": "0.15"})
check("optics di", row(r, "di").split()[0], 0.3, 1e-9)
check("optics mag", row(r, "m").replace("x", ""), -2, 1e-9)
check("optics kind", row(r, "kind"), "nyata")
r = ml.run_tool("optics", {"mode": "dslit", "lam": "500e-9", "d": "1e-4", "L": "2"})
check("optics dy", row(r, "dy").split()[0], 0.01, 1e-9)

# shm
r = ml.run_tool("shm", {"mode": "mass", "m": "1", "k": "100"})
check("shm T", row(r, "T").split()[0], 2 * math.pi / 10, 1e-4)
check("shm f", row(r, "f").split()[0], 10 / (2 * math.pi), 1e-4)
r = ml.run_tool("shm", {"mode": "pend", "L": "1", "g": "9.81"})
check("shm pendulum T", row(r, "T").split()[0], 2 * math.pi / math.sqrt(9.81), 1e-4)
r = ml.run_tool("shm", {"mode": "energy", "A": "0.1", "k": "100"})
check("shm E", row(r, "E").split()[0], 0.5, 1e-9)

# emind
r = ml.run_tool("emind", {"mode": "faraday", "N": "100", "dphi": "0.5"})
check("emind faraday", row(r, "EMF").split()[0], 50, 1e-9)
r = ml.run_tool("emind", {"mode": "trafo", "v1": "240", "n1": "1000", "n2": "100"})
check("emind V2", row(r, "V2").split()[0], 24, 1e-9)
check("emind kind", row(r, "kind"), "step-down")
r = ml.run_tool("emind", {"mode": "motional", "B": "0.5", "v": "10", "L": "0.2"})
check("emind motional", row(r, "EMF").split()[0], 1, 1e-9)

print(f"\n=== {PASS} pass, {FAIL} fail ===")
