# ============================================================
# GRAPHLAB - backend utk 15 advanced graphing tools (prefix g*).
# Semua graph INTERAKTIF jalan client-side (graphers.js) — backend
# cuma VALIDASI parameter + hitung readout konstanta (efisiensi,
# Tc, photon sphere, dst) biar ada lapisan yang bisa dites.
# Tool balikin {canvas: true, engine: <id>, params: {...}, rows: [...]}.
# GAK nyentuh physics.py/vectorcalc.py/mathlab.py sama sekali.
# ============================================================
import math

from mathlab import LabError, _num, _fmt
from simlab import _int


def _ndef(d, key, default):
    """Default aman-nol: 0/0.0 sah sebagai nilai user, bukan 'pakai default'."""
    v = d.get(key)
    return default if v is None or (isinstance(v, str) and not v.strip()) else v

SCH_M = 1.0            # massa Schwarzschild natural (geodesic)


def _clamp(v, lo, hi):
    return max(lo, min(hi, v))


# ---------- gdomain: domain coloring ----------
def g_domain(d):
    res = _int(_ndef(d, "res", 480), "res", 120, 720)
    rng = _num(_ndef(d, "range", 4), "range", minv=0.5, maxv=20.0)
    scheme = str(d.get("scheme") or "hue").strip().lower()
    if scheme not in ("hue", "phase", "stripes", "shade"):
        raise LabError("Skema warna tidak dikenal.", "err.scheme")
    return {"canvas": True, "engine": "gdomain",
            "params": {"res": res, "range": rng, "scheme": scheme,
                       "expr": str(d.get("expr") or "1/z")[:200]},
            "rows": [["map", r"f(z) \text{ di bidang kompleks},\ \mathrm{hue} = \arg f,\ \mathrm{shade} = |f|", True]]}


# ---------- gfractal: Mandelbrot / Julia / Newton ----------
def g_fractal(d):
    mode = str(d.get("mode") or "mandelbrot").strip().lower()
    if mode not in ("mandelbrot", "julia", "newton"):
        raise LabError("Mode fractal tidak dikenal.", "err.mode", "fractal")
    it = _int(_ndef(d, "iter", 150), "iter", 20, 800)
    res = _int(_ndef(d, "res", 480), "res", 120, 640)
    cre = _num(_ndef(d, "cre", "-0.7269"), "cre", minv=-2.0, maxv=2.0)
    cim = _num(_ndef(d, "cim", "0.1889"), "cim", minv=-2.0, maxv=2.0)
    power = _int(_ndef(d, "power", 2), "power", 2, 6)
    params = {"mode": mode, "iter": it, "res": res, "power": power}
    if mode == "julia":
        params["cre"], params["cim"] = cre, cim
    note = {
        "mandelbrot": r"z_{n+1} = z_n^{2} + c,\ c \in \mathbb{C}",
        "julia": r"z_{n+1} = z_n^{2} + c\ (\text{fixed } c)",
        "newton": r"z_{n+1} = z_n - \dfrac{p(z_n)}{p'(z_n)}",
    }[mode]
    return {"canvas": True, "engine": "gfractal", "params": params,
            "rows": [["note", note, True], ["iter", str(it), False]]}


# ---------- gsurf3d: surface z=f(x,y) + tangent plane ----------
def g_surf3d(d):
    n = _int(_ndef(d, "n", 40), "n", 16, 60)
    x0 = _num(_ndef(d, "px", 1), "px", minv=-10.0, maxv=10.0)
    y0 = _num(_ndef(d, "py", 1), "py", minv=-10.0, maxv=10.0)
    rng = _num(_ndef(d, "range", 4), "range", minv=0.5, maxv=10.0)
    return {"canvas": True, "engine": "gsurf3d",
            "params": {"n": n, "px": x0, "py": y0, "range": rng,
                       "expr": str(d.get("expr") or "sin(x)*cos(2*y)")[:200]},
            "rows": [["note", r"z = f(x,y)\ +\ \text{bidang singgung di } (x_0, y_0)", True]]}


