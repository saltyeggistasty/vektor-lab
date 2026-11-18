# -*- coding: utf-8 -*-
# Art placeholder 15 graphing tool — motif spesifik, gold-dark.
# Output: menu_screen/graph_card_art/<id>.jpg (600x960)
import cmath
import math
import os
import random

from PIL import Image, ImageDraw

OUT = r"G:\vektor-lab(1)\vektor-lab\menu_screen\graph_card_art"
os.makedirs(OUT, exist_ok=True)
W, H = 600, 960
GOLD = (224, 176, 74)
GOLD_DIM = (140, 108, 48)
GOLD_HI = (255, 214, 140)
BG = (10, 13, 20)


def canvas():
    return Image.new("RGB", (W, H), BG)


def frame(d):
    d.rectangle([16, 16, W - 16, H - 16], outline=GOLD_DIM, width=2)


def save(img, name):
    img.save(os.path.join(OUT, name), "JPEG", quality=88)
    print(name, os.path.getsize(OUT and os.path.join(OUT, name)), "bytes")


def hsv(h, s, v):
    i0 = int(h * 6) % 6
    f = h * 6 - int(h * 6)
    q = v * (1 - s * f)
    t = v * (1 - s * (1 - f))
    return [(v, t, 0), (q, v, 0), (0, v, t), (0, q, v), (t, 0, v), (v, 0, q)][i0]


# 1. gdomain: domain coloring asli f(z) = (z^2-1)/(z^2+1)... pakai 1/(z^3-1)
img = canvas()
px = img.load()
R = 2.2
for py in range(H):
    for pxc in range(W):
        x = (pxc / W - 0.5) * 2 * R
        y = (0.5 - py / H) * 2 * R
        z = complex(x, y)
        try:
            w = 1 / (z**3 - 1)
        except ZeroDivisionError:
            w = complex(1e9)
        mag = math.log(1 + abs(w))
        hue = ((cmath.phase(w) + math.pi) / (2 * math.pi)) % 1
        v = max(0.15, min(1.0, 0.35 + 0.65 * min(mag, 1.5) / 1.5))
        r, g, b = hsv(hue, 0.85, v)
        px[pxc, py] = (int(r * 255), int(g * 255), int(b * 255))
d = ImageDraw.Draw(img)
frame(d)
save(img, "gdomain.jpg")

# 2. gfractal: mandelbrot escape
img = canvas()
px = img.load()
R = 1.6
for py in range(0, H):
    for pxc in range(0, W):
        x = (pxc / W - 0.42) * 2 * R
        y = (0.55 - py / H) * 2 * R
        zx = zy = 0
        n = 0
        while n < 90 and zx * zx + zy * zy <= 16:
            zx, zy = zx * zx - zy * zy + x, 2 * zx * zy + y
            n += 1
        if n >= 90:
            px[pxc, py] = (8, 8, 14)
        else:
            t = n / 90
            r, g, b = hsv(0.62 - 0.85 * math.sqrt(t), 0.85, 0.35 + 0.65 * math.sqrt(t))
            px[pxc, py] = (int(r * 255), int(g * 255), int(b * 255))
d = ImageDraw.Draw(img)
frame(d)
save(img, "gfractal.jpg")

# 3. gsurf3d: wireframe permukaan 3D
img = canvas()
d = ImageDraw.Draw(img)
CX, CY = W / 2, H / 2 + 30
def proj(x, y, z):
    t = 0.5
    sx2 = x * math.cos(0.6) - y * math.sin(0.6)
    sy2 = x * math.sin(0.6) + y * math.cos(0.6)
    return (CX + sx2 * 55, CY - (z * 55) * t - sy2 * 28)
for i in range(24):
    pts = [proj(-2 + 4 * i / 23, -2 + 4 * j / 23, math.sin(-2 + 4 * i / 23) * math.cos(2 * (-2 + 4 * j / 23)))
           for j in range(24)]
    d.line(pts, fill=GOLD_DIM, width=1)
for j in range(24):
    pts = [proj(-2 + 4 * i / 23, -2 + 4 * j / 23, math.sin(-2 + 4 * i / 23) * math.cos(2 * (-2 + 4 * j / 23)))
           for i in range(24)]
    d.line(pts, fill=GOLD_DIM, width=1)
