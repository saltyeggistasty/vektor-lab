# -*- coding: utf-8 -*-
"""qm_card.jpg v3 — canvas 700x1630 (rasio ~0.43), kompromi antara kartu
pendek (~246x430, rasio 0.57) dan penuh (~246x830, rasio 0.30).
Persamaan Schrodinger ditaruh di ZONA AMAN (y 17%, lebar 66%) supaya
tetap utuh di kedua ukuran: verifikasi crop 246x430 & 246x830."""
from PIL import Image, ImageDraw, ImageFilter
import os, random

src = Image.open("menu_screen/QM.png").convert("RGB")

eq = src.crop((385, 172, 1035, 300))          # persamaan, latar hitam murni
from PIL import ImageEnhance
eq = ImageEnhance.Contrast(eq).enhance(1.35)
eq = ImageEnhance.Brightness(eq).enhance(1.3)
wave = src.crop((240, 290, 720, 784))         # gelombang gel crest (1.46x stretch)

CWD, CHD = 700, 1630
card = Image.new("RGBA", (CWD, CHD), (2, 4, 10, 255))
d = ImageDraw.Draw(card, "RGBA")

random.seed(7)
for _ in range(110):
    gx, gy = random.randint(10, CWD - 10), random.randint(int(CHD * .05), int(CHD * .55))
    r = random.choice([1, 1, 2])
    d.ellipse((gx, gy, gx + r, gy + r), fill=(150, 180, 255, 50))

# persamaan: lebar 73% (maks zero-cut utk crop tegak 246x830: jendela 69.02%
# canvas, konten persamaan 93.4% lebar -> 0.6902/0.934 = 73.9% muat pas),
# posisi atas 17%
tarW = int(CWD * .715)
rp = tarW / eq.width
eq_big = eq.resize((tarW, round(eq.height * rp)), Image.LANCZOS)
card.paste(eq_big, ((CWD - tarW) // 2, int(CHD * .17)))

# gelombang: lebar penuh, nempel bawah, fade alpha di kepala
wave_big = wave.resize((CWD, round(wave.height * (CWD / wave.width))), Image.LANCZOS)
wh = wave_big.height
dwh = wave_big.convert("RGBA")
mask = Image.new("L", dwh.size, 255)
mkd = ImageDraw.Draw(mask)
FZ = min(200, wh // 3)
for i in range(FZ):
    mkd.line([(0, i), (dwh.width, i)], fill=int(255 * (i / FZ) ** .8))
dwh.putalpha(mask)
card.alpha_composite(dwh, (0, CHD - wh))

out = card.convert("RGB")

# penerangan +40% ala gamma-lift: bayangan naik (tak begitu geko hitam),
# sorotan TIDAK terpotong ke putih (v=255 tetap 255)
LIFT = 1.4
out = out.point(lambda p: round(255 * (p / 255) ** (1 / LIFT)))
out.save("menu_screen/qm_card.jpg", "JPEG", quality=90, subsampling=0, optimize=True)
print("qm_card.jpg", out.size)

tmp = os.environ.get("TEMP", ".")
def sim(name, cw, ch, ox=.5, oy=.5):
    sc = max(cw / CWD, ch / CHD)
    sw, sh = round(CWD * sc), round(CHD * sc)
    big = out.resize((sw, sh), Image.LANCZOS)
    x0, y0 = round((sw - cw) * ox), round((sh - ch) * oy)
    band = big.crop((x0, y0, x0 + cw, y0 + ch))
    p = os.path.join(tmp, "nabla_cover_lines", name)
    band.save(p, "JPEG", quality=88)
    print(name, "| x", round(x0 / sw * 100, 1), "-", round((x0 + cw) / sw * 100, 1),
          "% y", round(y0 / sh * 100, 1), "-", round((y0 + ch) / sh * 100, 1), "%")

sim("sim_qm430.jpg", 246, 430)   # kartu user sekarang
sim("sim_qm830.jpg", 246, 830)   # kartu layar penuh
