# Uji referensi semua tool mathlab - nilai dibandingkan dgn hasil analitik.
import math
import mathlab as ml

PASS = FAIL = 0

def check(name, got, want, tol=1e-6):
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

# 1. integral
r = ml.run_tool("integral", {"expr": "x**2", "mode": "def", "a": 0, "b": 3})
check("integral def", row(r, "num"), 9)
r = ml.run_tool("integral", {"expr": "sin(x)", "mode": "indef"})
print("  indef latex:", row(r, "sym"))
assert "cos" in row(r, "sym")
r = ml.run_tool("integral", {"expr": "sin(x)/x", "mode": "lim", "x0": 0})
check("integral limit", row(r, "num"), 1)

# 2. matrix
r = ml.run_tool("matrix", {"matrix": "1,2;3,4", "op": "det"})
check("matrix det", row(r, "R"), -2)
r = ml.run_tool("matrix", {"matrix": "4,7;2,6", "op": "inv"})
print("  inv latex:", row(r, "R"))
r = ml.run_tool("matrix", {"matrix": "1,2,3;4,5,6;7,8,9", "op": "rank"})
check("matrix rank", row(r, "R"), 2)
r = ml.run_tool("matrix", {"matrix": "2,0;0,3", "op": "eig"})
print("  eig:", row(r, "R"))
r = ml.run_tool("matrix", {"matrix": "1,2;3,4;5,6", "op": "T"})
print("  transpose:", row(r, "R"))

# 3. ode
r = ml.run_tool("ode", {"eq": "y' = y"})
print("  ode latex:", row(r, "y"))
assert "e^{x}" in row(r, "y")
r = ml.run_tool("ode", {"eq": "y'' + y = 0", "ics": "y(0) = 1, y'(0) = 0"})
print("  ode ics latex:", row(r, "y"))
assert "cos" in row(r, "y")

# 4. stats: [2,4,4,4,5,5,7,9] mean=5, median=4.5, std_s=2.2677868
r = ml.run_tool("stats", {"data": "2,4,4,4,5,5,7,9"})
check("stats mean", r["mean"], 5)
check("stats median", r["median"], 4.5)
check("stats std_s", r["std_s"], 2.13809, 1e-5)
check("stats n", r["n"], 8)
check("stats mode", r["mode"], 4)

# 5. thermo
r = ml.run_tool("thermo", {"mode": "ideal", "v": "1", "n": "1", "t": "273.15", "solve": "P"})
check("thermo ideal P", row(r, "P"), 8.314462618 * 273.15, 1e-5)
r = ml.run_tool("thermo", {"mode": "carnot", "thot": 600, "tcold": 400})
check("thermo carnot", row(r, "eta"), 1 / 3, 1e-6)

# 6. qm
r = ml.run_tool("qm", {"mode": "debr", "mass": "9.11e-31", "vel": "1e6"})
check("qm debr", row(r, "lambda").split()[0], 7.2738e-10, 1e-3)
r = ml.run_tool("qm", {"mode": "photon", "freq": "1e15"})
check("qm photon eV", row(r, "E_eV").split()[0], 4.135667, 1e-4)
r = ml.run_tool("qm", {"mode": "photo", "freq": "1e15", "work": "2.0"})
check("qm photo eV", row(r, "KE_eV").split()[0], 2.135667, 1e-4)
try:
    ml.run_tool("qm", {"mode": "photo", "freq": "1e14", "work": "2.0"})
    print("FAIL qm photo no-emission should raise")
except ml.LabError as e:
    print(f"PASS qm photo no-emission raises: {e}")

# 7. es
r = ml.run_tool("es", {"mode": "coulomb", "q1": "1", "q2": "1", "r": "1"})
check("es coulomb", row(r, "F").split()[0], 8.98755e9, 1e-4)
assert row(r, "kind") == "tolak"
r = ml.run_tool("es", {"mode": "field", "q1": "1", "r": "2"})
check("es field", row(r, "E").split()[0], 8.98755e9 / 4, 1e-4)
r = ml.run_tool("es", {"mode": "cap", "a": "1", "d": "0.001"})
check("es cap", row(r, "C").split()[0], 8.854e-9, 1e-3)

# 8. rel
r = ml.run_tool("rel", {"mode": "gamma", "v": "0.5"})
check("rel gamma", row(r, "gamma"), 1.1547005, 1e-6)
r = ml.run_tool("rel", {"mode": "dilation", "v": "0.5", "t0": "10"})
check("rel dilation", row(r, "dt").split()[0], 11.547005, 1e-6)
r = ml.run_tool("rel", {"mode": "energy", "v": "0.5", "m": "1"})
E0 = 8.987551787e16
check("rel E0", row(r, "E0").split()[0], E0, 1e-5)

# 9. proj: v0=20, 45deg, h0=0, g=9.81
r = ml.run_tool("proj", {"v0": "20", "angle": "45", "h0": "0", "g": "9.81"})
check("proj range", row(r, "x_max").split()[0], 40.7747, 1e-4)
check("proj hmax", row(r, "y_max").split()[0], 10.1937, 1e-4)
check("proj tof", row(r, "t").split()[0], 2.883209, 1e-5)
assert len(r["plot"]["x"]) == 240 and abs(r["plot"]["y"][0]) < 1e-9

# 10. hydro
r = ml.run_tool("hydro", {"mode": "hstat", "rho": "1000", "h": "10"})
check("hydro hstat gauge", row(r, "P_gauge").split()[0], 98066.5, 1e-4)
r = ml.run_tool("hydro", {"mode": "cont", "a1": "2", "a2": "1", "v1": "3"})
check("hydro cont", row(r, "v2").split()[0], 6, 1e-9)
r = ml.run_tool("hydro", {"mode": "bern", "rho": "1000", "v1": "1", "p1": "200000", "p2": "100000", "h1": "0", "h2": "0"})
want = math.sqrt(1 + 2 * (200000 - 100000) / 1000)
check("hydro bern", row(r, "v2").split()[0], want, 1e-5)

# error paths
for bad in [
    ("integral", {"expr": "__import__('os')", "mode": "indef"}),
    ("matrix", {"matrix": "1,2;3", "op": "det"}),
    ("matrix", {"matrix": "a,b;c,d", "op": "det"}),
    ("thermo", {"mode": "carnot", "thot": 300, "tcold": 400}),
    ("stats", {"data": "a,b,c"}),
    ("ode", {"eq": "y + x = 2"}),
    ("rel", {"mode": "gamma", "v": "1.2"}),
    ("ngetoolNgawur", {}),
]:
    try:
        ml.run_tool(*bad)
        print(f"FAIL error-path {bad[0]} should raise")
    except ml.LabError as e:
        print(f"PASS error-path {bad[0]}: {e}")

print(f"\n=== {PASS} pass, {FAIL} fail ===")
