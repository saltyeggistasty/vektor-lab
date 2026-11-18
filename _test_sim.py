# -*- coding: utf-8 -*-
# Tes referensi simlab.py — validasi tiap simulasi terhadap teori.
# Jalankan: venv\Scripts\python.exe _test_sim.py
import math
import sys

import numpy as np

import simlab as sl

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


print("== M1 slogistic ==")
r1 = sl.run_tool("slogistic", {"r": 2, "x0": 0.2, "n": 200, "mode": "series"})
check("r=2 konvergen ke 0.5", abs(numrow(r1, "x_final") - 0.5) < 1e-9)
check("r=2 titik tetap 0.5", abs(numrow(r1, "x_star") - 0.5) < 1e-12)
check("r=2 regime titik_tetap", rows(r1)["regime"] == "titik_tetap")
r2 = sl.run_tool("slogistic", {"r": 3.2, "x0": 0.2, "n": 400, "mode": "series"})
check("r=3.2 period 2", rows(r2)["period"] == "2", rows(r2)["period"])
check("r=3.2 regime periodik", rows(r2)["regime"] == "periodik")
r3 = sl.run_tool("slogistic", {"r": 0.5, "x0": 0.7, "n": 100, "mode": "series"})
check("r=0.5 punah", rows(r3)["regime"] == "punah" and numrow(r3, "x_final") < 1e-9)
r4 = sl.run_tool("slogistic", {"r": 4, "x0": 0.31, "n": 2000, "mode": "series"})
check("r=4 lyapunov ~ ln2", abs(numrow(r4, "lyap") - math.log(2)) < 0.05, numrow(r4, "lyap"))
r5 = sl.run_tool("slogistic", {"r": 2.8, "x0": 0.2, "n": 30, "mode": "cobweb"})
check("cobweb punya 3 trace", len(r5["plot"]["traces"]) == 3)
r6 = sl.run_tool("slogistic", {"mode": "bifurcation"})
check("bifurkasi scatter >= 20rb titik", len(r6["plot"]["traces"][0]["x"]) >= 20000)

print("== M2 slorenz ==")
s1 = sl.run_tool("slorenz", {"sigma": 10, "rho": 10, "beta": 2.6667, "dt": 0.005, "steps": 20000})
check("rho=10 -> titik_tetap", rows(s1)["regime"] == "titik_tetap", rows(s1)["regime"])
# titik tetap: z* = rho-1 = 9, x* = sqrt(beta(rho-1)) = sqrt(26.667)=5.164
check("rho=10 z akhir ~ 9", abs(float(s1["plot"]["traces"][0]["y"][-1]) - 9.0) < 0.2,
      s1["plot"]["traces"][0]["y"][-1])
s2 = sl.run_tool("slorenz", {"sigma": 10, "rho": 28, "beta": 2.6667, "dt": 0.005, "steps": 20000})
check("rho=28 -> kacau", rows(s2)["regime"] == "kacau")
check("rho=28 bounded < 100", numrow(s2, "state_max") < 100)
check("rho=28 z maks ~ 45-50", 40 < max(s2["plot"]["traces"][0]["y"]) < 55,
      max(s2["plot"]["traces"][0]["y"]))

print("== M3 sfourier ==")
f1 = sl.run_tool("sfourier", {"expr": "x", "L": "3.141592653589793", "N": 20})
check("f=x: b1 ~ 2", abs(numrow(f1, "b1") - 2) < 1e-3, numrow(f1, "b1"))
check("f=x: b2 ~ -1", abs(numrow(f1, "b2") + 1) < 1e-3, numrow(f1, "b2"))
check("f=x: a0 ~ 0", abs(numrow(f1, "a0")) < 1e-6)
check("f=x: a1 ~ 0", abs(numrow(f1, "a1")) < 1e-6)
f2 = sl.run_tool("sfourier", {"expr": "1", "L": 2, "N": 5})
check("f=1: a0 ~ 1", abs(numrow(f2, "a0") - 1) < 1e-9)
check("f=1: b1 ~ 0", abs(numrow(f2, "b1")) < 1e-6)
f3 = sl.run_tool("sfourier", {"expr": "sin(x)", "L": "3.141592653589793", "N": 10})
check("f=sin: b1 ~ 1", abs(numrow(f3, "b1") - 1) < 1e-6)
check("f=sin: b2 ~ 0", abs(numrow(f3, "b2")) < 1e-4)
f4 = sl.run_tool("sfourier", {"expr": "x^2", "L": 1, "N": 30})
# x^2 di [-1,1]: a0 = 2*Integral(0..1 x^2)/2 = 1/3
check("f=x^2: a0 ~ 1/3", abs(numrow(f4, "a0") - 1 / 3) < 1e-6)
check("f=x^2: 2 trace", len(f4["plot"]["traces"]) == 2)

