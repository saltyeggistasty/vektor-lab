# -*- coding: utf-8 -*-
# Art placeholder 10 kartu simulasi — motif spesifik per simulasi,
# gaya gold-dark konsisten. Output: menu_screen/sim_card_art/<id>.jpg
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

OUT = r"G:\vektor-lab(1)\vektor-lab\menu_screen\sim_card_art"
os.makedirs(OUT, exist_ok=True)
W, H = 600, 960
GOLD = (224, 176, 74)
GOLD_DIM = (140, 108, 48)
GOLD_HI = (255, 214, 140)
BG1 = (10, 13, 20)
BG2 = (26, 20, 12)


def canvas():
    img = Image.new("RGB", (W, H))
    px = img.load()
    for y in range(H):
        t = y / H
        px_row = tuple(int(BG1[i] + (BG2[i] - BG1[i]) * t) for i in range(3))
        for x in range(W):
            px[x, y] = px_row
    return img


def frame(draw):
    draw.rectangle([16, 16, W - 16, H - 16], outline=GOLD_DIM, width=2)
    draw.line([(16, 60), (W - 16, 60)], fill=GOLD_DIM, width=1)


def grid(draw, step=48, alpha=(60, 52, 36)):
    for x in range(0, W, step):
        draw.line([(x, 0), (x, H)], fill=alpha, width=1)
    for y in range(0, H, step):
        draw.line([(0, y), (W, y)], fill=alpha, width=1)


def save(img, name):
    p = os.path.join(OUT, name)
    img.save(p, "JPEG", quality=88)
    print(name, os.path.getsize(p), "bytes")


# 1. slogistic: pohon bifurkasi (cabang rekursif)
img = canvas()
d = ImageDraw.Draw(img)
grid(d)
rng = np.random.RandomState(7)


def branch(x, y, ang, ln, depth):
    if depth == 0 or ln < 8:
        return
    x2 = x + ln * math.sin(ang)
    y2 = y - ln * math.cos(ang)
    col = GOLD if depth > 3 else GOLD_DIM
    d.line([(x, y), (x2, y2)], fill=col, width=3 if depth > 4 else 2)
    branch(x2, y2, ang - 0.55 + rng.uniform(-0.12, 0.12), ln * 0.72, depth - 1)
    branch(x2, y2, ang + 0.55 + rng.uniform(-0.12, 0.12), ln * 0.72, depth - 1)


branch(W / 2, H - 80, 0, 110, 7)
frame(d)
save(img, "slogistic.jpg")

# 2. slorenz: atraktor kupu-kupu (integrasi euler asli)
img = canvas()
d = ImageDraw.Draw(img)
grid(d)
sigma, rho, beta = 10.0, 28.0, 8.0 / 3.0
st = np.array([1.0, 1.0, 1.0])
pts = []
dt = 0.004
for _ in range(12000):
    dx = sigma * (st[1] - st[0])
    dy = st[0] * (rho - st[2]) - st[1]
    dz = st[0] * st[1] - beta * st[2]
    st = st + dt * np.array([dx, dy, dz])
    pts.append((st[0], st[2]))
sx = [p[0] for p in pts]
sz = [p[1] for p in pts]
x0, x1 = min(sx) - 2, max(sx) + 2
z0, z1 = min(sz) - 2, max(sz) + 2


def mx(v, a, b):
    return (v - a) / (b - a)


