# -*- coding: utf-8 -*-
"""Hapus key menu.series_math & menu.series_phys dari 7 file bahasa —
   tulisan "Perangkat Fisika/Matematika" gak dipakai lagi (posisi
   tersebut sekarang dipakai tombol back arrow)."""
import json, io

for lang in ["english", "indonesia", "melayu", "russia", "ukraina", "irish", "arab"]:
    p = f"i18n/{lang}.json"
    with io.open(p, encoding="utf-8") as f:
        d = json.load(f)
    m = d.get("menu", {})
    a = m.pop("series_math", None)
    b = m.pop("series_phys", None)
    if a is None and b is None:
        print(lang, "KEY TAK ADA")
        continue
    with io.open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(lang, "OK")
