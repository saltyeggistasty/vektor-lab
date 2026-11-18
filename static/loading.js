/* ================= LOADING SCREEN Nabla Workspace =================
   Modular: gambar + teks dari /loading_screen/config.json
   (folder loading_screen/, lihat README.md di sana).

   Sistem GATED: loader TIDAK otomatis jalan saat halamna dibuka.
     1) boot() langsung menyiapkan config + slide + langkah pemanasan
        (grafik & fisika diwarna di belakang layar bahasa).
     2) Setelah user memilih bahasa (i18n.js), layar bahasa fade-out dan
        memanggil window.NablaLoader.start() -> timer + min_duration_ms
        mulai dihitung dari SAAT ITU, slide berjalan, lalu fade out.

   Label teks loader lewat i18n: window.I18N.t("loading.status_*") dgn
   cadangan nilai config.json (config.json JANGAN diubah di sini).
   ============================================================= */
(function () {
  "use strict";

  const $ = (id) => document.getElementById(id);
  const scr = $("loadScreen");
  if (!scr) return;

  const DEF = {
    min_duration_ms: 13000,
    max_wait_ms: 25000,
    slide_ms: 5500,
    fade_ms: 1400,
    rigged: false,
    shuffle: false,
    brand: "Nabla Workspace",
    status_initial: "Menyiapkan lab",
    status_panels: "Menyiapkan tampilan lab",
    status_graph: "Menghitung grafik 3D bawaan",
    status_physics: "Menyiapkan simulasi fisika Monte Carlo",
    status_tidy: "Merapikan tampilan",
    slides: [],
  };

  const el = {
    slides: $("lsSlides"), artist: $("lsArtist"),
    eq: $("lsEq"), bar: $("lsBar"), status: $("lsStatus"),
    credit: $("lsCredit"), brand: $("lsBrand"),
  };

  /* label via i18n (kunci: loading.*, slides.*) dgn cadangan config */
  const T = (key, fb) => {
    try {
      const v = window.I18N && window.I18N.t(key, fb);
      return (v === undefined || v === null) ? fb : v;
    } catch (e) { return fb; }
  };

  /* ---------- helper ---------- */
  const wait = (ms) => new Promise((r) => setTimeout(r, ms));
  function poll(fn, every) {
    return new Promise((resolve) => {
      const t0 = Date.now();
      (function step() {
        let ok = false;
        try { ok = fn(); } catch (e) {}
        if (ok) return resolve();
        if (Date.now() - t0 > 120000) return resolve(); // jangan menggantung selamanya
        setTimeout(step, every || 400);
      })();
    });
  }
  function esc(s) {
    return s.replace(/[&<>"']/g, (c) => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"})[c]);
  }
  /* render segmen \( ... \) manual - KaTeX dimuat defer tanpa auto-render */
  function renderInlineMath(node) {
    const txt = node.textContent || "";
    if (!window.katex || !txt.includes("\\(")) return;
    try {
      node.innerHTML = txt.split(/\\\(|\\\)/).map((chunk, i) =>
        i % 2 ? window.katex.renderToString(chunk, {throwOnError: false}) : esc(chunk)
      ).join("");
    } catch (e) {}
  }

  /* ---------- slide gambar ---------- */
  const layers = [];
  function buildSlides(slides, fadeMs) {
    const driftOn = !(window.PERF && window.PERF.drift === false);
    (slides || []).forEach((s, i) => {
      const d = document.createElement("div");
      d.className = "ls-slide " + (driftOn ? (i % 2 ? "drift-l" : "drift-r") : "");
      d.style.transition = "opacity " + (fadeMs || 1400) + "ms ease";
      if ((s.fit || "cover") === "contain") d.classList.add("fit-contain");
      const img = document.createElement("img");
      img.src = "/loading_screen/" + encodeURIComponent(s.file || "");
      img.alt = "";
      img.decoding = "async";
      if (s.pos) img.style.objectPosition = s.pos;
      if (s.drift_ms) img.style.animationDuration = s.drift_ms + "ms";
      d.appendChild(img);
      el.slides.appendChild(d);
      layers.push({d, s: s || {}, img});
    });
  }
  function preload(l) {
    return new Promise((resolve) => {
      if (l.ready) return resolve(true);
      const done = (ok) => { l.ready = ok === true; resolve(l.ready); };
      if (l.img.complete) return done(l.img.naturalWidth > 0);
      l.img.onload = () => done(true);
      l.img.onerror = () => done(false);
      setTimeout(() => done(l.img.naturalWidth > 0), 9000);
    });
  }
  function showSlide(i) {
    const l = layers[i];
    if (!l) return;
    layers.forEach((x, k) => x.d.classList.toggle("on", k === i));
    cur = i;
    // judul/sub slide DIHAPUS (ref layout), slotnya diganti kredit artist
    if (l.s.equation && window.katex) {
      try { window.katex.render(l.s.equation, el.eq); }
      catch (e) { el.eq.textContent = l.s.equation; }
    } else {
      el.eq.textContent = l.s.equation || "";
      renderInlineMath(el.eq);
    }
    /* kredit artist dr loading_screen/artist.json, di bawah brand */
    const art = ART_BY_FILE[l.s.file] || "";
    el.artist.textContent = art ? "Artist: " + art : "";
    el.credit.textContent = "";   // kredit pojok dihapus (ref layout)
  }
  let cur = 0, timer = null;
  function startSlides(slideMs) {
    if (layers.length < 2) return; // satu gambar? biarkan diam aja
    // preload SEMUA slide paralel sejak awal, biar pindah slide tepat waktu
    const ensured = layers.map((l) => preload(l));
    const next = () => {
      const target = (cur + 1) % layers.length;
      ensured[target].then(() => { showSlide(target); timer = setTimeout(next, slideMs); });
    };
    timer = setTimeout(next, slideMs);
  }

  /* ---------- pemanasan (pre-compute di belakang layar) ---------- */

  /* openPanels: hidupkan panel-tools selagi loader menyelimuti viewport.
     Plotly yang digambar saat panel display:none berukuran 0 x 0 ->
     saat panel dibuka dia HARUS redraw penuh = stutter jelas di laptop
     kentang. Dengan panel terbuka (di balik layar) semua canvas dirender
     di ukuran NYATA, jadi first-open mulus. */
  const TOOL_PANELS = ["calc", "graph", "physics"];
  let warmWarfs = false;

  function openPanels() {
    warmWarfs = document.body.classList.contains("warfs");
    // ukur panel dgn layout SEPERTI saat user nanti membukanya (tanpa warfs),
    // supaya dimensi saat loader == dimensi saat dibuka -> tidak ada resize
    if (warmWarfs) document.body.classList.remove("warfs");
    const lab = $("physLab");
    if (lab) lab.classList.remove("hidden");
    TOOL_PANELS.forEach((id) => {
      const p = $(id);
      if (p) p.classList.add("active");
    });
  }

  function closePanels() {
    TOOL_PANELS.forEach((id) => {
      const p = $(id);
      if (p) p.classList.remove("active");
    });
    const lab = $("physLab");
    if (lab) lab.classList.add("hidden");
    // kembalikan state boot: field select penuh layar (bilah bahasa udah tak aktif)
    document.querySelectorAll(".panel-wrap").forEach((p) =>
      p.classList.toggle("active", p.id === "fieldSel"));
    document.body.classList.toggle("warfs", warmWarfs);
  }

  async function warmGraph() {
    await poll(() => document.getElementById("runGraph"), 150);
    const b = document.getElementById("runGraph");
    if (!b) return;
    const already = () => !!document.querySelector("#plot .main-svg");
    if (!already()) b.click(); // hitung persis seperti tombol Gambar
    await poll(() => {
      const msg = document.getElementById("graphMsg");
      return already() || (msg && msg.classList.contains("err"));
    }, 300);
  }

  async function warmPhysics() {
    await poll(() => {
      const body = document.getElementById("physStatBody");
      return !!body && !!body.querySelector(".pstat, .pstat-k");
    }, 300);
  }

  /* ---------- state global loader ---------- */
  let CFG = DEF;
  let ART_BY_FILE = {};                  // dr loading_screen/artist.json (per file)
  let steps = [];
  let started = false;
  let t0 = null;
  let tick = null;

  /* ---------- inti boot: siapkan semuanya, TAPI belum tayangkan loader ---------- */
  (async function boot() {
    let cfg = DEF;
    try {
      const r = await fetch("/loading_screen/config.json", {cache: "no-cache"});
      if (r.ok) cfg = {...DEF, ...(await r.json())};
    } catch (e) {}
    CFG = cfg;
    /* kredit artist: JSON terpisah biar user isi sendiri (Artist: "nama") */
    try {
      const ra = await fetch("/loading_screen/artist.json", {cache: "no-cache"});
      if (ra.ok) {
        const aj = await ra.json();
        ART_BY_FILE = (aj && typeof aj === "object") ? aj : {};
      }
    } catch (e) {}
    el.brand.textContent = cfg.brand || DEF.brand;
    el.status.textContent = T("loading.status_initial", cfg.status_initial || DEF.status_initial) + "...";

    buildSlides(cfg.slides, cfg.fade_ms);
    if (cfg.shuffle && layers.length > 1) layers.sort(() => Math.random() - 0.5);
    if (layers.length) {
      await preload(layers[0]); // decode slide pertama dulu biar tak blank
    }
    // KaTeX defer: begitu siap, render ulang caption slide saat ini
    poll(() => !!window.katex, 250).then(() => { if (layers.length) showSlide(cur); });

    steps = [
      // 1) buka panel-tools di balik layar (agar render berukuran nyata)
      {key: "loading.status_panels", fb: cfg.status_panels || DEF.status_panels, done: false,
        run: async () => { openPanels(); await wait(260); }},
      // 2) grafik 3D: gambar saat panel MEMANG terbuka (ukuran nyata)
      {key: "loading.status_graph", fb: cfg.status_graph || DEF.status_graph, done: false, run: warmGraph},
      // 3) fisika: tunggu Monte Carlo auto-run + refit plot di ukuran nyata
      {key: "loading.status_physics", fb: cfg.status_physics || DEF.status_physics, done: false,
        run: async () => {
          await warmPhysics();
          try { if (window.physOnShow) window.physOnShow(); } catch (e) {}
        }},
      // 4) rapikan: kembalikan state awal (field select, lab tersembunyi)
      {key: "loading.status_tidy", fb: cfg.status_tidy || DEF.status_tidy, done: false,
        run: async () => { await wait(200); closePanels(); }},
    ];
    // SEQUENTIAL: hindari dua render berat berebut CPU/GPU sekaligus
    (async () => {
      for (const s of steps) {
        el.status.textContent = T(s.key, s.fb) + "...";
        try { await s.run(); } catch (e) {}
        s.done = true;
      }
    })();

    // bahasa berganti -> segarkan slide saat ini (judul/sub) & status berikutnya
    try {
      if (window.I18N) window.I18N.onChange(() => {
        if (started && layers.length) showSlide(cur);
      });
    } catch (e) {}

    // bayu: start-nya dibuka sistem pilih bahasa (i18n.js)
    window.NablaLoader = { start };
  })();

  /* ---------- start: dipanggil setelah user memilih bahasa ---------- */
  function start() {
    if (started) return;
    started = true;
    t0 = performance.now();

    scr.classList.remove("hidden"); // loader tayang
    if (layers.length) {
      showSlide(0);
      startSlides(CFG.slide_ms || DEF.slide_ms);
    }

    tick = setInterval(() => {
      const pending = steps.filter((s) => !s.done);
      el.status.textContent = pending.length
        ? (T(pending[0].key, pending[0].fb) + "...")
        : T("loading.ready", "Hampir siap...");
      // bar cukup crawl halus mengikuti durasi config
      const minMs = Math.max(CFG.min_duration_ms || DEF.min_duration_ms, 1);
      const ms = performance.now() - t0;
      el.bar.style.width = Math.min(96, 97 * Math.min(ms / minMs, 1)) + "%";
    }, 180);

    finish();
  }

  async function finish() {
    // - rigged (mode presentasi): TEPAT di min_duration_ms, hitungan asli diabaikan
    // - normal: semua tugas beres + waktu minimum terlampaui (atau batas keras)
    if (CFG.rigged) {
      const exactMs = Math.max(CFG.min_duration_ms || DEF.min_duration_ms, 1000);
      await poll(() => performance.now() - t0 >= exactMs, 200);
    } else {
      await poll(() => {
        const ms = performance.now() - t0;
        const allDone = steps.every((s) => s.done);
        return (allDone && ms >= (CFG.min_duration_ms || DEF.min_duration_ms)) ||
               ms >= (CFG.max_wait_ms || DEF.max_wait_ms);
      }, 200);
    }

    // jangan fade sebelum pemanasan tampilan beres (tapi kasih batas keras,
    // jangan pernah menggantung user kalau langkah pemanasan macet)
    await Promise.race([
      poll(() => steps.every((s) => s.done), 250),
      wait(14000),
    ]);

    clearInterval(tick);
    if (timer) clearTimeout(timer);
    el.bar.style.width = "100%";
    el.status.textContent = T("loading.done", "Siap.");
    await wait(450);
    scr.classList.add("done");
    await wait(800);
    scr.remove();
    if (window.physOnShow) window.physOnShow(); // refit plot fisika
    try { window.Plotly && Plotly.Plots.resize("plot"); } catch (e) {} // refit grafik 3D
  }
})();