d.line([proj(-1, 0, 1), proj(1, 0, 1)], fill=GOLD_HI, width=3)
frame(d)
save(img, "gsurf3d.jpg")

# 4. gfrenet: heliks + frame T N B
img = canvas()
d = ImageDraw.Draw(img)
pts = []
for i in range(300):
    t = i / 300 * 4 * math.pi
    x, y, z = 150 * math.cos(t), 150 * math.sin(t), (t / (4 * math.pi) - 0.5) * 700
    sxp = W / 2 + x * math.cos(0.5) - y * math.sin(0.5)
    syp = H / 2 - z * 0.9 - (x * math.sin(0.5) + y * math.cos(0.5)) * 0.35
    pts.append((sxp, syp))
d.line(pts, fill=GOLD, width=3)
t0 = 2.4
x0, y0, z0 = 150 * math.cos(t0), 150 * math.sin(t0), (t0 / (4 * math.pi) - 0.5) * 700
sx0 = W / 2 + x0 * math.cos(0.5) - y0 * math.sin(0.5)
sy0 = H / 2 - z0 * 0.9 - (x0 * math.sin(0.5) + y0 * math.cos(0.5)) * 0.35
d.line([(sx0, sy0), (sx0 + 60, sy0 - 20)], fill=(159, 216, 159), width=4)
d.line([(sx0, sy0), (sx0 - 20, sy0 + 60)], fill=(127, 180, 216), width=4)
d.line([(sx0, sy0), (sx0 + 20, sy0 - 70)], fill=(216, 127, 127), width=4)
frame(d)
save(img, "gfrenet.jpg")

# 5. gtrans3d: kubus transformasi
img = canvas()
d = ImageDraw.Draw(img)
M = [[1.4, 0.6, 0], [0.2, 1.2, 0.5], [0, 0.3, 1.3]]
verts = []
for i in range(8):
    v = [i & 1 and 1 or -1, i & 2 and 1 or -1, i & 4 and 1 or -1]
    tv = [sum(M[r][c] * v[c] for c in range(3)) for r in range(3)]
    verts.append((W / 2 + tv[0] * 80, H / 2 - tv[1] * 80 + tv[2] * 20))
E = [(0, 1), (0, 2), (1, 3), (2, 3), (4, 5), (4, 6), (5, 7), (6, 7), (0, 4), (1, 5), (2, 6), (3, 7)]
d.line([verts[0], verts[3], verts[5], verts[6], verts[0]], fill=GOLD_DIM, width=1)
for a, b in E:
    d.line([verts[a], verts[b]], fill=GOLD, width=2)
for col, v in ((GOLD_HI, [1, 0, 0]), ((159, 216, 159), [0, 1, 0]), ((127, 180, 216), [0, 0, 1])):
    tv = [sum(M[r][c] * v[c] for c in range(3)) for r in range(3)]
    d.line([(W / 2, H / 2), (W / 2 + tv[0] * 80, H / 2 - tv[1] * 80 + tv[2] * 20)], fill=col, width=4)
frame(d)
save(img, "gtrans3d.jpg")

# 6. gslope: slope field
img = canvas()
d = ImageDraw.Draw(img)
rng = random.Random(3)
for gy in range(16):
    for gx in range(15):
        x = -7 + gx * 14 / 15
        y = -8 + gy * 16 / 15
        m = x - y
        ang = math.atan2(m, 1)
        L = 26
        cxp, cyp = 45 + gx * (W - 90) / 14, 60 + gy * (H - 120) / 15
        d.line([(cxp - L * math.cos(ang), cyp - L * math.sin(ang)),
                (cxp + L * math.cos(ang), cyp + L * math.sin(ang))], fill=GOLD_DIM, width=2)
d.line([(80, H / 2), (W - 80, H / 2)], fill=GOLD, width=2)
frame(d)
save(img, "gslope.jpg")

# 7. gdist: kurva distribusi + area
img = canvas()
d = ImageDraw.Draw(img)
mu, sd = 0, 1.2
pts = []
for i in range(240):
    x = -4 + 8 * i / 239
    y = math.exp(-((x - mu) ** 2) / (2 * sd * sd)) / (sd * math.sqrt(2 * math.pi))
    pts.append((40 + (x + 4) / 8 * (W - 80), H - 180 - y * 700))