print("== M4 smatrix ==")
m1 = sl.run_tool("smatrix", {"matrix": "2,0;0,3"})
check("det=6", abs(numrow(m1, "det") - 6) < 1e-12)
check("kind skala", rows(m1)["kind"] == "skala")
m2 = sl.run_tool("smatrix", {"matrix": "0,-1;1,0"})
check("rotasi 90: eigen i", "i" in rows(m2)["lam"], rows(m2)["lam"])
check("rotasi 90: kind rotasi", rows(m2)["kind"] == "rotasi")
m3 = sl.run_tool("smatrix", {"matrix": "1,2;2,4"})
check("singular det=0", abs(numrow(m3, "det")) < 1e-12)
check("kind singular", rows(m3)["kind"] == "singular")
m4 = sl.run_tool("smatrix", {"matrix": "0,1;1,0"})
check("refleksi: kind refleksi", rows(m4)["kind"] == "refleksi")
m5 = sl.run_tool("smatrix", {"matrix": "1,1;0,1"})
check("shear: det=1 kind shear", rows(m5)["kind"] == "shear")

print("== M5 swalk ==")
w1 = sl.run_tool("swalk", {"n": 300, "steps": 2000, "seed": 42})
w1b = sl.run_tool("swalk", {"n": 300, "steps": 2000, "seed": 42})
check("seed deterministik", rows(w1)["rms"] == rows(w1b)["rms"])
check("RMS ~ sqrt(2000)=44.7 (20%)", 0.8 * 44.72 < numrow(w1, "rms") < 1.2 * 44.72,
      numrow(w1, "rms"))
check("mean_x kecil (< 3)", abs(numrow(w1, "mean_x")) < 3.0)
w2 = sl.run_tool("swalk", {"n": 50, "steps": 500, "seed": 7})
check("RMS ~ sqrt(500)=22.4", 0.75 * 22.36 < numrow(w2, "rms") < 1.3 * 22.36)

print("== F1 sdblpend ==")
p1 = sl.run_tool("sdblpend", {"m1": 1, "m2": 1, "L1": 1, "L2": 1, "th1": 5, "th2": 5,
                              "g": 9.81, "t_end": 10, "view": "angles"})
check("drift energi < 0.01%", numrow(p1, "drift") < 0.01, numrow(p1, "drift"))
# batas pendulum tunggal (m2 ~ 0): T = 2*pi*sqrt(L1/g) = 2.006 s
p3 = sl.run_tool("sdblpend", {"m1": 1, "m2": 0.001, "L1": 1, "L2": 1, "th1": 5, "th2": 0,
                              "g": 9.81, "t_end": 10, "view": "angles"})
ys = p3["plot"]["traces"][0]["y"]; xs = p3["plot"]["traces"][0]["x"]
zc = [xs[i] for i in range(1, len(ys)) if ys[i - 1] < 0 <= ys[i]]
if len(zc) >= 2:
    T_meas = zc[1] - zc[0]   # silang naik berturutan = 1 periode penuh
    check("periode kecil ~ 2.006 s (2%)", abs(T_meas - 2.006) / 2.006 < 0.02, T_meas)
else:
    check("periode kecil ~ 2.006 s (2%)", False, "zero-crossing kurang")
p2 = sl.run_tool("sdblpend", {"m1": 1, "m2": 1, "L1": 1, "L2": 1, "th1": 120, "th2": -30,
                              "g": 9.81, "t_end": 20, "view": "path"})
check("chaos: drift tetap kecil < 0.1%", numrow(p2, "drift") < 0.1, numrow(p2, "drift"))
# chaos = sensitivitas kondisi awal: beda 1e-6 rad -> lintasan divergen > 5 deg
pa = sl.run_tool("sdblpend", {"m1": 1, "m2": 1, "L1": 1, "L2": 1, "th1": 170, "th2": 30,
                              "g": 9.81, "t_end": 15, "view": "angles"})
pb = sl.run_tool("sdblpend", {"m1": 1, "m2": 1, "L1": 1, "L2": 1, "th1": 170.000001, "th2": 30,
                              "g": 9.81, "t_end": 15, "view": "angles"})
dth = abs(pa["plot"]["traces"][0]["y"][-1] - pb["plot"]["traces"][0]["y"][-1])
check("chaos: divergensi eksponensial > 5 deg", dth > 5.0, dth)

print("== F2 sdrag ==")
d1 = sl.run_tool("sdrag", {"v0": 20, "angle": 45, "m": 1, "Cd": 0, "rho": 0, "A": 0.01, "g": 9.81})
vac = 20 ** 2 * math.sin(math.radians(90)) / 9.81
check("rho=0: range = teori vakum", abs(numrow(d1, "range_drag") - vac) < 0.05, numrow(d1, "range_drag"))
d2 = sl.run_tool("sdrag", {"v0": 30, "angle": 45, "m": 0.145, "Cd": 0.47, "rho": 1.225,
                           "A": 0.00426, "g": 9.81})
vac2 = 30 ** 2 / 9.81
rd = numrow(d2, "range_drag")
check("bola baseball: hambatan mengurangi jangkauan", 0 < rd < vac2, f"{rd} vs {vac2}")
check("rasio masuk akal 0.3-0.95", 0.3 < numrow(d2, "ratio") < 0.95, numrow(d2, "ratio"))
check("h_max < vakum hmax (22.9)", 5 < numrow(d2, "h_max") < 22.9)

