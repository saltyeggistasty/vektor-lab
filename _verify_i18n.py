# -*- coding: utf-8 -*-
import json
import os
import re

BASE = r"G:\vektor-lab(1)\vektor-lab"
LANGS = ["indonesia", "english", "melayu", "russia", "ukraina", "irish", "arab"]
data = {l: json.load(open(os.path.join(BASE, "i18n", l + ".json"), encoding="utf-8"))
        for l in LANGS}

src = open(os.path.join(BASE, "static", "i18n.js"), encoding="utf-8").read()
# buang baris komentar dulu biar selector yang di-comment gak ikut dicek
src = "\n".join(l for l in src.splitlines() if not l.strip().startswith("//"))
keys = set()
for m in re.finditer(r'\[\s*(?:"#|"\.)[^,]+,\s*"([a-z0-9_.]+)"', src):
    keys.add(m.group(1))

tjs = open(os.path.join(BASE, "static", "tools.js"), encoding="utf-8").read()
for k in re.findall(r'"((?:tools|sims)\.[a-z0-9_]+)"', tjs):
    keys.add(k)

bad = 0
for key in sorted(keys):
    grp, _, k = key.partition(".")
    for l in LANGS:
        if k not in data[l].get(grp, {}):
            print(f"MISSING {key} @ {l}")
            bad += 1
print(f"dicek {len(keys)} kunci unik x {len(LANGS)} bahasa — hilang: {bad}")