# ---------- gfrenet: kurva parametrik 3D + Frenet ----------
def g_frenet(d):
    tmax = _num(_ndef(d, "tmax", 18), "tmax", minv=0.5, maxv=60.0)
    tt = _num(_ndef(d, "t", 2), "t", minv=0.01, maxv=60.0)
    n = _int(_ndef(d, "n", 300), "n", 50, 600)
    return {"canvas": True, "engine": "gfrenet",
            "params": {"tmax": tmax, "t": tt, "n": n,
                       "xt": str(d.get("xt") or "3*cos(t)")[:200],
                       "yt": str(d.get("yt") or "3*sin(t)")[:200],
                       "zt": str(d.get("zt") or "t/2")[:200]},
            "rows": [["note", r"\mathbf{T}, \mathbf{N}, \mathbf{B} = \text{frame Frenet},\ \kappa, \tau \text{ numerik}", True]]}


# ---------- gtrans3d: transformasi linear 3D ----------
def g_trans3d(d):
    m = []
    raw = str(_ndef(d, "matrix", "1,0.5,0;0,1,0.3;0,0.3,1")).strip()
    rows = [r for r in raw.split(";") if r.strip()]
    if len(rows) != 3:
        raise LabError("Matriks harus tepat 3 baris, pisah dengan ';'.",
                   "err.matrix_rows3")
    for r in rows:
        parts = [p for p in r.replace(",", " ").split() if p]
        if len(parts) != 3:
            raise LabError("Setiap baris harus tepat 3 angka.", "err.matrix_cells3")
        m.append([_num(p, "elemen") for p in parts])
    det = (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
           - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
           + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))
    return {"canvas": True, "engine": "gtrans3d",
            "params": {"matrix": m},
            "rows": [["det", _fmt(det), False],
                     ["note", r"\det A = \text{faktor volume},\ \text{basis } \mathbf{i},\mathbf{j},\mathbf{k} \text{ ikut}", True]]}


# ---------- gslope: slope field ----------
def g_slope(d):
    dens = _int(_ndef(d, "density", 20), "density", 8, 40)
    xlo = _num(_ndef(d, "xlo", -8), "xlo", minv=-50.0, maxv=50.0)
    xhi = _num(_ndef(d, "xhi", 8), "xhi", minv=-50.0, maxv=50.0)
    if xhi <= xlo:
        raise LabError("Batas x harus naik (xhi > xlo).", "err.range_x")
    return {"canvas": True, "engine": "gslope",
            "params": {"density": dens, "xlo": xlo, "xhi": xhi, "ylo": -6.0, "yhi": 6.0,
                       "expr": str(d.get("expr") or "x - y")[:200]},
            "rows": [["note", r"y' = f(x,y)\ \text{— klik titik awal untuk solusi RK4}", True]]}


