# -*- coding: utf-8 -*-
"""Terangkan cover war menu ~40% (gamma-lift, BUKAN multiply linear):
   out = 255 * (v/255)^(1/LIFT), LIFT=1.4
   -> bayangan & mid naik (hitam geko jadi kelihatan), sorotan v=255
      tetap 255 alias TIDAK ketos ke putih.
   Original disalin ke menu_screen/_orig_backup/ sekali (idempoten)."""
import os, shutil
from PIL import Image

FOLDER = os.path.dirname(os.path.abspath(__file__))
BACKUP = os.path.join(FOLDER, "_orig_backup")
LIFT = 1.4
FILES = [
    "mc_calc.jpg", "mc_graph.jpg", "mc_lin.jpg", "mc_ode.jpg",
    "magnetic_field_cover.jpg", "solar_flare.jpg",
]

os.makedirs(BACKUP, exist_ok=True)
for name in FILES:
    p = os.path.join(FOLDER, name)
    bak = os.path.join(BACKUP, name)
    im = Image.open(p).convert("RGB")
    if not os.path.exists(bak):
        shutil.copyfile(p, bak)          # backup KONDISI SEBELUM lift
    lifted = im.point(lambda v: round(255 * (v / 255) ** (1 / LIFT)))
    lifted.save(p, "JPEG", quality=90, subsampling=0, optimize=True)
    print(f"{name}: {im.size} dilift gamma {LIFT} (backup: {os.path.basename(bak)})")
print("beres.")
