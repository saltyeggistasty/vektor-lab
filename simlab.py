# ============================================================
# SIMLAB - mesin 10 simulasi advanced untuk tool cards baru.
# MODUL TERPISAH: gak nyentuh physics.py / vectorcalc.py /
# mathlab.py sama sekali (hanya impor helper). Semua simulasi
# numerik (RK4 / split-step / numpy), deterministik via seed.
# Semua tool balikin dict polos {rows, plot} - frontend yang
# ngurusi label i18n & render Plotly. Error user = raise LabError.
# Row keys ASCII (kunci i18n), nilai LaTeX = isL True.
# ============================================================
import math

import numpy as np
import sympy as sp

from mathlab import LabError, _num, _fmt, _expr

X_SYM = sp.Symbol("x")


def _trapz(y, x):
    """np.trapz hilang di numpy 2.x — pakai trapezoid kalau ada."""
    return float(np.trapezoid(y, x) if hasattr(np, "trapezoid") else np.trapz(y, x))


def _int(v, name, minv, maxv):
    """Parse integer ketat dengan batas."""
    try:
        n = int(round(float(str(v).replace(",", "."))))
    except (TypeError, ValueError):
        raise LabError(f"Nilai '{name}' harus bilangan bulat.",
                       "err.int", name)
    if n < minv or n > maxv:
        raise LabError(f"Nilai '{name}' harus antara {minv} dan {maxv}.",
                       "err.between", name, minv, maxv)
    return n


def _pick(v, name, allowed):
    s = str(v or "").strip().lower()
    if s not in allowed:
        raise LabError(f"Mode '{name}' tidak dikenal.", "err.mode", name)
    return s


def _rk4(f, s, dt, n):
    """Integrator RK4 klasik. f(state, t) -> dstate/dt (numpy array)."""
    out = np.empty((n + 1, len(s)), dtype=np.float64)
    out[0] = s
    st = np.asarray(s, dtype=np.float64)
    t = 0.0
    for i in range(n):
        k1 = f(st, t)
        k2 = f(st + 0.5 * dt * k1, t + 0.5 * dt)
        k3 = f(st + 0.5 * dt * k2, t + 0.5 * dt)
        k4 = f(st + dt * k3, t + dt)
        st = st + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
        if not np.all(np.isfinite(st)):
            raise LabError("Simulasi divergen (nilai tak hingga). Kecilkan langkah waktu.",
                   "err.sim_diverge")
        t += dt
        out[i + 1] = st
    return out


def _matrix2(s):
    """Parse 'a,b;c,d' -> numpy 2x2 ketat."""
    rows = [r for r in str(s or "").split(";") if r.strip()]
    if len(rows) != 2:
        raise LabError("Matriks harus tepat 2 baris, pisah dengan ';'.",
                   "err.matrix_rows2")
    m = []
    for r in rows:
        parts = [p for p in r.replace(",", " ").split() if p]
        if len(parts) != 2:
            raise LabError("Setiap baris harus tepat 2 angka, pisah dengan koma/spasi.",
                   "err.matrix_cells2")
        m.append([_num(p, "elemen matriks") for p in parts])
    return np.array(m, dtype=np.float64)


# ============================================================
# M1. SLOGISTIC — peta logistik: seri waktu / cobweb / bifurkasi
# ============================================================
def _logi_step(r, x):
    return r * x * (1.0 - x)