print("== F3 skepler ==")
k1 = sl.run_tool("skepler", {"a": 1, "e": 0, "mu": 1, "orbits": 2})
check("e=0: T_terukur ~ 2pi (0.5%)", abs(numrow(k1, "T_meas") - 2 * math.pi) / (2 * math.pi) < 0.005,
      numrow(k1, "T_meas"))
check("e=0: r_per ~ r_ap ~ 1", abs(numrow(k1, "r_per") - 1) < 1e-3 and abs(numrow(k1, "r_ap") - 1) < 1e-3)
check("e=0: drift < 1e-6%", numrow(k1, "drift") < 1e-6, numrow(k1, "drift"))
k2 = sl.run_tool("skepler", {"a": 1, "e": 0.5, "mu": 1, "orbits": 2})
check("e=0.5: r_per = 0.5", abs(numrow(k2, "r_per") - 0.5) < 1e-3)
check("e=0.5: r_ap = 1.5", abs(numrow(k2, "r_ap") - 1.5) < 1e-3)
check("e=0.5: r_per+r_ap = 2a", abs(numrow(k2, "r_per") + numrow(k2, "r_ap") - 2) < 1e-3)
check("e=0.5: T sama dgn e=0 (Hukum III)", abs(numrow(k2, "T_meas") - 2 * math.pi) / (2 * math.pi) < 0.01,
      numrow(k2, "T_meas"))
check("e=0.5: drift energi < 1e-6%", numrow(k2, "drift") < 1e-6)
k3 = sl.run_tool("skepler", {"a": 4, "e": 0.2, "mu": 2, "orbits": 1})
T3 = 2 * math.pi * math.sqrt(64 / 2)
check("a=4,mu=2: T ~ 2pi sqrt(32)", abs(numrow(k3, "T_meas") - T3) / T3 < 0.01,
      f"{numrow(k3, 'T_meas')} vs {T3}")

print("== F4 sslit ==")
lam, dd, L = 500e-9, 1e-4, 2.0
s1 = sl.run_tool("sslit", {"lam": lam, "d": dd, "L": L, "a": 0, "span": 5})
dy_theory = lam * L / dd
check("jarak frinje = lam*L/d", abs(numrow(s1, "dy") - dy_theory * 1000) < 1e-9,
      f"{numrow(s1, 'dy')} vs {dy_theory*1000}")
s2 = sl.run_tool("sslit", {"lam": lam, "d": dd, "L": L, "a": 2.5e-5, "span": 5})
ys_p = s2["plot"]["traces"][0]["x"]; Is = s2["plot"]["traces"][0]["y"]
imax = int(np.argmax(Is))   # kurva dgn envelope: max unik = puncak tengah
check("puncak tengah di y=0", abs(ys_p[imax]) < 0.05, ys_p[imax])
# envelope min pertama: y = lam*L/a = 500e-9*2/2.5e-5 = 0.04 m = 40 mm
check("minimum envelope di 40mm", abs(numrow(s2, "y_env") - 40.0) < 1e-6, numrow(s2, "y_env"))
ymin_idx = min(range(len(ys_p)), key=lambda i: abs(ys_p[i] - 40.0))
check("I di envelope min ~ 0 (< 2%)", Is[ymin_idx] < 0.02, Is[ymin_idx])

print("== F5 sschrod ==")
q1 = sl.run_tool("sschrod", {"k0": 1.5, "x0": -40, "sigma": 5, "V0": 0, "w": 0, "steps": 3000})
check("bebas: norm drift ~ 0 (< 0.01%)", numrow(q1, "drift") < 0.01, numrow(q1, "drift"))
check("bebas: v_terukur ~ k0=1.5 (5%)", abs(numrow(q1, "v_meas") - 1.5) / 1.5 < 0.05,
      numrow(q1, "v_meas"))
check("bebas: T_prob = 1", abs(numrow(q1, "T_prob") - 1) < 1e-6)
q2 = sl.run_tool("sschrod", {"k0": 1.5, "x0": -40, "sigma": 4, "V0": 0.4, "w": 8, "steps": 5000})
E = 1.5 ** 2 / 2  # 1.125
check("E=1.125 > V0=0.4: transmisi dominan (> 0.7)", numrow(q2, "T_prob") > 0.7, numrow(q2, "T_prob"))
q3 = sl.run_tool("sschrod", {"k0": 1.0, "x0": -40, "sigma": 4, "V0": 3.0, "w": 8, "steps": 3000})
# E=0.5 << V0=3: sebagian besar pantul
check("E=0.5 << V0=3: refleksi dominan (> 0.6)", numrow(q3, "R_prob") > 0.6, numrow(q3, "R_prob"))
check("norm tetap 1 (0.5%)", numrow(q3, "drift") < 0.5)

print(f"\nTOTAL: {PASS} OK, {FAIL} FAIL")
sys.exit(1 if FAIL else 0)