# ---------- gdist: distribution explorer ----------
def _norm_cdf(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def g_dist(d):
    dist = str(d.get("dist") or "normal").strip().lower()
    if dist not in ("normal", "binomial", "poisson", "exponential", "uniform"):
        raise LabError("Distribusi tidak dikenal.", "err.dist")
    rows = []
    params = {"dist": dist}
    if dist == "normal":
        mu = _num(_ndef(d, "mu", 0), "mu", minv=-100.0, maxv=100.0)
        sd = _num(_ndef(d, "sd", 1), "sd", minv=0.05, maxv=50.0)
        a = _num(_ndef(d, "a", mu - 3 * sd), "a", minv=-1e6, maxv=1e6)
        b = _num(_ndef(d, "b", mu + 3 * sd), "b", minv=-1e6, maxv=1e6)
        if b < a:
            a, b = b, a
        pa = _norm_cdf((a - mu) / sd)
        pb = _norm_cdf((b - mu) / sd)
        rows = [["P(a≤X≤b)", f"{pb - pa:.10g}", False],
                ["mean", _fmt(mu), False], ["sd", _fmt(sd), False]]
        params.update({"mu": mu, "sd": sd, "a": a, "b": b})
    elif dist == "binomial":
        n = _int(_ndef(d, "n", 10), "n", 1, 400)
        p = _num(_ndef(d, "p", 0.5), "p", minv=0.0, maxv=1.0)
        a = _int(_ndef(d, "a", 0), "a", 0, n)
        b = _int(_ndef(d, "b", n), "b", 0, n)
        if b < a:
            a, b = b, a
        # P(a<=X<=b) via pmf
        def pmf(k):
            if p in (0.0, 1.0):
                return 1.0 if k == (0 if p == 0.0 else n) else 0.0
            logc = math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)
            return math.exp(logc + k * math.log(p) + (n - k) * math.log(1 - p))
        tot = sum(pmf(k) for k in range(a, b + 1))
        rows = [["P(a≤X≤b)", f"{tot:.10g}", False],
                ["mean", _fmt(n * p), False], ["var", _fmt(n * p * (1 - p)), False]]
        params.update({"n": n, "p": p, "a": a, "b": b})
    elif dist == "poisson":
        lam = _num(_ndef(d, "lam", 2), "lam", minv=0.01, maxv=500.0)
        a = _int(_ndef(d, "a", 0), "a", 0, 2000)
        b = _int(_ndef(d, "b", max(20, int(3 * lam + 5))), "b", 0, 2000)
        if b < a:
            a, b = b, a
        def pmf(k):
            return math.exp(-lam + k * math.log(lam) - math.lgamma(k + 1)) if k > 0 \
                else math.exp(-lam)
        tot = sum(pmf(k) for k in range(a, b + 1))
        rows = [["P(a≤X≤b)", f"{tot:.10g}", False], ["mean", _fmt(lam), False]]
        params.update({"lam": lam, "a": a, "b": b})
    elif dist == "exponential":
        lam = _num(_ndef(d, "lam", 1), "lam", minv=0.001, maxv=100.0)
        a = _num(_ndef(d, "a", 0), "a", minv=0.0, maxv=1e6)
        b = _num(_ndef(d, "b", 3 / lam), "b", minv=0.0, maxv=1e6)
        if b < a:
            a, b = b, a
        cdf = lambda x: 1.0 - math.exp(-lam * x) if x > 0 else 0.0
        rows = [["P(a≤X≤b)", f"{cdf(b) - cdf(a):.10g}", False],
                ["mean", _fmt(1 / lam), False]]
        params.update({"lam": lam, "a": a, "b": b})
    else:  # uniform
        lo = _num(_ndef(d, "lo", 0), "lo", minv=-1e6, maxv=1e6)
        hi = _num(_ndef(d, "hi", 10), "hi", minv=-1e6, maxv=1e6)
        if hi <= lo:
            raise LabError("Batas atas harus > batas bawah.", "err.range")
        a = _clamp(_num(_ndef(d, "a", lo), "a", minv=-1e6, maxv=1e6), lo, hi)
        b = _clamp(_num(_ndef(d, "b", hi), "b", minv=-1e6, maxv=1e6), lo, hi)
        rows = [["P(a≤X≤b)", f"{(b - a) / (hi - lo):.10g}", False],
                ["mean", _fmt((lo + hi) / 2), False]]
        params.update({"lo": lo, "hi": hi, "a": a, "b": b})
    return {"canvas": True, "engine": "gdist", "params": params, "rows": rows}


# ---------- ggraphalgo: Dijkstra / BFS / DFS / MST ----------
def g_graphalgo(d):
    algo = str(d.get("algo") or "dijkstra").strip().lower()
    if algo not in ("dijkstra", "bfs", "dfs", "kruskal"):
        raise LabError("Algoritma tidak dikenal.", "err.algo")
    n = _int(_ndef(d, "n", 12), "n", 4, 26)
    density = _num(_ndef(d, "density", 0.35), "density", minv=0.1, maxv=0.9)
    seed = _int(_ndef(d, "seed", 42), "seed", 0, 999999)
    return {"canvas": True, "engine": "ggraphalgo",
            "params": {"algo": algo, "n": n, "density": density, "seed": seed},
            "rows": [["note", r"\text{drag node, pilih algoritma, lihat animasi langkah}", True]]}


