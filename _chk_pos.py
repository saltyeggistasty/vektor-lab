# -*- coding: utf-8 -*-
# Verifikasi posisi kartu grapher: setiap id harus muncul TEPAT 1x dan di
# grid umbrella yang benar.
import re

html = open(r"G:\vektor-lab(1)\vektor-lab\templates\index.html", encoding="utf-8").read()
grids = []
for m in re.finditer(r'data-umb="([a-z0-9_-]+)"', html):
    grids.append((m.group(1), m.start()))
grids.append(("EOF", len(html)))

EXPECT = {
    "gdomain": "complex", "gfractal": "complex",
    "gsurf3d": "calculus", "gfrenet": "calculus",
    "gtrans3d": "algebra", "gslope": "ode", "gdist": "stats",
    "ggraphalgo": "discrete", "gfield": "electro", "gpvcycle": "thermo",
    "gising": "thermo", "gminkowski": "relativity", "gfluid": "hydro",
    "ggeodesic": "gr", "gray": "wave",
}
fail = 0
for tool, umb in EXPECT.items():
    m = re.search(r'data-tool="' + tool + '"', html)
    if not m:
        print(f"MISSING CARD {tool}")
        fail += 1
        continue
    pos = m.start()
    cur = grids[0][0]
    for name, start in grids:
        if start < pos:
            cur = name
        else:
            break
    ok = cur == umb
    print(f"{'OK  ' if ok else 'SALAH'} {tool:12} di {cur:12} (harus {umb})")
    fail += 0 if ok else 1
    # cek duplikat
    cnt = len(re.findall(r'data-tool="' + tool + '"', html))
    if cnt != 1:
        print(f"  DUPLIKAT {tool}: {cnt}x")
        fail += 1
print("FAIL =", fail)
