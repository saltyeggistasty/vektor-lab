/* ================= WAR STORIES (MATEMATIKA + FISIKA) =================
   Dua menu kampanye dari satu mesin: kartu vertikal, latar blur
   mengikuti kartu ter-hover, ESC/ENTER ala konsol, dan header HUD
   (auto-hide ke atas di semua halaman).
   MURNI UI, tidak menyentuh mesin fisika/matematika sama sekali.  */
(function () {
  /* ---------- HUD: header slide-in saat cursor menjulur ke tepi atas,
     lalu AUTO-HIDE kalau idle 2.4 detik (mis. abis pencet tombol bar).
     LAYAR SUPER SEMPIT (zoom 400%+): bar hanya muncul saat halaman ada
     di PALING ATAS — hover ke daerah atas gak memicu, biar kartu gak
     ketutup. ---------- */
  let hudTimer = 0;
  const hudUltra = window.matchMedia("(max-width: 380px)");
  function hudUltraSync() {
    clearTimeout(hudTimer);
    document.body.classList.toggle("hud-show", window.scrollY <= 2);
  }
  document.addEventListener("mousemove", (e) => {
    if (hudUltra.matches) return;         // ultra: dikendalikan scroll, bukan mouse
    document.body.classList.toggle("hud-show", e.clientY < 64);
    clearTimeout(hudTimer);
    if (e.clientY < 64)
      hudTimer = setTimeout(() => document.body.classList.remove("hud-show"), 2400);
  });
  document.addEventListener("scroll", () => {
    if (hudUltra.matches) hudUltraSync();
  }, true);
  hudUltra.addEventListener("change", () => {
    clearTimeout(hudTimer);
    hudUltraSync();
  });
  hudUltraSync();

  function inTab(name) {
    const t = document.querySelector(".tab.active");
    return t && t.dataset.tab === name;
  }

  /* ---------- drag-scroll + wheel horizontal untuk grid kartu ----------
     Grid yang isinya banyak kartu (Math & Physics) bisa digeser dengan
     tahan-klik + geser mouse, dan scroll mouse: ke atas = geser kanan,
     ke bawah = geser kiri. Klik gak nempel kalau ternyata lagi nge-drag. */
  document.querySelectorAll(".wm-grid").forEach((grid) => {
    let down = false, startX = 0, startLeft = 0, moved = false;
    grid.addEventListener("mousedown", (e) => {
      down = true; moved = false;
      startX = e.pageX; startLeft = grid.scrollLeft;
    });
    window.addEventListener("mouseup", () => { down = false; });
    window.addEventListener("mousemove", (e) => {
      if (!down) return;
      const dx = e.pageX - startX;
      if (Math.abs(dx) > 5) moved = true;
      grid.scrollLeft = startLeft - dx;
    });
    grid.addEventListener("wheel", (e) => {
      /* mobile: grid wrap vertikal — scroll halaman harus jalan normal */
      if (window.matchMedia("(max-width: 900px)").matches) return;
      /* desktop: hijack cuma kalau grid benar-benar overflow horizontal */
      if (grid.scrollWidth <= grid.clientWidth) return;
      if (Math.abs(e.deltaY) > Math.abs(e.deltaX)) {
        e.preventDefault();
        grid.scrollLeft -= e.deltaY;      // scroll atas = geser kanan
      }
    }, { passive: false });
    grid.addEventListener("dragstart", (e) => e.preventDefault());
    grid.addEventListener("click", (e) => {
      if (moved) {                        // drag = bukan klik
        e.stopPropagation();
        e.preventDefault();
        moved = false;
      }
    }, true);
  });

  /* ---------- warp: transisi ala game (GSAP, card swipe saja) ----------
     OPTIMASI: pop-up landing (scale .9 -> 1 + fade fullscreen) DIMATIKAN,
     dua animasi bareng (swipe + zoom) memaksa re-raster seluruh panel di
     tiap frame sambil decode gambar = patah-patah. Sekarang cuma swipe
     keluar, panel baru muncul langsung. Transform murni = compositor GPU. */
  let warpBusy = false;
  function warpTo(swap) {
    if (warpBusy) return;               // klik ganda di tengah transisi diabaikan
    warpBusy = true;
    /* WAJIB: matikan engine grapher aktif — loop Ising/fluid/domain gak boleh
       jalan di background setelah panel pindah (bug bocor CPU/lag) */
    if (window.__GRAPH_STOP) { try { window.__GRAPH_STOP(); } catch (e) {} }
    /* panel aktif yang PALING ATAS (terakhir di DOM): saat calc/graph terbuka,
       #math masih .active di belakangnya, querySelector pertama salah pilih
       dan swipe keluar terjadi di panel tersembunyi = transisi kena "gak ada" */
    const olds = document.querySelectorAll(".panel-wrap.active");
    const old = olds.length ? olds[olds.length - 1] : null;
    const done = () => { warpBusy = false; };
    if (!window.gsap) { swap(); done(); return; }
    const tl = gsap.timeline({ onComplete: done });
    // fase 1, card lama DISWAP keluar: murni horizontal, tanpa fade
    // (panel sudah keluar layar di -112%, opacity fade cuma tambahan biaya)
    if (old) {
      tl.fromTo(old,
        { xPercent: 0 },
        { xPercent: -112, duration: .42, ease: "power2.in" }, 0);
      tl.set(old, { clearProps: "all" }, .44);
    }
    // fase 2, panel baru muncul di t=.44 + slide-in tipis dari kanan
    // (transform murni = compositor; memberi arah transisi tanpa lag)
    tl.call(swap, [], .44);
    tl.call(() => {
      const np = document.querySelector(".panel-wrap.active");
      if (np) gsap.fromTo(np,
        { x: 40, opacity: 0 },
        { x: 0, opacity: 1, duration: .3, ease: "power2.out", clearProps: "all" });
    }, [], .44);
    tl.add(() => {}, .5);               // sedikit buffer selesai
  }
  window.warpTo = warpTo;

  /* ---------- light swipe: versi RINGAN utk ganti tab bidang ----------
     Panel war menu itu berat (bg blur + 20 kartu) — traverse -112% penuh
     bikin stutter. Ini cukup: keluar tipis + fade, masuk dari kanan. */
  let lightBusy = false;
  window.lightSwipe = function (apply) {
    if (lightBusy) return;
    const olds = document.querySelectorAll(".panel-wrap.active");
    const old = olds.length ? olds[olds.length - 1] : null;
    if (!window.gsap || document.hidden) { apply(); return; }
    lightBusy = true;
    const tl = gsap.timeline({ onComplete: () => {
      lightBusy = false;
      if (old) gsap.set(old, { clearProps: "all" });
    } });
    if (old) tl.to(old, { x: -34, opacity: 0, duration: .18, ease: "power2.in" });
    tl.call(() => {
      apply();
      const np = document.querySelector(".panel-wrap.active");
      if (np) gsap.fromTo(np,
        { x: 34, opacity: 0 },
        { x: 0, opacity: 1, duration: .28, ease: "power2.out", clearProps: "all" });
    });
  };

  /* ---------- pabrik menu war ---------- */
  function makeMenu(menuId, bg0Id, bg1Id, onOpen) {
    const menu = $(menuId);
    if (!menu) return null;
    const bgs = [$(bg0Id), $(bg1Id)];
    let front = 0;

    function setBg(src, pos) {
      if (!src) return;                       // kartu CSS: pertahankan latar terakhir
      const nxt = bgs[1 - front];
      nxt.style.backgroundImage = 'url("' + src + '")';
      nxt.style.backgroundPosition = pos || "50% 40%";
      nxt.classList.add("on");
      bgs[front].classList.remove("on");
      front = 1 - front;
    }

    const first = menu.querySelector(".wtile[data-img]");
    if (first) setBg(first.dataset.img, first.dataset.pos);

    /* hover-intent: backdrop gak boleh ikut-ikutan tiap card disapu cepat
       (bikin pusing). Mouse harus "diam" di card ≥170ms baru backdrop
       berganti; pindah card sebelum itu = timer batal. Berlaku utk kartu
       payung & kartu alat. */
    let bgHoverTimer = null;
    menu.querySelectorAll(".wtile").forEach((t) => {
      t.addEventListener("mouseenter", () => {
        clearTimeout(bgHoverTimer);
        bgHoverTimer = setTimeout(() =>
          setBg(t.dataset.img || "", t.dataset.pos || "50% 40%"), 170);
      });
      t.addEventListener("mouseleave", () => clearTimeout(bgHoverTimer));
      t.addEventListener("click", () => {
        clearTimeout(bgHoverTimer);
        if (t.classList.contains("locked")) {
          t.classList.remove("shake");
          void t.offsetWidth;                 // restart animasi
          t.classList.add("shake");
          return;
        }
        onOpen(t);
      });
    });

    return {
      el: menu,
      isVisible: () => !menu.classList.contains("hidden"),
      show() {
        menu.classList.remove("hidden");
        /* grid scroll horizontal DIRESTORE browser saat reload — kartu
           pertama jadi terpotong kiri di tampilan awal. Reset saat menu
           tampil agar baris selalu mulai dr kartu pertama. */
        menu.querySelectorAll(".wm-grid").forEach((g) => { g.scrollLeft = 0; });
      },
      hide() { menu.classList.add("hidden"); },
    };
  }

  /* ---------- pre-warm decode gambar kartu ----------
     Reveal layer dari display:none memaksa browser mengantri DECODE ULANG
     semua img lapis itu di frame pertama (bitmap hasil decode elemen
     display:none dibuang oleh Chrome). Lapis payung = 8 kartu, gambarnya
     5-10x lebih besar pikselnya dr lapis alat => decode segalanya di satu
     frame = freeze ratusan ms s/d detik di CPU/GPU lemah, paling parah
     saat BALIK dari lapis alat ke payung. img.decode() mengantri decode
     di thread background JAUH SEBELUM layer di-reveal (bitmap panas =
     frame reveal tinggal paint), tanpa mengubah tampilan sedikit pun;
     kalau bitmap masih panas, biayanya ~0. */
  function prewarmImgs(root) {
    if (!root) return;
    root.querySelectorAll("img").forEach((im) => {
      try {
        const d = im.decode();
        if (d && d.catch) d.catch(() => {});
      } catch (e) {}
    });
  }

  /* ---------- transisi antar lapis DLM menu (payung <-> alat) ----------
     Kartu lama luncur keluar, kartu baru masuk dari arah berlawanan.
     Fallback instan bila GSAP belum siap / tab tak kelihatan (rAF beku). */
  let swapBusy = false;
  function layerSwap(hideEl, showEl, back) {
    if (swapBusy) return;
    if (!window.gsap || document.hidden) {
      hideEl.classList.add("hidden");
      showEl.classList.remove("hidden");
      return;
    }
    swapBusy = true;
    const dir = back ? 1 : -1;              // maju: keluar ke kiri; mundur: keluar ke kanan
    const tl = gsap.timeline({
      onComplete: () => {
        swapBusy = false;
        gsap.set(hideEl, { clearProps: "all" });
        gsap.set(showEl, { clearProps: "all" });
        /* kedua lapis di-warm setelah animasi aman: yang tampil biar tetap
           panas, yang tersembunyi biar reveal berikutnya gak decode ulang */
        prewarmImgs(hideEl);
        prewarmImgs(showEl);
      }
    });
    tl.to(hideEl, { xPercent: 10 * dir, opacity: 0, duration: .22, ease: "power2.in" });
    tl.add(() => {
      hideEl.classList.add("hidden");
      showEl.classList.remove("hidden");
      if (showEl.querySelectorAll) showEl.querySelectorAll(".wm-grid")
        .forEach((g) => { g.scrollLeft = 0; });
      gsap.set(showEl, { xPercent: -10 * dir, opacity: 0 });
    });
    tl.to(showEl, { xPercent: 0, opacity: 1, duration: .34, ease: "power3.out" });
  }

  /* ================= FIELD SELECT (pilih bidang studi) ================= */
  const fsSelSec = $("fieldSel");
  document.querySelectorAll(".fs-side").forEach((b) => {
    b.addEventListener("click", () => {
      const tab = document.querySelector('.tab[data-tab="' + b.dataset.tab + '"]');
      if (tab) { tab.click(); window.scrollTo(0, 0); }
    });
  });

  function showFieldSel() {
    document.querySelectorAll(".panel-wrap").forEach((p) =>
      p.classList.toggle("active", p.id === "fieldSel"));
    document.body.classList.add("warfs");
    document.body.classList.remove("hud-show");
    window.scrollTo(0, 0);              // mobile: overlay pilih bidang di paling atas
  }
  window.warFieldSel = { show: showFieldSel };

  /* ================= MATEMATIKA =================
     Multi-payung: tiap kartu payung punya lapis alat sendiri
     (.wm-grid-tools[data-umb="..."]). Kartu alat punya data-view
     (panel lama) atau data-tool (panel generik Nabla Lab). */
  const mathSec = $("math"), calcSec = $("calc"), graphSec = $("graph");
  const mathUmb = $("mathUmb");
  const mathGrps = [...document.querySelectorAll("#mathMenu .wm-grid-tools")];
  let mathGrp = null;                    // lapis alat yang lagi aktif
  const mathMenu0 = makeMenu("mathMenu", "wmmBg0", "wmmBg1", (t) => {
    if (t.dataset.umbrella) {
      const grp = mathGrps.find((g) => g.dataset.umb === t.dataset.umbrella);
      if (!grp) return;
      mathGrp = grp;
      /* kartu payung -> transisi DLM menu: lapis payung -> lapis alat */
      layerSwap(mathUmb, grp, false);
      const firstTool = grp.querySelector(".wtile[data-img]");
      if (firstTool) firstTool.dispatchEvent(new Event("mouseenter"));
    } else if (t.dataset.view) {
      warpTo(() => mathEnter(t.dataset.view));
    } else if (t.dataset.tool) {
      const card = t;
      warpTo(() => window.openTool && window.openTool(t.dataset.tool, card));
    }
  });

  function mathEnter(view) {
    document.body.classList.remove("warfs");          // view alat: layout normal
    $("tool").classList.remove("active");
    mathMenu0.hide();
    calcSec.classList.toggle("active", view === "calc");
    graphSec.classList.toggle("active", view === "graph");
    window.scrollTo(0, 0);
    if (view === "graph" && $("plot") && window.Plotly) Plotly.Plots.resize($("plot"));
  }

  function mathReset() {
    if (window.__GRAPH_STOP) { try { window.__GRAPH_STOP(); } catch (e) {} }
    calcSec.classList.remove("active");
    graphSec.classList.remove("active");
    mathUmb.classList.remove("hidden");
    mathGrps.forEach((g) => g.classList.add("hidden"));
    mathMenu0.show();
    document.body.classList.remove("hud-show");
  }

  /* balik dari tool LEVEL-1: langsung ke lapis alat payung asalnya.
       #tool WAJIB di-nonaktifkan, kalau tidak, dua panel muncul bersamaan
       (bug bocor: menu payung muncul di bawah lapis alat) */
  function backToMathTools() {
    warpTo(() => {
      calcSec.classList.remove("active");
      graphSec.classList.remove("active");
      $("tool").classList.remove("active");
      mathSec.classList.add("active");
      document.body.classList.add("warfs");
      mathMenu0.show();
      mathUmb.classList.add("hidden");
      mathGrps.forEach((g) => g.classList.add("hidden"));
      if (!mathGrp) mathGrp = mathGrps[0] || null;
      if (mathGrp) mathGrp.classList.remove("hidden");
      prewarmImgs(mathGrp);
      prewarmImgs(mathUmb);
      document.body.classList.remove("hud-show");
      const firstTool = mathGrp && mathGrp.querySelector(".wtile[data-img]");
      if (firstTool) firstTool.dispatchEvent(new Event("mouseenter"));
      window.scrollTo(0, 0);            // menu selalu mulai dr atas
    });
  }

  $("calcBack").addEventListener("click", () => {
    if (inTab("math")) backToMathTools();
  });
  $("graphBack").addEventListener("click", () => {
    if (inTab("math")) backToMathTools();
  });

  /* ================= FISIKA =================
     Sama seperti matematika: multi-payung + data-tool generik. */
  const physSec = $("physics");
  const physUmb = $("physUmb");
  const physGrps = [...document.querySelectorAll("#physMenu .wm-grid-tools")];
  let physGrp = null;                    // lapis alat yang lagi aktif
  const physMenu0 = makeMenu("physMenu", "wmBg0", "wmBg1", (t) => {
    if (t.dataset.umbrella) {
      const grp = physGrps.find((g) => g.dataset.umb === t.dataset.umbrella);
      if (!grp) return;
      physGrp = grp;
      /* kartu payung Elektrodinamika -> lapis pemilih alat */
      layerSwap(physUmb, grp, false);
      const firstTool = grp.querySelector(".wtile[data-img]");
      if (firstTool) firstTool.dispatchEvent(new Event("mouseenter"));
    } else if (t.dataset.tool) {
      const card = t;
      warpTo(() => window.openTool && window.openTool(t.dataset.tool, card));
    } else {
      warpTo(() => physEnter(t.dataset.cat));
    }
  });

  function physEnter(cat) {
    document.body.classList.remove("warfs");          // lab: header normal flow
    $("tool").classList.remove("active");
    physMenu0.hide();
    $("physLab").classList.remove("hidden");
    catTagSet = true;                                 // label disetel via warp
    if (cat) {
      /* nama kategori diambil dari TITLE tile yang sudah diterjemahkan,
         bukan data-cat mentah (masih bahasa sumber). Suffix "· Bidang
         Studi" dihapus (ref layout baru). */
      const tile = document.querySelector('#physMenu .wtile[data-cat="' + cat + '"] .wt-title');
      $("physCatTag").textContent = tile ? tile.textContent : cat;
    }
    window.scrollTo(0, 0);              // lab selalu mulai dr atas (hasil tabel panjang)
    if ($("ppplot") && window.Plotly) {
      Plotly.Plots.resize($("ppplot"));
      /* re-fit lagi setelah layout & animasi masuk settle — size Plotly
         bisa stale kalau user ganti zoom pas panel lagi hidden */
      requestAnimationFrame(() => requestAnimationFrame(() => {
        if (!$("physLab").classList.contains("hidden") && window.Plotly)
          Plotly.Plots.resize($("ppplot"));
      }));
    }
    if (window.physOnShow) window.physOnShow();
  }
  let catTagSet = false;

  /* bahasa berganti saat lab belum dibuka -> label kategori default ikut;
     kalau user pernah warp (catTagSet), label punya tile terakhir, biarkan */
  try {
    if (window.I18N) window.I18N.onChange(() => {
      if (catTagSet) return;
      const t0 = document.querySelector('#physMenu .wtile[data-cat="ELECTRODINAMIKA"] .wt-title');
      $("physCatTag").textContent = t0 ? t0.textContent : "Elektrodinamika";
    });
  } catch (e) {}

  function physReset() {
    if (window.__GRAPH_STOP) { try { window.__GRAPH_STOP(); } catch (e) {} }
    $("physLab").classList.add("hidden");
    physUmb.classList.remove("hidden");
    physGrps.forEach((g) => g.classList.add("hidden"));
    physMenu0.show();
    document.body.classList.remove("hud-show");
  }

  /* balik dari tool LEVEL-1: langsung ke lapis alat payung asalnya.
       #tool WAJIB di-nonaktifkan (bug bocor sama seperti sisi matematika) */
  function backToPhysTools() {
    warpTo(() => {
      $("physLab").classList.add("hidden");
      $("tool").classList.remove("active");
      physSec.classList.add("active");
      document.body.classList.add("warfs");
      physMenu0.show();
      physUmb.classList.add("hidden");
      physGrps.forEach((g) => g.classList.add("hidden"));
      if (!physGrp) physGrp = physGrps[0] || null;
      if (physGrp) physGrp.classList.remove("hidden");
      prewarmImgs(physGrp);
      prewarmImgs(physUmb);
      document.body.classList.remove("hud-show");
      const firstTool = physGrp && physGrp.querySelector(".wtile[data-img]");
      if (firstTool) firstTool.dispatchEvent(new Event("mouseenter"));
      window.scrollTo(0, 0);            // menu selalu mulai dr atas
    });
  }

  $("physBack").addEventListener("click", () => {
    if (inTab("physics")) backToPhysTools();
  });

  /* ---------- filter kategori fisika: Klasik / Moderen / Semua ----------
     Kartu payung fisika punya data-phycat; tombol .cat-btn menyaring
     tanpa mengganggu rantai ESC maupun lapis alat (payung-saja). */
  const physCatBtns = [...document.querySelectorAll("#physCatBar .cat-btn")];
  function applyPhysCat(filter) {
    physCatBtns.forEach((b) =>
      b.classList.toggle("active", b.dataset.phyfilter === filter));
    const showing = [], hiding = [];
    physUmb.querySelectorAll(".wtile").forEach((t) => {
      const tampil = filter === "all" || t.dataset.phycat === filter;
      (tampil ? showing : hiding).push(t);
    });
    if (window.gsap && !document.hidden) {
      /* swipe mini: card tersembunyi luncur keluar, card tampil masuk
         berjenjang, konsisten dengan transisi antar-card war menu */
      gsap.killTweensOf(physUmb.querySelectorAll(".wtile"));
      gsap.to(hiding, { opacity: 0, x: -26, duration: .16, ease: "power2.in",
        onComplete: () => {
          hiding.forEach((t) => t.classList.add("cat-off"));
          gsap.set(hiding, { clearProps: "all" });
          showing.forEach((t) => t.classList.remove("cat-off"));
          gsap.fromTo(showing, { opacity: 0, x: 30 },
            { opacity: 1, x: 0, duration: .32, ease: "power2.out", stagger: .045,
              clearProps: "all" });
        } });
    } else {
      physUmb.querySelectorAll(".wtile").forEach((t) => {
        t.classList.toggle("cat-off", !showing.includes(t));
      });
    }
    const firstVisible = showing[0] || null;
    if (firstVisible) firstVisible.dispatchEvent(new Event("mouseenter"));
  }
  physCatBtns.forEach((b) => {
    b.addEventListener("click", () => applyPhysCat(b.dataset.phyfilter));
  });

  /* ---------- mobile: toggle 1/2 kolom card (tampil hanya ≤900px) ---------- */
  function applyCols() {
    let two = false;
    try { two = localStorage.getItem("wmCols") === "2"; } catch (e) {}
    document.body.classList.toggle("mcols-2", two);
    const label = two ? "menu.cols_2" : "menu.cols_1";
    const fb = two ? "2 Kartu" : "1 Kartu";
    document.querySelectorAll(".wm-cols-btn").forEach((b) => {
      b.textContent = window.I18N ? I18N.t(label, fb) : fb;
    });
  }
  document.querySelectorAll(".wm-head").forEach((h) => {
    const b = document.createElement("button");
    b.type = "button";
    b.className = "wm-cols-btn";
    b.addEventListener("click", () => {
      let cur = "1";
      try { cur = localStorage.getItem("wmCols") || "1"; } catch (e) {}
      try { localStorage.setItem("wmCols", cur === "2" ? "1" : "2"); } catch (e) {}
      applyCols();
    });
    h.appendChild(b);
  });
  applyCols();
  if (window.I18N && I18N.onChange) I18N.onChange(() => applyCols());


  /* ---------- tombol mode tampilan: Mobile <-> Desktop ----------
     Menggantikan wm-tag di wm-foot. Label = mode tujuan (klik untuk
     pindah). Paksa mobile = kolom aplikasi menyempit ke tengah dengan
     bar hitam di kiri-kanan + kartu portrait penuh vertikal. Pilihan
     diingat di localStorage; viewport <= 900px tetap mobile native. */
  const WM_MODE_KEY = "wmViewMode";
  function wmModeApply() {
    const forced = (() => {
      try { return localStorage.getItem(WM_MODE_KEY) === "mobile"; }
      catch (e) { return false; }
    })();
    document.body.classList.toggle("wm-mobile", forced);
    const realMobile = window.matchMedia("(max-width: 900px)").matches;
    const inMobile = forced || realMobile;
    document.querySelectorAll(".wm-mode-btn").forEach((b) => {
      b.textContent = inMobile ? "Desktop" : "Mobile";
    });
  }
  document.querySelectorAll(".wm-mode-btn").forEach((b) => {
    b.addEventListener("click", () => {
      try {
        const on = localStorage.getItem(WM_MODE_KEY) === "mobile";
        if (on) localStorage.removeItem(WM_MODE_KEY);
        else localStorage.setItem(WM_MODE_KEY, "mobile");
      } catch (e) {}
      wmModeApply();
    });
  });
  window.addEventListener("resize", wmModeApply);
  wmModeApply();

  /* ---------- satu langkah mundur (rantai sama seperti ESC keyboard) ----------
     Tombol arrow ◀ di header menu memanggil ini juga, jadi klik = ESC. */
  function menuEscStep() {
    // rantai keluar: lab/alat -> lapis alat -> lapis payung -> pilih bidang
    if (inTab("physics") && physMenu0) {
      if (!physMenu0.isVisible()) {        // dari lab -> balik LAPIS ALAT (bukan loncat ke payung)
        backToPhysTools();
      } else if (physUmb.classList.contains("hidden")) {  // dari lapis alat -> balik lapis payung
        layerSwap(physGrp || physGrps[0], physUmb, true);
        const firstTile = physUmb.querySelector(".wtile[data-img]");
        if (firstTile) firstTile.dispatchEvent(new Event("mouseenter"));
      } else {                             // dari lapis payung -> layar pilih bidang
        window.lightSwipe(showFieldSel);   // light swipe (warp berat = fps drop)
      }
    } else if (inTab("math") && mathMenu0) {
      if (!mathMenu0.isVisible()) {        // dari kalkulator/grafik -> balik LAPIS ALAT
        backToMathTools();
      } else if (mathUmb.classList.contains("hidden")) {  // dari lapis alat -> balik lapis payung
        layerSwap(mathGrp || mathGrps[0], mathUmb, true);
        const firstTile = mathUmb.querySelector(".wtile[data-img]");
        if (firstTile) firstTile.dispatchEvent(new Event("mouseenter"));
      } else {                             // dari lapis payung -> layar pilih bidang
        window.lightSwipe(showFieldSel);
      }
    } else if (fsSelSec && !fsSelSec.classList.contains("active")) {
      window.lightSwipe(showFieldSel);
    }
  }

  /* tombol ◀ header menu war (math & fisika; layar bahasa tidak punya) */
  document.querySelectorAll(".wm-back").forEach((btn) => {
    btn.addEventListener("click", () => menuEscStep());
  });

  /* ================= keyboard konsol ================= */
  let hotTile = null;
  document.addEventListener("mouseover", (e) => {
    if (e.target && e.target.closest)
      hotTile = e.target.closest(".wtile, .fs-side") || null;
  });

  document.addEventListener("keydown", (e) => {
    const el = e.target instanceof Element ? e.target : null;
    const typing = el && el.closest("input, textarea, select, math-field");

    if (e.key === "Escape") {
      e.preventDefault();
      menuEscStep();
    } else if (e.key === "Enter" && !typing) {
      const tile = hotTile;
      if (tile && document.body.classList.contains("warfs"))
        tile.click();
    }
  });

  window.warMath = { resetMenu: mathReset };
  window.warPhys = { resetMenu: physReset };
  /* dipakai tools.js: tombol back & ESC dari panel tool generik */
  window.warNav = { toMathTools: backToMathTools, toPhysTools: backToPhysTools };

document.body.classList.toggle("warfs", inTab("math") || inTab("physics"));

/* warm awal: dua lapis payung di-decode di background saat halaman nganggur,
   biar reveal PERTAMA (fieldSel -> menu) juga bebas freeze decode */
setTimeout(() => { prewarmImgs(mathUmb); prewarmImgs(physUmb); }, 1500);
})();
