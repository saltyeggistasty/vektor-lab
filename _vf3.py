# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
fp = r"G:\vektor-lab(1)\vektor-lab\static\donation.js"
js = open(fp, encoding="utf-8").read()

old = '''  document.addEventListener("keydown", (e) => {
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
new = '''  const auditBox = sec.querySelector("#auditBox");

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
  }'''
if old in js:
    js = js.replace(old, new, 1)
    open(fp, "w", encoding="utf-8", newline="\n").write(js)
    print("fixed, refs auditBox:", js.count("auditBox"))
else:
    print("MISS")
