/* ============================================================
   GRAPHERS 2, 6 engine Plotly (gsurf3d, gfrenet, gtrans3d,
   gdist, gpvcycle, ggeodesic). Merge ke window.GRAPH_ENGINES.
   Butuh graphers.js (parser) + app.js (layout2d) lebih dulu.
   ============================================================ */
(function () {
  "use strict";
  const G = window.GRAPH_ENGINES || {};
  const { compileReal } = window.__GRAPH_TEST || {};
  const layout2d = () => (typeof window.layout2d === "function" ? window.layout2d() : {});
  const theme = () => document.documentElement.dataset.theme || "gold";
  const cssv = (v) => getComputedStyle(document.documentElement).getPropertyValue(v).trim();

  /* ---------- gsurf3d: surface + tangent plane + level curves ---------- */
  G.gsurf3d = {
    kind: "plotly",
    mount(el, p) {
      this.update(p, el);
    },
    update(p, elArg) {
      const el = elArg || this._el;
      if (!el || !window.Plotly || !compileReal) return;
      this._el = el;
      let f;
      try { f = compileReal(p.expr || "sin(x)*cos(2*y)", ["x", "y"]); }
      catch (e) { el.textContent = "Expr error: " + e.message; return; }
      const n = p.n || 40, rng = p.range || 4;
      const xs = [], ys = [], zz = [];
      for (let i = 0; i <= n; i++) xs.push(-rng + (2 * rng * i) / n);
      for (let j = 0; j <= n; j++) ys.push(-rng + (2 * rng * j) / n);
      for (let j = 0; j <= n; j++) {
        const row = [];
        for (let i = 0; i <= n; i++) {
          let v = 0;
          try { v = f(xs[i], ys[j]); } catch (e) { v = NaN; }
          row.push(isFinite(v) ? v : null);
        }
        zz.push(row);
      }
      const px = Math.max(-rng, Math.min(rng, p.px || 1));
      const py = Math.max(-rng, Math.min(rng, p.py || 1));
      let f0 = 0, fx = 0, fy = 0;
      const h = 1e-4;
      try {
        f0 = f(px, py);
        fx = (f(px + h, py) - f(px - h, py)) / (2 * h);
        fy = (f(px, py + h) - f(px, py - h)) / (2 * h);
      } catch (e) {}
      const R = rng * 0.5;
      const plane = {
        type: "surface", opacity: 0.55, showscale: false, colorscale: [[0, "#7fb4d8"], [1, "#7fb4d8"]],
        x: [px - R, px + R], y: [py - R, py + R],
        z: [[f0 + fx * (-R) + fy * (-R), f0 + fx * R + fy * (-R)],
            [f0 + fx * (-R) + fy * R, f0 + fx * R + fy * R]],
        hoverinfo: "skip",
      };
      const grad = {
        type: "scatter3d", mode: "lines+markers",
        x: [px, px + fx * R * 0.45], y: [py, py + fy * R * 0.45],
        z: [f0, f0 + (fx * fx + fy * fy) * R * 0.45],
        line: { color: "#d87f7f", width: 8 }, marker: { size: 5, color: "#d87f7f" },
        name: "grad f",
      };
      const traces = [{
        type: "surface", x: xs, y: ys, z: zz,
        colorscale: "Cividis", showscale: false,
        contours: { z: { show: true, usecolormap: true, project: { z: true } } },
      }, plane, grad, {
        type: "scatter3d", mode: "markers",
        x: [px], y: [py], z: [f0], marker: { size: 6, color: "#d87f7f" },
        name: "(x₀,y₀)",
      }];
      const txt = cssv("--cream") || "#f2e394";
      const bg = theme() === "light" ? "#fbf3df" : theme() === "black" ? "#000" : "#1d130b";
      const grid = theme() === "light" ? "#d8c9a6" : theme() === "black" ? "#444" : "#5a3f26";
      const ax = (t) => ({ title: { text: t, font: { color: txt, size: 13 } }, gridcolor: grid,
        zerolinecolor: grid, tickfont: { color: txt, size: 10 }, backgroundcolor: bg, showbackground: true });
      Plotly.react(el, traces, {
        paper_bgcolor: "rgba(0,0,0,0)", font: { color: txt },
        margin: { l: 0, r: 0, t: 0, b: 0 }, showlegend: false,
        scene: { xaxis: ax("x"), yaxis: ax("y"), zaxis: ax("z"), aspectmode: "cube" },
      }, { responsive: true, displaylogo: false });
    },
  };

  /* ---------- gfrenet: kurva parametrik + frame Frenet ---------- */
  G.gfrenet = {
    kind: "plotly",
    mount(el, p) { this.update(p, el); },
    update(p, elArg) {
      const el = elArg || this._el;
      if (!el || !window.Plotly || !compileReal) return;
      this._el = el;
      let fx, fy, fz;
      try {
        fx = compileReal(p.xt || "3*cos(t)", ["t"]);
        fy = compileReal(p.yt || "3*sin(t)", ["t"]);
        fz = compileReal(p.zt || "t/2", ["t"]);
      } catch (e) { el.textContent = "Expr error: " + e.message; return; }
      const n = p.n || 300, tmax = p.tmax || 18;
      const t0 = 0.001, tt = Math.min(tmax, p.t || 2);
      const pts = { x: [], y: [], z: [] };
      const r1 = 1e-4;
      const P = (t) => {
        const a = fx(t), b = fy(t), c = fz(t);
        const a2 = fx(t + r1), b2 = fy(t + r1), c2 = fz(t + r1);
        return { p: [a, b, c], v: [(a2 - a) / r1, (b2 - b) / r1, (c2 - c) / r1] };
      };
      const norm = (v) => {
        const m = Math.hypot(v[0], v[1], v[2]) || 1;
        return [v[0] / m, v[1] / m, v[2] / m];
      };
      const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
      for (let i = 0; i <= n; i++) {
        const t = t0 + (tmax - t0) * i / n;
        const r = P(t);
        pts.x.push(r.p[0]); pts.y.push(r.p[1]); pts.z.push(r.p[2]);
      }
      const cur = P(tt);
      const T = norm(cur.v);
      // N via dT/dt numerik
      const e2 = 1e-3;
      const T2 = norm(P(tt + e2).v), T1 = norm(P(Math.max(t0, tt - e2)).v);
      const dT = [T2[0] - T1[0], T2[1] - T1[1], T2[2] - T1[2]];
      const Nv = norm(dT);
      const B = norm(cross(T, Nv));
      const dN = [Nv[0] - T[0], Nv[1] - T[1], Nv[2] - T[2]];
      const kappa = Math.hypot(dT[0], dT[1], dT[2]) / e2 / (Math.hypot(cur.v[0], cur.v[1], cur.v[2]) || 1);
      const tau = Math.abs((cross(dT, Nv)[0] * B[0] + cross(dT, Nv)[1] * B[1] + cross(dT, Nv)[2] * B[2])) / e2;
      const arrow = (dir, color, name) => ({
        type: "scatter3d", mode: "lines", name,
        x: [cur.p[0], cur.p[0] + dir[0] * 0.8],
        y: [cur.p[1], cur.p[1] + dir[1] * 0.8],
        z: [cur.p[2], cur.p[2] + dir[2] * 0.8],
        line: { color, width: 9 },
      });
      const txt = cssv("--cream") || "#f2e394";
      const bg = theme() === "light" ? "#fbf3df" : theme() === "black" ? "#000" : "#1d130b";
      const grid = theme() === "light" ? "#d8c9a6" : theme() === "black" ? "#444" : "#5a3f26";
      const ax = (t) => ({ title: { text: t, font: { color: txt, size: 13 } }, gridcolor: grid,
        zerolinecolor: grid, tickfont: { color: txt, size: 10 }, backgroundcolor: bg, showbackground: true });
      Plotly.react(el, [
        { type: "scatter3d", mode: "lines", x: pts.x, y: pts.y, z: pts.z,
          line: { color: "#e0b04a", width: 6 } },
        arrow(T, "#9fd89f", "T"), arrow(Nv, "#7fb4d8", "N"), arrow(B, "#d87f7f", "B"),
        { type: "scatter3d", mode: "markers", x: [cur.p[0]], y: [cur.p[1]], z: [cur.p[2]],
          marker: { size: 5, color: "#fff" }, name: "t=" + tt.toFixed(2) },
      ], {
        paper_bgcolor: "rgba(0,0,0,0)", font: { color: txt },
        margin: { l: 0, r: 0, t: 0, b: 0 }, showlegend: true,
        legend: { font: { color: txt, size: 10 } },
        scene: { xaxis: ax("x"), yaxis: ax("y"), zaxis: ax("z"), aspectmode: "data" },
      }, { responsive: true, displaylogo: false });
    },
  };

  /* ---------- gtrans3d: transformasi linear 3D ---------- */
  G.gtrans3d = {
    kind: "plotly",
    _t: 1,
    mount(el, p) {
      this._M = p.matrix;
      if (p.morph != null) this._t = +p.morph;
      this.update(p, el);
    },
    update(p, elArg) {
      if (p.matrix) this._M = p.matrix;
      if (p.morph != null) this._t = +p.morph;
      const M = this._M;
      const t = this._t == null ? 1 : this._t;
      const el = elArg || this._el;
      if (!el || !window.Plotly) return;
      this._el = el;
      // M(t) = I + t*(M - I), morph animasi
      const Mi = [[1, 0, 0], [0, 1, 0], [0, 0, 1]];
      const Mt = Mi.map((row, i) => row.map((v, j) => v + t * (M[i][j] - v)));
      const mul = (A, v) => A.map((row) => row.reduce((s, x, i) => s + x * v[i], 0));
      // cube wireframe
      const verts = [];
      for (let i = 0; i < 8; i++) verts.push([i & 1 ? 1 : -1, i & 2 ? 1 : -1, i & 4 ? 1 : -1]);
      const E12 = [[0, 1], [0, 2], [1, 3], [2, 3], [4, 5], [4, 6], [5, 7], [6, 7], [0, 4], [1, 5], [2, 6], [3, 7]];
      const lines = { type: "scatter3d", mode: "lines", line: { color: "#e0b04a", width: 5 }, x: [], y: [], z: [] };
      E12.forEach(([a, b]) => {
        [verts[a], verts[b]].forEach((v) => {
          const tv = mul(Mt, v);
          lines.x.push(tv[0]); lines.y.push(tv[1]); lines.z.push(tv[2]);
        });
        lines.x.push(null); lines.y.push(null); lines.z.push(null);
      });
      // grid plane z=-1: garis x & y
      const gridL = { type: "scatter3d", mode: "lines", line: { color: "rgba(141,127,97.5)", width: 2 }, x: [], y: [], z: [], hoverinfo: "skip" };
      for (let g = -1; g <= 1; g += 0.5) {
        [[g, -1, g, 1], [-1, g, 1, g]].forEach(([x1, z1, x2, z2]) => {
          [[x1, -1, z1], [x2, -1, z2]].forEach((v) => {
            const tv = mul(Mt, v); gridL.x.push(tv[0]); gridL.y.push(tv[1]); gridL.z.push(tv[2]);
          });
          gridL.x.push(null); gridL.y.push(null); gridL.z.push(null);
        });
      }
      const basis = { type: "scatter3d", mode: "lines+markers", line: { width: 9 }, marker: { size: 5 }, x: [], y: [], z: [] };
      const bcol = ["#d87f7f", "#9fd89f", "#7fb4d8"];
      [[1, 0, 0], [0, 1, 0], [0, 0, 1]].forEach((v, i) => {
        const tv = mul(Mt, v);
        basis.x.push(0, tv[0], null); basis.y.push(0, tv[1], null); basis.z.push(0, tv[2], null);
      });
      basis.line.color = bcol;
      // eigen (Jacobi 3x3 simetris hanya; kalau tak simetris tampilkan det)
      const txt = cssv("--cream") || "#f2e394";
      const bg = theme() === "light" ? "#fbf3df" : theme() === "black" ? "#000" : "#1d130b";
      const grid = theme() === "light" ? "#d8c9a6" : theme() === "black" ? "#444" : "#5a3f26";
      const ax = (t2) => ({ title: { text: t2, font: { color: txt, size: 13 } }, gridcolor: grid,
        zerolinecolor: grid, tickfont: { color: txt, size: 10 }, backgroundcolor: bg, showbackground: true,
        range: [-3.2, 3.2] });
      Plotly.react(el, [gridL, lines, basis], {
        paper_bgcolor: "rgba(0,0,0,0)", font: { color: txt },
        margin: { l: 0, r: 0, t: 0, b: 0 }, showlegend: false,
        scene: { xaxis: ax("x"), yaxis: ax("y"), zaxis: ax("z"), aspectmode: "cube" },
      }, { responsive: true, displaylogo: false });
    },
    // slider morph
    setT(t) { this._t = t; this.update({}); },
  };

  /* ---------- gdist: distribution explorer ---------- */
  G.gdist = {
    kind: "plotly",
    mount(el, p) { this.update(p, el); },
    update(p, elArg) {
      const el = elArg || this._el;
      if (!el || !window.Plotly) return;
      this._el = el;
      const dist = p.dist || "normal";
      const traces = [];
      const txt = cssv("--cream") || "#f2e394";
      const gold = cssv("--gold") || "#e0b04a";
      const pdfLine = (xs, ys, name) => ({ type: "scatter", mode: "lines", x: xs, y: ys, name, line: { color: gold, width: 3 } });
      const area = (xs, ys) => ({ type: "scatter", mode: "lines", x: xs, y: ys, fill: "tozeroy",
        fillcolor: "rgba(224,176,74.25)", line: { width: 0 }, showlegend: false, hoverinfo: "skip" });
      const bars = (ks, ps, inRange) => ({
        type: "bar", x: ks, y: ps, marker: { color: ks.map((k) => (k >= p.a && k <= p.b ? gold : "rgba(141,127,97.5)")) },
      });
      if (dist === "normal") {
        const mu = p.mu || 0, sd = p.sd || 1;
        const xs = [], ys = [];
        for (let x = mu - 4 * sd; x <= mu + 4 * sd; x += (8 * sd) / 240) {
          xs.push(x);
          ys.push(Math.exp(-((x - mu) ** 2) / (2 * sd * sd)) / (sd * Math.sqrt(2 * Math.PI)));
        }
        traces.push(pdfLine(xs, ys, "PDF"));
        const ax2 = [], ay = [];
        for (let x = Math.max(p.a, mu - 4 * sd); x <= Math.min(p.b, mu + 4 * sd); x += (8 * sd) / 240) {
          ax2.push(x);
          ay.push(Math.exp(-((x - mu) ** 2) / (2 * sd * sd)) / (sd * Math.sqrt(2 * Math.PI)));
        }
        traces.push(area(ax2, ay));
      } else if (dist === "binomial") {
        const n = p.n || 10, pp = p.p || 0.5;
        const ks = [], ps = [];
        for (let k = 0; k <= n; k++) {
          const lg = math_lgamma(n + 1) - math_lgamma(k + 1) - math_lgamma(n - k + 1);
          ks.push(k); ps.push(pp === 0 ? (k === 0 ? 1 : 0) : pp === 1 ? (k === n ? 1 : 0) : Math.exp(lg + k * Math.log(pp) + (n - k) * Math.log(1 - pp)));
        }
        traces.push(bars(ks, ps));
      } else if (dist === "poisson") {
        const lam = p.lam || 2;
        const ks = [], ps = [];
        for (let k = 0; k <= Math.max(20, Math.ceil(lam * 3)); k++) {
          ks.push(k);
          ps.push(k === 0 ? Math.exp(-lam) : Math.exp(-lam + k * Math.log(lam) - math_lgamma(k + 1)));
        }
        traces.push(bars(ks, ps));
      } else if (dist === "exponential") {
        const lam = p.lam || 1;
        const xs = [], ys = [];
        for (let x = 0; x <= 6 / lam; x += (6 / lam) / 240) { xs.push(x); ys.push(lam * Math.exp(-lam * x)); }
        traces.push(pdfLine(xs, ys, "PDF"));
        const ax2 = [], ay = [];
        for (let x = Math.max(0, p.a); x <= Math.min(p.b, 6 / lam); x += (6 / lam) / 240) {
          ax2.push(x); ay.push(lam * Math.exp(-lam * x));
        }
        traces.push(area(ax2, ay));
      } else {
        const lo = p.lo || 0, hi = p.hi || 10;
        traces.push(pdfLine([lo, hi], [1 / (hi - lo), 1 / (hi - lo)], "PDF"));
        traces.push(area([Math.max(lo, p.a), Math.min(hi, p.b)],
          [1 / (hi - lo), 1 / (hi - lo)]));
      }
      const lay = layout2d();
      lay.bargap = 0.08;
      Plotly.react(el, traces, lay, { responsive: true, displaylogo: false });
    },
  };
  function math_lgamma(x) {
    // Lanczos lgamma ringkas
    const g = 7, C = [0.99999999999980993, 676.5203681218851, -1259.1392167224028,
      771.32342877765313, -176.61502916214059, 12.507343278686905, -0.13857109526572012,
      9.9843695780195716e-6, 1.5056327351493116e-7];
    if (x < 0.5) return Math.log(Math.PI / Math.sin(Math.PI * x)) - math_lgamma(1 - x);
    x -= 1;
    let a = C[0];
    const t = x + g + 0.5;
    for (let i = 1; i < g + 2; i++) a += C[i] / (x + i);
    return 0.5 * Math.log(2 * Math.PI) + (x + 0.5) * Math.log(t) - t + Math.log(a);
  }

  /* ---------- gpvcycle: P-V Carnot / Otto / Diesel ---------- */
  G.gpvcycle = {
    kind: "plotly",
    _phase: 0,
    mount(el, p) { this.update(p, el); this._timer && clearInterval(this._timer); },
    update(p, elArg) {
      const el = elArg || this._el;
      if (!el || !window.Plotly) return;
      this._el = el;
      const gamma = p.gamma || 1.4;
      let segs = [];
      if (p.cycle === "carnot") {
        const Th = p.th || 600, Tc = p.tc || 300;
        const V1 = 1, V2 = 2, f = Math.pow(Th / Tc, 1 / (gamma - 1));
        const V3 = V2 * f, V4 = V1 * f;
        const A = Th * Math.pow(V1, gamma - 1);   // nR
        segs.push({ f: (V) => A * Tc / Th * Math.pow(V1, gamma - 1) / Math.pow(V, 0) + 0, v: [V1, V2], k: "iso_h" });
        // gunakan bentuk eksplisit: isotherm P = C/V
        segs = [
          { pts: curve((V) => (Th * Math.pow(V1, gamma - 1)) / V, V1, V2), label: "T_h" },
          { pts: curve((V) => (Th * Math.pow(V1, gamma - 1) * Math.pow(V2, gamma)) / Math.pow(V, gamma), V2, V3), label: "adiabat" },
          { pts: curve((V) => (Tc * Math.pow(V4, gamma - 1)) / V, V3, V4), label: "T_c" },
          { pts: curve((V) => (Tc * Math.pow(V4, gamma - 1) * Math.pow(V4, gamma)) / Math.pow(V, gamma), V4, V1), label: "adiabat" },
        ];
      } else if (p.cycle === "otto") {
        const r = p.r || 9;
        const V1 = 1, V2 = 1 / r;
        const P1 = 1, P2 = P1 * Math.pow(r, gamma), P3 = P2 * 1.9, P4 = P3 / Math.pow(r, gamma);
        segs = [
          { pts: curve((V) => P1 * Math.pow(V1 / V, gamma), V1, V2), label: "kompresi" },
          { pts: line([[V2, P2], [V2, P3]]), label: "heat" },
          { pts: curve((V) => P3 * Math.pow(V2 / V, gamma), V2, V1), label: "usaha" },
          { pts: line([[V1, P4], [V1, P1]]), label: "cool" },
        ];
      } else {
        const r = p.r || 18, rc = p.rc || 2.5;
        const V1 = 1, V2 = 1 / r, V3 = V2 * rc;
        const P1 = 1, P2 = P1 * Math.pow(r, gamma), P3 = P2 * 1.6, P4 = P3 * Math.pow(V3 / V1, gamma);
        segs = [
          { pts: curve((V) => P1 * Math.pow(V1 / V, gamma), V1, V2), label: "kompresi" },
          { pts: line([[V2, P2], [V3, P2 * 1.6]]), label: "heat P" },
          { pts: curve((V) => P3 * Math.pow(V3 / V, gamma), V3, V1), label: "usaha" },
          { pts: line([[V1, P4], [V1, P1]]), label: "cool" },
        ];
      }
      const traces = segs.map((s) => ({
        type: "scatter", mode: "lines", x: s.pts.map((q) => q[0]), y: s.pts.map((q) => q[1]),
        line: { color: gold2(), width: 3 }, name: s.label,
      }));
      const all = segs.flatMap((s) => s.pts);
      const dot = all[Math.floor((this._phase % 100) / 100 * all.length)] || all[0];
      traces.push({ type: "scatter", mode: "markers", x: [dot[0]], y: [dot[1]],
        marker: { size: 12, color: "#d87f7f" }, name: "keadaan" });
      const lay = layout2d();
      lay.xaxis.title = { text: "V (relatif)", font: { size: 13, color: txt2() } };
      lay.yaxis.title = { text: "P (relatif)", font: { size: 13, color: txt2() } };
      Plotly.react(el, traces, lay, { responsive: true, displaylogo: false });
      // animasi dot — interval HARUS bisa dimatikan dari luar (pindah panel)
      clearInterval(this._timer);
      this._timer = setInterval(() => {
        this._phase = (this._phase + 2) % 100;
        const all2 = segs.flatMap((s) => s.pts);
        const d2 = all2[Math.floor((this._phase / 100) * all2.length)];
        if (d2 && this._el) Plotly.restyle(this._el, { x: [[d2[0]]], y: [[d2[1]]] }, [3]);
      }, 90);
    },
    /* dipanggil saat engine ditutup — matikan interval dot keadaan */
    destroy() {
      if (this._timer) { clearInterval(this._timer); this._timer = null; }
    },
  };
  function curve(f, a, b) {
    const pts = [];
    for (let i = 0; i <= 80; i++) {
      const V = a + (b - a) * i / 80;
      pts.push([V, f(V)]);
    }
    return pts;
  }
  function line(pts) { return pts; }
  function gold2() { return cssv("--gold") || "#e0b04a"; }
  function txt2() { return cssv("--cream") || "#f2e394"; }

  /* ---------- ggeodesic: Schwarzschild geodesics ---------- */
  G.ggeodesic = {
    kind: "plotly",
    mount(el, p) { this.update(p, el); },
    update(p, elArg) {
      const el = elArg || this._el;
      if (!el || !window.Plotly) return;
      this._el = el;
      const mode = p.mode || "light";
      const M = 0.5;                       // rs = 1 → M = 0.5
      const traces = [];
      let paths = [];
      if (mode === "light") {
        [2.6, 2.8, 3.2, 4.0, 5.5].forEach((b) => paths.push(traceLight(b)));
        traces.push(traceLightOne(p.b || 3, "#d87f7f", 5));
      } else {
        [0.6, 0.8, 1.0].forEach((L) => paths.push(traceMassive(p.E || 0.95, L)));
        traces.push(traceMassiveOne(p.E || 0.95, p.L || 1.2));
      }
      function traceLight(b, color, w) {
        // u'' = 1.5 u^2 - u (rs=1), mulai u=1/b, u'=0
        let u = 1 / b, du = 0;
        const dphi = 0.004, pts = { x: [], y: [] };
        for (let i = 0; i < 3000; i++) {
          const r = 1 / u;
          pts.x.push(r * Math.cos(i * dphi));
          pts.y.push(r * Math.sin(i * dphi));
          const k1 = 1.5 * u * u - u;
          const k2 = 1.5 * (u + dphi / 2 * k1) ** 2 - (u + dphi / 2 * k1);
          const k3 = 1.5 * (u + dphi / 2 * k2) ** 2 - (u + dphi / 2 * k2);
          const k4 = 1.5 * (u + dphi * k3) ** 2 - (u + dphi * k3);
          du += dphi / 6 * (k1 + 2 * k2 + 2 * k3 + k4);
          u += dphi * du;
          if (u < 0 || u > 30 || Math.hypot(pts.x[i], pts.y[i]) > 14) break;
        }
        return { ...pts, type: "scatter", mode: "lines",
          line: { color: color || "rgba(127,180,216.75)", width: w || 2 },
          name: color ? "b = " + b : undefined, hoverinfo: "x+y" };
      }
      function traceLightOne(b, color, w) { return traceLight(b, color, w); }
      function traceMassive(E, L) {
        // u'' + u = M/L^2 + 3 M u^2, mulai u=1/r_peri (titik balik), u'=0
        const u0 = (M + Math.sqrt(M * M + 2 * E * L * L)) / (2 * L * L);
        let u = u0, du = 0;
        const dphi = 0.005, pts = { x: [], y: [] };
        for (let i = 0; i < 4000; i++) {
          const r = 1 / u;
          pts.x.push(r * Math.cos(i * dphi));
          pts.y.push(r * Math.sin(i * dphi));
          const k1 = M / (L * L) + 3 * M * u * u - u;
          const k2 = M / (L * L) + 3 * M * (u + dphi / 2 * k1) ** 2 - (u + dphi / 2 * k1);
          const k3 = M / (L * L) + 3 * M * (u + dphi / 2 * k2) ** 2 - (u + dphi / 2 * k2);
          const k4 = M / (L * L) + 3 * M * (u + dphi * k3) ** 2 - (u + dphi * k3);
          du += dphi / 6 * (k1 + 2 * k2 + 2 * k3 + k4);
          u += dphi * du;
          if (!isFinite(u) || u > 25) break;
        }
        return { ...pts, type: "scatter", mode: "lines",
          line: { color: "rgba(159,216,159.6)", width: 2 }, hoverinfo: "x+y" };
      }
      function traceMassiveOne(E, L) {
        const tr = traceMassive(E, L);
        tr.line = { color: "#d87f7f", width: 4 };
        tr.name = "E=" + E + ", L=" + L;
        return tr;
      }
      const circle = (r, color, dash, name) => ({
        type: "scatter", mode: "lines",
        x: Array.from({ length: 90 }, (_, i) => r * Math.cos(i / 89 * 2 * Math.PI)),
        y: Array.from({ length: 90 }, (_, i) => r * Math.sin(i / 89 * 2 * Math.PI)),
        line: { color, width: 2, dash }, name,
      });
      traces.push(circle(1, "#d87f7f", "solid", "event horizon"));
      traces.push(circle(1.5, "#e0b04a", "dash", "photon sphere"));
      const lay = layout2d();
      lay.yaxis.scaleanchor = "x";
      lay.yaxis.scaleratio = 1;
      Plotly.react(el, traces, lay, { responsive: true, displaylogo: false });
    },
  };

  window.GRAPH_ENGINES = G;
})();
