# -*- coding: utf-8 -*-
"""Bendera untuk layar pemilih bahasa (file kecil 480 x 320).
   Dipakai dua peran: ikon kiri item bahasa + backdrop blur menu bahasa.
   Arabic nasibnya pakai bendera PALESTINA (request user), bukan Saudi."""
import os, math
from PIL import Image, ImageDraw

FOLDER = os.path.dirname(os.path.abspath(__file__))
os.makedirs(FOLDER, exist_ok=True)
W, H = 480, 320

def save(im, name):
    im.convert("RGB").save(os.path.join(FOLDER, name), "JPEG", quality=88, optimize=True)
    print(name, "ok")

def neutral(x):  # Indonesia: merah atas, putih bawah
    d = ImageDraw.Draw(x)
    d.rectangle([0, 0, W, H // 2], fill=(206, 17, 38))
    d.rectangle([0, H // 2, W, H], fill=(255, 255, 255))

def malaysia(x):  # 14 lajur merah putih + kanton biru + sabit & bintang kuning
    d = ImageDraw.Draw(x)
    n = 14
    for i in range(n):
        col = (204, 17, 38) if i % 2 == 0 else (255, 255, 255)
        d.rectangle([0, H * i // n, W, H * (i + 1) // n], fill=col)
    cw, ch = int(W * .44), int(H * .5)
    d.rectangle([0, 0, cw, ch], fill=(16, 52, 132))
    # sabit: lingkaran kuning digerudi lingkaran biru
    r = int(ch * .42)
    cx, cy = int(cw * .48), int(ch * .5)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 204, 0))
    r2 = int(r * .82)
    d.ellipse([cx + int(r * .25) - r2, cy - r2, cx + int(r * .25) + r2, cy + r2], fill=(16, 52, 132))
    # bintang 8 lidi
    s, scx, scy = int(ch * .30), int(cw * .78), int(ch * .5)
    pts = []
    for k in range(16):
        ang = math.pi * k / 8 + math.pi / 16
        rad = s if k % 2 == 0 else s * .42
        pts.append((scx + rad * math.cos(ang), scy + rad * math.sin(ang)))
    d.polygon(pts, fill=(255, 204, 0))

def russia(x):
    d = ImageDraw.Draw(x)
    for i, c in enumerate([(255, 255, 255), (0, 57, 166), (213, 43, 30)]):
        d.rectangle([0, H * i // 3, W, H * (i + 1) // 3], fill=c)

def ukraine(x):
    d = ImageDraw.Draw(x)
    d.rectangle([0, 0, W, H // 2], fill=(0, 91, 187))
    d.rectangle([0, H // 2, W, H], fill=(255, 215, 0))

def ireland(x):
    d = ImageDraw.Draw(x)
    cols = [(22, 155, 98), (255, 255, 255), (255, 136, 62)]
    for i, c in enumerate(cols):
        d.rectangle([W * i // 3, 0, W * (i + 1) // 3, H], fill=c)

def palestine(x):  # hitam putih hijau horizontal + segitiga merah kiri
    d = ImageDraw.Draw(x)
    for i, c in enumerate([(0, 0, 0), (233, 236, 239), (0, 114, 60)]):
        d.rectangle([0, H * i // 3, W, H * (i + 1) // 3], fill=c)
    d.polygon([(0, 0), (0, H), (int(W * .42), H / 2)], fill=(206, 17, 38))

def united_kingdom(x):
    NAVY, WHITE, RED = (1, 33, 105), (255, 255, 255), (200, 16, 46)
    d = ImageDraw.Draw(x)
    d.rectangle([0, 0, W, H], fill=NAVY)
    off = 44                      # diagonal putih lebar (lidi dgn offset biar simetris)
    for sign in (1, -1):
        # putih diagonal
        d.polygon([(-off, 0 if sign > 0 else H), (0, 0 if sign > 0 else H),
                   (W + off, H if sign > 0 else 0), (W, H if sign > 0 else 0)], fill=WHITE)
        d.polygon([(0, -off if sign > 0 else H + off), (0, 0 if sign > 0 else H),
                   (W, H + off if sign > 0 else -off), (W, H if sign > 0 else 0)], fill=WHITE)
    di = 16                       # diagonal merah lebih kurus (bukan setia bendera asli,
    for sign in (1, -1):          # cukup dikenali = versi sederhana)
        d.line([(-di, 0 if sign > 0 else H), (W + di, H if sign > 0 else 0)], fill=RED, width=di * 2)
        d.line([(W + di, 0 if sign > 0 else H), (-di, H if sign > 0 else 0)], fill=RED, width=di * 2)
    # cross putih lalu merah di tengah
    d.rectangle([W // 2 - 68, 0, W // 2 + 68, H], fill=WHITE)
    d.rectangle([0, H // 2 - 56, W, H // 2 + 56], fill=WHITE)
    d.rectangle([W // 2 - 42, 0, W // 2 + 42, H], fill=RED)
    d.rectangle([0, H // 2 - 32, W, H // 2 + 32], fill=RED)

gen = {
    "indonesia.jpg": neutral,
    "malaysia.jpg": malaysia,
    "russia.jpg": russia,
    "ukraine.jpg": ukraine,
    "ireland.jpg": ireland,
    "palestine.jpg": palestine,
    "united_kingdom.jpg": united_kingdom,
}
for name, fn in gen.items():
    im = Image.new("RGB", (W, H))
    fn(im)
    save(im, name)
print("beres, folder:", FOLDER)
