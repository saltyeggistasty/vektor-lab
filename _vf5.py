# -*- coding: utf-8 -*-
import io, sys, re, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
base = r"G:\vektor-lab(1)\vektor-lab"

# ---------- 1) HTML: pindahkan auditBox keluar .d-text + hapus lead ----------
fp = base + r"\templates\index.html"
html = open(fp, encoding="utf-8").read()
# ambil blok details auditBox
m = re.search(r"[ \t]*<details class=\"d-audit\" id=\"auditBox\">.*?</details>\n", html, re.S)
assert m, "auditBox not found"
block = m.group(0)
html = html.replace(block, "", 1)
# lead dihapus
m2 = re.search(r"[ \t]*<p class=\"d-lead\"[^>]*>.*?</p>\n", html, re.S)
if m2:
    html = html.replace(m2.group(0), "", 1)
    print("lead <p> dihapus")
# sisipkan auditBox setelah </div> penutup .d-text: cari penutup d-text.
# .d-text dibuka dengan <div class="d-text"> ... kita cari pola </div> yang
# menutup d-text = baris setelah blok terakhir d-qa-note? Aman: sisipkan
# sebelum <footer/ elemen .l-foot di dalam d-inner? gunakan anchor: block
# dulu setelah d-text ditutup — cari '</div>\n\n' setelah posisi lead dulu.
i = html.find('<div class="d-text">')
j = html.find("</div>", html.find("d-qa-note", i))
# j = penutup .d-note? cek struktur: d-qa-note berada dalam d-text? cari
# dengan keseimbangan sederhana: mulai dari i, scan tag div
depth = 0
k = i
while True:
    mo = re.compile(r"<div\b|</div>").search(html, k)
    if not mo: break
    if mo.group(0) == "<div": depth += 1
    else:
        depth -= 1
        if depth == 0:
            j = mo.start(); break
    k = mo.end()
insert_at = html.find("\n", j)  # akhir baris penutup d-text
html = html[:insert_at] + "\n" + block.rstrip("\n") + html[insert_at:]
open(fp, "w", encoding="utf-8", newline="\n").write(html)
print("auditBox dipindah jadi anak .d-inner (setelah .d-text)")

# verifikasi struktur
d2 = open(fp, encoding="utf-8").read()
for pat in ["d-lead", "auditBox"]:
    print(pat, "count:", d2.count(pat))

# ---------- 2) i18n: hapus donasi.lead di 7 bahasa ----------
for lg in ["indonesia", "english", "melayu", "russia", "ukraina", "irish", "arab"]:
    fp2 = os.path.join(base, "i18n", lg + ".json")
    d = json.load(open(fp2, encoding="utf-8"))
    removed = d.get("donasi", {}).pop("lead", None)
    json.dump(d, open(fp2, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(lg, "lead removed:", removed is not None)

# ---------- 3) CSS: jarak 20% + margin qa_q ----------
fp3 = base + r"\static\style.css"
css = open(fp3, encoding="utf-8").read()
old = """/* ---- donasi: jarak koin -> pertanyaan dipangkas 20% ----
   Jarak lama = gap flex 12px + margin .d-text .8vh; -20% dari totalnya. */
#donSel .d-text { margin-top: max(0px, calc(.64vh - 2.4px)); }"""
new = """/* ---- donasi: jarak koin -> pertanyaan dipangkas 20% ----
   Jarak lama = gap flex 12px + margin .d-text .8vh + margin default
   .d-qa-q 1em (26.4px); margin qa_q dinolkan, sisanya dikompensasi. */
#donSel .d-text { margin-top: calc(.64vh + 18.7px); }
#donSel .d-qa-q { margin-top: 0; }"""
if old in css:
    css = css.replace(old, new, 1)
    open(fp3, "w", encoding="utf-8", newline="\n").write(css)
    print("CSS jarak ok, braces:", css.count("{"), css.count("}"))
else:
    print("CSS jarak MISS")