d.line(pts, fill=GOLD, width=3)
area = [p for p in pts if p[0] > W / 2 - 90 and p[0] < W / 2 + 90]
d.polygon(area + [(area[-1][0], H - 180), (area[0][0], H - 180)], fill=(224, 176, 74, 60))
d.line([(40, H - 180), (W - 40, H - 180)], fill=GOLD_DIM, width=2)
frame(d)
save(img, "gdist.jpg")

# 8. ggraphalgo: graf + node
img = canvas()
d = ImageDraw.Draw(img)
rng = random.Random(11)
nodes = [(90 + rng.next() if hasattr(rng, "next") else rng.random(), 0) for _ in range(0)]
nodes = []
for i in range(10):
    nodes.append((80 + rng.random() * (W - 160), 120 + rng.random() * (H - 260)))
edges = []
for i in range(10):
    for j in range(i + 1, 10):
        if rng.random() < 0.3:
            edges.append((i, j))
edges.append((0, 1)); edges.append((1, 4)); edges.append((4, 8)); edges.append((0, 3))
mst = {(0, 1), (1, 4), (4, 8), (0, 3), (3, 6)}
for a, b in edges:
    col = GOLD_HI if (a, b) in mst else GOLD_DIM
    d.line([nodes[a], nodes[b]], fill=col, width=4 if (a, b) in mst else 2)
for i, (x, y) in enumerate(nodes):
    d.ellipse([x - 14, y - 14, x + 14, y + 14], fill=GOLD if i in (0, 9) else (30, 26, 18),
              outline=GOLD_DIM, width=2)
    d.text((x - 4, y - 7), chr(65 + i), fill=(20, 20, 20))
frame(d)
save(img, "ggraphalgo.jpg")

# 9. gfield: medan muatan
img = canvas()
d = ImageDraw.Draw(img)
charges = [(W * 0.35, H * 0.42, 1), (W * 0.65, H * 0.58, -1)]
for gy in range(0, H, 34):
    for gx in range(0, W, 34):
        ex = ey = 0.0
        for cx2, cy2, q in charges:
            dx, dy = gx - cx2, gy - cy2
            r2 = dx * dx + dy * dy + 50
            ex += q * dx / r2 ** 1.5
            ey += q * dy / r2 ** 1.5
        m = math.hypot(ex, ey)
        if m < 1e-6:
            continue
        L = min(26, 14 * math.log(1 + m * 50))
        d.line([(gx - ex / m * L / 2, gy - ey / m * L / 2),
                (gx + ex / m * L / 2, gy + ey / m * L / 2)], fill=GOLD_DIM, width=1)
for cx2, cy2, q in charges:
    col = (216, 127, 127) if q > 0 else (127, 180, 216)
    d.ellipse([cx2 - 15, cy2 - 15, cx2 + 15, cy2 + 15], fill=col, outline=GOLD, width=2)
frame(d)
save(img, "gfield.jpg")

# 10. gpvcycle: loop P-V
img = canvas()
d = ImageDraw.Draw(img)
gamma = 1.4
V1, V2 = 1.0, 0.28
P1 = 1.0
P2 = P1 * (V1 / V2) ** gamma
P3 = P2 * 1.7
P4 = P3 * (V2 / V1) ** gamma
pts = []
for i in range(80):
    V = V1 * (V2 / V1) ** (i / 79)
    pts.append((V, P1 * (V1 / V) ** gamma))
for i in range(30):
    pts.append((V2, P2 + (P3 - P2) * i / 29))
for i in range(80):
    V = V2 * (V1 / V2) ** (i / 79)
    pts.append((V, P3 * (V2 / V) ** gamma))
for i in range(20):
    pts.append((V1, P4 - (P4 - P1) * i / 19))
scr = [(40 + (p[0] - 0.2) * (W - 100) / 1.1, H - 150 - (p[1] - 0.8) * 260) for p in pts]
d.line(scr, fill=GOLD, width=4)
d.ellipse([scr[0][0] - 7, scr[0][1] - 7, scr[0][0] + 7, scr[0][1] + 7], fill=GOLD_HI)
d.line([(40, H - 150), (W - 40, H - 150)], fill=GOLD_DIM, width=2)
frame(d)
save(img, "gpvcycle.jpg")