# ---------- gfield: muatan draggable + ekipotensial ----------
def g_field(d):
    n = _int(_ndef(d, "n", 4), "n", 1, 8)
    seed = _int(_ndef(d, "seed", 7), "seed", 0, 999999)
    equip = _int(_ndef(d, "equip", 18), "equip", 0, 40)
    return {"canvas": True, "engine": "gfield",
            "params": {"n": n, "seed": seed, "equip": equip},
            "rows": [["note", r"\mathbf{E} = \sum_i \dfrac{k q_i}{r_i^{2}}\hat{r}_i\ \text{— drag muatan!}", True]]}


# ---------- gpvcycle: P-V Carnot / Otto / Diesel ----------
def g_pvcycle(d):
    cycle = str(d.get("cycle") or "carnot").strip().lower()
    if cycle not in ("carnot", "otto", "diesel"):
        raise LabError("Siklus tidak dikenal.", "err.cycle")
    rows = []
    params = {"cycle": cycle}
    gamma = _num(_ndef(d, "gamma", 1.4), "gamma", minv=1.05, maxv=1.8)
    if cycle == "carnot":
        th = _num(_ndef(d, "th", 600), "th", minv=1.0, maxv=2000.0)
        tc = _num(_ndef(d, "tc", 300), "tc", minv=0.1, maxv=2000.0)
        if tc >= th:
            raise LabError("T dingin harus < T panas.", "err.pv_tc")
        eta = 1.0 - tc / th
        rows = [["eta", f"{eta * 100:.10g} %", False],
                ["formula", r"\eta = 1 - \dfrac{T_c}{T_h}", True]]
        params.update({"th": th, "tc": tc, "gamma": gamma})
    elif cycle == "otto":
        r = _num(_ndef(d, "r", 9), "r", minv=1.5, maxv=30.0)
        eta = 1.0 - r ** (1.0 - gamma)
        rows = [["eta", f"{eta * 100:.10g} %", False],
                ["formula", r"\eta = 1 - r^{1-\gamma}", True]]
        params.update({"r": r, "gamma": gamma})
    else:
        r = _num(_ndef(d, "r", 18), "r", minv=1.5, maxv=30.0)
        rc = _num(_ndef(d, "rc", 2.5), "rc", minv=1.2, maxv=8.0)
        if rc >= r:
            raise LabError("Cut-off rc harus < r kompresi.", "err.pv_rc")
        eta = 1.0 - (1.0 / gamma) * (rc ** gamma - 1) / (rc ** (gamma - 1) * (r ** (gamma - 1)))
        rows = [["eta", f"{eta * 100:.10g} %", False],
                ["formula", r"\eta = 1 - \dfrac{1}{\gamma}\dfrac{r_c^{\gamma}-1}{r^{\gamma-1}(r_c-1)}", True]]
        params.update({"r": r, "rc": rc, "gamma": gamma})
    return {"canvas": True, "engine": "gpvcycle", "params": params, "rows": rows}


# ---------- gising: Ising Monte Carlo ----------
def g_ising(d):
    size = _int(_ndef(d, "size", 100), "size", 16, 160)
    temp = _num(_ndef(d, "temp", 2.269), "temp", minv=0.05, maxv=8.0)
    speed = _int(_ndef(d, "speed", 30), "speed", 1, 60)
    return {"canvas": True, "engine": "gising",
            "params": {"size": size, "temp": temp, "speed": speed},
            "rows": [["note", r"\text{Metropolis: } \Delta E = 2Js_i,\ T_c \approx 2.269\,J/\text{kb}", True]]}