def sim_slogistic(d):
    mode = _pick(d.get("mode"), "mode", ("series", "cobweb", "bifurcation"))
    if mode == "bifurcation":
        return sim_slogistic_bifurcation()
    r = _num(d.get("r"), "r", minv=0.5, maxv=4.0)
    x0 = _num(d.get("x0"), "x0", minv=1e-9, maxv=1.0)
    n = _int(d.get("n"), "n", 10, 2000)
    xstar = (r - 1.0) / r if r > 1.0 else 0.0

    if mode in ("series", "cobweb"):
        xs = np.empty(n + 1)
        xs[0] = x0
        for k in range(n):
            xs[k + 1] = _logi_step(r, xs[k])
        if mode == "series":
            tail = xs[-min(60, n + 1):]
            uniq = np.unique(np.round(tail, 6))
            period = len(uniq) if len(uniq) <= 8 else 0
            if r < 1.0:
                regime = "punah"
            elif period == 1:
                regime = "titik_tetap"
            elif 2 <= period <= 8:
                regime = "periodik"
            else:
                regime = "kacau"
            lam = float(np.mean(np.log(np.maximum(r * np.abs(1 - 2 * xs[:-1]), 1e-300))))
            return {"rows": [
                ["r", _fmt(r), False],
                ["x0", _fmt(x0), False],
                ["x_final", _fmt(xs[-1]), False],
                ["x_star", _fmt(xstar), False],
                ["period", str(period) if period else "-", False],
                ["lyap", _fmt(lam), False],
                ["regime", regime, False],
            ], "plot": {"traces": [
                {"x": list(range(n + 1)), "y": [float(v) for v in xs], "mode": "lines"},
            ], "xlabel": "k", "ylabel": "x_k"}}
        # cobweb
        tx, ty = [x0], [0.0]
        x = x0
        for _ in range(min(n, 120)):
            y = _logi_step(r, x)
            tx.extend([x, x])
            ty.extend([y, y])
            x = y
            tx.append(x)
            ty.append(y)
            if abs(x - _logi_step(r, x)) < 1e-12:
                break
        gx = np.linspace(0.0, 1.0, 200)
        return {"rows": [
            ["r", _fmt(r), False],
            ["x0", _fmt(x0), False],
            ["x_final", _fmt(x), False],
            ["x_star", _fmt(xstar), False],
            ["map", r"x_{k+1} = r\,x_k(1 - x_k)", True],
        ], "plot": {"traces": [
            {"x": [float(v) for v in gx], "y": [float(_logi_step(r, v)) for v in gx], "mode": "lines"},
            {"x": [0.0, 1.0], "y": [0.0, 1.0], "mode": "lines", "dash": "dot"},
            {"x": tx, "y": ty, "mode": "lines"},
        ], "xlabel": "x_k", "ylabel": "x_{k+1}"}}

    # bifurkasi: sapu r, scatter titik atraktor
    return sim_slogistic_bifurcation()


def sim_slogistic_bifurcation():
    rs = np.linspace(2.5, 4.0, 400)
    tail = 60
    px, py = [], []
    for rv in rs:
        x = 0.5
        for _ in range(400):
            x = _logi_step(rv, x)
        for _ in range(tail):
            x = _logi_step(rv, x)
            px.append(float(rv))
            py.append(float(x))
    return {"rows": [
        ["note", r"\text{setiap kolom titik = atraktor } x \text{ pada } r \in [2.5,\,4]", True],
        ["map", r"x_{k+1} = r\,x_k(1 - x_k)", True],
    ], "plot": {"traces": [
        {"x": px, "y": py, "mode": "markers", "msize": 2},
    ], "xlabel": "r", "ylabel": "x"}}


