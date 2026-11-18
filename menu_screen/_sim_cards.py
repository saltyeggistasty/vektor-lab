# -*- coding: utf-8 -*-
"""SIM crop card potret (tile 246x830, object-fit cover, posisi center)
untuk solar_flare.jpg & QM.png — biar tahu posisi mana yang paling
'nyentring & fit-frame'. Simpan beberapa kandidat crop utk dilirik."""
from PIL import Image
import os

TMP = os.path.join(os.environ.get("TEMP", "."), "nabla_cover_lines")
os.makedirs(TMP, exist_ok=True)

def sim_card(path, name, ox_frac=0.5, oy_frac=0.5, cw=246, ch=830):
    img = Image.open(path).convert("RGB")
    W, H_ = img.size
    sc = max(cw / W, ch / H_)                 # cover
    sw, sh = round(W * sc), round(H_ * sc)
    big = img.resize((sw, sh), Image.LANCZOS)
    ox = round((sw - cw) * ox_frac)
    oy = round((sh - ch) * oy_frac)
    band = big.crop((ox, oy, ox + cw, oy + ch))
    p = os.path.join(TMP, name)
    band.save(p, "JPEG", quality=88)
    print(name, "->", p, "| x-window",
          round(ox / sw * 100, 1), "-", round((ox + cw) / sw * 100, 1), "%")

# solar flare: tengah & sedikit turun (disc penuh lebihnya)
sim_card("menu_screen/solar_flare.jpg", "sim_solar_center.jpg", .5, .5)
sim_card("menu_screen/solar_flare.jpg", "sim_solar_lower.jpg", .5, .62)
# QM: tengah vs gelombang kirinya vs bawah banget (full wave tanpa eq)
sim_card("menu_screen/QM.png", "sim_qm_center.jpg", .5, .5)
sim_card("menu_screen/QM.png", "sim_qm_left_crest.jpg", .30, .55)
sim_card("menu_screen/QM.png", "sim_qm_bottom.jpg", .5, .8)
