/* ============================================================
   GRAPHERS, mesin 15 graphing interaktif (client-side penuh).
   Core: parser ekspresi real (x,y,t) & complex (z), pan/zoom,
   canvas HiDPI, tema. Engines di-register ke window.GRAPH_ENGINES.
   Pure math terekspos ke __GRAPH_TEST utk node tests.
   ============================================================ */
(function () {
  "use strict";

  /* ================= CORE: tema & canvas ================= */
  function TC() {
    const s = getComputedStyle(document.documentElement);
    const g = (v, fb) => (s.getPropertyValue(v) || "").trim() || fb;
    return {
      cream: g("--cream", "#f2e394"), gold: g("--gold", "#e0b04a"),
      line: g("--line", "#4a3320"), bg2: g("--bg2", "#22170e"),
      bg: g("--bg", "#17100a"), muted: g("--muted", "#8d7f61"),
    };
  }
  function fitCanvas(cv) {
    /* DPR dibatasi perf.dpr_cap (igpu mode = hemat fill-rate GPU iGPU) */
    const cap = (window.PERF && window.PERF.dpr_cap) || 2;
    const dpr = Math.min(window.devicePixelRatio || 1, cap);
    const w = cv.clientWidth || cv.parentElement.clientWidth || 600;
    const h = cv.clientHeight || 420;
    if (cv.width !== Math.round(w * dpr) || cv.height !== Math.round(h * dpr)) {
      cv.width = Math.round(w * dpr);
      cv.height = Math.round(h * dpr);
    }
    const ctx = cv.getContext("2d");
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    return { ctx, w, h };
  }
  /* view dunia<->layar: cx,cy = pusat dunia; ppu = pixel per unit */
  function makeView(cv, cx, cy, ppu) {
    const v = {
      cx: cx || 0, cy: cy || 0, ppu: ppu || 60,
      sx(x) { return cv.clientWidth / 2 + (x - v.cx) * v.ppu; },
      sy(y) { return cv.clientHeight / 2 - (y - v.cy) * v.ppu; },
      wx(px) { return v.cx + (px - cv.clientWidth / 2) / v.ppu; },
      wy(py) { return v.cy - (py - cv.clientHeight / 2) / v.ppu; },
    };
    return v;
  }
  function attachPanZoom(cv, view, redraw) {
    let drag = null;
    const onDown = (e) => {
      drag = { x: e.clientX, y: e.clientY, cx: view.cx, cy: view.cy };
      cv.setPointerCapture(e.pointerId);
    };
    const onMove = (e) => {
      if (!drag) return;
      view.cx = drag.cx - (e.clientX - drag.x) / view.ppu;
      view.cy = drag.cy + (e.clientY - drag.y) / view.ppu;
      redraw();
    };
    const stop = () => { drag = null; };
    const onWheel = (e) => {
      e.preventDefault();
      const f = e.deltaY < 0 ? 1.12 : 1 / 1.12;
      const wx = view.wx(e.offsetX), wy = view.wy(e.offsetY);
      view.ppu = Math.min(4000, Math.max(6, view.ppu * f));
      view.cx = wx - (e.offsetX - cv.clientWidth / 2) / view.ppu;
      view.cy = wy + (e.offsetY - cv.clientHeight / 2) / view.ppu;
      redraw();
    };
    cv.addEventListener("pointerdown", onDown);
    cv.addEventListener("pointermove", onMove);
    cv.addEventListener("pointerup", stop);
    cv.addEventListener("pointercancel", stop);
    cv.addEventListener("wheel", onWheel, { passive: false });
    registerDispose(() => {
      cv.removeEventListener("pointerdown", onDown);
      cv.removeEventListener("pointermove", onMove);
      cv.removeEventListener("pointerup", stop);
      cv.removeEventListener("pointercancel", stop);
      cv.removeEventListener("wheel", onWheel);
    });
  }
  const rafThrottle = (fn) => {
    let q = false;
    return (...a) => {
      if (q) return;
      q = true;
      requestAnimationFrame(() => { q = false; fn(...a); });
    };
  };
  /* grid + sumbu bertema */
  function drawGrid(ctx, w, h, view) {
    const c = TC();
    ctx.fillStyle = c.bg;
    ctx.fillRect(0, 0, w, h);
    const step = Math.pow(10, Math.floor(Math.log10(80 / view.ppu)));
    ctx.lineWidth = 1;
    ctx.font = "10px sans-serif";
    const x0 = Math.floor(view.wx(0) / step) * step;
    const x1 = view.wx(w);
    for (let x = x0; x <= x1; x += step) {
      const px = Math.round(view.sx(x)) + 0.5;
      ctx.strokeStyle = Math.abs(x) < step / 2 ? c.muted : c.line;
      ctx.beginPath(); ctx.moveTo(px, 0); ctx.lineTo(px, h); ctx.stroke();
      if (Math.abs(x) > step / 2) {
        ctx.fillStyle = c.muted;
        ctx.fillText(String(+x.toFixed(6)), px + 2, view.sy(0) + 12);
      }
    }
    const y0 = Math.floor(view.wy(h) / step) * step;
    const y1 = view.wy(0);
    for (let y = y0; y <= y1; y += step) {
      const py = Math.round(view.sy(y)) + 0.5;
      ctx.strokeStyle = Math.abs(y) < step / 2 ? c.muted : c.line;
      ctx.beginPath(); ctx.moveTo(0, py); ctx.lineTo(w, py); ctx.stroke();
      if (Math.abs(y) > step / 2) {
        ctx.fillStyle = c.muted;
        ctx.fillText(String(+y.toFixed(6)), view.sx(0) + 4, py - 2);
      }
    }
  }

  /* ================= CORE: real parser (Pratt) ================= */
  const RFN = {
    sin: Math.sin, cos: Math.cos, tan: Math.tan,
    asin: Math.asin, acos: Math.acos, atan: Math.atan,
    sinh: Math.sinh, cosh: Math.cosh, tanh: Math.tanh,
    exp: Math.exp, log: Math.log, ln: Math.log, log10: Math.log10,
    sqrt: Math.sqrt, abs: Math.abs, floor: Math.floor, ceil: Math.ceil,
    sign: Math.sign, atan2: Math.atan2, min: Math.min, max: Math.max,
    pow: Math.pow, mod: (a, b) => a - b * Math.floor(a / b),
  };
  const RCONST = { pi: Math.PI, e: Math.E };
  function tokenize(s) {
    const out = [];
    let i = 0;
    while (i < s.length) {
      const ch = s[i];
      if (/\s/.test(ch)) { i++; continue; }
      if (/[0-9.]/.test(ch)) {
        let j = i;
        while (j < s.length && /[0-9.]/.test(s[j])) j++;
        out.push({ t: "num", v: parseFloat(s.slice(i, j)) });
        i = j;
      } else if (/[a-zA-Z_]/.test(ch)) {
        let j = i;
        while (j < s.length && /[a-zA-Z0-9_]/.test(s[j])) j++;
        out.push({ t: "id", v: s.slice(i, j) });
        i = j;
      } else if ("+-*/^(),%".includes(ch)) {
        out.push({ t: ch });
        i++;
      } else {
        throw new Error("Karakter tidak dikenal: " + ch);
      }
    }
    return out;
  }
  /* parse ke closure (env: objek variabel) */
  function parseReal(tokens) {
    let p = 0;
    const peek = () => tokens[p];
    const eat = () => tokens[p++];
    function expr(minp) {
      let left = unary();
      while (peek() && peek().t in BIN) {
        const op = peek().t;
        const prec = BIN[op];
        if (prec[0] < minp) break;
        eat();
        const right = expr(prec[0] + (prec[1] ? 0 : 1));
        const lc = left, rc = right, fn = prec[2];
        left = () => fn(lc, rc);     // LAZY: evaluasi saat dipanggil, bukan saat parse
      }
      return left;
    }
    const BIN = {
      "+": [1, false, (a, b) => a() + b()],
      "-": [1, false, (a, b) => a() - b()],
      "*": [2, false, (a, b) => a() * b()],
      "/": [2, false, (a, b) => a() / b()],
      "%": [2, false, (a, b) => RFN.mod(a(), b())],
      "^": [4, true, (a, b) => Math.pow(a(), b())],
    };
    function unary() {
      const t = peek();
      if (t && t.t === "-") { eat(); const v = expr(3); return () => -v(); }
      if (t && t.t === "+") { eat(); return expr(3); }
      return prim();
    }
    function prim() {
      const t = eat();
      if (!t) throw new Error("Ekspresi berakhir tak wajar.");
      if (t.t === "num") { const v = t.v; return () => v; }
      if (t.t === "id") {
        if (peek() && peek().t === "(") {
          eat();
          const args = [];
          if (peek() && peek().t !== ")") {
            args.push(expr(0));
            while (peek() && peek().t === ",") { eat(); args.push(expr(0)); }
          }
          if (!peek() || eat().t !== ")") throw new Error("Kurung tutup hilang.");
          const fn = RFN[t.v];
          if (!fn) throw new Error("Fungsi tidak dikenal: " + t.v);
          return () => fn(...args.map((a) => a()));
        }
        if (t.v in RCONST) { const v = RCONST[t.v]; return () => v; }
        const name = t.v;
        return () => {
          const v = ENV[name];
          if (v === undefined) throw new Error("Variabel belum diisi: " + name);
          return v;
        };
      }
      if (t.t === "(") {
        const v = expr(0);
        if (!peek() || eat().t !== ")") throw new Error("Kurung tutup hilang.");
        return () => v();
      }
      throw new Error("Token tak terduga: " + (t.v || t.t));
    }
    const root = expr(0);
    if (p < tokens.length) throw new Error("Sisa token tak terpakai.");
    return root;
  }
  let ENV = {};
  function compileReal(exprStr, varNames) {
    const toks = implicitMult(tokenize(String(exprStr || "")), (id) => id in RFN);
    // validasi statis: semua id harus fungsi dikenal / konstanta / variabel
    toks.forEach((t, i) => {
      if (t.t !== "id" || t.v in RFN || t.v in RCONST) return;
      const nx = toks[i + 1];
      if (nx && nx.t === "(") return;             // panggilan fungsi: divalidasi saat evaluasi
      if (!varNames.includes(t.v)) throw new Error("Variabel tidak dikenal: " + t.v);
    });
    const fn = parseReal(toks);
    return (...vals) => {
      ENV = {};
      varNames.forEach((v, i) => { ENV[v] = vals[i]; });
      return fn();
    };
  }

  /* ================= CORE: complex parser ================= */
  const C = (re, im) => ({ re, im });
  const cadd = (a, b) => C(a.re + b.re, a.im + b.im);
  const csub = (a, b) => C(a.re - b.re, a.im - b.im);
  const cmul = (a, b) => C(a.re * b.re - a.im * b.im, a.re * b.im + a.im * b.re);
  const cdiv = (a, b) => {
    const d = b.re * b.re + b.im * b.im;
    if (d === 0) return C(Infinity, Infinity);
    return C((a.re * b.re + a.im * b.im) / d, (a.im * b.re - a.re * b.im) / d);
  };
  const cabs = (a) => Math.hypot(a.re, a.im);
  const carg = (a) => Math.atan2(a.im, a.re);
  const cexp = (a) => C(Math.exp(a.re) * Math.cos(a.im), Math.exp(a.re) * Math.sin(a.im));
  const clog = (a) => C(Math.log(cabs(a) || 1e-300), carg(a));
  const cpow = (a, b) => {
    if (b.im === 0 && Number.isInteger(b.re)) {
      const n = b.re;
      let r = C(1, 0), base = C(a.re, a.im);
      const m = Math.abs(n);
      for (let k = 0; k < m; k++) r = cmul(r, base);
      return n < 0 ? cdiv(C(1, 0), r) : r;
    }
    return cexp(cmul(b, clog(a)));
  };
  const csin = (a) => C(Math.sin(a.re) * Math.cosh(a.im), Math.cos(a.re) * Math.sinh(a.im));
  const ccos = (a) => C(Math.cos(a.re) * Math.cosh(a.im), -Math.sin(a.re) * Math.sinh(a.im));
  const ctan = (a) => cdiv(csin(a), ccos(a));
  const csinh = (a) => C(Math.sinh(a.re) * Math.cos(a.im), Math.cosh(a.re) * Math.sin(a.im));
  const ccosh = (a) => C(Math.cosh(a.re) * Math.cos(a.im), Math.sinh(a.re) * Math.sin(a.im));
  const ctanh = (a) => cdiv(csinh(a), ccosh(a));
  const csqrt = (a) => {
    const r = Math.sqrt(cabs(a));
    const th = carg(a) / 2;
    return C(r * Math.cos(th), r * Math.sin(th));
  };
  const CFN = {
    sin: csin, cos: ccos, tan: ctan, exp: cexp, log: clog, ln: clog,
    sqrt: csqrt, sinh: csinh, cosh: ccosh, tanh: ctanh,
    abs: (a) => C(cabs(a), 0), arg: (a) => C(carg(a), 0),
  };
  function parseComplex(tokens) {
    let p = 0;
    const peek = () => tokens[p];
    const eat = () => tokens[p++];
    const CBIN = {
      "+": [1, false, (a, b) => cadd(a(), b())],
      "-": [1, false, (a, b) => csub(a(), b())],
      "*": [2, false, (a, b) => cmul(a(), b())],
      "/": [2, false, (a, b) => cdiv(a(), b())],
      "^": [4, true, (a, b) => cpow(a(), b())],
    };
    function expr(minp) {
      let left = unary();
      while (peek() && peek().t in CBIN) {
        const op = peek().t;
        const prec = CBIN[op];
        if (prec[0] < minp) break;
        eat();
        const right = expr(prec[0] + (prec[1] ? 0 : 1));
        const lc = left, rc = right, fn = prec[2];
        left = () => fn(lc, rc);     // LAZY
      }
      return left;
    }
    function unary() {
      const t = peek();
      if (t && t.t === "-") { eat(); const v = expr(3); return () => { const r = v(); return C(-r.re, -r.im); }; }
      if (t && t.t === "+") { eat(); return expr(3); }
      return prim();
    }
    function prim() {
      const t = eat();
      if (!t) throw new Error("Ekspresi berakhir tak wajar.");
      if (t.t === "num") { const v = t.v; return () => C(v, 0); }
      if (t.t === "id") {
        if (peek() && peek().t === "(") {
          eat();
          const args = [];
          if (peek() && peek().t !== ")") {
            args.push(expr(0));
            while (peek() && peek().t === ",") { eat(); args.push(expr(0)); }
          }
          if (!peek() || eat().t !== ")") throw new Error("Kurung tutup hilang.");
          const fn = CFN[t.v];
          if (!fn) throw new Error("Fungsi kompleks tidak dikenal: " + t.v);
          return () => fn(...args.map((a) => a()));
        }
        if (t.v === "z") return () => ZENV.z;
        if (t.v === "i") return () => C(0, 1);
        if (t.v === "pi") { const v = Math.PI; return () => C(v, 0); }
        if (t.v === "e") { const v = Math.E; return () => C(v, 0); }
        throw new Error("Simbol tidak dikenal: " + t.v + " (pakai z, i, pi, e)");
      }
      if (t.t === "(") {
        const v = expr(0);
        if (!peek() || eat().t !== ")") throw new Error("Kurung tutup hilang.");
        return () => v();
      }
      throw new Error("Token tak terduga: " + (t.v || t.t));
    }
    const root = expr(0);
    if (p < tokens.length) throw new Error("Sisa token tak terpakai.");
    return root;
  }
  /* normalisasi implicit multiplication: 2z -> 2*z, (z+1)(z-1) -> mul,
     xy -> x*y. id + "(" hanya fungsi kalau id dikenal (sin, exp, ...). */
  function implicitMult(tokens, isFn) {
    const out = [];
    for (let k = 0; k < tokens.length; k++) {
      const t = tokens[k];
      const prev = out[out.length - 1];
      if (prev) {
        const nextIsOperand = t.t === "id" || t.t === "num" || t.t === "(";
        const prevOperand =
          prev.t === "num" ||
          prev.t === ")" ||
          (prev.t === "id" && !(t.t === "(" && isFn(prev.v)));
        if (nextIsOperand && prevOperand) out.push({ t: "*" });
      }
      out.push(t);
    }
    return out;
  }
  let ZENV = { z: C(0, 0) };
  function compileComplex(exprStr) {
    const toks = implicitMult(tokenize(String(exprStr || "")), (id) => id in CFN);
    toks.forEach((t, i) => {
      if (t.t !== "id" || t.v in CFN || t.v === "z" || t.v === "i" ||
          t.v === "pi" || t.v === "e") return;
      const nx = toks[i + 1];
      if (nx && nx.t === "(") return;
      throw new Error("Simbol tidak dikenal: " + t.v + " (pakai z, i, pi, e)");
    });
    const fn = parseComplex(toks);
    return (z) => { ZENV = { z }; return fn(); };
  }

  /* ================= ENGINES registry ================= */
  const G = {};
  const mounts = [];   // {el, dispose} aktif

  function clearMounts() {
    mounts.forEach((m) => { try { m.dispose(); } catch (e) {} });
    mounts.length = 0;
  }
  function registerDispose(dispose) { mounts.push({ dispose }); }
  window.__GRAPH_CLEAR = clearMounts;

  /* ---------- gdomain: domain coloring ---------- */
  G.gdomain = {
    kind: "canvas",
    mount(cv, p) {
      const expr = p.expr || "1/z";
      let f;
      try { f = compileComplex(expr); } catch (e) {
        cv.getContext("2d").fillText("Expr error: " + e.message, 10, 20);
        return;
      }
      const view = makeView(cv, 0, 0, (cv.clientWidth || 600) / (2 * (p.range || 4)));
      let zmin = 0.0;                    // brightness cutoff log |f|
      function draw() {
        const { ctx, w, h } = fitCanvas(cv);
        const img = ctx.createImageData(w, h);
        const d = img.data;
        for (let py = 0; py < h; py++) {
          for (let px = 0; px < w; px++) {
            const z = C(view.wx(px), view.wy(py));
            let fw;                       // JANGAN shadow w (lebar canvas)!
            try { fw = f(z); } catch (e) { fw = C(NaN, NaN); }
            const k = (py * w + px) * 4;
            if (!isFinite(fw.re) || !isFinite(fw.im)) {
              d[k] = 10; d[k + 1] = 10; d[k + 2] = 10; d[k + 3] = 255;
              continue;
            }
            const hue = (carg(fw) + Math.PI) / (2 * Math.PI);     // 0..1
            const mag = Math.log(1 + cabs(fw));
            const stripes = p.scheme === "stripes"
              ? 0.5 + 0.5 * Math.sin(mag * Math.PI * 2 * 2) : 1;
            const shade = p.scheme === "shade"
              ? 1 / (1 + Math.exp(-2 * (mag - 1.5))) : 0.75 + 0.25 * Math.min(mag, 1);
            const sat = p.scheme === "phase" ? 0.55 : 0.85;
            // HSV -> RGB (v = brightness)
            const i0 = Math.floor(hue * 6), fr = hue * 6 - i0;
            const v = Math.max(0.12, Math.min(1, shade * stripes));
            const s = sat;
            const q = v * (1 - s * fr), t2 = v * (1 - s * (1 - fr));
            let r, g2, b;
            switch (i0 % 6) {
              case 0: r = v; g2 = t2; b = 0; break;
              case 1: r = q; g2 = v; b = 0; break;
              case 2: r = 0; g2 = v; b = t2; break;
              case 3: r = 0; g2 = q; b = v; break;
              case 4: r = t2; g2 = 0; b = v; break;
              default: r = v; g2 = 0; b = q;
            }
            d[k] = r * 255; d[k + 1] = g2 * 255; d[k + 2] = b * 255; d[k + 3] = 255;
          }
        }
        ctx.putImageData(img, 0, 0);
        // overlay grid tipis
        ctx.strokeStyle = "rgba(255,255,255,.25)";
        ctx.beginPath();
        ctx.moveTo(0, view.sy(0) + 0.5); ctx.lineTo(w, view.sy(0) + 0.5);
        ctx.moveTo(view.sx(0) + 0.5, 0); ctx.lineTo(view.sx(0) + 0.5, h);
        ctx.stroke();
        ctx.fillStyle = "rgba(255,255,255,.6)";
        ctx.font = "11px sans-serif";
        for (let gx = Math.ceil(view.wx(0)); gx <= Math.floor(view.wx(w)); gx++) {
          ctx.fillText(String(gx), view.sx(gx) + 2, view.sy(0) + 13);
        }
        for (let gy = Math.ceil(view.wy(h)); gy <= Math.floor(view.wy(0)); gy++) {
          if (gy !== 0) ctx.fillText((gy > 0 ? "i" : "-i") + Math.abs(gy), view.sx(0) + 4, view.sy(gy) - 2);
        }
      }
      const rd = rafThrottle(draw);
      attachPanZoom(cv, view, rd);
      draw();
      registerDispose(() => { });
      const ro = new ResizeObserver(rd);
      ro.observe(cv);
      registerDispose(() => ro.disconnect());
    },
  };

  /* ---------- gfractal: Mandelbrot / Julia / Newton ---------- */
  G.gfractal = {
    kind: "canvas",
    mount(cv, p) {
      const view = makeView(cv, p.mode === "julia" ? 0 : -0.6,
        0, (cv.clientWidth || 600) / 3.2);
      const it = p.iter || 150, mode = p.mode || "mandelbrot";
      const pw = p.power || 2;
      const cc = C(p.cre || -0.7269, p.cim || 0.1889);
      // newton: akar z^3-1 (3 warna)
      const roots3 = [C(1, 0), C(-0.5, Math.sqrt(3) / 2), C(-0.5, -Math.sqrt(3) / 2)];
      function draw() {
        const { ctx, w, h } = fitCanvas(cv);
        const img = ctx.createImageData(w, h);
        const d = img.data;
        for (let py = 0; py < h; py++) {
          for (let px = 0; px < w; px++) {
            const z0 = C(view.wx(px), view.wy(py));
            const k = (py * w + px) * 4;
            let r, g2, b;
            if (mode === "newton") {
              let z = z0, ok = false;
              for (let n = 0; n < it; n++) {
                // newton z^3 - 1 : z - (z^3-1)/(3z^2)
                const z2 = cmul(z, z), z3 = cmul(z2, z);
                const step = cdiv(csub(z3, C(1, 0)), cmul(C(3, 0), z2));
                z = csub(z, step);
                if (cabs(step) < 1e-10) { ok = true; break; }
              }
              if (ok) {
                let best = 0, bd = 1e9;
                roots3.forEach((rt, i) => {
                  const dd = cabs(csub(z, rt));
                  if (dd < bd) { bd = dd; best = i; }
                });
                const hue = [0.33, 0.0, 0.83][best];
                [r, g2, b] = hsv(hue, 0.8, 0.55 + 0.45 * (1 - Math.min(1, bd * 4)));
              } else { r = 5; g2 = 5; b = 5; }
            } else {
              let z = mode === "julia" ? z0 : C(0, 0);
              const c = mode === "julia" ? cc : z0;
              let n = 0;
              while (n < it && cabs(z) <= 4) {
                z = cpow(z, C(pw, 0));
                z = cadd(z, c);
                n++;
              }
              if (n >= it) { r = 8; g2 = 8; b = 14; }
              else {
                const smooth = n + 1 - Math.log2(Math.max(1, Math.log2(cabs(z))));
                const t = smooth / it;
                [r, g2, b] = hsv(0.62 - 0.85 * Math.pow(t, 0.5), 0.85, 0.35 + 0.65 * Math.pow(t, 0.35));
              }
            }
            d[k] = r * 255; d[k + 1] = g2 * 255; d[k + 2] = b * 255; d[k + 3] = 255;
          }
        }
        ctx.putImageData(img, 0, 0);
      }
      const rd = rafThrottle(draw);
      attachPanZoom(cv, view, rd);
      draw();
      const ro = new ResizeObserver(rd);
      ro.observe(cv);
      registerDispose(() => ro.disconnect());
    },
  };
  function hsv(h, s, v) {
    const i0 = Math.floor(h * 6), fr = h * 6 - i0;
    const q = v * (1 - s * fr), t2 = v * (1 - s * (1 - fr));
    switch (i0 % 6) {
      case 0: return [v, t2, 0];
      case 1: return [q, v, 0];
      case 2: return [0, v, t2];
      case 3: return [0, q, v];
      case 4: return [t2, 0, v];
      default: return [v, 0, q];
    }
  }

  /* ---------- gslope: slope field + klik solusi ---------- */
  G.gslope = {
    kind: "canvas",
    mount(cv, p) {
      let f;
      try { f = compileReal(p.expr || "x - y", ["x", "y"]); } catch (e) {
        cv.getContext("2d").fillText("Expr error: " + e.message, 10, 20);
        return;
      }
      const view = makeView(cv, (p.xlo + p.xhi) / 2, 0,
        (cv.clientWidth || 600) / (p.xhi - p.xlo));
      const sols = [];      // {x0,y0}
      const dens = p.density || 20;
      const xr = p.xhi - p.xlo;
      function rk4(x, y, dir) {
        const h = 0.04 * dir;
        const pts = [[x, y]];
        for (let k = 0; k < 500; k++) {
          const k1 = f(x, y), k2 = f(x + h / 2, y + h / 2 * k1),
            k3 = f(x + h / 2, y + h / 2 * k2), k4 = f(x + h, y + h * k3);
          y += h / 6 * (k1 + 2 * k2 + 2 * k3 + k4);
          x += h;
          if (!isFinite(y)) break;
          pts.push([x, y]);
          if (view.sy(y) < -50 || view.sy(y) > cv.clientHeight + 50) break;
        }
        return pts;
      }
      function draw() {
        const { ctx, w, h } = fitCanvas(cv);
        drawGrid(ctx, w, h, view);
        const dx = xr / dens;
        ctx.strokeStyle = TC().gold;
        ctx.lineWidth = 1.4;
        for (let gx = p.xlo; gx <= p.xhi + dx / 2; gx += dx) {
          for (let gy = p.ylo; gy <= p.yhi + dx / 2; gy += dx) {
            const m = f(gx, gy);
            if (!isFinite(m)) continue;
            const ang = Math.atan2(m, 1);
            const L = Math.min(dx / 2.4, 1) * view.ppu * 0.42;
            const px = view.sx(gx), py = view.sy(gy);
            ctx.beginPath();
            ctx.moveTo(px - L * Math.cos(ang), py + L * Math.sin(ang));
            ctx.lineTo(px + L * Math.cos(ang), py - L * Math.sin(ang));
            ctx.stroke();
          }
        }
        // solusi klik (RK4 dua arah)
        ctx.lineWidth = 2.2;
        ctx.strokeStyle = "#7fb4d8";
        sols.forEach((s) => {
          ctx.beginPath();
          [[1, rk4(s.x0, s.y0, 1)], [-1, rk4(s.x0, s.y0, -1)]].forEach(([dir, pts]) => {
            pts.forEach((pt, i) => {
              const X = view.sx(pt[0]), Y = view.sy(pt[1]);
              if (i === 0) ctx.moveTo(X, Y); else ctx.lineTo(X, Y);
            });
          });
          ctx.stroke();
          ctx.fillStyle = "#d87f7f";
          ctx.beginPath();
          ctx.arc(view.sx(s.x0), view.sy(s.y0), 4, 0, 7);
          ctx.fill();
        });
      }
      const rd = rafThrottle(draw);
      attachPanZoom(cv, view, rd);
      const onSlopeDown = (e) => {
        if (e.button !== 0) return;
        sols.push({ x0: view.wx(e.offsetX), y0: view.wy(e.offsetY) });
        rd();
      };
      cv.addEventListener("pointerdown", onSlopeDown);
      draw();
      const ro = new ResizeObserver(rd);
      ro.observe(cv);
      registerDispose(() => { ro.disconnect(); cv.removeEventListener("pointerdown", onSlopeDown); });
    },
  };

  /* ---------- gfield: muatan draggable + ekipotensial ---------- */
  G.gfield = {
    kind: "canvas",
    mount(cv, p) {
      const rng = new (function () { let s = p.seed || 7; return { next() { s = (s * 1103515245 + 12345) & 0x7fffffff; return s / 0x7fffffff; } }; })();
      const charges = [];
      for (let i = 0; i < (p.n || 4); i++) {
        charges.push({
          x: 0.25 + 0.5 * rng.next(), y: 0.25 + 0.5 * rng.next(),
          q: (i % 2 ? -1 : 1) * (0.5 + rng.next()),
        });
      }
      const view = makeView(cv, 0.5, 0.5, cv.clientWidth || 600);  // dunia [0,1]
      view.sx = (x) => x * cv.clientWidth;
      view.sy = (y) => (1 - y) * cv.clientHeight;
      view.wx = (px) => px / cv.clientWidth;
      view.wy = (py) => 1 - py / cv.clientHeight;
      const equipN = p.equip == null ? 18 : p.equip;
      let drag = -1;
      function E(x, y) {
        let ex = 0, ey = 0, pot = 0;
        charges.forEach((c) => {
          const dx = x - c.x, dy = y - c.y;
          const r2 = dx * dx + dy * dy + 1e-6;
          const r = Math.sqrt(r2);
          ex += (c.q * dx) / (r2 * r);
          ey += (c.q * dy) / (r2 * r);
          pot += c.q / r;
        });
        return [ex, ey, pot];
      }
      function draw() {
        const { ctx, w, h } = fitCanvas(cv);
        ctx.fillStyle = TC().bg;
        ctx.fillRect(0, 0, w, h);
        // ekipotensial: marching-ish sampling garis pot = level
        const NG = 90;
        const grid = [];
        for (let j = 0; j <= NG; j++) {
          grid.push([]);
          for (let i = 0; i <= NG; i++) {
            grid[j].push(E(i / NG, j / NG)[2]);
          }
        }
        const levels = [];
        for (let k = 0; k < equipN; k++) levels.push(-3 + 6 * k / Math.max(equipN - 1, 1));
        ctx.strokeStyle = "rgba(224,176,74.28)";
        ctx.lineWidth = 1;
        levels.forEach((lv) => {
          ctx.beginPath();
          for (let j = 0; j < NG; j++) {
            for (let i = 0; i < NG; i++) {
              const a = grid[j][i] - lv, b = grid[j][i + 1] - lv,
                c2 = grid[j + 1][i] - lv, dd = grid[j + 1][i + 1] - lv;
              const pts = [];
              [[a, b, i, j, i + 1, j], [b, dd, i + 1, j, i + 1, j + 1],
               [dd, c2, i + 1, j + 1, i, j + 1], [c2, a, i, j + 1, i, j]].forEach(([u, v2, x1, y1, x2, y2]) => {
                if ((u < 0) !== (v2 < 0)) {
                  const t = u / (u - v2);
                  pts.push([x1 + (x2 - x1) * t, y1 + (y2 - y1) * t]);
                }
              });
              if (pts.length >= 2) {
                ctx.moveTo(pts[0][0] / NG * w, (1 - pts[0][1] / NG) * h);
                ctx.lineTo(pts[1][0] / NG * w, (1 - pts[1][1] / NG) * h);
              }
            }
          }
          ctx.stroke();
        });
        // panah medan
        const step = w / 26;
        ctx.strokeStyle = TC().cream;
        for (let py = step / 2; py < h; py += step) {
          for (let px = step / 2; px < w; px += step) {
            const [ex, ey] = E(px / w, 1 - py / h);
            const m = Math.hypot(ex, ey);
            if (m < 1e-9) continue;
            const L = Math.min(step, step * Math.log(1 + m * 40)) * 0.55;
            const ux = ex / m, uy = -ey / m;   // y layar kebalik
            ctx.beginPath();
            ctx.moveTo(px - ux * L / 2, py - uy * L / 2);
            ctx.lineTo(px + ux * L / 2, py + uy * L / 2);
            ctx.stroke();
            // kepala panah
            ctx.beginPath();
            ctx.arc(px + ux * L / 2, py + uy * L / 2, 1.4, 0, 7);
            ctx.fillStyle = TC().cream;
            ctx.fill();
          }
        }
        // muatan
        charges.forEach((c) => {
          const px = c.x * w, py = (1 - c.y) * h;
          ctx.beginPath();
          ctx.arc(px, py, 13, 0, 7);
          ctx.fillStyle = c.q > 0 ? "#d87f7f" : "#7fb4d8";
          ctx.fill();
          ctx.strokeStyle = TC().gold;
          ctx.lineWidth = 2;
          ctx.stroke();
          ctx.fillStyle = "#141820";
          ctx.font = "bold 14px sans-serif";
          ctx.textAlign = "center";
          ctx.textBaseline = "middle";
          ctx.fillText(c.q > 0 ? "+" : "−", px, py + 1);
          ctx.textAlign = "left";
          ctx.textBaseline = "alphabetic";
        });
      }
      const rd = rafThrottle(draw);
      const onFieldDown = (e) => {
        charges.forEach((c, i) => {
          const px = c.x * cv.clientWidth, py = (1 - c.y) * cv.clientHeight;
          if (Math.hypot(e.offsetX - px, e.offsetY - py) < 18) drag = i;
        });
        if (drag >= 0) cv.setPointerCapture(e.pointerId);
      };
      const onFieldMove = (e) => {
        if (drag < 0) return;
        charges[drag].x = Math.min(1, Math.max(0, e.offsetX / cv.clientWidth));
        charges[drag].y = Math.min(1, Math.max(0, 1 - e.offsetY / cv.clientHeight));
        rd();
      };
      const stop = () => { drag = -1; };
      cv.addEventListener("pointerdown", onFieldDown);
      cv.addEventListener("pointermove", onFieldMove);
      cv.addEventListener("pointerup", stop);
      cv.addEventListener("pointercancel", stop);
      draw();
      const ro = new ResizeObserver(rd);
      ro.observe(cv);
      registerDispose(() => { ro.disconnect(); cv.removeEventListener("pointerdown", onFieldDown); cv.removeEventListener("pointermove", onFieldMove); cv.removeEventListener("pointerup", stop); cv.removeEventListener("pointercancel", stop); });
    },
  };

  /* ---------- gising: Ising Monte Carlo live ---------- */
  G.gising = {
    kind: "canvas",
    mount(cv, p) {
      const N = p.size || 100;
      const lat = new Int8Array(N * N);
      for (let i = 0; i < lat.length; i++) lat[i] = Math.random() < 0.5 ? -1 : 1;
      let T = p.temp || 2.269;
      const speed = p.speed || 30;
      let running = true;
      const expTab = {};
      function expLookup(dE) {
        const k = dE.toFixed(3);
        if (expTab[k] === undefined) expTab[k] = Math.exp(-dE / T);
        return expTab[k];
      }
      function step(sw) {
        const sweeps = Math.max(1, Math.round(speed * N / 60));
        for (let s = 0; s < sweeps; s++) {
          for (let k = 0; k < N * N; k++) {
            const i = (Math.random() * N) | 0, j = (Math.random() * N) | 0;
            const up = lat[((i + N - 1) % N) * N + j] + lat[((i + 1) % N) * N + j]
              + lat[i * N + (j + N - 1) % N] + lat[i * N + (j + 1) % N];
            const dE = 2 * lat[i * N + j] * up;
            if (dE <= 0 || Math.random() < expLookup(dE)) {
              lat[i * N + j] *= -1;
            }
          }
          if (sw) break;
        }
      }
      function draw() {
        const { ctx, w, h } = fitCanvas(cv);
        const img = ctx.createImageData(N, N);
        const d = img.data;
        let mag = 0;
        for (let i = 0; i < N * N; i++) {
          const up = lat[i] > 0;
          mag += lat[i];
          d[i * 4] = up ? 224 : 40;
          d[i * 4 + 1] = up ? 176 : 45;
          d[i * 4 + 2] = up ? 74 : 60;
          d[i * 4 + 3] = 255;
        }
        const off = document.createElement("canvas");
        off.width = N; off.height = N;
        off.getContext("2d").putImageData(img, 0, 0);
        ctx.imageSmoothingEnabled = false;
        ctx.drawImage(off, 0, 0, w, h);
        ctx.fillStyle = "rgba(0,0,0.55)";
        ctx.fillRect(6, 6, 150, 24);
        ctx.fillStyle = TC().cream;
        ctx.font = "12px sans-serif";
        ctx.fillText("m = " + (mag / (N * N)).toFixed(3) + "   T = " + T.toFixed(2), 12, 22);
      }
      function loop() {
        if (!running) return;
        step(false);
        draw();
        requestAnimationFrame(loop);
      }
      // slider T live: intercept via p.__live? gunakan update API
      G.gising._setT = (t) => { T = t; expTabClear(); };
      function expTabClear() { for (const k in expTab) delete expTab[k]; }
      draw();
      loop();
      registerDispose(() => { running = false; });
    },
    update(p) { if (p.temp != null && G.gising._setT) G.gising._setT(p.temp); },
  };

  /* ---------- gminkowski: diagram Minkowski ---------- */
  G.gminkowski = {
    kind: "canvas",
    mount(cv, p) {
      this._cv = cv;
      let v = Math.min(0.99, p.v || 0.5);
      this._setV = (nv) => { v = Math.min(0.99, nv); rd(); };
      const view = makeView(cv, 0, 0, (cv.clientWidth || 600) / 5);
      const events = [{ x: 0.8, ct: 0.6 }, { x: -0.5, ct: 1.1 }, { x: 0.3, ct: -0.7 }];
      let drag = -1;
      function draw() {
        const { ctx, w, h } = fitCanvas(cv);
        drawGrid(ctx, w, h, view);
        const c = TC();
        const beta = v, gamma = 1 / Math.sqrt(1 - beta * beta);
        const ang = Math.atan(beta);              // kemiringan sumbu ct'/x'
        // kerucut cahaya
        ctx.strokeStyle = "rgba(250,226,140.8)";
        ctx.lineWidth = 2;
        const R = Math.max(w, h);
        ctx.beginPath();
        ctx.moveTo(view.sx(-R / view.ppu), view.sy(-R / view.ppu));
        ctx.lineTo(view.sx(R / view.ppu), view.sy(R / view.ppu));
        ctx.moveTo(view.sx(-R / view.ppu), view.sy(R / view.ppu));
        ctx.lineTo(view.sx(R / view.ppu), view.sy(-R / view.ppu));
        ctx.stroke();
        // sumbu primed (frame bergerak) + garis simultan
        ctx.strokeStyle = "#7fb4d8";
        ctx.lineWidth = 2;
        const L = 2.4;
        ctx.beginPath();
        ctx.moveTo(view.sx(-L * Math.cos(ang)), view.sy(-L * Math.sin(ang)));
        ctx.lineTo(view.sx(L * Math.cos(ang)), view.sy(L * Math.sin(ang)));
        ctx.moveTo(view.sx(L * Math.sin(ang)), view.sy(-L * Math.cos(ang)));
        ctx.lineTo(view.sx(-L * Math.sin(ang)), view.sy(L * Math.cos(ang)));
        ctx.stroke();
        ctx.fillStyle = "#7fb4d8";
        ctx.font = "12px sans-serif";
        ctx.fillText("x'", view.sx(L * Math.cos(ang)) + 4, view.sy(L * Math.sin(ang)));
        ctx.fillText("ct'", view.sx(-L * Math.sin(ang)) + 4, view.sy(L * Math.cos(ang)) - 4);
        // hiperbola kalibrasi ct'^2 - x'^2 = 1
        ctx.strokeStyle = "rgba(217,127,127.9)";
        ctx.beginPath();
        for (let t = -3; t <= 3; t += 0.02) {
          const x = Math.sinh(t) / gamma, ct = Math.cosh(t) / gamma;
          const X = view.sx(x), Y = view.sy(ct);
          if (t === -3) ctx.moveTo(X, Y); else ctx.lineTo(X, Y);
        }
        ctx.stroke();
        // events + interval invarian
        events.forEach((ev) => {
          const X = view.sx(ev.x), Y = view.sy(ev.ct);
          ctx.fillStyle = TC().gold;
          ctx.beginPath(); ctx.arc(X, Y, 5, 0, 7); ctx.fill();
          const s2 = ev.ct * ev.ct - ev.x * ev.x;
          ctx.fillStyle = c.cream;
          ctx.font = "11px sans-serif";
          ctx.fillText("s² = " + s2.toFixed(2) + (s2 > 0 ? " (future)" : s2 < 0 ? " (spacelike)" : " (light)"),
            X + 8, Y - 6);
        });
        ctx.fillStyle = c.muted;
        ctx.font = "12px sans-serif";
        ctx.fillText("v = " + v.toFixed(3) + "c   γ = " + gamma.toFixed(3), 10, 18);
      }
      const rd = rafThrottle(draw);
      attachPanZoom(cv, view, rd);
      const onMinkDown = (e) => {
        events.forEach((ev, i) => {
          if (Math.hypot(e.offsetX - view.sx(ev.x), e.offsetY - view.sy(ev.ct)) < 12) {
            drag = i;
            cv.setPointerCapture(e.pointerId);
          }
        });
      };
      const onMinkMove = (e) => {
        if (drag < 0) return;
        events[drag].x = view.wx(e.offsetX);
        events[drag].ct = view.wy(e.offsetY);
        rd();
      };
      const stop = () => { drag = -1; };
      cv.addEventListener("pointerdown", onMinkDown);
      cv.addEventListener("pointermove", onMinkMove);
      cv.addEventListener("pointerup", stop);
      cv.addEventListener("pointercancel", stop);
      draw();
      const ro = new ResizeObserver(rd);
      ro.observe(cv);
      registerDispose(() => { ro.disconnect(); cv.removeEventListener("pointerdown", onMinkDown); cv.removeEventListener("pointermove", onMinkMove); cv.removeEventListener("pointerup", stop); cv.removeEventListener("pointercancel", stop); });
      registerDispose(() => ro.disconnect());
    },
    update(p) {
      /* v berubah -> cukup redraw dengan v baru (tanpa remount/leak) */
      if (this._setV && p.v != null) this._setV(p.v);
    },
  };

  /* ---------- ggraphalgo: Dijkstra / BFS / DFS / MST ---------- */
  G.ggraphalgo = {
    kind: "canvas",
    mount(cv, p) {
      const N = p.n || 12;
      let s = (p.seed || 42) >>> 0;
      const rnd = () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; };
      const nodes = [];
      for (let i = 0; i < N; i++) nodes.push({ x: 0.12 + 0.76 * rnd(), y: 0.14 + 0.72 * rnd() });
      const edges = [];
      for (let i = 0; i < N; i++) {
        for (let j = i + 1; j < N; j++) {
          if (rnd() < (p.density || 0.35)) {
            const d = Math.hypot(nodes[i].x - nodes[j].x, nodes[i].y - nodes[j].y);
            edges.push({ a: i, b: j, w: Math.round(2 + d * 22) });
          }
        }
      }
      // pastikan connected: sambung node berurutan
      for (let i = 1; i < N; i++) {
        const d = Math.hypot(nodes[i].x - nodes[i - 1].x, nodes[i].y - nodes[i - 1].y);
        if (!edges.some((e) => (e.a === i && e.b === i - 1) || (e.a === i - 1 && e.b === i)))
          edges.push({ a: i - 1, b: i, w: Math.round(2 + d * 22) });
      }
      const adj = nodes.map(() => []);
      edges.forEach((e, i) => { adj[e.a].push({ to: e.b, w: e.w, ei: i }); adj[e.b].push({ to: e.a, w: e.w, ei: i }); });
      // jalankan algoritma -> steps animasi
      const steps = [];
      const algo = p.algo || "dijkstra";
      const start = 0, goal = N - 1;
      const vis = new Array(N).fill(false);
      if (algo === "dijkstra") {
        const dist = new Array(N).fill(Infinity), par = new Array(N).fill(-1);
        dist[start] = 0;
        const done = new Array(N).fill(false);
        for (let it = 0; it < N; it++) {
          let u = -1, bd = Infinity;
          for (let i = 0; i < N; i++) if (!done[i] && dist[i] < bd) { bd = dist[i]; u = i; }
          if (u < 0) break;
          done[u] = true;
          steps.push({ type: "visit", node: u, note: "d=" + (bd === Infinity ? "∞" : bd.toFixed(0)) });
          adj[u].forEach(({ to, w, ei }) => {
            if (!done[to] && dist[u] + w < dist[to]) {
              dist[to] = dist[u] + w; par[to] = u;
              steps.push({ type: "edge", ei, note: "d→" + to + "=" + dist[to] });
            }
          });
        }
        let cur = goal;
        while (cur !== start && cur >= 0) {
          steps.push({ type: "path-node", node: cur });
          cur = par[cur];
        }
        steps.push({ type: "path-node", node: start });
      } else if (algo === "bfs" || algo === "dfs") {
        const stack = algo === "dfs";
        const seen = new Array(N).fill(false);
        const order = stack ? [[start]] : [start];
        seen[start] = true;
        const seq = [];
        if (stack) {
          (function dfs(u) {
            seen[u] = true; seq.push(u);
            adj[u].forEach(({ to }) => { if (!seen[to]) dfs(to); });
          })(start);
        } else {
          const q = [start];
          while (q.length) {
            const u = q.shift(); seq.push(u);
            adj[u].forEach(({ to }) => { if (!seen[to]) { seen[to] = true; q.push(to); } });
          }
        }
        seq.forEach((u, i) => steps.push({ type: "visit", node: u, note: "#" + (i + 1) }));
      } else {  // kruskal
        const parent = nodes.map((_, i) => i);
        const find = (x) => (parent[x] === x ? x : (parent[x] = find(parent[x])));
        const sorted = edges.slice().sort((a, b) => a.w - b.w);
        sorted.forEach((e) => {
          const ra = find(e.a), rb = find(e.b);
          if (ra !== rb) { parent[ra] = rb; steps.push({ type: "mst", ei: edges.indexOf(e), note: "w=" + e.w }); }
        });
      }
      // animasi
      let si = 0;
      const visNodes = new Set(), visEdges = new Set(), pathNodes = new Set(), mstE = new Set();
      const stepMs = 260;
      let running = true;
      function tick() {
        if (!running) return;
        if (si < steps.length) {
          const s2 = steps[si++];
          if (s2.type === "visit") visNodes.add(s2.node);
          if (s2.type === "edge") visEdges.add(s2.ei);
          if (s2.type === "path-node") pathNodes.add(s2.node);
          if (s2.type === "mst") mstE.add(s2.ei);
        }
        draw();
        setTimeout(tick, stepMs);
      }
      function draw() {
        const { ctx, w, h } = fitCanvas(cv);
        ctx.fillStyle = TC().bg;
        ctx.fillRect(0, 0, w, h);
        const PX = (n) => nodes[n].x * w, PY = (n) => nodes[n].y * h;
        edges.forEach((e, i) => {
          ctx.strokeStyle = mstE.has(i) ? TC().gold : (visEdges.has(i) ? "rgba(127,180,216.8)" : cEdge(i));
          ctx.lineWidth = mstE.has(i) ? 3.4 : 1.4;
          ctx.beginPath(); ctx.moveTo(PX(e.a), PY(e.a)); ctx.lineTo(PX(e.b), PY(e.b)); ctx.stroke();
          ctx.fillStyle = TC().muted;
          ctx.font = "10px sans-serif";
          ctx.fillText(e.w, (PX(e.a) + PX(e.b)) / 2 + 3, (PY(e.a) + PY(e.b)) / 2 - 3);
        });
        function cEdge() { return "rgba(141,127,97.35)"; }
        nodes.forEach((n, i) => {
          ctx.beginPath(); ctx.arc(PX(i), PY(i), 13, 0, 7);
          ctx.fillStyle = pathNodes.has(i) ? "#d87f7f" : visNodes.has(i) ? TC().gold : TC().bg2;
          ctx.fill();
          ctx.strokeStyle = TC().line; ctx.lineWidth = 1.5; ctx.stroke();
          ctx.fillStyle = TC().cream;
          ctx.font = "bold 11px sans-serif";
          ctx.textAlign = "center"; ctx.textBaseline = "middle";
          ctx.fillText(String.fromCharCode(65 + i), PX(i), PY(i) + 1);
          ctx.textAlign = "left"; ctx.textBaseline = "alphabetic";
        });
        ctx.fillStyle = TC().muted;
        ctx.font = "11px sans-serif";
        ctx.fillText((algo + ": " + Math.min(si, steps.length) + "/" + steps.length + " langkah (A=start, I=goal)").toUpperCase(), 8, 16);
      }
      draw();
      tick();
      registerDispose(() => { running = false; });
    },
  };

  /* ---------- gray: ray tracing lensa tipis ---------- */
  G.gray = {
    kind: "canvas",
    mount(cv, p) {
      const f1 = p.f1 || 150, f2 = p.f2 || -150, d12 = p.d12 || 320, nray = p.nray || 7;
      const view = makeView(cv, 0, 0, 1);
      view.ppu = 1;   // pakai pixel langsung
      view.sx = (x) => x + cv.clientWidth * 0.18;
      view.sy = (y) => cv.clientHeight / 2 - y;
      const L1x = cv.clientWidth * 0.22, L2x = L1x + d12;
      function draw() {
        const { ctx, w, h } = fitCanvas(cv);
        drawGrid(ctx, w, h, { ...view, ppu: 60, sx: (x) => x + w * 0.18, sy: (y) => h / 2 - y });
        const c = TC();
        const cy = h / 2;
        // lensa: dua panah vertikal
        [[L1x, f1], [L2x, f2]].forEach(([lx, f]) => {
          ctx.strokeStyle = f > 0 ? "#9fd89f" : "#d87f7f";
          ctx.lineWidth = 3;
          ctx.beginPath();
          ctx.moveTo(lx, cy - 90); ctx.lineTo(lx, cy + 90);
          ctx.stroke();
          [f, -f].forEach((ff) => {
            if (f > 0) {
              ctx.fillStyle = "rgba(224,176,74.9)";
              ctx.beginPath(); ctx.arc(lx + ff, cy, 3.4, 0, 7); ctx.fill();
            }
          });
        });
        ctx.strokeStyle = c.line;
        ctx.beginPath(); ctx.moveTo(0, cy); ctx.lineTo(w, cy); ctx.stroke();
        // sinar paralel
        ctx.lineWidth = 1.6;
        for (let i = 0; i < nray; i++) {
          const y0 = -110 + 220 * (i / (nray - 1 || 1));
          let x = 0, y = y0, ang = 0;   // sinar paralel sumbu
          ctx.strokeStyle = "rgba(242,227,148.85)";
          ctx.beginPath(); ctx.moveTo(view.sx(x), view.sy(y));
          // ke lensa 1
          ctx.lineTo(L1x, view.sy(y));
          if (f1 !== 0) ang = -y / f1; else ang = 0;
          // ke lensa 2
          const y1 = y + ang * (L2x - L1x);
          ctx.lineTo(L2x, view.sy(y1));
          let ang2 = ang;
          if (f2 !== 0) ang2 = ang - y1 / f2;
          // terus sampai tepi
          const xEnd = w;
          const yEnd = y1 + ang2 * (xEnd - L2x);
          ctx.lineTo(xEnd, view.sy(yEnd));
          ctx.stroke();
        }
        ctx.fillStyle = c.muted;
        ctx.font = "12px sans-serif";
        ctx.fillText("f₁ = " + f1 + "   f₂ = " + f2 + "   d = " + d12, 8, 18);
      }
      const rd = rafThrottle(draw);
      attachPanZoom(cv, { ...view, ppu: 1, sx: (x) => x, sy: (y) => y, wx: (x) => x, wy: (y) => y }, rd);
      draw();
      const ro = new ResizeObserver(rd);
      ro.observe(cv);
      registerDispose(() => ro.disconnect());
    },
  };

  /* ---------- gfluid: Stable Fluids (Jos Stam) ---------- */
  G.gfluid = {
    kind: "canvas",
    mount(cv, p) {
      const N = p.size || 128;
      const visc = p.visc == null ? 0.000001 : p.visc;
      const diff = p.diff == null ? 0.0000001 : p.diff;
      const size = (N + 2) * (N + 2);
      const IX = (i, j) => i + (N + 2) * j;
      const u = new Float32Array(size), v = new Float32Array(size),
        u0 = new Float32Array(size), v0 = new Float32Array(size),
        dens = new Float32Array(size), dens0 = new Float32Array(size);
      function addSource(x, s, dt) { for (let i = 0; i < size; i++) x[i] += dt * s[i]; }
      function setBnd(b, x) {
        for (let i = 1; i <= N; i++) {
          x[IX(0, i)] = b === 1 ? -x[IX(1, i)] : x[IX(1, i)];
          x[IX(N + 1, i)] = b === 1 ? -x[IX(N, i)] : x[IX(N, i)];
          x[IX(i, 0)] = b === 2 ? -x[IX(i, 1)] : x[IX(i, 1)];
          x[IX(i, N + 1)] = b === 2 ? -x[IX(i, N)] : x[IX(i, N)];
        }
        x[IX(0, 0)] = 0.5 * (x[IX(1, 0)] + x[IX(0, 1)]);
        x[IX(0, N + 1)] = 0.5 * (x[IX(1, N + 1)] + x[IX(0, N)]);
        x[IX(N + 1, 0)] = 0.5 * (x[IX(N, 0)] + x[IX(N + 1, 1)]);
        x[IX(N + 1, N + 1)] = 0.5 * (x[IX(N, N + 1)] + x[IX(N + 1, N)]);
      }
      function linSolve(b, x, x0, a, c2, iters) {
        for (let k = 0; k < iters; k++) {
          for (let i = 1; i <= N; i++)
            for (let j = 1; j <= N; j++)
              x[IX(i, j)] = (x0[IX(i, j)] + a * (x[IX(i - 1, j)] + x[IX(i + 1, j)] + x[IX(i, j - 1)] + x[IX(i, j + 1)])) / c2;
          setBnd(b, x);
        }
      }
      function diffuse(b, x, x0, dt) {
        const a = dt * diff * N * N;
        linSolve(b, x, x0, a, 1 + 4 * a, 6);
      }
      function advect(b, d, d0, u2, v2, dt) {
        const dt0 = dt * N;
        for (let i = 1; i <= N; i++) {
          for (let j = 1; j <= N; j++) {
            let x = i - dt0 * u2[IX(i, j)], y = j - dt0 * v2[IX(i, j)];
            x = Math.max(0.5, Math.min(N + 0.5, x));
            y = Math.max(0.5, Math.min(N + 0.5, y));
            const i0 = x | 0, i1 = i0 + 1, j0 = y | 0, j1 = j0 + 1;
            const s1 = x - i0, s2 = 1 - s1, t1 = y - j0, t2 = 1 - t1;
            d[IX(i, j)] = s2 * (t1 * d0[IX(i0, j1)] + t2 * d0[IX(i0, j0)])
              + s1 * (t1 * d0[IX(i1, j1)] + t2 * d0[IX(i1, j0)]);
          }
        }
        setBnd(b, d);
      }
      function project(uu, vv, pp, div) {
        for (let i = 1; i <= N; i++)
          for (let j = 1; j <= N; j++) {
            div[IX(i, j)] = -0.5 * (uu[IX(i + 1, j)] - uu[IX(i - 1, j)] + vv[IX(i, j + 1)] - vv[IX(i, j - 1)]) / N;
            pp[IX(i, j)] = 0;
          }
        setBnd(0, div); setBnd(0, pp);
        linSolve(0, pp, div, 1, 4, 14);
        for (let i = 1; i <= N; i++)
          for (let j = 1; j <= N; j++) {
            uu[IX(i, j)] -= 0.5 * N * (pp[IX(i + 1, j)] - pp[IX(i - 1, j)]);
            vv[IX(i, j)] -= 0.5 * N * (pp[IX(i, j + 1)] - pp[IX(i, j - 1)]);
          }
        setBnd(1, uu); setBnd(2, vv);
      }
      let mx = -1, my = -1, pmx = -1, pmy = -1;
      const dt = 0.016;
      let running = true;
      function stepFrame() {
        if (mx >= 0 && pmx >= 0) {
          const ci = 1 + (mx / cv.clientWidth * N) | 0;
          const cj = 1 + ((1 - my / cv.clientHeight) * N) | 0;
          if (ci >= 1 && ci <= N && cj >= 1 && cj <= N) {
            u[IX(ci, cj)] += (mx - pmx) * 12;
            v[IX(ci, cj)] += -(my - pmy) * 12;
            dens[IX(ci, cj)] = Math.min(4, dens[IX(ci, cj)] + 3);
          }
        }
        pmx = mx; pmy = my;
        addSource(u, u0.map((x) => 0), 0);
        // pakai source array util
        const sv = new Float32Array(size);
        // vorticity konfinemen ringan? skip, cukup basic
        diffuse(1, u0, u, dt); diffuse(2, v0, v, dt);
        project(u0, v0, u, v);
        advect(1, u, u0, u0, v0, dt); advect(2, v, v0, u0, v0, dt);
        project(u, v, u0, v0);
        diffuse(0, dens0, dens, dt); advect(0, dens, dens0, u, v, dt);
      }
      function draw() {
        const { ctx, w, h } = fitCanvas(cv);
        const img = ctx.createImageData(w, h);
        const d = img.data;
        for (let py = 0; py < h; py++) {
          for (let px = 0; px < w; px++) {
            const i = 1 + ((px / w * N) | 0), j = 1 + ((py / h * N) | 0);
            const val = Math.min(1, Math.max(0, dens[IX(i, j)]));
            const k = (py * w + px) * 4;
            const [r, g2, b2] = hsv(0.12 - 0.12 * val, 0.8, 0.08 + 0.92 * val);
            d[k] = r * 255; d[k + 1] = g2 * 255; d[k + 2] = b2 * 255; d[k + 3] = 255;
          }
        }
        ctx.putImageData(img, 0, 0);
      }
      const onFluidMove = (e) => {
        const r = cv.getBoundingClientRect();
        mx = e.clientX - r.left; my = e.clientY - r.top;
      };
      const onFluidLeave = () => { mx = pmx = -1; };
      const onFluidDown = (e) => {
        const r = cv.getBoundingClientRect();
        mx = pmx = e.clientX - r.left; my = pmy = e.clientY - r.top;
        const ci = 1 + (mx / cv.clientWidth * N) | 0;
        const cj = 1 + ((1 - my / cv.clientHeight) * N) | 0;
        for (let di = -2; di <= 2; di++) for (let dj = -2; dj <= 2; dj++) {
          const i = ci + di, j = cj + dj;
          if (i >= 1 && i <= N && j >= 1 && j <= N) dens[IX(i, j)] = Math.min(4, dens[IX(i, j)] + 2);
        }
      };
      cv.addEventListener("pointermove", onFluidMove);
      cv.addEventListener("pointerleave", onFluidLeave);
      cv.addEventListener("pointerdown", onFluidDown);
      let last = performance.now(), acc = 0;
      function loop(now) {
        if (!running) return;
        acc += now - last; last = now;
        if (acc > 16) { acc = 0; stepFrame(); draw(); }
        requestAnimationFrame(loop);
      }
      requestAnimationFrame(loop);
      registerDispose(() => { running = false; cv.removeEventListener("pointermove", onFluidMove); cv.removeEventListener("pointerleave", onFluidLeave); cv.removeEventListener("pointerdown", onFluidDown); });
    },
  };

  /* ================= ekspos ================= */
  window.GRAPH_ENGINES = G;
  window.__GRAPH_TEST = {
    tokenize, compileReal, compileComplex, cadd, cmul, cdiv, cpow, cabs, carg,
    hsv, makeView,
  };
})();
