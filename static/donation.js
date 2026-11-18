/* ================= DONASI (overlay ala layar bahasa) =================
   Tombol ❤ di bar atas -> layar donasi (USDC / USDT / Monero).
   Alamat wallet diambil dari /donation_addresses (address.json di root
   project, bisa disunting pemilik web tanpa sentuh kode).
   Hover kartu koin -> alamat terbuka; klik -> alamat disalin (toast).
   MURNI UI, tidak menyentuh mesin fisika/matematika. */
(function () {
  const sec = document.getElementById("donSel");
  if (!sec) return;
  if (typeof $ !== "function") return;   // helper $ dari app.js harus siap

  let addrCache = null;

  /* ambil alamat wallet sekali, lalu pasang ke tiap kartu koin */
  async function loadAddrs() {
    if (addrCache) return addrCache;
    try {
      const res = await fetch("/donation_addresses");
      const data = await res.json();
      Object.keys(data).forEach((key) => {
        if (!key || key.startsWith("_")) return;          // _READ_ME diabaikan
        const btn = sec.querySelector('.d-coin[data-coin="' + key + '"]');
        if (!btn || !data[key] || !data[key].address) return;
        const code = btn.querySelector(".d-addr-code");
        if (code) code.textContent = data[key].address;
        const net = btn.querySelector(".d-net");
        if (net && data[key].network) net.textContent = data[key].network;
      });
      addrCache = data;
      return data;
    } catch (e) {
      /* offline / address.json rusak: kartu tetap tampil tanpa alamat */
      return null;
    }
  }

  function toast(msg) {
    const tip = sec.querySelector("#donCopyTip");
    if (msg) tip.textContent = msg;
    tip.classList.add("show");
    clearTimeout(tip._t);
    tip._t = setTimeout(() => tip.classList.remove("show"), 1700);
  }

  async function copyAddr(btn) {
    const code = btn.querySelector(".d-addr-code");
    const addr = code ? code.textContent.trim() : "";
    if (!addr) return;
    try {
      await navigator.clipboard.writeText(addr);
      toast();
    } catch (e) {
      /* fallback ala lama */
      try {
        const ta = document.createElement("textarea");
        ta.value = addr;
        ta.style.position = "fixed"; ta.style.opacity = "0";
        document.body.appendChild(ta);
        ta.select();
        document.execCommand("copy");
        ta.remove();
        toast();
      } catch (e2) {
        toast(I18N.t("donasi.copy_fail", "Gagal menyalin"));
      }
    }
  }

  let closeTween = null;   // animasi tutup yang masih jalan (anti-race klik cepat)

  /* zoom 90% khusus bahasa INDONESIA: naskah donasinya panjang, jadi saat
     page donasi dibuka zoom-nya diturunin biar muat banyak (default browser
     100%). Bahasa lain & saat overlay ketutup -> kembali normal */
  function applyDonZoom(on) {
    const idn = window.I18N && I18N.lang === "indonesia";
    document.body.style.zoom = (on && idn) ? "0.9" : "";
  }

  function open() {
    if (closeTween) { closeTween.kill(); closeTween = null; }
    const wasOpen = sec.classList.contains("active");
    sec.classList.add("active");
    /* body.don-open: angkat header DI ATAS overlay (z 9100) biar bar atas
       bisa dipakai user untuk pindah tab langsung dari page donasi */
    document.body.classList.add("don-open");
       applyDonZoom(true);
       loadAddrs();
    /* transisi masuk: overlay fade + panel glide dari bawah (ala layar bahasa) */
    if (window.gsap && !wasOpen) {
      gsap.fromTo(sec, { opacity: 0 }, { opacity: 1, duration: .38, ease: "power2.out",
        onComplete: () => gsap.set(sec, { clearProps: "opacity" }) });
      const inner = sec.querySelector(".d-inner");
      if (inner) gsap.fromTo(inner, { y: 28, opacity: 0, scale: .985 },
        { y: 0, opacity: 1, scale: 1, duration: .52, ease: "power3.out", delay: .06,
          onComplete: () => gsap.set(inner, { clearProps: "all" }) });
    }
  }
  function close() {
    if (!sec.classList.contains("active")) return;
    document.body.classList.remove("don-open");
    applyDonZoom(false);
    /* transisi keluar: fade dulu, BARU display:none (klo langsung remove
       class, overlay ngepot tanpa animasi) */
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

  /* reveal alamat & dim kartu lain via CLASS (bukan cuma :hover) supaya
     tetap bekerja di layar sentuh, keyboard, dan testing */
  const coins = [...sec.querySelectorAll(".d-coin")];
  coins.forEach((btn) => {
    btn.addEventListener("mouseenter", () => reveal(btn));
    btn.addEventListener("mouseleave", () => unreveal());
    btn.addEventListener("focus", () => reveal(btn));
    btn.addEventListener("blur", () => unreveal());
  });
  function reveal(btn) {
    coins.forEach((b) => b.classList.toggle("d-dim", b !== btn));
    btn.classList.add("d-open");
  }
  function unreveal() {
    coins.forEach((b) => { b.classList.remove("d-dim"); b.classList.remove("d-open"); });
  }

  sec.querySelectorAll(".d-coin").forEach((btn) => {
    btn.addEventListener("click", () => copyAddr(btn));
  });

  const closeBtn = document.getElementById("donClose");
  if (closeBtn) closeBtn.addEventListener("click", close);

  /* ESC menutup layar donasi, capture-phase + stopPropagation
     agar rantai ESC menu war (menu.js) TIDAK ikut jalan di tekanan ini */
  const auditBox = sec.querySelector("#auditBox");

  document.addEventListener("keydown", (e) => {
    if (e.key !== "Escape" || !sec.classList.contains("active")) return;
    e.preventDefault();
    e.stopPropagation();
    /* ESC di mode fullscreen audit: tutup fullscreen-nya dulu, donasi tetap
       terbuka. ESC lagi baru menutup layar donasi. */
    if (sec.classList.contains("audit-fs") && auditBox && auditBox.open) {
      auditBox.open = false;
      return;
    }
    close();
  }, true);

  /* ---------- audit expand -> fullscreen ----------
     details[open] -> pasang .audit-fs (panel jadi fullscreen, elemen luar
     autohide), lalu 2 rAF kemudian .audit-fs-in -> konten fade+slide masuk
     berjenjang (transisi opacity/transform murni = ringan). */
  if (auditBox) {
    auditBox.addEventListener("toggle", () => {
      if (auditBox.open) {
        sec.classList.remove("audit-fs-in");
        sec.classList.add("audit-fs");
        requestAnimationFrame(() => requestAnimationFrame(() =>
          sec.classList.add("audit-fs-in")));
      } else {
        sec.classList.remove("audit-fs-in");
        setTimeout(() => sec.classList.remove("audit-fs"), 180);
      }
    });
  }

  /* ---------- form audit donasi (panel collapsible) ----------
     Foto + identitas dikirim ke email pemilik web lewat /api/audit
     (SMTP dibaca backend dari config.json). Murni UI di sini. */
  const auditForm = sec.querySelector("#auditForm");
  const auditMsg = sec.querySelector("#auditMsg");
  const photoIn = sec.querySelector("#auditPhoto");
  const photoCirc = sec.querySelector("#auditPhotoCirc");
  const photoPrev = sec.querySelector("#auditPhotoPrev");
  const at = (k, fb) => I18N.t(k, fb);

  if (photoIn && photoCirc && photoPrev) {
    photoIn.addEventListener("change", () => {
      const f = photoIn.files && photoIn.files[0];
      if (!f) return;
      const rd = new FileReader();
      rd.onload = () => {
        photoPrev.src = rd.result;
        photoPrev.classList.remove("hidden");
        photoCirc.classList.add("has-photo");   // sembunyikan teks ajakan
      };
      rd.readAsDataURL(f);
    });
  }

  if (auditForm && auditMsg) {
    auditForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      auditMsg.className = "hint";
      /* validasi ringan client-side biar gak buang request */
      if (!$("aFullname").value.trim() || !$("aNickname").value.trim() ||
          !$("aCountry").value.trim()) {
        auditMsg.textContent = at("donasi.audit.err_required",
          "Isi dulu nama lengkap, nama panggilan, dan asal negara ya.");
        auditMsg.className = "hint err";
        return;
      }
      const photo = photoIn && photoIn.files && photoIn.files[0];
      if (!photo) {
        auditMsg.textContent = at("donasi.audit.err_photo", "Foto publik wajib diunggah.");
        auditMsg.className = "hint err";
        return;
      }
      const btn = sec.querySelector("#auditSend");
      btn.disabled = true;
      auditMsg.textContent = at("donasi.audit.sending", "Mengirim...");
      try {
        const res = await fetch("/api/audit", { method: "POST", body: new FormData(auditForm) });
        const j = await res.json();
        if (!j.ok) throw new Error(j.error || "gagal");
        auditMsg.textContent = at("donasi.audit.sent_ok",
          "✔ Terima kasih! Form audit kamu sudah terkirim.");
        auditMsg.className = "hint ok";
        auditForm.reset();
        photoPrev.classList.add("hidden");
        photoCirc.classList.remove("has-photo");
        photoIn.value = "";
      } catch (err) {
        auditMsg.textContent = at("donasi.audit.sent_fail", "Gagal mengirim") + ": " + err.message;
        auditMsg.className = "hint err";
      } finally {
        btn.disabled = false;
      }
    });
  }

  /* bahasa berganti selagi page donasi masih terbuka (via bar atas -> 🌐):
     zoom 90% ikut disegarkan biar gak nyangkut di bahasa lain */
  try {
    if (window.I18N) I18N.onChange(() => {
      if (sec.classList.contains("active")) applyDonZoom(true);
    });
  } catch (e) {}

  window.warDonation = { open, close };
})();