# ---------- gminkowski: diagram Minkowski ----------
def g_minkowski(d):
    v = _num(_ndef(d, "v", 0.5), "v", minv=0.0, maxv=0.999)
    gamma = 1.0 / math.sqrt(1.0 - v * v)
    return {"canvas": True, "engine": "gminkowski",
            "params": {"v": v, "gamma": gamma},
            "rows": [["gamma", _fmt(gamma), False],
                     ["formula", r"\gamma = \dfrac{1}{\sqrt{1-v^{2}/c^{2}}}", True]]}


# ---------- gfluid: Stable Fluids (Jos Stam) ----------
def g_fluid(d):
    size = _int(_ndef(d, "size", 128), "size", 48, 192)
    visc = _num(_ndef(d, "visc", 0.000001), "visc", minv=0.0, maxv=0.001)
    diff = _num(_ndef(d, "diff", 0.0000001), "diff", minv=0.0, maxv=0.001)
    return {"canvas": True, "engine": "gfluid",
            "params": {"size": size, "visc": visc, "diff": diff},
            "rows": [["note", r"\text{Navier-Stokes semi-Lagrangian (Jos Stam)}", True]]}


# ---------- ggeodesic: Schwarzschild geodesic ----------
def g_geodesic(d):
    mode = str(d.get("mode") or "light").strip().lower()
    if mode not in ("light", "massive"):
        raise LabError("Mode geodesik tidak dikenal.", "err.mode", "geodesik")
    b = _num(_ndef(d, "b", 3.0), "b", minv=1.05, maxv=6.0)      # impact param / rs
    E = _num(_ndef(d, "E", 0.9), "E", minv=0.55, maxv=2.0)      # energi/m (massive)
    L = _num(_ndef(d, "L", 1.2), "L", minv=0.0, maxv=6.0)       # momentum sudut / rs
    params = {"mode": mode, "b": b, "E": E, "L": L}
    rows = [["photon_sphere", "1.5", False],
            ["rs", "1.0", False],
            ["formula", r"\dfrac{d^{2}u}{d\varphi^{2}} = \dfrac{3}{2}u^{2} - u\ (u = r_s/r)", True]]
    if mode == "light" and b < 1.5:
        rows.append(["fate", "capture", False])
    elif mode == "light":
        rows.append(["fate", "deflect", False])
    return {"canvas": True, "engine": "ggeodesic", "params": params, "rows": rows}


# ---------- gray: ray tracing lensa ----------
def g_ray(d):
    f1 = _num(_ndef(d, "f1", 150), "f1", minv=-300.0, maxv=300.0, allow_zero=False)
    f2 = _num(_ndef(d, "f2", -150), "f2", minv=-300.0, maxv=300.0, allow_zero=False)
    nray = _int(_ndef(d, "nray", 7), "nray", 3, 15)
    d12 = _num(_ndef(d, "d12", 320), "d12", minv=40.0, maxv=800.0)
    return {"canvas": True, "engine": "gray",
            "params": {"f1": f1, "f2": f2, "nray": nray, "d12": d12},
            "rows": [["formula", r"\dfrac{1}{f} = \dfrac{1}{d_o} + \dfrac{1}{d_i}", True]]}


TOOLS = {
    "gdomain": g_domain, "gfractal": g_fractal, "gsurf3d": g_surf3d,
    "gfrenet": g_frenet, "gtrans3d": g_trans3d, "gslope": g_slope,
    "gdist": g_dist, "ggraphalgo": g_graphalgo, "gfield": g_field,
    "gpvcycle": g_pvcycle, "gising": g_ising, "gminkowski": g_minkowski,
    "gfluid": g_fluid, "ggeodesic": g_geodesic, "gray": g_ray,
}


def run_tool(tool, data):
    fn = TOOLS.get(str(tool or ""))
    if not fn:
        raise LabError(f"Graphing tool '{tool}' tidak dikenal.", "err.tool", tool)
    return fn(data or {})