for i in range(0, len(pts) - 1, 2):
    xa = int(60 + mx(sx[i], x0, x1) * (W - 120))
    za = int(H - 70 - mx(sz[i], z0, z1) * (H - 160))
    xb = int(60 + mx(sx[i + 1], x0, x1) * (W - 120))
    zb = int(H - 70 - mx(sz[i + 1], z0, z1) * (H - 160))
    col = GOLD if (i // 2) % 3 else GOLD_HI
    d.line([(xa, za), (xb, zb)], fill=col, width=1)
frame(d)
save(img, "slorenz.jpg")

# 3. sfourier: harmonik menumpuk jadi gelombang persegi
img = canvas()
d = ImageDraw.Draw(img)
grid(d)
for k, amp in ((1, 1.0), (3, 0.33), (5, 0.2), (7, 0.14)):
    pts = [(x, H / 2 - 190 * amp * math.sin(2 * math.pi * k * x / W) + (k - 1) * 0)
           for x in range(40, W - 40, 3)]
    d.line(pts, fill=GOLD_DIM if k > 1 else GOLD, width=2)
# target: gelombang persegi
sq = []
for x in range(40, W - 40):
    v = 1 if math.sin(2 * math.pi * x / W) >= 0 else -1
    sq.append((x, H - 240 - 120 * v))
d.line(sq, fill=GOLD_HI, width=3)
d.text((44, 60), "SUM of harmonics", fill=GOLD_DIM)
frame(d)
save(img, "sfourier.jpg")

# 4. smatrix: grid miring + persegi tertransformasi + vektor
img = canvas()
d = ImageDraw.Draw(img)
M = np.array([[1.6, 0.7], [0.4, 1.3]])
cx, cy = W / 2, H / 2
for i in range(-6, 7):
    d.line([(cx + i * 42, 40), (cx + i * 42, H - 40)], fill=(48, 42, 30), width=1)
    d.line([(40, cy + i * 42), (W - 40, cy + i * 42)], fill=(48, 42, 30), width=1)
sq = np.array([[0, 1, 1, 0], [0, 0, 1, 1]])
t1 = M @ sq


def P(v):
    return (cx + v[0] * 52, cy - v[1] * 52)


d.polygon([P(sq[:, i]) for i in range(4)], outline=GOLD_DIM, width=2)
d.polygon([P(t1[:, i]) for i in range(4)], fill=(70, 56, 26), outline=GOLD, width=3)
for v in (np.array([1, 0]), np.array([0, 1])):
    tv = M @ v
    d.line([P(np.array([0, 0])), P(tv)], fill=GOLD_HI, width=4)
    d.ellipse([P(tv)[0] - 6, P(tv)[1] - 6, P(tv)[0] + 6, P(tv)[1] + 6], fill=GOLD_HI)
frame(d)
save(img, "smatrix.jpg")

# 5. swalk: jalur random walk
img = canvas()
d = ImageDraw.Draw(img)
grid(d)
rng = np.random.RandomState(11)
for p in range(7):
    x, y = W / 2, H / 2
    pts = [(x, y)]
    for _ in range(600):
        a = rng.uniform(0, 2 * math.pi)
        x += 9 * math.cos(a)
        y += 9 * math.sin(a)
        x = min(max(x, 40), W - 40)
        y = min(max(y, 80), H - 60)
        pts.append((x, y))
    d.line(pts, fill=GOLD_DIM if p else GOLD, width=2)
frame(d)
save(img, "swalk.jpg")

# 6. sdblpend: pendulum ganda + jejak
img = canvas()
d = ImageDraw.Draw(img)
grid(d)
ax, ay = W / 2, 240
a1, a2 = 0.9, 2.2
b1 = (ax + 190 * math.sin(a1), ay + 190 * math.cos(a1))
b2 = (b1[0] + 190 * math.sin(a1 + a2), b1[1] + 190 * math.cos(a1 + a2))
d.ellipse([ax - 9, ay - 9, ax + 9, ay + 9], fill=GOLD_DIM)
d.line([(ax, ay), b1], fill=GOLD, width=5)
d.line([b1, b2], fill=GOLD_HI, width=5)
d.ellipse([b1[0] - 13, b1[1] - 13, b1[0] + 13, b1[1] + 13], fill=GOLD)
d.ellipse([b2[0] - 15, b2[1] - 15, b2[0] + 15, b2[1] + 15], fill=GOLD_HI)
# jejak chaos: titik-titik melengkung
for k in range(40):
    aa = 2.2 + 0.16 * math.sin(k * 0.45)
    px = b1[0] + 190 * math.sin(a1 + aa) + 150 * math.sin(k * 0.31)
    py = b1[1] + 190 * math.cos(a1 + aa) + 120 * math.cos(k * 0.27)
    d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=GOLD_DIM)
frame(d)
save(img, "sdblpend.jpg")

# 7. sdrag: dua parabola (vakum vs hambatan)
img = canvas()
d = ImageDraw.Draw(img)
grid(d)
vac = [(x, H - 140 - 1.15 * (x - 60) + 0.00215 * (x - 60) ** 2) for x in range(60, W - 60, 4)]
d.line(vac, fill=GOLD_DIM, width=2)
for x, y in vac[::12]:
    d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=GOLD_DIM)
d.line([(x, y + 40) for x, y in vac], fill=GOLD, width=4)
d.line([(40, H - 140), (W - 40, H - 140)], fill=GOLD_DIM, width=3)
frame(d)
save(img, "sdrag.jpg")

# 8. skepler: elips + fokus + swept area
img = canvas()
d = ImageDraw.Draw(img)
grid(d)
cx, cy = W / 2, H / 2 + 20
a, b, ecc = 200, 130, 0.6
fx = cx - a * ecc
d.ellipse([cx - a, cy - b, cx + a, cy + b], outline=GOLD, width=4)
d.ellipse([fx - 9, cy - 9, fx + 9, cy + 9], fill=GOLD_HI)
pts = [(cx + a * math.cos(t), cy + b * math.sin(t)) for t in np.linspace(0.15, 1.5, 40)]
d.polygon([(fx, cy)] + pts, fill=(70, 56, 26))
d.ellipse([cx + a * math.cos(0.8) - 8, cy + b * math.sin(0.8) - 8,
           cx + a * math.cos(0.8) + 8, cy + b * math.sin(0.8) + 8], fill=GOLD)
frame(d)
save(img, "skepler.jpg")

# 9. sslit: frinje interferensi dgn envelope
img = canvas()
d = ImageDraw.Draw(img)
grid(d, 40)
for x in range(60, W - 60, 3):
    t = (x - W / 2) / 220
    env = math.exp(-(t ** 2) * 2.2)
    fr = (math.cos(t * 26) ** 2)
    I = env * fr
    d.line([(x, H / 2 - 210 * I), (x, H / 2 + 40)], fill=GOLD if I > 0.55 else GOLD_DIM, width=3)
    d.ellipse([x - 2, H / 2 - 210 * I - 2, x + 2, H / 2 - 210 * I + 2], fill=GOLD_HI)
d.line([(60, H / 2 + 40), (W - 60, H / 2 + 40)], fill=GOLD_DIM, width=3)
frame(d)
save(img, "sslit.jpg")

# 10. sschrod: paket gelombang + barrier
img = canvas()
d = ImageDraw.Draw(img)
grid(d)
bx0, bx1 = W * 0.58, W * 0.66
for x in range(40, W - 40, 2):
    t = (x - W * 0.28) / 150
    pk = math.exp(-(t ** 2)) * math.cos(x * 0.22) * 0.5 + math.exp(-(t ** 2)) * 0.5
    y = H * 0.52 - 240 * max(pk, 0)
    d.line([(x, y), (x + 2, y)], fill=GOLD, width=2)
d.rectangle([bx0, H * 0.52 - 130, bx1, H * 0.52 + 90], fill=(70, 56, 26), outline=GOLD_HI, width=2)
d.text((44, 70), "|psi|^2", fill=GOLD_DIM)
frame(d)
save(img, "sschrod.jpg")

print("DONE ->", OUT)
