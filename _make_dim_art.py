# -*- coding: utf-8 -*-
"""Buat copy gelap (60% lebih gelap) dari 5 art backdrop kartu fisika.
   Copy DIPISAH supaya art kartu (hover caption) tetap asli terang,
   hanya BACKDROP (hover-bg) yang memakai versi gelap.质地 jpeg/png dijaga."""
import os
from PIL import Image, ImageEnhance

SRC = [
    ("menu_screen/qm_wave.jpg",            "menu_screen/dim/dim_qm_wave.jpg"),
    ("menu_screen/QM.png",                 "menu_screen/dim/dim_QM.png"),   # art lama Mekanika Kuantum
    ("menu_screen/Relativity Cover.jpg",   "menu_screen/dim/dim_Relativity_Cover.jpg"),
    ("menu_screen/NewtonianMechanics.jpg", "menu_screen/dim/dim_NewtonianMechanics.jpg"),
    ("menu_screen/Hydrodynamic.jpg",       "menu_screen/dim/dim_Hydrodynamic.jpg"),
    ("menu_screen/wm/wm_wave.jpg",         "menu_screen/dim/dim_wm_wave.jpg"),
]

os.makedirs("menu_screen/dim", exist_ok=True)
for src, dst in SRC:
    im = Image.open(src).convert("RGB")
    # 60% lebih gelap = brightness 0.4
    out = ImageEnhance.Brightness(im).enhance(0.4)
    # format ngikutin extension tujuan
    dst_fmt = "PNG" if dst.lower().endswith(".png") else "JPEG"
    kwargs = {"format": dst_fmt}
    if dst_fmt == "JPEG":
        kwargs["quality"] = 90
    out.save(dst, **kwargs)
    print(f"{src} -> {dst}  ({im.size[0]}x{im.size[1]})")
