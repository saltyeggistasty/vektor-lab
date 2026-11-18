/* =================================================================
   ABOUT US — overlay pola #donSel (tema flat teal #225659, gold #f2e394).
   Profil tim + form kritik/saran/lapor bug -> /api/feedback (email
   pemilik web via SMTP config.json, sama dengan form audit donasi).
   MURNI UI, tidak menyentuh mesin fisika/matematika sama sekali.
   ================================================================= */
(function () {
  "use strict";

  const sec = document.getElementById("aboutSel");
  if (!sec || typeof $ !== "function") return;
  const gsapAvailable = () => typeof window.gsap === "function";

  let closeTween = null;   // animasi tutup yang masih jalan (anti-race klik cepat)

  function open() {
    if (closeTween) { closeTween.kill(); closeTween = null; }
    const wasOpen = sec.classList.contains("active");
    sec.classList.add("active");
    /* body.about-open: angkat header DI ATAS overlay (z 9100) — bar atas
       tetap bisa dipakai pindah tab langsung dari layar about */
    document.body.classList.add("about-open");
    if (window.gsap && !wasOpen) {
      gsap.fromTo(sec, { opacity: 0 }, { opacity: 1, duration: .38, ease: "power2.out",
        onComplete: () => gsap.set(sec, { clearProps: "opacity" }) });
      const inner = sec.querySelector(".a-inner");
      if (inner) gsap.fromTo(inner, { y: 28, opacity: 0, scale: .985 },
        { y: 0, opacity: 1, scale: 1, duration: .52, ease: "power3.out", delay: .06,
          onComplete: () => gsap.set(inner, { clearProps: "all" }) });
    }
  }

  function close() {
    if (!sec.classList.contains("active")) return;
    document.body.classList.remove("about-open");
    /* fade dulu, BARU display:none (langsung remove class = ngepot) */
    if (window.gsap) {
      closeTween = gsap.to(sec, { opacity: 0, duration: .26, ease: "power2.in",
        onComplete: () => {
          closeTween = null;
          gsap.set(sec, { clearProps: "opacity" });
          sec.classList.remove("active");
        } });
    } else {
      sec.classList.remove("active");
    }
  }

  function toggle() {
    if (sec.classList.contains("active")) close();
    else open();
  }

  /* ESC menutup layar about, capture-phase + stopPropagation agar rantai
     ESC menu war (menu.js) TIDAK ikut jalan di tekanan ini */
  document.addEventListener("keydown", (e) => {
    if (e.key !== "Escape" || !sec.classList.contains("active")) return;
    e.preventDefault();
    e.stopPropagation();
    close();
  }, true);

  /* ---------- form kritik / lapor bug ----------
     name & contact opsional; message wajib. Kirim FormData ke
     /api/feedback — backend yang handle SMTP (config.json). */
  const form = sec.querySelector("#aboutForm");
  const msgEl = sec.querySelector("#aboutMsg");
  const at = (k, fb) => (window.I18N ? I18N.t(k, fb) : fb);

  if (form && msgEl) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      msgEl.className = "hint";
      const message = $("abMsg").value.trim();
      if (!message) {
        msgEl.textContent = at("about.err_msg", "Pesan nya jangan kosong ya.");
        msgEl.className = "hint err";
        return;
      }
      const btn = sec.querySelector("#aboutSend");
      btn.disabled = true;
      msgEl.textContent = at("about.sending", "Mengirim...");
      try {
        const res = await fetch("/api/feedback", { method: "POST", body: new FormData(form) });
        const j = await res.json();
        if (!j.ok) throw new Error(j.error || "gagal");
        msgEl.textContent = at("about.sent_ok",
          "✔ Terima kasih! Pesan kamu sudah terkirim ke kami.");
        msgEl.className = "hint ok";
        form.reset();
      } catch (err) {
        msgEl.textContent = at("about.sent_fail", "Gagal mengirim") + ": " + err.message;
        msgEl.className = "hint err";
      } finally {
        btn.disabled = false;
      }
    });
  }

  window.warAbout = { open, close, toggle };
})();