# 11. gising: lattice spin
img = canvas()
px = img.load()
rng = random.Random(5)
N = 96
for j in range(H):
    for i in range(W):
        s = 1 if rng.random() < 0.5 else -1
        px[i, j] = (224, 176, 74) if s > 0 else (35, 30, 40)
d = ImageDraw.Draw(img)
d.text((20, 20), "T = 2.27", fill=(20, 18, 14))
frame(d)
save(img, "gising.jpg")

# 12. gminkowski: kerucut + sumbu primed
img = canvas()
d = ImageDraw.Draw(img)
cx, cy = W / 2, H / 2
d.line([(cx - 280, cy + 200), (cx + 280, cy - 200)], fill=(127, 180, 216), width=3)
d.line([(cx - 280, cy - 200), (cx + 280, cy + 200)], fill=(127, 180, 216), width=3)
d.line([(cx, cy - 300), (cx, cy + 300)], fill=GOLD_DIM, width=2)
d.line([(cx - 300, cy), (cx + 300, cy)], fill=GOLD_DIM, width=2)
d.polygon([(cx, cy), (cx + 160, cy - 260), (cx - 160, cy - 260)], outline=GOLD_HI)
for t in range(-6, 7):
    x = t * 0.12
    ct = math.sqrt(1 + x * x)
    d.ellipse([cx + x * 260 - 4, cy - ct * 230 - 4, cx + x * 260 + 4, cy - ct * 230 + 4], fill=GOLD)
frame(d)
save(img, "gminkowski.jpg")

# 13. gfluid: swirl tinta
img = canvas()
px = img.load()
cx, cy = W * 0.4, H * 0.5
for j in range(H):
    for i in range(W):
        dx, dy = i - cx, j - cy
        r2 = dx * dx + dy * dy
        ang = math.atan2(dy, dx) + 6.0 / (1 + r2 / 9000)
        v = math.exp(-r2 / 90000) * 1.4 + 0.06
        r, g, b = hsv(0.1 + 0.06 * math.sin(ang * 2), 0.75, min(1, v))
        px[i, j] = (int(r * 120), int(g * 100), int(b * 80))
d = ImageDraw.Draw(img)
frame(d)
save(img, "gfluid.jpg")

# 14. ggeodesic: pembelokan cahaya
img = canvas()
d = ImageDraw.Draw(img)
cx, cy = W * 0.62, H * 0.55
d.ellipse([cx - 55, cy - 55, cx + 55, cy + 55], fill=(0, 0, 0), outline=(216, 127, 127), width=3)
d.ellipse([cx - 82, cy - 82, cx + 82, cy + 82], outline=GOLD_DIM, width=1)
for b in (90, 120, 160, 210, 270):
    pts = []
    for i in range(300):
        t = i / 299 * 2 * math.pi
        rr = b * (1 + 0.55 / (1 + 0.6 * abs(math.sin(t))))
        pts.append((cx + rr * math.cos(t + math.pi), cy + rr * math.sin(t + math.pi) * 0.85))
    d.line(pts, fill=GOLD_DIM if b != 160 else GOLD, width=2)
frame(d)
save(img, "ggeodesic.jpg")

# 15. gray: sinar melewati 2 lensa
img = canvas()
d = ImageDraw.Draw(img)
L1x, L2x = W * 0.35, W * 0.68
cy = H * 0.45
for lx, f, col in ((L1x, 150, (159, 216, 159)), (L2x, -150, (216, 159, 159))):
    d.line([(lx, cy - 110), (lx, cy + 110)], fill=col, width=4)
d.line([(30, cy), (W - 30, cy)], fill=GOLD_DIM, width=2)
for i in range(7):
    y0 = -100 + 200 * i / 6
    d.line([(30, cy + y0), (L1x, cy + y0)], fill=GOLD, width=2)
    ang = -y0 / 150
    y1 = y0 + ang * (L2x - L1x)
    d.line([(L1x, cy + y0), (L2x, cy + y1)], fill=GOLD, width=2)
    ang2 = ang + y1 / 150
    d.line([(L2x, cy + y1), (W - 30, cy + y1 + ang2 * (W - 30 - L2x))], fill=GOLD, width=2)
frame(d)
save(img, "gray.jpg")

print("DONE ->", OUT)