# ============================================================
# M2. SLORENZ — atraktor Lorenz (RK4)
# ============================================================
def sim_slorenz(d):
    sigma = _num(d.get("sigma"), "sigma", minv=0.1, maxv=50.0)
    rho = _num(d.get("rho"), "rho", minv=0.1, maxv=120.0)
    beta = _num(d.get("beta"), "beta", minv=0.05, maxv=20.0)
    dt = _num(d.get("dt"), "dt", minv=0.0005, maxv=0.02)
    steps = _int(d.get("steps"), "steps", 500, 40000)
    t_end = dt * steps

    def f(s, t):
        return np.array([
            sigma * (s[1] - s[0]),
            s[0] * (rho - s[2]) - s[1],
            s[0] * s[1] - beta * s[2],
        ])

    traj = _rk4(f, np.array([1.0, 1.0, 1.0]), dt, steps)
    x, y, z = traj[:, 0], traj[:, 1], traj[:, 2]
    smax = float(np.max(np.abs(traj)))
    if smax > 1e4:
        raise LabError("Trajektori meledak — kecilkan rho atau dt.",
                   "err.sim_explode")

    fp_x = math.sqrt(max(beta * (rho - 1.0), 0.0))
    fp = r"(\pm\sqrt{\beta(\rho-1)},\ \pm\sqrt{\beta(\rho-1)},\ \rho-1)"
    dx = x[-200:] - fp_x
    dz = z[-200:] - (rho - 1.0)
    near_fp = bool(np.max(np.hypot(dx, dz)) < 0.5) if rho > 1 else False
    regime = "titik_tetap" if (rho <= 24.74 and near_fp) else "kacau"

    down = max(1, steps // 6000)
    return {"rows": [
        ["sigma", _fmt(sigma), False],
        ["rho", _fmt(rho), False],
        ["beta", _fmt(beta), False],
        ["t_end", _fmt(t_end) + " t", False],
        ["state_max", _fmt(smax), False],
        ["fp", fp, True],
        ["regime", regime, False],
    ], "plot": {"traces": [
        {"x": [float(v) for v in x[::down]], "y": [float(v) for v in z[::down]],
         "mode": "lines"},
    ], "xlabel": "x", "ylabel": "z"}}


# ============================================================
# M3. SFOURIER — sintesis deret Fourier (koefisien numerik)
# ============================================================
def sim_sfourier(d):
    expr_raw = str(d.get("expr") or "").strip()
    L = _num(d.get("L"), "L", minv=0.1, maxv=100.0)
    N = _int(d.get("N"), "N", 1, 60)
    f = _expr(expr_raw, ("x",))

    try:
        fn = sp.lambdify(X_SYM, f, modules=["numpy"])
        npts = 4000
        xs = np.linspace(-L, L, npts)
        with np.errstate(all="ignore"):
            ys = np.asarray(fn(xs), dtype=np.float64)
        if ys.ndim == 0:
            ys = np.full(npts, float(ys))
        if ys.shape != xs.shape:
            ys = np.broadcast_to(ys, xs.shape).astype(np.float64)
    except Exception as e:
        raise LabError(f"Fungsi tidak bisa dievaluasi: {e}", "err.func_eval", str(e))
    if not np.all(np.isfinite(ys)):
        raise LabError("Fungsi punya nilai tak hingga/NaN di interval [-L, L].",
                   "err.func_infinite")
    ys = np.clip(ys, -1e8, 1e8)

    a0 = _trapz(ys, xs) / (2 * L)
    an, bn = [], []
    for k in range(1, N + 1):
        ck = k * math.pi / L
        an.append(_trapz(ys * np.cos(ck * xs), xs) / L)
        bn.append(_trapz(ys * np.sin(ck * xs), xs) / L)

    def partial(xv):
        s = np.full_like(xv, a0, dtype=np.float64)
        for k in range(1, N + 1):
            ck = k * math.pi / L
            s += an[k - 1] * np.cos(ck * xv) + bn[k - 1] * np.sin(ck * xv)
        return s

    ps = partial(xs)
    rows = [["L", _fmt(L), False], ["N", str(N), False],
            ["a0", _fmt(a0), False]]
    for k in range(1, min(N, 3) + 1):
        rows.append([f"a{k}", _fmt(an[k - 1]), False])
        rows.append([f"b{k}", _fmt(bn[k - 1]), False])
    rows.append(["series",
                 r"f(x) \approx \dfrac{a_0}{2} + \sum_{n=1}^{N}\left[a_n\cos\dfrac{n\pi x}{L} + b_n\sin\dfrac{n\pi x}{L}\right]", True])
    step = max(1, npts // 500)
    return {"rows": rows, "plot": {"traces": [
        {"x": [float(v) for v in xs[::step]], "y": [float(v) for v in ys[::step]], "mode": "lines", "dash": "dot"},
        {"x": [float(v) for v in xs[::step]], "y": [float(v) for v in ps[::step]], "mode": "lines"},
    ], "xlabel": "x", "ylabel": "f(x)"}}


# ============================================================
# M4. SMATRIX — visualisasi transformasi matriks 2x2
# ============================================================
def sim_smatrix(d):
    M = _matrix2(d.get("matrix"))
    det = float(np.linalg.det(M))
    tr = float(np.trace(M))
    disc = tr * tr - 4 * det
    if disc >= 0:
        lam1 = (tr + math.sqrt(disc)) / 2
        lam2 = (tr - math.sqrt(disc)) / 2
        lam_txt = f"{_fmt(lam1)}, {_fmt(lam2)}"
    else:
        re = tr / 2
        im = math.sqrt(-disc) / 2
        lam_txt = f"{_fmt(re)} \u00b1 {_fmt(im)}i"

    orth = bool(np.allclose(M @ M.T, np.eye(2), atol=1e-9))
    if abs(det) < 1e-12:
        kind = "singular"
    elif orth and det > 0:
        kind = "rotasi"
    elif orth and det < 0:
        kind = "refleksi"
    elif abs(det - 1.0) < 1e-9:
        kind = "shear"
    else:
        kind = "skala"

    ang = np.linspace(0, 2 * math.pi, 73)
    circ_x, circ_y = np.cos(ang), np.sin(ang)
    txy = M @ np.vstack([circ_x, circ_y])

    sq = np.array([[0, 1, 1, 0, 0], [0, 0, 1, 1, 0]])
    tsq = M @ sq
    ev1 = M @ np.array([1, 0])
    ev2 = M @ np.array([0, 1])

    def tr_line(p0, p1):
        return {"x": [float(p0[0]), float(p1[0])], "y": [float(p0[1]), float(p1[1])],
                "mode": "lines+markers"}

    return {"rows": [
        ["det", _fmt(det), False],
        ["trace", _fmt(tr), False],
        ["lam", lam_txt, False],
        ["area", _fmt(abs(det)), False],
        ["kind", kind, False],
    ], "plot": {"traces": [
        {"x": [float(v) for v in circ_x], "y": [float(v) for v in circ_y], "mode": "lines", "dash": "dot"},
        {"x": [float(v) for v in txy[0]], "y": [float(v) for v in txy[1]], "mode": "lines"},
        {"x": [float(v) for v in sq[0]], "y": [float(v) for v in sq[1]], "mode": "lines", "dash": "dot"},
        {"x": [float(v) for v in tsq[0]], "y": [float(v) for v in tsq[1]], "mode": "lines", "fill": "toself", "opacity": 0.35},
        tr_line((0, 0), (1, 0)),
        tr_line((0, 0), ev1),
        tr_line((0, 0), (0, 1)),
        tr_line((0, 0), ev2),
    ], "xlabel": "x", "ylabel": "y"}}


# ============================================================
# M5. SWALK — random walk 2D & Brownian (deterministik via seed)
# ============================================================
def sim_swalk(d):
    n = _int(d.get("n"), "n", 1, 300)
    steps = _int(d.get("steps"), "steps", 10, 4000)
    seed = _int(d.get("seed"), "seed", 0, 999999)
    rng = np.random.RandomState(seed)
    ang = rng.uniform(0, 2 * math.pi, size=(n, steps))
    X = np.cumsum(np.cos(ang), axis=1)
    Y = np.cumsum(np.sin(ang), axis=1)
    X0 = np.hstack([np.zeros((n, 1)), X])
    Y0 = np.hstack([np.zeros((n, 1)), Y])
    r_end = np.hypot(X0[:, -1], Y0[:, -1])
    rms = float(np.sqrt(np.mean(r_end ** 2)))
    rms_th = math.sqrt(steps)

    traces = []
    shown = min(n, 12)
    sub = max(1, steps // 400)
    for i in range(shown):
        traces.append({"x": [float(v) for v in X0[i, ::sub]], "y": [float(v) for v in Y0[i, ::sub]],
                       "mode": "lines", "opacity": 0.55})
    traces.append({"x": [float(v) for v in X0[:, -1]], "y": [float(v) for v in Y0[:, -1]],
                   "mode": "markers"})
    return {"rows": [
        ["n", str(n), False],
        ["steps", str(steps), False],
        ["seed", str(seed), False],
        ["rms", _fmt(rms), False],
        ["rms_theory", _fmt(rms_th), False],
        ["mean_x", _fmt(float(np.mean(X0[:, -1]))), False],
        ["mean_y", _fmt(float(np.mean(Y0[:, -1]))), False],
        ["max_r", _fmt(float(np.max(r_end))), False],
    ], "plot": {"traces": traces, "xlabel": "x", "ylabel": "y"}}


# ============================================================
# F1. SDBLPEND — pendulum ganda (RK4, chaos + konservasi energi)
# ============================================================
def sim_sdblpend(d):
    m1 = _num(d.get("m1"), "m1", minv=0.01, maxv=100.0)
    m2 = _num(d.get("m2"), "m2", minv=0.001, maxv=100.0)
    L1 = _num(d.get("L1"), "L1", minv=0.1, maxv=10.0)
    L2 = _num(d.get("L2"), "L2", minv=0.1, maxv=10.0)
    g = _num(d.get("g"), "g", minv=0.5, maxv=50.0)
    th1 = math.radians(_num(d.get("th1"), "th1", minv=-179.0, maxv=179.0))
    th2 = math.radians(_num(d.get("th2"), "th2", minv=-179.0, maxv=179.0))
    t_end = _num(d.get("t_end"), "t_end", minv=1.0, maxv=60.0)
    dt = 0.002
    steps = min(int(t_end / dt), 40000)

    def f(s, t):
        a1, a2, w1, w2 = s
        dl = a1 - a2
        den = 2 * m1 + m2 - m2 * math.cos(2 * dl)
        dw1 = (-g * (2 * m1 + m2) * math.sin(a1)
               - m2 * g * math.sin(a1 - 2 * a2)
               - 2 * math.sin(dl) * m2 * (w2 * w2 * L2 + w1 * w1 * L1 * math.cos(dl))
               ) / (L1 * den)
        dw2 = (2 * math.sin(dl) * (w1 * w1 * L1 * (m1 + m2)
               + g * (m1 + m2) * math.cos(a1)
               + w2 * w2 * L2 * m2 * math.cos(dl))
               ) / (L2 * den)
        return np.array([w1, w2, dw1, dw2])

    def energy(s):
        a1, a2, w1, w2 = s
        y1 = -L1 * math.cos(a1)
        y2 = y1 - L2 * math.cos(a2)
        v1sq = (L1 * w1) ** 2
        v2sq = v1sq + (L2 * w2) ** 2 + 2 * L1 * L2 * w1 * w2 * math.cos(a1 - a2)
        # V = m1*g*y1 + m2*g*y2 (y2 sudah absolut dr pivot — JANGAN (m1+m2)*y1)
        return 0.5 * m1 * v1sq + 0.5 * m2 * v2sq + m1 * g * y1 + m2 * g * y2

    s0 = np.array([th1, th2, 0.0, 0.0])
    E0 = energy(s0)
    traj = _rk4(f, s0, dt, steps)
    E1 = energy(traj[-1])
    drift = abs((E1 - E0) / E0) if abs(E0) > 1e-12 else 0.0
    # jumlah putaran penuh rod 2 = lompatan 2pi di theta2 MENTAH (sebelum unwrap)
    flips = int(np.sum(np.abs(np.diff(traj[:, 1])) > math.pi))
    t = np.arange(steps + 1) * dt

    mode = _pick(d.get("view"), "view", ("angles", "path"))
    if mode == "angles":
        sub = max(1, steps // 3000)
        traces = [
            {"x": [float(v) for v in t[::sub]], "y": [math.degrees(v) for v in traj[::sub, 0]], "mode": "lines"},
            {"x": [float(v) for v in t[::sub]], "y": [math.degrees(v) for v in traj[::sub, 1]], "mode": "lines", "dash": "dash"},
        ]
        xl, yl = "t (s)", "theta (deg)"
    else:
        x2 = L1 * np.sin(traj[:, 0]) + L2 * np.sin(traj[:, 1])
        y2 = -(L1 * np.cos(traj[:, 0]) + L2 * np.cos(traj[:, 1]))
        sub = max(1, steps // 6000)
        traces = [{"x": [float(v) for v in x2[::sub]], "y": [float(v) for v in y2[::sub]], "mode": "lines"}]
        xl, yl = "x", "y"

    return {"rows": [
        ["E0", _fmt(E0) + " J", False],
        ["E1", _fmt(E1) + " J", False],
        ["drift", _fmt(drift * 100) + " %", False],
        ["flips", str(flips), False],
        ["t_end", _fmt(t_end) + " s", False],
    ], "plot": {"traces": traces, "xlabel": xl, "ylabel": yl}}


# ============================================================
# F2. SDRAG — proyektil dengan hambatan udara kuadratik (RK4)
# ============================================================
def sim_sdrag(d):
    v0 = _num(d.get("v0"), "v0", minv=0.1, maxv=1000.0)
    ang = math.radians(_num(d.get("angle"), "angle", minv=0.1, maxv=89.9))
    m = _num(d.get("m"), "m", minv=0.001, maxv=1000.0)
    Cd = _num(d.get("Cd"), "Cd", minv=0.0, maxv=2.0)
    rho = _num(d.get("rho"), "rho", minv=0.0, maxv=20.0)
    A = _num(d.get("A"), "A", minv=1e-6, maxv=10.0)
    g = _num(d.get("g"), "g", minv=0.5, maxv=50.0)
    k = rho * Cd * A / (2.0 * m)

    dt = 0.001

    def fire(with_drag):
        s = np.array([0.0, 0.0, v0 * math.cos(ang), v0 * math.sin(ang)])
        xs, ys = [0.0], [0.0]
        t = 0.0
        if with_drag:
            def ff(st, tt):
                vx, vy = st[2], st[3]
                v = math.hypot(vx, vy)
                return np.array([vx, vy, -k * v * vx, -g - k * v * vy])
        else:
            def ff(st, tt):
                return np.array([st[2], st[3], 0.0, -g])
        for _ in range(120000):
            k1 = ff(s, t)
            k2 = ff(s + 0.5 * dt * k1, t + 0.5 * dt)
            k3 = ff(s + 0.5 * dt * k2, t + 0.5 * dt)
            k4 = ff(s + dt * k3, t + dt)
            new = s + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
            if new[1] < 0:
                y_prev = ys[-1]
                frac = y_prev / (y_prev - new[1]) if y_prev != new[1] else 0.0
                xs.append(float(s[0] + (new[0] - s[0]) * frac))
                ys.append(0.0)
                return xs, ys, t + dt * frac
            s = new
            t += dt
            xs.append(float(s[0]))
            ys.append(float(s[1]))
        raise LabError("Simulasi terlalu lama — kecilkan v0.",
                   "err.sim_too_long")

    xs_d, ys_d, t_d = fire(True)
    xs_v, ys_v, t_v = fire(False)
    rng_d, rng_v = xs_d[-1], xs_v[-1]

    return {"rows": [
        ["k", _fmt(k) + " 1/m", False],
        ["range_drag", _fmt(rng_d) + " m", False],
        ["range_vac", _fmt(rng_v) + " m", False],
        ["ratio", _fmt(rng_d / rng_v) if rng_v > 0 else "-", False],
        ["h_max", _fmt(max(ys_d)) + " m", False],
        ["t_flight", _fmt(t_d) + " s", False],
    ], "plot": {"traces": [
        {"x": xs_v[::4], "y": ys_v[::4], "mode": "lines", "dash": "dot"},
        {"x": xs_d[::4], "y": ys_d[::4], "mode": "lines"},
    ], "xlabel": "x (m)", "ylabel": "y (m)"}}


# ============================================================
# F3. SKEPLER — orbit Kepler dua benda (RK4, vis-viva)
# ============================================================
def sim_skepler(d):
    a = _num(d.get("a"), "a", minv=0.1, maxv=100.0)
    e = _num(d.get("e"), "e", minv=0.0, maxv=0.95)
    mu = _num(d.get("mu"), "mu", minv=0.1, maxv=1000.0)
    orbits = _int(d.get("orbits"), "orbits", 1, 5)

    T_theory = 2.0 * math.pi * math.sqrt(a ** 3 / mu)
    steps = 4000
    dt = T_theory * orbits / steps
    r_per = a * (1 - e)
    v_per = math.sqrt(mu * (2.0 / r_per - 1.0 / a))   # vis-viva
    s0 = np.array([r_per, 0.0, 0.0, v_per])

    def f(s, t):
        x, y, vx, vy = s
        r3 = (x * x + y * y) ** 1.5
        return np.array([vx, vy, -mu * x / r3, -mu * y / r3])

    traj = _rk4(f, s0, dt, steps)
    x, y = traj[:, 0], traj[:, 1]
    r = np.hypot(x, y)

    # periode terukur: lintasan mulai dr perihelion ke atas, kembali
    # melintasi y=0 dr bawah ke atas = 1 orbit penuh
    up = np.where((y[:-1] < 0) & (y[1:] >= 0))[0]
    T_meas = float(dt * up[0]) if len(up) else T_theory
    E0 = 0.5 * (traj[0, 2] ** 2 + traj[0, 3] ** 2) - mu / r[0]
    E1 = 0.5 * (traj[-1, 2] ** 2 + traj[-1, 3] ** 2) - mu / r[-1]
    drift = abs((E1 - E0) / E0) if abs(E0) > 1e-12 else 0.0

    traces = [
        {"x": [float(v) for v in x[::2]], "y": [float(v) for v in y[::2]], "mode": "lines"},
        {"x": [0.0], "y": [0.0], "mode": "markers"},
        {"x": [float(x[0])], "y": [float(y[0])], "mode": "markers"},
    ]
    return {"rows": [
        ["a", _fmt(a), False],
        ["e", _fmt(e), False],
        ["r_per", _fmt(float(r.min())), False],
        ["r_ap", _fmt(float(r.max())), False],
        ["T_theory", _fmt(T_theory), False],
        ["T_meas", _fmt(T_meas), False],
        ["E", _fmt(E0), False],
        ["drift", _fmt(drift * 100) + " %", False],
        ["visviva", r"v^{2} = \mu\left(\dfrac{2}{r} - \dfrac{1}{a}\right)", True],
    ], "plot": {"traces": traces, "xlabel": "x", "ylabel": "y"}}


# ============================================================
# F4. SSLIT — pola interferensi celah ganda (+ envelope celah tunggal)
# ============================================================
def sim_sslit(d):
    lam = _num(d.get("lam"), "lam", minv=1e-11, maxv=1e-3)
    dd = _num(d.get("d"), "d", minv=1e-9, maxv=1e-2)
    L = _num(d.get("L"), "L", minv=0.01, maxv=100.0)
    a = _num(d.get("a"), "a", minv=0.0, maxv=1e-2)
    if a > dd:
        raise LabError("Lebar celah a harus <= jarak antar celah d.",
                   "err.dblslit_ad")
    span = _num(d.get("span"), "span", minv=0.5, maxv=30.0)
    dy = lam * L / dd
    ys = np.linspace(-span * dy, span * dy, 3000)
    b = math.pi * dd * ys / (lam * L)
    I = np.cos(b) ** 2
    if a > 0:
        al = math.pi * a * ys / (lam * L)
        with np.errstate(all="ignore"):
            env = np.where(np.abs(al) < 1e-12, 1.0, (np.sin(al) / al) ** 2)
        I = I * env
    I = I / float(I.max())

    rows = [
        ["dy", _fmt(dy * 1000) + " mm", False],
        ["formula", r"\Delta y = \dfrac{\lambda L}{d}", True],
        ["n_fringes", str(2 * int(span) + 1), False],
    ]
    if a > 0:
        rows.append(["y_env", _fmt(lam * L / a * 1000) + " mm", False])
        rows.append(["envmin", r"y_m = \dfrac{m\lambda L}{a}", True])
    traces = [{"x": [float(v * 1000) for v in ys], "y": [float(v) for v in I], "mode": "lines"}]
    return {"rows": rows, "plot": {"traces": traces, "xlabel": "y (mm)", "ylabel": "I/I0"}}


# ============================================================
# F5. SSCHROD — evolusi paket gelombang 1D (split-step Fourier)
#     Satuan natural: hbar = m = 1. E = k0^2/2.
# ============================================================
def sim_sschrod(d):
    k0 = _num(d.get("k0"), "k0", minv=0.1, maxv=3.0)
    x0 = _num(d.get("x0"), "x0", minv=-60.0, maxv=60.0)
    sigma = _num(d.get("sigma"), "sigma", minv=0.5, maxv=20.0)
    V0 = _num(d.get("V0"), "V0", minv=0.0, maxv=10.0)
    w = _num(d.get("w"), "w", minv=0.0, maxv=40.0)
    steps = _int(d.get("steps"), "steps", 100, 6000)
    dt = 0.01

    N = 1024
    half = 75.0
    xs = np.linspace(-half, half, N)
    dx = xs[1] - xs[0]

    if abs(x0) + 4 * sigma > half - 5:
        raise LabError("Paket terlalu lebar/dekat tepi domain — kecilkan sigma atau geser x0.",
                   "err.gauss_width")
    t_end = steps * dt
    if k0 * t_end > 120.0:
        raise LabError("Paket keluar domain (k0 * waktu terlalu besar) — kecilkan steps.",
                   "err.gauss_domain")

    psi = np.exp(-(xs - x0) ** 2 / (4 * sigma ** 2)).astype(np.complex128)
    psi *= np.exp(1j * k0 * xs)
    psi /= math.sqrt(_trapz(np.abs(psi) ** 2, xs))

    V = np.zeros(N)
    if V0 > 0 and w > 0:
        V += V0 * ((xs >= -w / 2) & (xs <= w / 2))

    kx = 2 * math.pi * np.fft.fftfreq(N, d=dx)
    half_step = np.exp(-0.5j * V * dt)
    k_step = np.exp(-0.5j * kx ** 2 * dt)

    snaps = []
    snap_every = max(1, steps // 5)
    psi_t = psi.copy()
    for i in range(steps + 1):
        if i % snap_every == 0 or i == steps:
            snaps.append(np.abs(psi_t) ** 2)
        if i == steps:
            break
        psi_t = half_step * psi_t
        psi_t = np.fft.ifft(k_step * np.fft.fft(psi_t))
        psi_t = half_step * psi_t

    normT = _trapz(snaps[-1], xs)
    x_center0 = _trapz(xs * snaps[0], xs)
    x_centerT = _trapz(xs * snaps[-1], xs)
    v_meas = (x_centerT - x_center0) / t_end if t_end > 0 else 0.0
    if w > 0 and V0 > 0:
        left = xs < (-w / 2 - 1e-9)
        right = xs > (w / 2 + 1e-9)
        R_prob = _trapz(snaps[-1][left], xs[left])
        T_prob = _trapz(snaps[-1][right], xs[right])
    else:
        R_prob, T_prob = 0.0, 1.0

    traces = []
    for j, dens in enumerate(snaps):
        traces.append({"x": [float(v) for v in xs[::2]], "y": [float(v) for v in dens[::2]],
                       "mode": "lines", "opacity": 0.4 + 0.6 * j / max(len(snaps) - 1, 1)})
    if V0 > 0 and w > 0:
        peak = float(np.max(snaps[-1]))
        traces.append({"x": [float(v) for v in xs[::2]],
                       "y": [float(v / V0 * peak * 0.5) for v in V[::2]],
                       "mode": "lines", "dash": "dot"})
    return {"rows": [
        ["norm0", "1", False],
        ["normT", _fmt(normT), False],
        ["drift", _fmt(abs(normT - 1.0) * 100) + " %", False],
        ["E", _fmt(k0 ** 2 / 2), False],
        ["v_theory", _fmt(k0), False],
        ["v_meas", _fmt(v_meas), False],
        ["R_prob", _fmt(R_prob), False],
        ["T_prob", _fmt(T_prob), False],
        ["units", r"\hbar = m = 1,\; E = k_0^{2}/2", True],
    ], "plot": {"traces": traces, "xlabel": "x", "ylabel": "|psi|^2"}}


TOOLS = {
    "slogistic": sim_slogistic,
    "slorenz": sim_slorenz,
    "sfourier": sim_sfourier,
    "smatrix": sim_smatrix,
    "swalk": sim_swalk,
    "sdblpend": sim_sdblpend,
    "sdrag": sim_sdrag,
    "skepler": sim_skepler,
    "sslit": sim_sslit,
    "sschrod": sim_sschrod,
}


def run_tool(tool, data):
    fn = TOOLS.get(str(tool or ""))
    if not fn:
        raise LabError(f"Simulasi '{tool}' tidak dikenal.", "err.tool", tool)
    return fn(data or {})
