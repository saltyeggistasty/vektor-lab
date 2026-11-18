# -*- coding: utf-8 -*-
"""Struktur art math menu:
   - root new_math_menu/  : file kualitas TERTINGGI (dipulihkan dr BAK)
   - optimized/           : versi 1400px JPEG q85 yg dipakai situs (utk
                            card + backdrop blur — decode ngikutin pixel,
                            bukan bytes, jadi makanya butuh resolusi kecil)
   Markup index.html mengarah ke optimized/. BAK tetap dippinggalkan."""
import os, shutil
from PIL import Image

DIR = "menu_screen/new_math_menu"
BAK = os.path.join(DIR, "BAK")
OUT = os.path.join(DIR, "optimized")

JOBS = ["Cryptography.jpg", "AljabarLinier.jpg", "DifferentialEquation.png",
        "ComplexAnalysis.png", "Statistics.png"]

MAX_DIM = 1400
os.makedirs(OUT, exist_ok=True)

# 1. pulihkan root dari BAK (kualitas tertinggi balik ke root)
for name in JOBS:
    bak = os.path.join(BAK, name)
    root = os.path.join(DIR, name)
    shutil.copy2(bak, root)
    print("root restored:", name)

# 2. buat versi optimized (1400px, JPEG q85) dari BAK
for name in JOBS:
    stem = os.path.splitext(name)[0]
    out = os.path.join(OUT, stem + ".jpg")
    im = Image.open(os.path.join(BAK, name)).convert("RGB")
    w, h = im.size
    if max(w, h) > MAX_DIM:
        sc = MAX_DIM / max(w, h)
        im = im.resize((round(w * sc), round(h * sc)), Image.LANCZOS)
    im.save(out, "JPEG", quality=85, optimize=True, progressive=True)
    kb = os.path.getsize(out) / 1024
    print(f"optimized: {stem}.jpg {im.size[0]}x{im.size[1]} {kb:.0f}KB")
