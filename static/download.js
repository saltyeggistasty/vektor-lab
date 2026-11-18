/* =================================================================
   DOWNLOAD VERSI OFFLINE — panel fullscreen bertema (pola #donSel).
   Info file (ukuran, sha256) dari /download/info; tombol Unduh
   nonaktif + pesan bila build belum tersedia. MURNI UI, tidak
   menyentuh mesin tools sama sekali.
   ================================================================= */
(function () {
  "use strict";

  const sec = document.getElementById("dlSel");
  if (!sec || typeof $ !== "function") return;
  const gsapAvailable = () => typeof window.gsap === "function";

  /* di dalam exe offline, tombol unduh versi offline tidak ada gunanya —
     sembunyikan (appinfo.frozen). Versi web: tetap tampil. */
  (async () => {
    try {
      const r = await fetch("/api/appinfo");
      const j = await r.json();
      if (j && j.ok && j.data && j.data.frozen) {
        const b = document.getElementById("dlBtn");
        if (b) b.classList.add("hidden");
      }
    } catch (e) { /* versi web: biarkan */ }
  })();

  function open() {
    sec.classList.add("active");
    document.body.classList.add("dl-open");
    refreshInfo();
    if (gsapAvailable()) {
      gsap.fromTo(sec, { opacity: 0 }, { opacity: 1, duration: .32, ease: "power2.out" });
      const inner = sec.querySelector(".dl-inner");
      if (inner) gsap.fromTo(inner, { y: 26, opacity: 0 },
        { y: 0, opacity: 1, duration: .45, ease: "power3.out" });
    }
  }

  function close() {
    if (gsapAvailable()) {
      gsap.to(sec, { opacity: 0, duration: .24, ease: "power2.in", onComplete: () => {
        sec.classList.remove("active");
        gsap.set(sec, { clearProps: "all" });
      } });
    } else {
      sec.classList.remove("active");
    }
    document.body.classList.remove("dl-open");
  }

  /* ---------- info file dari server ----------
     Gagal sekali (mis. server lagi restart) JANGAN langsung nampilin
     teks merah — retry sekali dulu; cuma gagal 2x baru disebut unavailable.
     Panel dibuka lagi / bahasa berganti = info di-refresh (self-heal). */
  async function refreshInfo() {
    const go = document.getElementById("dlGo");
    const meta = document.getElementById("dlMeta");
    const warn = document.getElementById("dlWarn");
    try {
      let j = null;
      for (let attempt = 0; attempt < 2; attempt++) {
        try {
          const r = await fetch("/download/info");
          j = await r.json();
          if (j && j.ok && j.data) break;
          j = null;
        } catch (e) { j = null; }
        if (attempt === 0) await new Promise(r => setTimeout(r, 900));
      }
      if (!j || !j.data) throw new Error("none");
      if (meta) meta.textContent =
        (j.data.size / (1024 * 1024)).toFixed(0) + " MB · SHA-256 " + j.data.sha256.slice(0, 12) + "…";
      if (go) { go.classList.remove("disabled"); go.removeAttribute("aria-disabled"); }
      if (warn) warn.classList.add("hidden");
    } catch (e) {
      if (meta) meta.textContent = "";
      if (go) { go.classList.add("disabled"); go.setAttribute("aria-disabled", "true"); }
      if (warn) warn.classList.remove("hidden");
    }
  }
  if (window.I18N && I18N.onChange) I18N.onChange(() => {
    if (sec.classList.contains("active")) refreshInfo();
  });

  const go = document.getElementById("dlGo");
  if (go) go.addEventListener("click", (e) => {
    if (go.classList.contains("disabled")) { e.preventDefault(); return; }
    go.classList.add("busy");
    setTimeout(() => go.classList.remove("busy"), 4000);
  });

  /* ESC: kalau layar bahasa lagi kebuka di atas panel ini, tutup layar
     bahasanya dulu; kalau tidak, tutup panel download. */
  document.addEventListener("keydown", (e) => {
    if (e.key !== "Escape" || !sec.classList.contains("active")) return;
    e.preventDefault();
    e.stopPropagation();
    const ls = document.getElementById("langSel");
    if (ls && ls.classList.contains("active")) {
      if (window.I18N && I18N.cancelLangScreen) I18N.cancelLangScreen();
      return;
    }
    close();
  }, true);

  function toggle() {
    if (sec.classList.contains("active")) close();
    else open();
  }

  window.warDownload = { open, close, toggle };
})();
