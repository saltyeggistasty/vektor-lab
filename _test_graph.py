# -*- coding: utf-8 -*-
# Tes referensi graphlab.py — jalankan: venv\Scripts\python.exe _test_graph.py
import math
import sys

import graphlab as gl

PASS = 0
FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  OK   {name}")
    else:
        FAIL += 1
        print(f"  FAIL {name}  {detail}")


def rows(res):
    return {r[0]: r[1] for r in res["rows"]}


def numrow(res, k):
    return float(str(rows(res)[k]).split()[0].replace(",", "."))


print("== gdomain ==")
r = gl.run_tool("gdomain", {"res": 360, "range": 4, "scheme": "hue"})
check("canvas+engine", r.get("canvas") is True and r["engine"] == "gdomain")
check("params res", r["params"]["res"] == 360)
try:
    gl.run_tool("gdomain", {"scheme": "ngawur"})
    check("skema salah ditolak", False)
except Exception:
    check("skema salah ditolak", True)

print("== gfractal ==")
r = gl.run_tool("gfractal", {"mode": "julia", "iter": 200, "res": 480, "cre": "-0.8", "cim": "0.156"})
check("julia params", r["params"]["cre"] == -0.8 and r["params"]["cim"] == 0.156)
try:
    gl.run_tool("gfractal", {"mode": "kuda"})
    check("mode salah ditolak", False)
except Exception:
    check("mode salah ditolak", True)

print("== gsurf3d ==")
r = gl.run_tool("gsurf3d", {"n": 40, "px": 1, "py": -2, "range": 4})
check("tangent point", r["params"]["px"] == 1 and r["params"]["py"] == -2)

print("== gfrenet ==")
r = gl.run_tool("gfrenet", {"tmax": 20, "t": 3.5, "n": 300})
check("frenet t", r["params"]["t"] == 3.5)

print("== gtrans3d ==")
r = gl.run_tool("gtrans3d", {"matrix": "2,0,0;0,2,0;0,0,2"})
check("det 3x3 skala=8", abs(numrow(r, "det") - 8) < 1e-12, numrow(r, "det"))
r = gl.run_tool("gtrans3d", {"matrix": "1,0,0;0,1,0;0,0,0"})
check("det 0 (flat)", abs(numrow(r, "det")) < 1e-12)

print("== gslope ==")
r = gl.run_tool("gslope", {"density": 20, "xlo": -5, "xhi": 5})
check("slope range", r["params"]["xlo"] == -5 and r["params"]["xhi"] == 5)
try:
    gl.run_tool("gslope", {"density": 20, "xlo": 5, "xhi": -5})
    check("range turun ditolak", False)
except Exception:
    check("range turun ditolak", True)

print("== gdist: normal ==")
r = gl.run_tool("gdist", {"dist": "normal", "mu": 0, "sd": 1, "a": "-1", "b": "1"})
check("P(-1<=X<=1) ~ 0.6827", abs(numrow(r, "P(a≤X≤b)") - 0.682689) < 1e-4, numrow(r, "P(a≤X≤b)"))
r = gl.run_tool("gdist", {"dist": "normal", "mu": 0, "sd": 1, "a": "-1e6", "b": "1"})
check("P(X<=1) ~ 0.8413", abs(numrow(r, "P(a≤X≤b)") - 0.841345) < 1e-4)

print("== gdist: binomial ==")
r = gl.run_tool("gdist", {"dist": "binomial", "n": 10, "p": 0.5, "a": 0, "b": 10})
check("pmf total = 1", abs(numrow(r, "P(a≤X≤b)") - 1) < 1e-9)
r = gl.run_tool("gdist", {"dist": "binomial", "n": 10, "p": 0.5, "a": 5, "b": 5})
check("P(X=5) ~ 0.2461", abs(numrow(r, "P(a≤X≤b)") - 0.246094) < 1e-4, numrow(r, "P(a≤X≤b)"))

print("== gdist: poisson ==")
r = gl.run_tool("gdist", {"dist": "poisson", "lam": 2, "a": 0, "b": 2000})
check("poisson cdf inf = 1", abs(numrow(r, "P(a≤X≤b)") - 1) < 1e-9)
r = gl.run_tool("gdist", {"dist": "poisson", "lam": 2, "a": 2, "b": 2})
check("P(X=2; lam=2) ~ 0.2707", abs(numrow(r, "P(a≤X≤b)") - 0.270671) < 1e-4)

