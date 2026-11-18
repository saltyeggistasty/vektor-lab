# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
base = r"G:\vektor-lab(1)\vektor-lab"

# ---------- 1) CSS: jarak -20% + audit fullscreen ----------
fp = base + r"\static\style.css"
css = open(fp, encoding="utf-8").read()
add = '''

/* ---- donasi: jarak koin -> pertanyaan dipangkas 20% ----
   Jarak lama = gap flex 12px + margin .d-text .8vh; -20% dari totalnya. */
#donSel .d-text { margin-top: max(0px, calc(.64vh - 2.4px)); }

/* ---- donasi: audit expand -> FULLSCREEN (transisi murni opacity/transform,
   gak ada animasi height/blur = ringan di GPU lemah) ----
   Saat .audit-fs dipasang: semua anak .d-inner SELAIN panel audit fade-out
   (autohide), panel audit jadi fixed inset 0 (latarnya = teal menu yg sama,
   jadi perpindahan posisinya gak kelihatan "lompat"). Konten masuk dengan
   fade+slide berjenjang (.audit-fs-in dipasang 2 rAF setelahnya). */
#donSel .d-inner > * { transition: opacity .32s ease; }
#donSel.audit-fs .d-inner > :not(.d-audit) { opacity: 0; pointer-events: none; }

#donSel.audit-fs .d-audit {
  position: fixed; inset: 0; z-index: 30;
  width: auto; max-width: none; margin: 0;
  border: 0; border-radius: 0;
  background: #266467;               /* = latar menu: snap tak terlihat */
  padding: 26px clamp(20px, 6vw, 90px) 34px;
  overflow-y: auto;
}
#donSel.audit-fs .d-audit > summary { font-size: 1.5rem; padding: 12px 0 16px;
  max-width: 1100px; margin: 0 auto; width: 100%; }
#donSel.audit-fs .d-audit-in { max-width: min(1100px, 92vw); margin: 0 auto; gap: 14px; }

/* elemen dalam ikut membesar karena panel jadi fullscreen */
#donSel.audit-fs .d-aud-intro, #donSel.audit-fs .d-aud-invite { font-size: 1.28rem; }
#donSel.audit-fs .d-aud-warn { font-size: 1.28rem; }
#donSel.audit-fs .d-aud-fields { gap: 20px 30px; }
#donSel.audit-fs .d-aud-fields .lbl { font-size: 1.12rem; }
#donSel.audit-fs .d-aud-fields input { font-size: 1.18rem; padding: 10px 2px; }
#donSel.audit-fs .d-aud-chk span { font-size: 1.12rem; }
#donSel.audit-fs .d-aud-send { font-size: 1.22rem; padding: 14px 64px; }
#donSel.audit-fs .d-photo-circ { width: 168px; height: 168px; }
#donSel.audit-fs .d-photo-txt { font-size: .95rem; }

/* animasi masuk konten: hidden saat .audit-fs (TANPA transisi), lalu
   .audit-fs-in (2 rAF kemudian) -> fade+slide berjenjang */
#donSel.audit-fs:not(.audit-fs-in) .d-audit-in > * { opacity: 0;
  transform: translateY(16px); transition: none; }
#donSel.audit-fs-in .d-audit-in > * { opacity: 1; transform: none;
  transition: opacity .42s ease, transform .42s ease; }
#donSel.audit-fs-in .d-audit-in > :nth-child(2) { transition-delay: .05s; }
#donSel.audit-fs-in .d-audit-in > :nth-child(3) { transition-delay: .09s; }
#donSel.audit-fs-in .d-audit-in > :nth-child(n+4) { transition-delay: .13s; }

@media (max-width: 900px) {
  #donSel.audit-fs .d-audit { padding: 16px 16px 24px; }
  #donSel.audit-fs .d-aud-intro, #donSel.audit-fs .d-aud-invite,
  #donSel.audit-fs .d-aud-warn { font-size: 1.08rem; }
  #donSel.audit-fs .d-audit > summary { font-size: 1.22rem; }
}'''
if "audit-fs" not in css:
    css += add
    open(fp, "w", encoding="utf-8", newline="\n").write(css)
    print("CSS ok, braces:", css.count("{"), css.count("}"))
else:
    print("CSS sudah ada")

# ---------- 2) donation.js: toggle + ESC ----------
fp = base + r"\static\donation.js"
js = open(fp, encoding="utf-8").read()
old_esc = '''  document.addEventListener("keydown", (e) => {
    if (e.key !== "Escape" || !sec.classList.contains("active")) return;
    e.preventDefault();
    e.stopPropagation();
    close();
  }, true);'''
new_esc = '''  document.addEventListener("keydown", (e) => {
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
  if (typeof auditBox === "undefined" || !window.__auditBoxHooked) {
    const ab = sec.querySelector("#auditBox");
    if (ab) {
      ab.addEventListener("toggle", () => {
        if (ab.open) {
          sec.classList.remove("audit-fs-in");
          sec.classList.add("audit-fs");
          requestAnimationFrame(() => requestAnimationFrame(() =>
            sec.classList.add("audit-fs-in")));
        } else {
          sec.classList.remove("audit-fs-in");
          setTimeout(() => sec.classList.remove("audit-fs"), 180);
        }
      });
      window.__auditBoxHooked = true;
    }
  }'''
if old_esc in js:
    js = js.replace(old_esc, new_esc, 1)
    open(fp, "w", encoding="utf-8", newline="\n").write(js)
    print("donation.js ok")
else:
    print("donation.js ESC MISS")
