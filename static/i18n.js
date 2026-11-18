/* =================================================================
   I18N Nabla Workspace, pemilih bahasa + mesin terjemahan modular.
   - Konfigurasi bahasa = berkas JSON terpisah di folder /i18n:
     english.json, indonesia.json, melayu.json, russia.json,
     ukraina.json, irish.json, arab.json
   - Berkas bahasa CUMA menyimpan kalimat/teks; ubah kata lewat berkas
     itu saja, tanpa menyentuh kode.
   - Kunci yang hilang di suatu bahasa otomatis turun ke english.json,
     lalu ke teks asli di HTML. Sisten tidak kaku: tambah/kurangi kunci
     sesukanya, aplikasi tetap jalan.
   - Teks statis diambil tiga cara:
       1) data-i18n="grup.kunci" di elemen (paling eksplisit)
       2) peta selektor SELECTORS di bawah (HTML lama tak dirombak)
       3) dari JS: window.I18N.t("grup.kunci", "cadangan")
   - Layar pilih bahasa muncul SEBELUM loading screen; bendera dari
     /menu_screen/flags/*.jpg (Arab pakai bendera Palestina).
   ================================================================= */
(function () {
  "use strict";

  const LANGS = [
    { id: "english",   native: "English (UK)", flag: "/menu_screen/flags/united_kingdom.jpg", file: "english", bd: "/language_select_backdrop/BritanniaStatue.jpg" },
    { id: "indonesia", native: "Bahasa Indonesia", flag: "/menu_screen/flags/indonesia.jpg",  file: "indonesia", bd: "/language_select_backdrop/JavanHawkEagle.jpg", bdv: "/language_select_backdrop/indonesia_video.mp4" },
    { id: "melayu",    native: "Melayu",           flag: "/menu_screen/flags/malaysia.jpg",   file: "melayu", bd: "/language_select_backdrop/SarawakKuchingMalay.jpg" },
    { id: "russia",    native: "Русский",      flag: "/menu_screen/flags/russia.jpg",         file: "russia", bd: "/language_select_backdrop/FriendsForeverWide.jpg" },
    { id: "ukraina",   native: "Українська",   flag: "/menu_screen/flags/ukraine.jpg",        file: "ukraina", bd: "/language_select_backdrop/TheSunflowerUkraine.jpg" },
    { id: "irish",     native: "Irish English", flag: "/menu_screen/flags/ireland.jpg",       file: "irish", bd: "/language_select_backdrop/IrishHare.jpg" },
    { id: "arab",      native: "العربية",      flag: "/menu_screen/flags/palestine.jpg",      file: "arab", bd: "/language_select_backdrop/FlowerThrowerBanksyPalestine.png" },
  ];

  /* label di atas tombol dropdown layar bahasa, auto-cycle 7 bahasa
     walau user belum hover pilihan mana pun */
  const PICK_LABELS = {
    indonesia: "Pilih Bahasa",
    english: "Pick a Language",
    melayu: "Pilih Bahasa",
    russia: "Выберите язык",
    ukraina: "Виберіть мову",
    irish: "Pick a Language",
    arab: "اختر لغة",
  };
  const PICK_ORDER = ["indonesia", "english", "melayu", "russia", "ukraina", "irish", "arab"];

  /* manifesto anti-A.I di dark backdrop layar bahasa, diketik ulang
     berganti bahasa (typewriter) walau user belum hover apa pun */
  const MANIFESTO = {
    indonesia: "Semua gambar, video, dan karya seni di website ini 100% Buatan manusia. Bebas dari A.I",
    english: "All images, videos, and artworks on this website are 100% human-made. Free from A.I",
    melayu: "Semua imej, video, dan karya seni di laman web ini 100% buatan manusia. Bebas dari A.I",
    russia: "Все изображения, видео и произведения искусства на этом сайте на 100% созданы человеком. Без ИИ.",
    ukraina: "Усі зображення, відео та твори мистецтва на цьому сайті на 100% створені людиною. Без ШІ.",
    irish: "All images, videos, and artworks on this website are 100% human-made. Free from A.I",
    arab: "جميع الصور ومقاطع الفيديو والأعمال الفنية في هذا الموقع من إنشاء بشري بنسبة 100%. خالية من الذكاء الاصطناعي.",
  };

  /* baris kecil DI ATAS manifesto utama, tipe bersamaan (sinkron per-tick) */
  const MANI_SUB = {
    indonesia: "Kumpulan alat-alat berat untuk Matematika dan Fisika ada disini.",
    english: "A collection of heavy-duty tools for Mathematics and Physics, right here.",
    melayu: "Kumpulan alat-alat berat untuk Matematik dan Fizik ada di sini.",
    russia: "Набор мощных инструментов по математике и физике, прямо здесь.",
    ukraina: "Набір потужних інструментів з математики та фізики, просто тут.",
    irish: "A collection of heavy-duty tools for Maths and Physics, right here.",
    arab: "مجموعة الأدوات الثقيلة للرياضيات والفيزياء موجودة هنا.",
  };

  /* bahasa yang DIPAKAI buat teks berputar (manifesto & caption):
     melayu & irish di-skip karena kalimatnya identik dgn indonesia/english */
  const CYCLE_LANGS = ["indonesia", "english", "russia", "ukraina", "arab"];

  /* ---------- util ---------- */
  const $ = (id) => document.getElementById(id);
  function getByPath(obj, key) {
    return key.split(".").reduce((o, k) => (o == null ? undefined : o[k]), obj);
  }
  function deepMerge(base, over) {
    const out = Array.isArray(base) ? base.slice() : Object.assign({}, base);
    for (const k of Object.keys(over)) {
      const b = base ? base[k] : undefined, v = over[k];
      if (b && v && typeof b === "object" && typeof v === "object" &&
          !Array.isArray(b) && !Array.isArray(v)) out[k] = deepMerge(b, v);
      else out[k] = v;
    }
    return out;
  }
  function esc(s) {
    return String(s).replace(/[&<>"']/g, (c) => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"})[c]);
  }
  async function loadFile(file) {
    try {
      const r = await fetch("/i18n/" + encodeURIComponent(file) + ".json", { cache: "no-cache" });
      if (!r.ok) return null;
      return await r.json();
    } catch (e) { return null; }
  }

  /* ---------- state ---------- */
  let dict = {};
  let enBase = null;     // bahasa cadangan (english), null = belum dicoba
  let curId = null;
  const changeHandlers = [];
  let selToken = 0;      // anti-race: pilihan TERBARU yang menang, fetch lama dibuang

  const I18N = {
    LANGS,
    get lang() { return curId; },
    get ready() { return enBase !== null; },
    t(key, fallback) {
      const v = getByPath(dict, key);
      if (v !== undefined && v !== null && v !== "") return v;
      return fallback;
    },
    onChange(fn) { changeHandlers.push(fn); },
    async setLang(id) {
      const token = ++selToken;
      const meta = LANGS.find((l) => l.id === id) || LANGS[0];
      const data = await loadFile(meta.file);
      if (token !== selToken) return false;         // sudah ada pilihan lebih baru
      if (enBase === null) enBase = (await loadFile("english")) || {};
      if (token !== selToken) return false;         // cek ulang: fetch english bisa lama
      if (!data) return false;                      // berkas gagal -> teks asli tetap
      dict = deepMerge(enBase, data);
      curId = meta.id;
      try { document.documentElement.lang = (data.meta && data.meta.lang) || meta.id; } catch (e) {}
      try { localStorage.setItem("nablaLang", meta.id); } catch (e) {}
      translateAll();
      syncDynOptions();     // opsi yang dibangun JS (ppreset) ikut disegarkan
      applyMathLive();      // locale + kamus menu MathLive (insert LaTeX)
      changeHandlers.forEach((fn) => { try { fn(curId); } catch (e) {} });
      return true;
    },
    /* balik ke layar pemilih bahasa (dipanggil tombol 🌐 di bar atas) */
    openLangScreen() { if (I18N._reopen) try { I18N._reopen(); } catch (e) {} },
    /* batalkan layar bahasa (mode buka-ulang SAJA), dipanggil tab lain di
       bar atas biar user bisa langsung lanjut ke menu yang dia klik */
    cancelLangScreen() { if (I18N._cancel) try { I18N._cancel(); } catch (e) {} },
  };
  window.I18N = I18N;

  /* ---------- MathLive (menu insert LaTeX) ----------
     locale MathLive butuh kode standard ("ru"/"uk"/"ar"/"id"/"ms"),
     bukan id internal kami; kamus label menu menyusul dari grup
     mlmenu_l10n di berkas bahasa (kunci penuh ber-titik, literal) */
  const ML_CODE = {
    english: "en", indonesia: "id", melayu: "ms",
    russia: "ru", ukraina: "uk", irish: "en", arab: "ar",
  };
  function applyMathLive() {
    if (!window.MathfieldElement) return;
    const code = ML_CODE[curId] || "en";
    try { MathfieldElement.locale = code; } catch (e) {}
    try {
      const blk = dict.mlmenu_l10n;
      if (blk && typeof blk === "object") MathfieldElement.strings = { [code]: blk };
    } catch (e) {}
  }

  /* opsi #ppreset dibangun JS dari #colorPreset saat init (sebelum dict siap);
     begitu bahasa termuat, salin ulang teksnya biar ikut terjemahan */
  function syncDynOptions() {
    if ($("ppreset") && $("colorPreset") && $("ppreset").options.length) {
      [...$("colorPreset").options].forEach((o, i) => {
        if ($("ppreset").options[i]) $("ppreset").options[i].text = o.text;
      });
    }
  }

  /* ---------- peta selektor -> kunci ----------
     mode: undefined = ganti text-node pertama (anak input/select selamat)
           "all" = textContent utuh        | "html" = innerHTML utuh
           "ph"  = atribut placeholder     | "title" = atribut title (tooltip) */
  const SELECTORS = [
    // header
    ['header .tab[data-tab="math"]', "header.tabs_math", "all"],
    ['header .tab[data-tab="physics"]', "header.tabs_phys", "all"],
    ['#langTab', "header.lang", "all"],
    ['#donBtn', "donasi.tab", "all"],
    ["#donSel .d-title", "donasi.title"],
    ["#donSel .d-sub", "donasi.sub"],
    ["#donSel #donCopyTip", "donasi.copied"],
    ['#themeSw button[data-t="gold"]', "header.th_gold", "all"],
    ['#themeSw button[data-t="light"]', "header.th_light", "all"],
    ['#themeSw button[data-t="black"]', "header.th_black", "all"],
    // field select
    [".fsel-title .t1", "fsel.title_a", "all"],
    [".fsel-title span:not(.t1)", "fsel.title_b", "all"],
    [".fsel-sub", "fsel.sub", "all"],
    ['#fieldSel .fs-side[data-tab="math"] .fs-name', "fsel.math_name", "all"],
    ['#fieldSel .fs-side[data-tab="math"] .fs-sub', "fsel.math_sub", "all"],
    ['#fieldSel .fs-side[data-tab="physics"] .fs-name', "fsel.phys_name", "all"],
    ['#fieldSel .fs-side[data-tab="physics"] .fs-sub', "fsel.phys_sub", "all"],
    [".fs-cta", "fsel.cta", "all"],
    // war menu (teks .wm-series dihapus, tulisan "Perangkat ..." tidak dipakai lagi)
    ["#mathMenu .wm-hints", "menu.hint_math", "html"],
    ["#physMenu .wm-hints", "menu.hint_phys", "html"],
    ["#mathMenu .wm-tag", "menu.foot_math"],
    ["#physMenu .wm-tag", "menu.foot_phys"],
    ["#mathMenu .wtile.locked .wt-eyebrow", "menu.soon"],
    ["#physMenu .wtile.locked .wt-eyebrow", "menu.soon"],
    ["#mathMenu .wtile[data-umbrella=calculus] .wt-title", "mathmenu.title_umbrella"],
    ["#mathMenu .wtile[data-view=calc] .wt-title", "mathmenu.title_calc"],
    ["#mathMenu .wtile[data-view=graph] .wt-title", "mathmenu.title_graph"],
    ['#mathMenu .wtile[data-img="/menu_screen/wm/wm_algebra.png"] .wt-title', "mathmenu.title_lin"],
    ['#mathMenu .wtile[data-img="/menu_screen/wm/wm_ode.png"] .wt-title', "mathmenu.title_ode"],
    ["#physMenu .wtile[data-umbrella=electro] .wt-title", "physmenu.title_electro"],
    ["#physMenu .wtile[data-cat=ELECTRODINAMIKA] .wt-title", "physmenu.tool_montecarlo"],
    ["#physMenu .wtile[data-cat=TERMODINAMIKA] .wt-title", "physmenu.title_thermo"],
    ["#physMenu .wtile[data-cat=MEKANIKA\\ KUANTUM] .wt-title", "physmenu.title_qm"],
    // Nabla Lab: kartu alat & payung baru
    ["#mathMenu .wtile[data-tool=integral] .wt-title", "mathmenu.tool_integral"],
    ["#mathMenu .wtile[data-tool=matrix] .wt-title", "mathmenu.tool_matrix"],
    ["#mathMenu .wtile[data-tool=ode] .wt-title", "mathmenu.tool_ode"],
    ["#mathMenu .wtile[data-tool=stats] .wt-title", "mathmenu.tool_stats"],
    ["#mathMenu .wtile[data-umbrella=stats] .wt-title", "mathmenu.title_statsumb"],
    ["#physMenu .wtile[data-tool=es] .wt-title", "physmenu.tool_es"],
    ["#physMenu .wtile[data-tool=thermo] .wt-title", "physmenu.tool_thermo"],
    ["#physMenu .wtile[data-tool=qm] .wt-title", "physmenu.tool_qm"],
    ["#physMenu .wtile[data-tool=rel] .wt-title", "physmenu.tool_rel"],
    ["#physMenu .wtile[data-tool=proj] .wt-title", "physmenu.tool_proj"],
    ["#physMenu .wtile[data-tool=hydro] .wt-title", "physmenu.tool_hydro"],
    ["#physMenu .wtile[data-umbrella=relativity] .wt-title", "physmenu.title_relativity"],
    ["#physMenu .wtile[data-umbrella=newton] .wt-title", "physmenu.title_newton"],
    ["#physMenu .wtile[data-umbrella=hydro] .wt-title", "physmenu.title_hydro"],
    // Nabla Lab gelombang 2
    ["#mathMenu .wtile[data-tool=complex] .wt-title", "mathmenu.tool_complex"],
    ["#mathMenu .wtile[data-tool=taylor] .wt-title", "mathmenu.tool_taylor"],
    ["#mathMenu .wtile[data-tool=modmath] .wt-title", "mathmenu.tool_modmath"],
    ["#mathMenu .wtile[data-tool=entropy] .wt-title", "mathmenu.tool_entropy"],
    ["#mathMenu .wtile[data-tool=poly] .wt-title", "mathmenu.tool_poly"],
    ["#mathMenu .wtile[data-umbrella=complex] .wt-title", "mathmenu.title_complex"],
    ["#mathMenu .wtile[data-umbrella=real] .wt-title", "mathmenu.title_real"],
    ["#mathMenu .wtile[data-umbrella=discrete] .wt-title", "mathmenu.title_discrete"],
    ["#mathMenu .wtile[data-umbrella=info] .wt-title", "mathmenu.title_info"],
    ["#physMenu .wtile[data-tool=schwartz] .wt-title", "physmenu.tool_schwartz"],
    ["#physMenu .wtile[data-tool=optics] .wt-title", "physmenu.tool_optics"],
    ["#physMenu .wtile[data-tool=shm] .wt-title", "physmenu.tool_shm"],
    ["#physMenu .wtile[data-tool=heatexp] .wt-title", "physmenu.tool_heatexp"],
    ["#physMenu .wtile[data-tool=emind] .wt-title", "physmenu.tool_emind"],
    ["#physMenu .wtile[data-umbrella=gr] .wt-title", "physmenu.title_gr"],
    ["#physMenu .wtile[data-umbrella=wave] .wt-title", "physmenu.title_wave"],
    // payung yang selector lamanya berbasis data-img (sekarang img baru)
    ["#mathMenu .wtile[data-umbrella=algebra] .wt-title", "mathmenu.title_lin"],
    ["#mathMenu .wtile[data-umbrella=ode] .wt-title", "mathmenu.title_ode"],
    ["#physMenu .wtile[data-umbrella=thermo] .wt-title", "physmenu.title_thermo"],
    ["#physMenu .wtile[data-umbrella=qm] .wt-title", "physmenu.title_qm"],
    ["#physMenu .wtile[data-umbrella=astro] .wt-title", "physmenu.title_astro"],
    // simulasi advanced (simlab.py), 10 kartu
    ["#mathMenu .wtile[data-tool=smatrix] .wt-title", "sims.title_smatrix"],
    ["#mathMenu .wtile[data-tool=slorenz] .wt-title", "sims.title_slorenz"],
    ["#mathMenu .wtile[data-tool=swalk] .wt-title", "sims.title_swalk"],
    ["#mathMenu .wtile[data-tool=sfourier] .wt-title", "sims.title_sfourier"],
    ["#mathMenu .wtile[data-tool=slogistic] .wt-title", "sims.title_slogistic"],
    ["#physMenu .wtile[data-tool=sschrod] .wt-title", "sims.title_sschrod"],
    ["#physMenu .wtile[data-tool=sdblpend] .wt-title", "sims.title_sdblpend"],
    ["#physMenu .wtile[data-tool=sdrag] .wt-title", "sims.title_sdrag"],
    ["#physMenu .wtile[data-tool=skepler] .wt-title", "sims.title_skepler"],
    ["#physMenu .wtile[data-tool=sslit] .wt-title", "sims.title_sslit"],
    /* opsi select lab fisika Monte Carlo */
    ['#pcat option[value="plate"]', "physlab.hsurf_plate"],
    ['#pcat option[value="wave"]', "physlab.hsurf_wave"],
    ['#pcat option[value="point"]', "physlab.hsurf_point"],
    ['#pcat option[value="parab"]', "physlab.hsurf_parab"],
    ['#pcat option[value="hill"]', "physlab.hsurf_hill"],
    ['#pcat option[value="custom"]', "physlab.hsurf_custom"],
    ['#fmode option[value="uniform"]', "physlab.cdist_uniform"],
    ['#fmode option[value="point"]', "physlab.cdist_point"],
    ['#fmode option[value="custom"]', "physlab.cdist_custom"],
    ['#pdir option[value="zplus"]', "physlab.fdir_zplus"],
    ['#pdir option[value="zminus"]', "physlab.fdir_zminus"],
    ['#pdir option[value="xplus"]', "physlab.fdir_xplus"],
    ['#pdir option[value="xminus"]', "physlab.fdir_xminus"],
    ['#pdir option[value="yplus"]', "physlab.fdir_yplus"],
    ['#pdir option[value="yminus"]', "physlab.fdir_yminus"],
    ['#pdir option[value="custom"]', "physlab.fdir_custom"],
    ["#advDir > summary", "physlab.h_dir_custom"],
    /* advanced graphers (15 kartu) */
    ["#mathMenu .wtile[data-tool=gdomain] .wt-title", "graph.title_gdomain"],
    ["#mathMenu .wtile[data-tool=gfractal] .wt-title", "graph.title_gfractal"],
    ["#mathMenu .wtile[data-tool=gsurf3d] .wt-title", "graph.title_gsurf3d"],
    ["#mathMenu .wtile[data-tool=gfrenet] .wt-title", "graph.title_gfrenet"],
    ["#mathMenu .wtile[data-tool=gtrans3d] .wt-title", "graph.title_gtrans3d"],
    ["#mathMenu .wtile[data-tool=gslope] .wt-title", "graph.title_gslope"],
    ["#mathMenu .wtile[data-tool=gdist] .wt-title", "graph.title_gdist"],
    ["#mathMenu .wtile[data-tool=ggraphalgo] .wt-title", "graph.title_ggraphalgo"],
    ["#physMenu .wtile[data-tool=gfield] .wt-title", "graph.title_gfield"],
    ["#physMenu .wtile[data-tool=gpvcycle] .wt-title", "graph.title_gpvcycle"],
    ["#physMenu .wtile[data-tool=gising] .wt-title", "graph.title_gising"],
    ["#physMenu .wtile[data-tool=gminkowski] .wt-title", "graph.title_gminkowski"],
    ["#physMenu .wtile[data-tool=gfluid] .wt-title", "graph.title_gfluid"],
    ["#physMenu .wtile[data-tool=ggeodesic] .wt-title", "graph.title_ggeodesic"],
    ["#physMenu .wtile[data-tool=gray] .wt-title", "graph.title_gray"],
    /* sub-caption kartu sim = "tahun · scientist" (language-neutral, gak perlu
       SELECTORS, konsisten dgn kartu kalkulator "1665 · Newton") */
    // kalkulator
    ["#calcBack", "calc.back", "all"],
    ['#op option[value="gradient"]', "calc.op_gradient"],
    ['#op option[value="partial"]', "calc.op_partial"],
    ['#op option[value="laplacian"]', "calc.op_laplacian"],
    ['#op option[value="hessian"]', "calc.op_hessian"],
    ['#op option[value="directional"]', "calc.op_directional"],
    ['#op option[value="divergence"]', "calc.op_divergence"],
    ['#op option[value="curl"]', "calc.op_curl"],
    ['#op option[value="jacobian"]', "calc.op_jacobian"],
    ["#partialIn label:first-of-type", "calc.variables"],
    ["#partialIn label:last-of-type", "calc.order"],
    ["#dirIn label:first-of-type", "calc.dir_in"],
    ["#runCalc", "calc.run", "all"],
    // grafik
    ["#graphBack", "graph.back", "all"],
    ['#gtype option[value="surface"]', "graph.type_surface"],
    ['#gtype option[value="field"]', "graph.type_field"],
    ['#gtype option[value="curve"]', "graph.type_curve"],
    ["#g-surface .row:nth-of-type(1) label:first-of-type", "graph.xmin"],
    ["#g-surface .row:nth-of-type(1) label:last-of-type", "graph.xmax"],
    ["#g-surface .row:nth-of-type(2) label:first-of-type", "graph.ymin"],
    ["#g-surface .row:nth-of-type(2) label:last-of-type", "graph.ymax"],
    ["#g-field .row label:first-of-type", "graph.min"],
    ["#g-field .row label:last-of-type", "graph.max"],
    ["#g-field label:nth-of-type(4)", "graph.density"],
    ["#g-curve .row label:first-of-type", "graph.t_min"],
    ["#g-curve .row label:last-of-type", "graph.t_max"],
    ['#colorPreset option[value="gold"]', "graph.color_gold"],
    ['#colorPreset option[value="viridis"]', "graph.color_viridis"],
    ['#colorPreset option[value="plasma"]', "graph.color_plasma"],
    ['#colorPreset option[value="rainbow"]', "graph.color_rainbow"],
    ['#colorPreset option[value="neon"]', "graph.color_neon"],
    ['#colorPreset option[value="coolwarm"]', "graph.color_coolwarm"],
    ['#colorPreset option[value="desmos"]', "graph.color_desmos"],
    // lab fisika
    ["#physBack", "physlab.back", "all"],
    ['#pcat option[value="plate"]', "physlab.cat_plate"],
    ['#pcat option[value="wave"]', "physlab.cat_wave"],
    ['#pcat option[value="point"]', "physlab.cat_point"],
    ['#pcat option[value="parab"]', "physlab.cat_parab"],
    ['#pcat option[value="hill"]', "physlab.cat_hill"],
    ['#pcat option[value="custom"]', "physlab.cat_custom"],
    ['#fmode option[value="uniform"]', "physlab.ft_uniform"],
    ['#fmode option[value="point"]', "physlab.ft_point"],
    ['#fmode option[value="custom"]', "physlab.ft_custom"],
    ["#pdir option[value=zplus]", "physlab.d_zplus"],
    ["#pdir option[value=zminus]", "physlab.d_zminus"],
    ["#pdir option[value=xplus]", "physlab.d_xplus"],
    ["#pdir option[value=xminus]", "physlab.d_xminus"],
    ["#pdir option[value=yplus]", "physlab.d_yplus"],
    ["#pdir option[value=yminus]", "physlab.d_yminus"],
    ["#pdir option[value=custom]", "physlab.d_custom"],
    ["#advDir summary", "physlab.comp_dir"],
    ["#advCustom summary", "physlab.comp_field"],
    ["#runPhys", "physlab.run", "all"],
    ["#advAI > summary", "physlab.ai_head"],
    // ["#aiText", "physlab.ai_ph", "ph"],  // fitur AI dihapus, key tidak ada lagi
    ["#runAI", "physlab.ai_run", "all"],
    ["#pseed", "physlab.seed_ph", "ph"],
    // keypad, tooltip (title)
    ["#keypadToggle", "keypad.t_open", "title"],
    ["#closeKeypad", "keypad.t_close", "title"],
    ['.kbtn[data-cmd="power"]', "keypad.t_power", "title"],
    ['.kbtn[data-cmd="fraction"]', "keypad.t_div", "title"],
    ['.kbtn[data-cmd="sqrt"]', "keypad.t_sqrt", "title"],
    ['.kbtn[data-insert="*"]', "keypad.t_mul", "title"],
    ['.kbtn[data-cmd="abs"]', "keypad.t_abs", "title"],
    ['.kbtn[data-insert="-"]', "keypad.t_sub", "title"],
    ['.kbtn[data-cmd="deleteBackward"]', "keypad.t_back", "title"],
    ['.kbtn[data-cmd="moveToPreviousChar"]', "keypad.t_left", "title"],
    ['.kbtn[data-cmd="moveToNextChar"]', "keypad.t_right", "title"],
    ['.kbtn[data-cmd="clear"]', "keypad.t_clear", "title"],
    ['.kbtn[data-insert="+"]', "keypad.t_add", "title"],
    ['.kbtn[data-cmd="def_int"]', "keypad.t_defint", "title"],
    ['.kbtn[data-cmd="indef_int"]', "keypad.t_indefint", "title"],
    // keypad
    ["#keypadToggle span", "keypad.toggle"],
    ['.kp-tab[data-panel="main"]', "keypad.tab_main", "all"],
    ['.kp-tab[data-panel="functions"]', "keypad.tab_fn", "all"],
    [".active-field-indicator", "keypad.input_prefix"],
    ["#kpSubmit", "keypad.submit", "all"],
    ["#panel-functions .fn-group:nth-of-type(1) h4", "keypad.g_calc"],
    ["#panel-functions .fn-group:nth-of-type(2) h4", "keypad.g_trig"],
    ["#panel-functions .fn-group:nth-of-type(3) h4", "keypad.g_inv"],
    ["#panel-functions .fn-group:nth-of-type(4) h4", "keypad.g_sym"],
  ];

  function put(el, txt, mode) {
    if (mode === "html") { el.innerHTML = txt; return; }
    if (mode === "ph") { el.setAttribute("placeholder", txt); return; }
    if (mode === "title") { el.setAttribute("title", txt); return; }
    if (mode === "all" || el.childElementCount === 0) { el.textContent = txt; return; }
    for (const n of el.childNodes) {
      if (n.nodeType === 3 && n.textContent.trim()) { n.textContent = txt; return; }
    }
    el.textContent = txt;
  }

  function translateAll() {
    document.querySelectorAll("[data-i18n]").forEach((el) => {
      const key = el.getAttribute("data-i18n");
      const v = I18N.t(key);
      if (v === false) {
        // konvensi: nilai false di JSON = elemen DISEMBUNYIKAN untuk bahasa itu
        // (mis. teks EEITSS donasi cuma tampil di indonesia), bukan error,
        // bukan fallback ke english/HTML, memang dimatikan via berkas bahasa
        el.classList.add("hidden");
        return;
      }
      if (v !== undefined) {
        el.classList.remove("hidden");
        put(el, v, el.getAttribute("data-i18n-mode") || undefined);
      }
    });
    SELECTORS.forEach(([sel, key, mode]) => {
      const v = I18N.t(key);
      if (v === undefined) return;                  // kunci tidak ada -> teks asli utuh
      document.querySelectorAll(sel).forEach((el) => put(el, v, mode));
    });
    // hasil bentang dinamis (calc & fisika): penggaris HANYA saat masih kosong
    // (class "muted"), hasil perhitungan yang sudah tampil tak disentuh
    [["resultBody", "calc.result_empty", "Belum ada perhitungan."],
     ["physStatBody", "physlab.result_empty", "Belum ada simulasi."]].forEach(([id, key, fb]) => {
      const el = document.getElementById(id);
      if (el && el.classList.contains("muted")) el.textContent = I18N.t(key, fb) || fb;
    });
  }
  I18N.trace = translateAll;

  /* ---------- layar pilih bahasa (sebelum loading screen) ----------
     - backdrop per-bahasa dr folder language_select_backdrop, cross-fade
     - parallax mousemove + drift pelan saat idle (rAF, tanpa blur)
     - daftar 2 baris (5 + 2) dengan bendera kiri + nama bahasanya sendiri
     - teks fakta negara memutari 7 bahasa (id -> en -> ms -> ru -> uk -> ga -> ar) */
  let LS_FACTS = null;          // {negara: {bahasa: kalimat}} dr i18n/facts.json

  function buildLangScreen() {
    const list = $("langList");
    if (!list) return;
    const factEl = $("langFact");
    const sec0 = $("langSel");
    const bgs = [$("langBg0"), $("langBg1")].filter(Boolean);
    const vid = $("langVideo");   // video backdrop khusus Indonesia (zona kanan)
    /* hl = yang lagi di-preview (hover/panah); selIdx = bahasa TERPILIH.
       Dipisah biar backdrop/caption bisa balik ke terpilih saat dropdown
       ditutup. Boot = -1 (BELUM ada bahasa terpilih): layar gelap +
       manifesto typewriter, tombol nunjukin "No language selected".
       Bahasa tersimpan cuma dipakai kalau layar dibuka ulang dr bar atas */
    let front = 0, hl = -1, selIdx = -1, chosen = false;

    function setBg(src) {
      if (!bgs.length || !src) return;
      const nxt = bgs[1 - front];
      nxt.style.backgroundImage = 'url("' + src + '")';
      nxt.classList.add("on");
      bgs[front].classList.remove("on");
      front = 1 - front;
      maniHide();    // foto nongol -> manifesto mundur
    }
    function mark(i) {
      hl = i;
      list.querySelectorAll(".l2-item").forEach((c, k) =>
        c.classList.toggle("sel", k === i));
    }

    /* ---------- video backdrop khusus Indonesia (FULLSCREEN) ----------
       Pengganti foto statis Elang Jawa: pas item Bahasa Indonesia
       di-preview, video main FULLSCREEN di tengah layar, dan PANEL
       PEMILIH auto-NGUMPET setelah mouse diem sebentar (mode idle,
       ala control video player). Gerak mouse = panel balik lagi.
       Item bahasa lain = foto statis + caption seperti biasa. */
    const VID_IDLE_MS = 1200;   /* mouse diem selama ini = panel ngumpet */
    let vidIdleOn = false;                      /* lg mode video-preview? */
    let vidIdleTimer = null;                    /* timeout id / null */
    let vidAnchorX = null, vidAnchorY = null;   /* acuan gerak */
    let vidLastX = null, vidLastY = null;       /* posisi event terakhir */

    function vidIdleHide() {                    /* mouse diem -> ngumpet */
      vidIdleTimer = null;   /* VID IDLE ON TETAP TRUE: gerak = bangunin */
      /* acuan = posisi mouse terakhir: noise ±2-3px SETELAH ngumpet
         tetap ke-dulang (kalau null, event pertama kebaca Infinity =
         kebangun sendiri) */
      vidAnchorX = vidLastX; vidAnchorY = vidLastY;
      sec0.classList.add("vid-focus");
    }
    function vidIdleRestart() {                 /* (re)jadwalin ngumpet */
      vidIdleOn = true;
      if (vidIdleTimer) clearTimeout(vidIdleTimer);
      vidAnchorX = vidAnchorY = null;           /* acuan dihitung dr nol */
      vidIdleTimer = setTimeout(vidIdleHide, VID_IDLE_MS);
    }
    function vidIdleStop() {                    /* keluar dr mode video */
      vidIdleOn = false;
      if (vidIdleTimer) clearTimeout(vidIdleTimer);
      vidIdleTimer = null;
      vidAnchorX = vidAnchorY = null;
      sec0.classList.remove("vid-focus");
    }

    function langVideoOn() {
      if (!vid) return;
      vid.classList.add("on");
      fitVideoBox();   // ukuran box dihitung ulang tiap nongol
      if (vid.paused) {
        try { vid.currentTime = 0; } catch (e) {}   // hover = mulai dr awal
        vid.play().catch(() => {});   // muted + playsinline: autoplay aman
      }
    }
    function langVideoOff() {
      if (!vid || !vid.classList.contains("on")) return;
      vid.classList.remove("on");
      vid.pause();
      try { vid.currentTime = 0; } catch (e) {}
    }
    /* tab sempat ke-background -> browser bisa nge-pause video & bekuin
       transisi. Balik ke depan: kalau video masih .on (Indonesia masih
       di-preview) tapi ke-pause, mainkan lagi. */
    document.addEventListener("visibilitychange", () => {
      if (!document.hidden && vid && vid.classList.contains("on") && vid.paused)
        vid.play().catch(() => {});
    });

    /* ---------- auto-fit box video (ANTI KEPOTONG) ----------
       Ukuran box element video dihitung EKSPLISIT dr rasio frame asli
       (videoWidth x videoHeight) vs ukuran layar — GAK ngandelin
       object-fit sama sekali (di sebagian renderer object-fit kurang
       dipercaya). Box = persis rasio video & di-CENTER-kan -> frame
       SELALU kelihatan utuh di zoom/ukuran layar/fullscreen apa pun. */
    function fitVideoBox() {
      if (!vid || !vid.videoWidth || !vid.videoHeight) return;
      const zr = vid.parentElement.getBoundingClientRect();
      const s = Math.min(zr.width / vid.videoWidth, zr.height / vid.videoHeight);
      const w = vid.videoWidth * s, h = vid.videoHeight * s;
      vid.style.width = Math.round(w) + "px";
      vid.style.height = Math.round(h) + "px";
      vid.style.left = Math.round((zr.width - w) / 2) + "px";   /* tengah */
      vid.style.top = Math.round((zr.height - h) / 2) + "px";
    }
    if (vid) {
      vid.addEventListener("loadedmetadata", fitVideoBox);
      vid.addEventListener("resize", fitVideoBox);   // rasio frame berubah
    }
    window.addEventListener("resize", fitVideoBox);   // zoom/fullscreen ikut

    /* gerak mouse = panel balik + reset timer idle. Yang dihitung GERAK
       BENERAN: cursor menjauh >= 8px dr TITIK ACUAN (dipasang tiap kali
       panel bangun/ngumpet), atau lompat >= 8px dalam 1 event. Noise
       sensor mouse (±2-3px sekitar acuan) DULANGKAN — mouse yang mau
       diem tetep dianggap diem, panel gak k-bangun sendiri. Gak ada lock:
       timernya selalu jalan lagi, jadi panel SELALU bisa ngumpet lagi
       (gak ada dead-end) dan auto-balik tiap gerak. */
    document.addEventListener("mousemove", (e) => {
      const dL = vidLastX === null ? 0
        : Math.hypot(e.clientX - vidLastX, e.clientY - vidLastY);
      vidLastX = e.clientX; vidLastY = e.clientY;
      if (!vidIdleOn) return;                  /* gak lg mode video */
      const dA = vidAnchorX === null ? Infinity
        : Math.hypot(e.clientX - vidAnchorX, e.clientY - vidAnchorY);
      if (dA < 8 && dL < 8) return;            /* noise: dianggap diem */
      vidAnchorX = e.clientX; vidAnchorY = e.clientY;
      sec0.classList.remove("vid-focus");      /* panel balik */
      clearTimeout(vidIdleTimer);
      vidIdleTimer = setTimeout(vidIdleHide, VID_IDLE_MS);
    });

    /* preview bahasa i: satu pintu buat hover & tombol panah.
       Bahasa ber-video (bdv): matiin semua foto statis + play video +
       TANPA caption (caption Elang Jawa dihapus — ini video). Bahasa
       lain: foto + caption klasik seperti sebelumnya. */
    function previewLang(i) {
      const l = LANGS[i];
      mark(i);
      setPickLabel(l.id);              // label ikut bahasa yang di-preview
      clearInterval(pickTimer);        // cycle label jeda selagi preview
      if (l.bdv) {
        bgs.forEach((b) => b.classList.remove("on"));  // foto diganti video
        langVideoOn();
        maniHide();                    // statement typewriter mundur
        vidIdleRestart();              // panel auto-ngumpet pas mouse diem
        clearInterval(factTimer);      // caption Elang Jawa: gak dipakai
        /* PENTING: batalkan swap caption yang lg nunggu timeout (hover
           pindah bahasa cepat) — tanpa ini, setTimeout swap dr bahasa
           lain nembak & caption-nya NEMPEL di atas video (bug bocor) */
        factCountry = "__video";
        if (factEl) factEl.classList.add("out");
        return;
      }
      vidIdleStop();                   // bahasa lain: panel tampil normal
      langVideoOff();
      setBg(l.bd);
      /* restart SELALU (tanpa guard factCountry): pas balik dr dark intro
         factTimer ke-clear, kalau di-guard caption gak bakal nongol lagi */
      if (LS_FACTS) restartFactCycle(l.id);
    }
    let saved = null;
    try { saved = localStorage.getItem("nablaLang"); } catch (e) {}
    const savedIdx = LANGS.findIndex((l) => l.id === saved);

    /* ---------- parallax mousemove + drift pelan saat idle (rAF) ----------
       butuh #9: backdrop ikut balik mouse + senyap-senyap jalan sendiri;
       simpel & murah: langsung set transform tiap frame saat overlay aktif */
    let mx = 0, my = 0;
    sec0.addEventListener("mousemove", (e) => {
      mx = (e.clientX / innerWidth - 0.5) * 2;
      my = (e.clientY / innerHeight - 0.5) * 2;
    });
    requestAnimationFrame(function lsParallax(t) {
      if (sec0.classList.contains("active") && bgs.length) {
        const ox = mx * 14 + Math.sin(t / 6400) * 7;
        const oy = my * 9 + Math.cos(t / 8600) * 5;
        for (const b of bgs) {
          /* mode paksa mobile: #langSel dikunci ke kolom 620px + overflow
             hidden (style.css) — parallax/zoom di-skip biar backdrop fit
             kolom tanpa ke-zoom 15% (transform inline bakal ngalahin CSS) */
          if (document.body.classList.contains("wm-mobile")) {
            b.style.transform = "";
            continue;
          }
          b.style.transform = "scale(1.15) translate(" + ox.toFixed(1) + "px," + oy.toFixed(1) + "px)";
        }
      }
      requestAnimationFrame(lsParallax);
    });

    /* ---------- teks fakta negara (butuh #2 #3) ---------- */
    const FACT_ORDER = CYCLE_LANGS;          // melayu & irish di-skip (identik)
    let factIdx = 0, factCountry = "indonesia";
    let factTimer = null;
    function factText(country, langId) {
      const f = LS_FACTS && LS_FACTS[country];
      return (f && (f[langId] || f.english)) || "";
    }
    function showFact(country, langId, instant) {
      if (!factEl) return;
      factCountry = country;
      const swap = () => {
        if (factCountry !== country) return;   // hover sudah pindah lagi -> buang
        const txt = factText(country, langId);
        if (!txt) return;
        factEl.textContent = txt;
        factEl.dir = langId === "arab" ? "rtl" : "ltr";
        factEl.classList.remove("out");
      };
      if (instant) { swap(); return; }
      factEl.classList.add("out");             // fade out -> ganti isi -> fade in
      setTimeout(swap, 460);
    }
    /* putaran bahasa SELALU mulai dr Indonesia saat negara ganti (butuh #3) */
    function restartFactCycle(country) {
      clearInterval(factTimer);
      /* ATURAN PUSAT: bahasa ber-video (Indonesia) = TANPA caption.
         Di-skip TOTAL di sini (satu-satunya pintu penampil caption)
         biar gak ada jalur mana pun — hover, restore, reopen, atau
         facts.json yang ke-load belakangan — yang bisa bikin caption
         bocor nimpa video (bug bocor caption). */
      const meta = LANGS.find((x) => x.id === country);
      if (meta && meta.bdv) {
        if (factEl) factEl.classList.add("out");
        return;
      }
      factIdx = 0;
      showFact(country, FACT_ORDER[0]);
      factTimer = setInterval(() => {
        const sec = $("langSel");
        if (!sec) return clearInterval(factTimer);
        if (!sec.classList.contains("active") || chosen) return;  // istirahat hemat
        factIdx = (factIdx + 1) % FACT_ORDER.length;
        showFact(factCountry, FACT_ORDER[factIdx]);
      }, 5500);   // 5.5 detik per caption sebelum transisi
    }

    /* ---------- dropdown pemilih bahasa (revamp) ----------
       Tombol kiri + panel slide-down; pilihan gak nutupin backdrop lagi.
       Label di atas tombol auto-cycle 7 bahasa; hover item = ganti
       backdrop + caption + label ikut bahasa itu. */
    const dd = $("langDd"), ddBtn = $("langDdBtn");
    const pickEl = $("langPick");
    const ddFlag = $("langDdFlag"), ddName = $("langDdName");

    function updateBtn(l) {
      if (!ddFlag || !ddName) return;
      if (!l) {                              // boot: belum ada bahasa terpilih
        ddFlag.style.display = "none";
        ddName.textContent = "No language selected";
        return;
      }
      ddFlag.style.display = "";
      ddFlag.src = l.flag;
      ddName.textContent = l.native;
    }
    function closeDd() {
      if (!dd || !ddBtn) return;
      dd.classList.remove("open");
      ddBtn.classList.remove("open");
      ddBtn.setAttribute("aria-expanded", "false");
      sec0.classList.remove("dd-open");     // kolom manifesto balik normal
    }
    /* backdrop/caption/label balik sesuai state setelah dropdown ditutup
       atau mouse keluar dr widget: belum ada terpilih -> dark + manifesto;
       sudah ada terpilih -> foto + caption bahasa terpilih */
    function restorePreview() {
      vidIdleStop();                     // panel pemilih balik tampil
      if (selIdx < 0) {
        mark(-1);
        bgs.forEach((b) => b.classList.remove("on"));   // matikan semua foto
        langVideoOff();                      // video ikut dimatikan
        clearInterval(factTimer);
        /* PENTING: batalkan swap caption yang lg nunggu timeout —
           hover English -> mouse keluar widget SEBELUM 460ms -> swap-
           nya nembak belakangan & guard factCountry masih match =
           caption Britannia NONGOL DI DARK STATE & mentok (bug bocor) */
        factCountry = "__dark";
        if (factEl) factEl.textContent = "";            // caption dikosongkan
        maniResume();                        // jangan restart teks yang udah jalan
        restartPickCycle(CYCLE_LANGS[0]);
        return;
      }
      mark(selIdx);
      const sl = LANGS[selIdx];
      if (sl.bdv) {                          // terpilih = Indonesia -> video
        bgs.forEach((b) => b.classList.remove("on"));
        langVideoOn();
        maniHide();
        clearInterval(factTimer);
        factCountry = "__video";             // batalkan swap caption pending
        if (factEl) factEl.classList.add("out");
      } else {
        langVideoOff();
        setBg(sl.bd);
        if (LS_FACTS) restartFactCycle(sl.id);
      }
      restartPickCycle(CYCLE_LANGS[0]);
    }
    function toggleDd(force) {
      if (!dd || !ddBtn) return;
      const wasOpen = dd.classList.contains("open");
      const open = force !== undefined ? force : !wasOpen;
      dd.classList.toggle("open", open);
      ddBtn.classList.toggle("open", open);
      ddBtn.setAttribute("aria-expanded", String(open));
      sec0.classList.toggle("dd-open", open);   // manifesto menyesuaikan kolomnya
      if (wasOpen && !open) restorePreview();   // ditutup -> balik ke terpilih
    }
    if (ddBtn) ddBtn.addEventListener("click", () => toggleDd());
    /* klik di luar widget -> tutup dropdown + restore preview */
    document.addEventListener("click", (e) => {
      if (e.target && e.target.closest && e.target.closest(".l-widget")) return;
      if (dd && dd.classList.contains("open")) { closeDd(); restorePreview(); }
    });

    /* label "Pilih Bahasa": auto-cycle bahasa + fade halus */
    let pickIdx = 0;
    function setPickLabel(langId, instant) {
      if (!pickEl) return;
      const swap = () => {
        pickEl.textContent = PICK_LABELS[langId] || PICK_LABELS.english;
        pickEl.dir = langId === "arab" ? "rtl" : "ltr";
        pickEl.classList.remove("out");
      };
      if (instant) { swap(); return; }
      pickEl.classList.add("out");
      setTimeout(swap, 290);
    }
    function restartPickCycle(startId) {
      clearInterval(pickTimer);
      pickIdx = Math.max(0, CYCLE_LANGS.indexOf(startId || "indonesia"));
      setPickLabel(CYCLE_LANGS[pickIdx], true);
      pickTimer = setInterval(() => {
        const sec = $("langSel");
        if (!sec) return clearInterval(pickTimer);
        if (!sec.classList.contains("active") || chosen) return;  // istirahat hemat
        pickIdx = (pickIdx + 1) % CYCLE_LANGS.length;
        setPickLabel(CYCLE_LANGS[pickIdx]);
      }, 3000);
    }
    let pickTimer = null;

    /* ---------- manifesto anti-A.I: typewriter di dark backdrop ----------
       ketik per huruf -> jeda -> hapus -> lanjut bahasa berikutnya,
       muter terus walau user belum hover pilihan mana pun */
    const maniEl = $("langManifesto"), maniTxt = $("maniTxt");
    const maniSubEl = $("maniSub"), maniSubTxt = $("maniTxtSub");
    let maniTimer = null, maniActive = false;

    /* baris judul/preview DI ATAS manifesto: transisi fade out->in kayak label
       "Pilih Bahasa" (bukan typewriter), berganti bahasa BERSAMAAN dengan
       saat teks utama mulai siklus bahasa barunya. .out di WRAPPER, blink
       jalan di inner span, jadi fade gak pernah diperangkok animasi blink. */
    function setManiSub(langId, instant) {
      if (!maniSubEl) return;
      const swap = () => {
        if (maniSubTxt) {
          maniSubTxt.textContent = MANI_SUB[langId] || MANI_SUB.english;
          maniSubTxt.dir = langId === "arab" ? "rtl" : "ltr";
        }
        maniSubEl.classList.remove("out");
      };
      if (instant) { swap(); return; }
      maniSubEl.classList.add("out");
      setTimeout(swap, 290);
    }

    function maniShow() {                    // dark + statement mulai diketik
      sec0.classList.add("mani-dark");
      if (maniEl) maniEl.classList.remove("out");
      maniActive = true;
      startManiCycle(0);
    }
    function maniHide() {                    // bahasa di-preview -> statement mundur
      sec0.classList.remove("mani-dark");
      if (maniEl) maniEl.classList.add("out");
      clearInterval(maniTimer);
      maniActive = false;
    }
    /* dark tanpa nge-restart typewriter (bugfix: spam klik tombol bikin
       teks balik ke awal mulu). Ini buat balik ke dark DENGAN teks
       masih jalan; maniShow() dipakai kalau emang mau mulai fresh */
    function maniResume() {
      sec0.classList.add("mani-dark");
      if (maniEl) maniEl.classList.remove("out");
      if (!maniActive) { maniActive = true; startManiCycle(0); }
    }
    function startManiCycle(startIdx) {
      clearInterval(maniTimer);
      let li = startIdx;
      (function play() {
        const id = CYCLE_LANGS[li % CYCLE_LANGS.length];   // melayu & irish di-skip
        const text = MANIFESTO[id] || MANIFESTO.english;
        if (!maniTxt) return;
        /* baris judul ikut transisi ke bahasa yang SAMA dgn teks utama */
        setManiSub(id, li === 0 && !(maniSubTxt && maniSubTxt.textContent));
        maniTxt.dir = id === "arab" ? "rtl" : "ltr";
        let i = 0;
        maniTimer = setInterval(() => {
          const sec = $("langSel");
          if (!sec || !sec.classList.contains("active") || chosen) return;  // istirahat
          maniTxt.textContent = text.slice(0, ++i);
          if (i >= text.length) {
            clearInterval(maniTimer);
            maniTimer = setTimeout(() => {   // selesai ngetik: jeda baca 5.5s, lalu hapus
              let del = text.length;
              maniTimer = setInterval(() => {
                const sec2 = $("langSel");
                if (!sec2 || !sec2.classList.contains("active") || chosen) return;
                maniTxt.textContent = text.slice(0, --del);
                if (del <= 0) {
                  clearInterval(maniTimer);
                  li++;
                  setTimeout(play, 380);
                }
              }, 14);
            }, 5500);
          }
        }, 34);
      })();
    }

    /* ---------- daftar pilihan di dalam dropdown ---------- */
    LANGS.forEach((l, i) => {
      const b = document.createElement("button");
      b.className = "l2-item" + (i === selIdx ? " sel" : "");
      b.type = "button";
      b.innerHTML =
        '<img src="' + l.flag + '" alt="' + esc(l.native) + '" draggable="false">' +
        '<span class="l-name">' + esc(l.native) + "</span>";
      b.dataset.id = l.id;
      b.addEventListener("mouseenter", () => {
        if (chosen) return;
        previewLang(i);
      });
      b.addEventListener("click", () => { if (!chosen) choose(l); });
      list.appendChild(b);
    });
    /* mouse keluar dr widget -> kembali ke state terpilih (dark/manifesto
       kalau belum ada yang terpilih) + label lanjut putar sendiri */
    const widget = document.querySelector("#langSel .l-widget");
    if (widget) widget.addEventListener("mouseleave", () => {
      /* panel lg ngumpet (mode idle video): mouseleave-nya jangan
         dianggap keluar beneran — panelnya emang lg sengaja disembunyi */
      if (sec0.classList.contains("vid-focus")) return;
      if (!chosen) restorePreview();
    });
    hl = -1; selIdx = -1;                  // refresh = belum ada bahasa terpilih
    updateBtn(null);                       // tombol: "No language selected"
    maniShow();                            // dark backdrop + statement typewriter
    setPickLabel(CYCLE_LANGS[0], true);
    restartPickCycle(CYCLE_LANGS[0]);

    /* ---------- dark intro mulai ulang dr Indonesia (permintaan pemilik) ----------
       User pindah page/tab atau window ke-unfocus lalu balik? Teks utama
       ("Kumpulan alat-alat berat..." + manifesto anti-A.I) JANGAN lanjut
       di tengah kalimat bahasa lain — mulai ulang siklus dr awal
       (Indonesia), sekalian label "Pilih Bahasa" biar tetak sinkron.
       Guard maniActive: kalau lagi preview foto (hover bahasa), jangan
       di-yank; guard chosen: layar udah selesai gak perlu apa-apa. */
    function maniRestartFromID() {
      const sec = $("langSel");
      if (!sec || !sec.classList.contains("active") || chosen || !maniActive) return;
      startManiCycle(0);
      restartPickCycle(CYCLE_LANGS[0]);
    }
    document.addEventListener("visibilitychange", () => {
      if (!document.hidden) maniRestartFromID();     // balik ke tab ini
    });
    window.addEventListener("focus", maniRestartFromID);  // balik ke window ini

    /* fakta dimuat belakangan -> nyalakan putaran HANYA kalau udah ada
       bahasa terpilih (boot dark gak boleh nongolin caption) */
    loadFile("facts").then((d) => {
      LS_FACTS = d || null;
      if (LS_FACTS && selIdx >= 0) restartFactCycle(LANGS[selIdx].id);
    });

    document.addEventListener("keydown", (e) => {
      const sec = $("langSel");
      if (!sec || !sec.classList.contains("active") || chosen) return;
      if (e.key === "ArrowDown" || e.key === "ArrowRight" ||
          e.key === "ArrowUp" || e.key === "ArrowLeft") {
        // panah = jalan di daftar; dropdown ikut kebuka biar keliatan
        e.preventDefault();
        const d = (e.key === "ArrowDown" || e.key === "ArrowRight") ? 1 : -1;
        const ni = (hl + d + LANGS.length) % LANGS.length;
        previewLang(ni);                 // satu pintu dgn hover (foto/video)
        toggleDd(true);
      } else if (e.key === "Enter") {
        e.preventDefault();
        if (dd && dd.classList.contains("open")) choose(LANGS[hl]);
        else toggleDd(true);              // Enter pertama: buka dropdown dulu
      } else if (e.key === "Escape" && reopenMode) {
        if (dd && dd.classList.contains("open")) { closeDd(); restorePreview(); return; }  // ESC 1x: tutup dropdown dulu
        // layar bahasa dibuka ulang dari bar atas -> Escape boleh menutupnya
        chosen = true;
        reopenMode = false;
        document.body.classList.remove("ls-open");
        if (window.gsap) {
          gsap.to(sec, { opacity: 0, duration: .24, ease: "power2.in",
            onComplete: () => {
              gsap.set(sec, { clearProps: "opacity" });
              sec.classList.remove("active");
            } });
        } else {
          sec.classList.remove("active", "fade-out");
        }
      }
    });

    async function choose(l) {
      chosen = true;
      closeDd();
      vidIdleStop();                     // panel balik (layar mau ditutup)
      langVideoOff();    // layar mau ditutup: video backdrop berhenti
      selIdx = Math.max(0, LANGS.findIndex((x) => x.id === l.id));
      hl = selIdx;
      mark(selIdx);
      updateBtn(l);
      document.body.classList.remove("ls-open");
      const ok = await I18N.setLang(l.id);
      if (!ok) { chosen = false; return; }
      /* LOADER DULU sebelum overlay membuka: dulu fade-out dulu baru
         start() = fieldSel bocor kelihatan di sela fade (bug ronde 34).
         #loadScreen z-9999 di atas semuanya, jadi aman ditutup duluan. */
      if (!reopenMode && window.NablaLoader) window.NablaLoader.start();
      const sec = $("langSel");
      sec.classList.add("fade-out");
      setTimeout(() => {
        sec.classList.remove("active");
        if (reopenMode) {
          reopenMode = false;
          sec.classList.remove("fade-out");
        }
      }, 300);
    }
    I18N._choose = choose;

    /* buka ulang layar bahasa dari bar atas (tombol 🌐):
       - mode "reopen": memilih bahasa TIDAK memompa ulang loader,
         cukup terapkan bahasa lalu tutup overlay
       - transisi masuk: fade + panel glide dari bawah (GSAP), sebelumnya
         overlay langsung ngepot tanpa animasi sama sekali */
    let reopenMode = false;
    I18N._reopen = () => {
      const sec = $("langSel");
      if (!sec) return;
      reopenMode = true;
      vidIdleStop();                     // mode idle video direset
      chosen = false;                       // buka kunci interaksi (Enter/panah/klik)
      document.body.classList.add("ls-open");  // header tampil di atas overlay
      sec.classList.remove("fade-out");
      sec.classList.add("active");
      /* buka ulang dr bar atas: mulai dr bahasa yang LAGI dipakai
         (bukan default Indonesia, ini konteks user yang udah di dalam app) */
      const curId = I18N.lang || (savedIdx >= 0 ? LANGS[savedIdx].id : "english");
      selIdx = Math.max(0, LANGS.findIndex((x) => x.id === curId));
      hl = selIdx;
      mark(hl);
      const cur = LANGS[hl];
      if (cur.bdv) {                        // terpilih = Indonesia -> video
        bgs.forEach((b) => b.classList.remove("on"));
        langVideoOn();
        maniHide();
        clearInterval(factTimer);
        factCountry = "__video";             // batalkan swap caption pending
        if (factEl) factEl.classList.add("out");
      } else {
        langVideoOff();
        setBg(cur.bd);                      // mulai dari bahasa yang tersimpan
        if (LS_FACTS) restartFactCycle(cur.id);   // fakta ikut disegarkan
      }
      closeDd();                            // dropdown mulai tertutup
      updateBtn(cur);
      restartPickCycle(CYCLE_LANGS[0]);      // label cycle ikut nyala lagi
      if (window.gsap) {
        gsap.fromTo(sec, { opacity: 0 }, { opacity: 1, duration: .38, ease: "power2.out",
          onComplete: () => gsap.set(sec, { clearProps: "opacity" }) });
        const inner = sec.querySelector(".l-inner");
        if (inner) gsap.fromTo(inner, { y: 28, opacity: 0 },
          { y: 0, opacity: 1, duration: .52, ease: "power3.out", delay: .06,
            onComplete: () => gsap.set(inner, { clearProps: "all" }) });
      }
    };

    /* batalkan layar bahasa: HANYA mode buka-ulang, layar bahasa BOOT
       (sebelum loader) tidak boleh ikut ke-cancel. Tab lain di bar atas
       memanggil ini supaya overlay langsung mengalah */
    I18N._cancel = () => {
      const sec = $("langSel");
      if (!sec || !reopenMode) return;
      reopenMode = false;
      vidIdleStop();
      langVideoOff();    // overlay ditutup paksa: video backdrop berhenti
      document.body.classList.remove("ls-open");
      if (window.gsap) {
        gsap.to(sec, { opacity: 0, duration: .22, ease: "power2.in",
          onComplete: () => {
            gsap.set(sec, { clearProps: "opacity" });
            sec.classList.remove("active");
          } });
      } else {
        sec.classList.remove("active");
      }
    };
  }

  /* boot: layar bahasa tampil FRESH, semua teks statis (hint foot, dll)
     pakai fallback Indonesia biar konsisten sama backdrop/caption yang
     juga mulai dr Indonesia. Bahasa tersimpan (nablaLang) baru diterapkan
     saat user benar-benar memilih di layar ini, tanpa pre-load */
  buildLangScreen();
})();
