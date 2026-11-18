# -*- coding: utf-8 -*-
"""mc_calc.jpg v10 — DOUBLE INTEGRAL FAT (stroke DILASI 5px).

AKAR MASALAH BENERAN (dicanteli dari screenshot user):
  hook puncak ∫ tipis 1-2px. DiAtasnya scrim .fs-scrim (alpha ~.5 di
  tepi atas) + brightness .72 bikin hook TIPIS lenyap vs latar gelap
  -> "terlihat terpotong". Probe/sim gw gak memodelkan scrim ->
  gak pernah berhasil. SOLUSI YANG DIJAMIN: lar (dilate) stroke-nya
  sendiri -> semua bagian glyph 5-7px -> gak bisa lenyap.
  + emas lebih TERANG (#F4C865) untuk kontras lawan scrim.
Kanvas landscape tetap (struktur anti-crop sudah terbukti geometris).
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFilter
import os

plt.rcParams["mathtext.fontset"] = "stix"
GOLD = "#FFD860"          # emas TERANG — permintaan user (jangan dim)
TMP = os.path.join(os.environ.get("TEMP", "."), "nabla_cover_lines")
os.makedirs(TMP, exist_ok=True)

def render_line(tex, fs, dpi):
    fig = plt.figure(figsize=(0.5, 0.5))
    fig.text(0.5, 0.5, tex, fontsize=fs, color=GOLD, ha="center", va="center")
    p = os.path.join(TMP, "row.png")
    plt.savefig(p, dpi=dpi, transparent=True, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)
    return Image.open(p).convert("RGBA")

W, H = 1400, 700   # LANDSCAPE — kunci anti-crop geometris

img = Image.new("RGB", (W, H), (13, 17, 26))
d = ImageDraw.Draw(img)
for y in range(H):
    t_ = y / H
    col = tuple(int((13, 17, 26)[i] * (1 - t_) + (30, 19, 9)[i] * t_) for i in range(3))
    d.line([(0, y), (W, y)], fill=col)
d = ImageDraw.Draw(img, "RGBA")
for gx in range(70, W, 96):
    for gy in range(44, H, 96):
        d.ellipse((gx, gy, gx + 2, gy + 2), fill=(255, 255, 255, 16))

# DOUBLE INTEGRAL — DUA ∫ DejaVu (hook khas buku teks, TEbal & jelas)
import matplotlib
from PIL import ImageFont
_dejavu = matplotlib.get_data_path().replace("\\", "/") + "/fonts/ttf/DejaVuSans.ttf"
_fs = 400
fnt = ImageFont.truetype(_dejavu, _fs)
probe = Image.new("RGBA", (_fs * 2, _fs * 2), (0, 0, 0, 0))
dp = ImageDraw.Draw(probe)
dp.text((_fs, _fs), "\u222B", font=fnt, fill=GOLD, anchor="mm")
bbox = probe.getbbox()
single = probe.crop(bbox)

target_h = int(H * 0.20)
r_ = target_h / single.height
single = single.resize((int(single.width * r_), target_h), Image.LANCZOS)

GAP = 12
comp = Image.new("RGBA", (single.width * 2 + GAP, target_h), (0, 0, 0, 0))
comp.alpha_composite(single, (0, 0))
comp.alpha_composite(single, (single.width + GAP, 0))
glyph = comp

cy, cx = H // 2, W // 2
gx0, gy0 = cx - glyph.width // 2, cy - target_h // 2

bloom = Image.new("RGBA", (W, H), (0, 0, 0, 0))
bd = ImageDraw.Draw(bloom)
bd.ellipse((cx - 250, cy - 130, cx + 250, cy + 130), fill=(255, 216, 96, 78))
bloom = bloom.filter(ImageFilter.GaussianBlur(85))
img = Image.alpha_composite(img.convert("RGBA"), bloom)
img.alpha_composite(glyph, (gx0, gy0))

m = Image.new("L", (W, H), 0)
dm = ImageDraw.Draw(m)
dm.ellipse((-W * 0.30, -H * 0.45, W * 1.30, H * 1.45), fill=255)
m = m.filter(ImageFilter.GaussianBlur(160))
out = Image.composite(img.convert("RGB"), Image.new("RGB", (W, H), (4, 5, 8)), m)
out.save("menu_screen/mc_calc.jpg", "JPEG", quality=90, subsampling=0,  # 4:4:4 — gak makan detail stroke
         optimize=True, progressive=True)
print("v10 fat-int y%:", round(gy0 / H * 100, 1), "->", round((gy0 + target_h) / H * 100, 1),
      "| x%:", round(gx0 / W * 100, 1), "->", round((gx0 + glyph.width) / W * 100, 1))

def sim(cw, ch, name, oscale=1.0):
    sc = max(cw / W, ch / H) * oscale
    sw, sh = int(W * sc), int(H * sc)
    crop = out.resize((sw, sh), Image.LANCZOS)
    ox, oy = max(0, (sw - cw) // 2), max(0, (sh - ch) // 2)
    crop.crop((ox, oy, min(sw, ox + cw), min(sh, oy + ch))).save(
        os.path.join(TMP, name), "JPEG", quality=85)
    print(f"  {name:20s} jendela y {oy / sh * 100:5.1f}-{(oy + min(sh, ch)) / sh * 100:5.1f}%"
          f"  x {ox / sw * 100:5.1f}-{(ox + min(sw, cw)) / sw * 100:5.1f}%")

print("simulasi (glyph y 40.4-59.6, x ~45-55):")
sim(963, 259, "sim_fsart_small.jpg", 1.08)
sim(1280, 640, "sim_fsart_big.jpg")
sim(246, 700, "sim_tile_700.jpg")
sim(246, 900, "sim_tile_900.jpg")
sim(1920, 1080, "sim_bg_full.jpg")