print("== gdist: exponential ==")
r = gl.run_tool("gdist", {"dist": "exponential", "lam": 1, "a": 0, "b": 1})
check("P(0<=X<=1; lam=1) = 1-e^-1", abs(numrow(r, "P(a≤X≤b)") - (1 - math.exp(-1))) < 1e-9)

print("== gdist: uniform ==")
r = gl.run_tool("gdist", {"dist": "uniform", "lo": 0, "hi": 10, "a": 2, "b": 5})
check("uniform P = 0.3", abs(numrow(r, "P(a≤X≤b)") - 0.3) < 1e-12)

print("== ggraphalgo ==")
r = gl.run_tool("ggraphalgo", {"algo": "dijkstra", "n": 12, "density": 0.3, "seed": 42})
check("algo+seed", r["params"]["algo"] == "dijkstra" and r["params"]["seed"] == 42)
try:
    gl.run_tool("ggraphalgo", {"algo": "astar"})
    check("algo asing ditolak", False)
except Exception:
    check("algo asing ditolak", True)

print("== gfield ==")
r = gl.run_tool("gfield", {"n": 4, "seed": 1, "equip": 20})
check("field n", r["params"]["n"] == 4)

print("== gpvcycle: carnot ==")
r = gl.run_tool("gpvcycle", {"cycle": "carnot", "th": 600, "tc": 300, "gamma": 1.4})
check("carnot eta 50%", abs(numrow(r, "eta") - 50) < 1e-9, numrow(r, "eta"))
try:
    gl.run_tool("gpvcycle", {"cycle": "carnot", "th": 300, "tc": 600})
    check("Tc>=Th ditolak", False)
except Exception:
    check("Tc>=Th ditolak", True)

print("== gpvcycle: otto ==")
r = gl.run_tool("gpvcycle", {"cycle": "otto", "r": 9, "gamma": 1.4})
eta_expect = (1 - 9 ** (1 - 1.4)) * 100
check("otto eta r=9 g=1.4", abs(numrow(r, "eta") - eta_expect) < 1e-6, numrow(r, "eta"))

print("== gpvcycle: diesel ==")
r = gl.run_tool("gpvcycle", {"cycle": "diesel", "r": 18, "rc": 2.5, "gamma": 1.4})
eta_expect = (1 - (1 / 1.4) * (2.5 ** 1.4 - 1) / (2.5 ** 0.4 * (18 ** 0.4))) * 100
check("diesel eta rumus", abs(numrow(r, "eta") - eta_expect) < 1e-6, numrow(r, "eta"))

print("== gising ==")
r = gl.run_tool("gising", {"size": 100, "temp": 2.269, "speed": 30})
check("Tc param", r["params"]["temp"] == 2.269)

print("== gminkowski ==")
r = gl.run_tool("gminkowski", {"v": 0.5})
check("gamma(0.5) ~ 1.1547", abs(numrow(r, "gamma") - 1.154701) < 1e-5)
r = gl.run_tool("gminkowski", {"v": 0})
check("gamma(0) = 1", abs(numrow(r, "gamma") - 1) < 1e-12)

print("== gfluid ==")
r = gl.run_tool("gfluid", {"size": 128, "visc": 0.0001, "diff": 0.00001})
check("fluid size", r["params"]["size"] == 128)

print("== ggeodesic ==")
r = gl.run_tool("ggeodesic", {"mode": "light", "b": 1.2})
check("b<1.5 photon -> capture", rows(r)["fate"] == "capture")
r = gl.run_tool("ggeodesic", {"mode": "light", "b": 3})
check("b>1.5 -> deflect", rows(r)["fate"] == "deflect")
check("photon sphere 1.5 rs", numrow(r, "photon_sphere") == 1.5)
check("rs 1.0", numrow(r, "rs") == 1.0)

print("== gray ==")
r = gl.run_tool("gray", {"f1": 100, "f2": -100, "nray": 7, "d12": 300})
check("ray params", r["params"]["f1"] == 100 and r["params"]["nray"] == 7)

print("== dispatch aman ==")
try:
    gl.run_tool("ngawur", {})
    check("tool asing ditolak", False)
except Exception:
    check("tool asing ditolak", True)

print(f"\nTOTAL: {PASS} OK, {FAIL} FAIL")
sys.exit(1 if FAIL else 0)
