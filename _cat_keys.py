# -*- coding: utf-8 -*-
"""Tambah key tombol kategori fisika ke 7 bahasa:
   menu.cat_classical / menu.cat_modern / menu.cat_all"""
import json, io

KEYS = ("cat_classical", "cat_modern", "cat_all")
TEXTS = {
    "indonesia": dict(cat_classical="Fisika Klasik", cat_modern="Fisika Moderen",
                      cat_all="Semua Bidang Fisika"),
    "english":   dict(cat_classical="Classical Physics", cat_modern="Modern Physics",
                      cat_all="All Fields of Physics"),
    "melayu":    dict(cat_classical="Fizik Klasik", cat_modern="Fizik Moden",
                      cat_all="Semua Bidang Fizik"),
    "russia":    dict(cat_classical="Классическая физика", cat_modern="Современная физика",
                      cat_all="Все области физики"),
    "ukraina":   dict(cat_classical="Класична фізика", cat_modern="Сучасна фізика",
                      cat_all="Усі галузі фізики"),
    "irish":     dict(cat_classical="Fisic Chlasiceach", cat_modern="Fisic Nua-Aimseartha",
                      cat_all="Gach Réimse Fisice"),
    "arab":      dict(cat_classical="الفيزياء الكلاسيكية", cat_modern="الفيزياء الحديثة",
                      cat_all="جميع مجالات الفيزياء"),
}

for lang, vals in TEXTS.items():
    p = f"i18n/{lang}.json"
    with io.open(p, encoding="utf-8") as f:
        d = json.load(f)
    m = d.setdefault("menu", {})
    for k in KEYS:
        m[k] = vals[k]
    with io.open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(lang, "OK")
