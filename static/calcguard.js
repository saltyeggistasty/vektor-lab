/* =================================================================
   CALC GUARD — anti-spam tombol kalkulasi + form donasi/about.
   1) Tombol kalkulasi (semua tools math & fisika): cooldown 5 detik.
      #runCalc / #runGraph / #runPhys / #toolRun — keypad #kpSubmit
      ikut ke-cover karena route via .click() tombol yang sama.
   2) Form audit donasi (#auditForm) & kritik/lapor bug (#aboutForm):
      cooldown 10 detik antar pengiriman — cegah spam email pemilik
      web. Cover KLIK tombol Kirim DAN submit via Enter (listener
      "submit" capture-phase).
   Spam saat cooldown: aksi DIBLOKIR (capture phase, sebelum handler
   tool/form jalan) + pesan kecil merah di bawah tombol/form.
   MURNI UI — tidak menyentuh mesin tools sama sekali.
   ================================================================= */
(function () {
  "use strict";

  const CALC_WAIT_MS = 5000;
  const CALC_SEL = "#runCalc, #runGraph, #runPhys, #toolRun";
  const FORM_WAIT_MS = 10000;
  const FORM_BTN_SEL = "#auditSend, #aboutSend";
  const FORM_IDS = { auditForm: 1, aboutForm: 1 };
  let lastCalc = 0;      // timestamp kalkulasi terakhir yang LOLOS
  let lastForm = 0;      // timestamp form terakhir yang LOLOS
  let hideT = null;

  /* ---------- pesan merah kecil di bawah tombol/form ---------- */
  let tip = document.getElementById("calcWaitTip");
  if (!tip) {
    tip = document.createElement("div");
    tip.id = "calcWaitTip";
    tip.className = "calc-wait-tip";
    tip.setAttribute("role", "alert");
    document.body.appendChild(tip);
  }
  tip.hidden = true;

  function showTip(anchor, key, fb) {
    tip.textContent = window.I18N ? I18N.t(key, fb) : fb;
    tip.hidden = false;
    /* posisi: nempel di BAWAH anchor (fixed -> aman di panel scroll) */
    const r = anchor.getBoundingClientRect();
    tip.style.top = Math.min(r.bottom + 6, window.innerHeight - 40) + "px";
    tip.style.left = Math.max(8,
      Math.min(r.left, window.innerWidth - tip.offsetWidth - 8)) + "px";
    clearTimeout(hideT);
    hideT = setTimeout(() => { tip.hidden = true; }, 2400);
  }

  function blocked(now, lastTs, waitMs) {
    return lastTs && now - lastTs < waitMs;
  }

  /* ---------- capture-phase: blokir spam SEBELUM handler tujuan ---------- */
  document.addEventListener("click", (e) => {
    const now = Date.now();
    const calcBtn = e.target.closest ? e.target.closest(CALC_SEL) : null;
    if (calcBtn) {
      if (blocked(now, lastCalc, CALC_WAIT_MS)) {
        e.preventDefault();
        e.stopPropagation();   // handler tool (.onclick) TIDAK jalan
        showTip(calcBtn, "err.calc_wait",
          "Please wait 5 seconds before your next calculation");
        return;
      }
      lastCalc = now;          // kalkulasi berikutnya mulai window baru
      return;
    }
    const formBtn = e.target.closest ? e.target.closest(FORM_BTN_SEL) : null;
    if (formBtn) {
      /* BLOKIR-SAJA: jangan catat lastForm di sini! Klik tombol submit
         juga memicu event "submit" — kalau dicatat di click, submit-nya
         keblokir oleh catatan sendiri (form gak pernah terkirim).
         Pencatatan cooldown = tugas listener "submit" di bawah. */
      if (blocked(now, lastForm, FORM_WAIT_MS)) {
        e.preventDefault();    // cegah submit default dari klik ini
        e.stopPropagation();
        showTip(formBtn, "err.form_wait",
          "Please wait 10 seconds before sending the form again");
      }
    }
  }, true);

  /* Enter di input -> submit event langsung (tanpa klik tombol) */
  document.addEventListener("submit", (e) => {
    if (!e.target || !FORM_IDS[e.target.id]) return;
    const now = Date.now();
    if (blocked(now, lastForm, FORM_WAIT_MS)) {
      e.preventDefault();
      e.stopPropagation();
      const btn = e.target.querySelector("#auditSend, #aboutSend") || e.target;
      showTip(btn, "err.form_wait",
        "Please wait 10 seconds before sending the form again");
      return;
    }
    lastForm = now;
  }, true);
})();
