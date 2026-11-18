# Generator cover art placeholder untuk Nabla Lab (bisa diganti pemilik web).
# Palet emas gelap senada dgn menu war; emblem geometris per tool.
import math
import os

from PIL import Image, ImageDraw

W, H = 640, 400
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "menu_screen")

GOLD = (224, 176, 74)
GOLD_HI = (250, 226, 140)
BG_TOP = (10, 13, 20)
BG_BOT = (24, 18, 10)


def base(name, hue=(10, 13, 20), hue2=(24, 18, 10)):
    img = Image.new("RGB", (W, H))
    px = img.load()
    for y in range(H):
        t = y / (H - 1)
        px_row = tuple(int(hue[i] + (hue2[i] - hue[i]) * t) for i in range(3))
        for x in range(W):
            px[x, y] = px_row
    d = ImageDraw.Draw(img)
    # grid tipis ala lab
    for gx in range(0, W, 40):
        d.line([(gx, 0), (gx, H)], fill=(255, 255, 255, 12), width=1)
    for gy in range(0, H, 40):
        d.line([(0, gy), (W, gy)], fill=(255, 255, 255, 12), width=1)
    return img, d


def glow_line(d, pts, color=GOLD, w=4):
    d.line(pts, fill=tuple(int(c * 0.35) for c in color), width=w + 8)
    d.line(pts, fill=color, width=w)


def save(img, name):
    img.save(os.path.join(OUT, name), "JPEG", quality=88)
    print("art:", name)


def art_integral():
    img, d = base("i")
    # kurva sin + luas area (fill) di bawah kurva
    pts = [(x, 200 - 90 * math.sin((x - W / 2) / 90)) for x in range(40, W - 39, 6)]
    area = pts + [(W - 40, H - 80), (40, H - 80)]
    d.polygon(area, fill=(224, 176, 74, 60))
    glow_line(d, pts, GOLD_HI, 5)
    d.rectangle([38, 78, 42, H - 82], fill=GOLD)
    d.rectangle([W - 42, 78, W - 38, H - 82], fill=GOLD)
    save(img, "lab_integral.jpg")


def art_matrix():
    img, d = base("m")
    # bracket + grid sel
    d.rectangle([120, 90, 150, 310], outline=GOLD, width=6)
    d.rectangle([W - 150, 90, W - 120, 310], outline=GOLD, width=6)
    for r in range(3):
        for c in range(3):
            x0, y0 = 190 + c * 90, 115 + r * 70
            v = 0.35 + ((r * 3 + c) % 5) / 6
            col = tuple(int(GOLD[0] * v + 40) for _ in range(1)) * 1
            col = (int(40 + GOLD[0] * v * 0.5), int(30 + GOLD[1] * v * 0.5), int(20 + GOLD[2] * v * 0.4))
            d.rectangle([x0, y0, x0 + 70, y0 + 50], fill=col, outline=(60, 50, 30))
    save(img, "lab_matrix.jpg")


def art_ode():
    img, d = base("o")
    # keluarga kurva eksponensial
    for k in (-1.2, -0.6, 0.3, 0.9):
        pts = [(x, 220 - 120 * math.exp(k * (x - W / 2) / 120) + k * 20)
               for x in range(30, W - 29, 6)]
        pts = [(x, max(20, min(H - 20, y))) for x, y in pts]
        glow_line(d, pts, GOLD if k < 0.5 else GOLD_HI, 3)
    save(img, "lab_ode.jpg")


def art_stats():
    img, d = base("s")
    # bar chart + kurva lonceng
    hs = [90, 150, 220, 170, 120, 200, 140]
    bw = 52
    for i, h in enumerate(hs):
        x0 = 60 + i * (bw + 18)
        d.rectangle([x0, H - 90 - h, x0 + bw, H - 90],
                    fill=(60, 46, 22), outline=GOLD, width=3)
    pts = [(x, H - 100 - 180 * math.exp(-((x - W / 2) ** 2) / (2 * 130 ** 2)))
           for x in range(50, W - 49, 6)]
    glow_line(d, pts, GOLD_HI, 4)
    save(img, "lab_stats.jpg")


def art_umb_stats():
    img, d = base("us")
    # dadu + distribusi
    d.ellipse([80, 120, 240, 280], outline=GOLD, width=6)
    for (cx, cy) in [(130, 170), (190, 230), (160, 200)]:
        d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=GOLD)
    pts = [(x, 240 - 130 * math.exp(-((x - 460) ** 2) / (2 * 90 ** 2)))
           for x in range(330, W - 29, 5)]
    glow_line(d, pts, GOLD_HI, 5)
    save(img, "lab_umb_stats.jpg")


def art_thermo():
    img, d = base("t", (26, 10, 8), (20, 8, 4))
    # termometer + gradien panas
    d.rectangle([180, 80, 240, 280], outline=GOLD, width=6)
    d.ellipse([160, 260, 260, 340], outline=GOLD, width=6)
    d.rectangle([196, 140, 224, 300], fill=(200, 60, 30))
    d.ellipse([180, 280, 240, 320], fill=(200, 60, 30))
    for i in range(5):
        x0 = 340 + i * 46
        y0 = 200 - 60 + i * 12
        d.arc([x0, y0, x0 + 90, y0 + 90], 300, 60, fill=GOLD, width=5)
    save(img, "lab_thermo.jpg")


def art_qm():
    img, d = base("q", (8, 12, 22), (14, 10, 26))
    # orbit atom
    cx, cy = W // 2, H // 2
    for ang in (0, 60, 120):
        a = math.radians(ang)
        rx, ry = 170, 62
        bbox = [cx - rx, cy - ry, cx + rx, cy + ry]
        rot = img.copy().rotate(0)
        # elips manual dgn transformasi titik
        pts = [(cx + rx * math.cos(t) * math.cos(a) - ry * math.sin(t) * math.sin(a),
                cy + rx * math.cos(t) * math.sin(a) + ry * math.sin(t) * math.cos(a))
               for t in [i * 0.05 for i in range(126)]]
        d.line(pts, fill=GOLD, width=4)
    d.ellipse([cx - 18, cy - 18, cx + 18, cy + 18], fill=GOLD_HI)
    save(img, "lab_qm.jpg")


def art_es():
    img, d = base("e")
    # medan radial dari muatan
    cx, cy = W // 2, H // 2
    d.ellipse([cx - 26, cy - 26, cx + 26, cy + 26], fill=(200, 60, 40), outline=GOLD_HI, width=4)
    for i in range(12):
        a = i * math.pi / 6
        x1, y1 = cx + 40 * math.cos(a), cy + 40 * math.sin(a)
        x2, y2 = cx + 190 * math.cos(a), cy + 190 * math.sin(a)
        d.line([(x1, y1), (x2, y2)], fill=GOLD, width=3)
        d.polygon([(x2, y2),
                   (x2 - 12 * math.cos(a - 0.4), y2 - 12 * math.sin(a - 0.4)),
                   (x2 - 12 * math.cos(a + 0.4), y2 - 12 * math.sin(a + 0.4))], fill=GOLD)
    save(img, "lab_es.jpg")


def art_rel():
    img, d = base("r", (6, 8, 18), (10, 8, 22))
    # kerucut cahaya: garis diagonal dari pusat + grid lengkung
    cx, cy = W // 2, H // 2
    d.line([(cx, cy), (40, 40)], fill=GOLD, width=5)
    d.line([(cx, cy), (W - 40, 40)], fill=GOLD, width=5)
    d.line([(cx, cy), (40, H - 40)], fill=(120, 90, 50), width=5)
    d.line([(cx, cy), (W - 40, H - 40)], fill=(120, 90, 50), width=5)
    for rr in (90, 170, 250):
        d.arc([cx - rr, cy - rr, cx + rr, cy + rr], 180, 360, fill=(150, 120, 70), width=3)
    d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=GOLD_HI)
    save(img, "lab_rel.jpg")


def art_umb_rel():
    img, d = base("ur", (6, 8, 18), (12, 8, 24))
    # kelingking spacetime: grid melengkung ke massa
    for i in range(7):
        y0 = 80 + i * 44
        pts = [(x, y0 + int(60 * math.exp(-((x - W / 2) ** 2) / (2 * 120 ** 2))))
               for x in range(0, W + 1, 8)]
        d.line(pts, fill=(90, 75, 45), width=2)
    d.ellipse([W // 2 - 44, H // 2 - 20, W // 2 + 44, H // 2 + 64], fill=GOLD)
    save(img, "lab_umb_rel.jpg")


def art_proj():
    img, d = base("p")
    # lintasan parabola + tanah + meriam kecil
    d.line([(0, H - 80), (W, H - 80)], fill=(90, 70, 40), width=4)
    pts = [(x, H - 80 - (4 * 200 / (300 ** 2)) * x * (300 - x))
           for x in range(0, 301, 6)]
    glow_line(d, pts, GOLD_HI, 5)
    for (px, py) in pts[::8]:
        d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=GOLD)
    d.rectangle([30, H - 110, 60, H - 80], fill=GOLD)
    save(img, "lab_proj.jpg")


def art_umb_newton():
    img, d = base("un")
    # apel + panah gaya
    d.ellipse([120, 150, 300, 330], outline=GOLD, width=6)
    d.line([(210, 150), (210, 120)], fill=(90, 130, 60), width=8)
    d.line([(360, 160), (360, 320)], fill=GOLD_HI, width=6)
    d.polygon([(360, 340), (348, 316), (372, 316)], fill=GOLD_HI)
    save(img, "lab_umb_newton.jpg")


def art_hydro():
    img, d = base("h", (6, 14, 20), (8, 20, 26))
    # gelombang berlapis
    for k in range(4):
        pts = [(x, 140 + k * 60 + 26 * math.sin(x / 46 + k))
               for x in range(0, W + 1, 6)]
        glow_line(d, pts, GOLD if k % 2 else GOLD_HI, 4)
    save(img, "lab_hydro.jpg")


def art_umb_hydro():
    img, d = base("uh", (6, 14, 20), (8, 22, 30))
    # tetesan + riak
    cx, cy = W // 2, 150
    d.ellipse([cx - 30, cy - 44, cx + 30, cy + 44], fill=(40, 90, 110), outline=GOLD_HI, width=4)
    d.polygon([(cx - 22, cy - 20), (cx, cy - 70), (cx + 22, cy - 20)], fill=(40, 90, 110))
    for rr in (60, 110, 170, 240):
        d.arc([cx - rr, cy - rr * 0.4, cx + rr, cy + rr * 0.4], 0, 180, fill=GOLD, width=3)
    save(img, "lab_umb_hydro.jpg")


# ---------- gelombang 2 ----------

def art_complex():
    img, d = base("cx", (10, 8, 24), (18, 10, 30))
    # bidang kompleks: sumbu + titik + spiral arg
    d.line([(60, H - 60), (W - 60, H - 60)], fill=(90, 75, 45), width=3)
    d.line([(80, 50), (80, H - 40)], fill=(90, 75, 45), width=3)
    cx, cy = W // 2, H // 2
    pts = [(cx + 150 * (t / 240) * math.cos(t / 26),
            cy + 150 * (t / 240) * math.sin(t / 26))
           for t in range(0, 240, 4)]
    glow_line(d, pts, GOLD_HI, 4)
    d.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], fill=GOLD)
    save(img, "lab_complex.jpg")


def art_umb_complex():
    img, d = base("ucx", (10, 8, 24), (16, 10, 28))
    for rr in (70, 130, 190):
        d.ellipse([W // 2 - rr, H // 2 - rr, W // 2 + rr, H // 2 + rr], outline=(110, 90, 50), width=2)
    d.line([(40, H // 2), (W - 40, H // 2)], fill=GOLD, width=3)
    d.line([(W // 2, 40), (W // 2, H - 40)], fill=GOLD, width=3)
    d.ellipse([W // 2 + 90 - 12, H // 2 - 92 - 12, W // 2 + 90 + 12, H // 2 - 92 + 12], fill=GOLD_HI)
    save(img, "lab_umb_complex.jpg")


def art_taylor():
    img, d = base("ty")
    # kurva + aproksimasi polinomial
    true_pts = [(x, 250 - 110 * math.sin((x - W / 2) / 110) - (x - W / 2) / 8)
                for x in range(40, W - 39, 5)]
    approx_pts = [(x, 250 - 110 * ((x - W / 2) / 110 - ((x - W / 2) / 110) ** 3 / 6))
                  for x in range(40, W - 39, 5)]
    d.line([(0, 250), (W, 250)], fill=(90, 75, 45), width=2)
    glow_line(d, true_pts, GOLD, 3)
    glow_line(d, approx_pts, GOLD_HI, 3)
    save(img, "lab_taylor.jpg")


def art_umb_real():
    img, d = base("ur")
    # epsilon-delta: kurva + pita
    pts = [(x, 200 + 60 * math.sin(x / 55)) for x in range(40, W - 39, 5)]
    d.line([(40, 200 + 60 * math.sin(40 / 55)) - None if False else (40, 260), (W - 40, 140)],
           fill=(90, 75, 45), width=2)
    glow_line(d, pts, GOLD_HI, 4)
    d.rectangle([40, 150, W - 40, 250], outline=(150, 120, 70), width=2)
    save(img, "lab_umb_real.jpg")


def art_modmath():
    img, d = base("md")
    # lingkaran modular (jam mod 12) + titik
    cx, cy = W // 2, H // 2
    d.ellipse([cx - 140, cy - 140, cx + 140, cy + 140], outline=GOLD, width=5)
    for i in range(12):
        a = i * math.pi / 6
        x, y = cx + 140 * math.cos(a), cy + 140 * math.sin(a)
        d.ellipse([x - 8, y - 8, x + 8, y + 8], fill=GOLD_HI)
    d.line([(cx + 140 * math.cos(0.3), cy + 140 * math.sin(0.3)),
            (cx + 140 * math.cos(2.2), cy + 140 * math.sin(2.2))], fill=GOLD_HI, width=3)
    d.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=GOLD)
    save(img, "lab_modmath.jpg")


def art_umb_discrete():
    img, d = base("ud")
    # graf titik-garis (node graph)
    nodes = [(120, 110), (320, 80), (520, 130), (180, 280), (420, 300), (560, 250)]
    edges = [(0, 1), (1, 2), (0, 3), (1, 4), (2, 5), (3, 4), (4, 5), (1, 3)]
    for a, b in edges:
        d.line([nodes[a], nodes[b]], fill=(110, 90, 50), width=3)
    for (x, y) in nodes:
        d.ellipse([x - 16, y - 16, x + 16, y + 16], fill=GOLD, outline=GOLD_HI, width=3)
    save(img, "lab_umb_discrete.jpg")


def art_entropy():
    img, d = base("en")
    # bar entropi: acak vs rapi
    hs = [150, 40, 190, 90, 240, 60, 170, 110]
    for i, h in enumerate(hs):
        x0 = 50 + i * 66
        d.rectangle([x0, H - 90 - h, x0 + 44, H - 90],
                    fill=(50 + i * 12, 40 + i * 8, 22), outline=GOLD, width=3)
    pts = [(x, 90 + 24 * math.sin(x / 18) * math.exp(-x / 500))
           for x in range(0, W, 5)]
    d.line(pts, fill=GOLD_HI, width=3)
    save(img, "lab_entropy.jpg")


def art_umb_info():
    img, d = base("ui")
    # bit stream 0/1
    for i in range(6):
        y0 = 70 + i * 52
        for j in range(14):
            x0 = 40 + j * 42
            ch = "1" if (i * 7 + j * 3) % 3 else "0"
            if ch == "1":
                d.rectangle([x0, y0, x0 + 26, y0 + 26], fill=GOLD)
            else:
                d.rectangle([x0, y0, x0 + 26, y0 + 26], outline=(120, 95, 55), width=2)
    save(img, "lab_umb_info.jpg")


def art_poly():
    img, d = base("pl")
    # kurva kubik + akar-akarnya di sumbu
    d.line([(0, H // 2), (W, H // 2)], fill=(90, 75, 45), width=3)
    pts = []
    for x in range(40, W - 39, 5):
        t = (x - W / 2) / 90
        y = H // 2 - 120 * (t ** 3 - 3 * t) / 3
        pts.append((x, max(20, min(H - 20, y))))
    glow_line(d, pts, GOLD_HI, 4)
    for rx in (W // 2 - 156, W // 2, W // 2 + 156):
        d.ellipse([rx - 9, H // 2 - 9, rx + 9, H // 2 + 9], fill=GOLD)
    save(img, "lab_poly.jpg")


def art_schwartz():
    img, d = base("sw", (5, 5, 12), (10, 8, 18))
    # lubang hitam + cincin akresi
    cx, cy = W // 2, H // 2
    d.ellipse([cx - 130, cy - 110, cx + 130, cy + 110], outline=GOLD, width=6)
    d.ellipse([cx - 90, cy - 74, cx + 90, cy + 74], outline=(180, 140, 80), width=4)
    d.ellipse([cx - 46, cy - 36, cx + 46, cy + 36], fill=(0, 0, 0), outline=GOLD_HI, width=3)
    save(img, "lab_schwartz.jpg")


def art_umb_gr():
    img, d = base("ugr", (5, 5, 12), (12, 8, 20))
    # grid spacetime dua arah melengkung
    for i in range(6):
        x0 = 60 + i * 90
        pts = [(x0 + int(50 * math.exp(-((y - H // 2) ** 2) / (2 * 100 ** 2))), y)
               for y in range(0, H + 1, 8)]
        d.line(pts, fill=(90, 75, 45), width=2)
    for i in range(6):
        y0 = 50 + i * 60
        pts = [(x, y0 + int(50 * math.exp(-((x - W // 2) ** 2) / (2 * 100 ** 2))))
               for x in range(0, W + 1, 8)]
        d.line(pts, fill=(90, 75, 45), width=2)
    d.ellipse([W // 2 - 34, H // 2 - 34, W // 2 + 34, H // 2 + 34], fill=GOLD)
    save(img, "lab_umb_gr.jpg")


def art_optics():
    img, d = base("op", (8, 10, 18), (10, 14, 24))
    # prisma + berkas dibiaskan
    d.polygon([(300, 80), (220, 300), (380, 300)], outline=GOLD, width=5)
    d.line([(80, 150), (287, 205)], fill=GOLD_HI, width=4)
    d.line([(295, 212), (560, 260)], fill=(200, 90, 60), width=4)
    d.line([(295, 212), (560, 180)], fill=(90, 160, 200), width=4)
    save(img, "lab_optics.jpg")


def art_shm():
    img, d = base("sh")
    # pegas + sinus
    d.line([(60, 120), (120, 120)], fill=(90, 75, 45), width=3)
    zz = [(120 + i * 14, 120 + (12 if i % 2 else -12)) for i in range(12)]
    glow_line(d, zz, GOLD, 3)
    d.rectangle([296, 100, 330, 140], fill=GOLD)
    pts = [(x, 260 - 70 * math.sin((x - 40) / 42)) for x in range(40, W - 39, 5)]
    d.line([(40, 260), (W - 40, 260)], fill=(90, 75, 45), width=2)
    glow_line(d, pts, GOLD_HI, 4)
    save(img, "lab_shm.jpg")


def art_umb_wave():
    img, d = base("uw", (8, 10, 18), (10, 16, 26))
    # gelombang berjalan berlapis
    for k in range(3):
        pts = [(x, H // 2 - 60 + k * 50 + 30 * math.sin(x / 40 + k * 1.1))
               for x in range(0, W + 1, 5)]
        glow_line(d, pts, GOLD if k % 2 else GOLD_HI, 4)
    save(img, "lab_umb_wave.jpg")


def art_heatexp():
    img, d = base("hx", (24, 12, 8), (18, 10, 6))
    # batang memuai + panah
    d.rectangle([80, 170, 480, 220], outline=GOLD, width=5)
    d.rectangle([80, 170, 440, 220], fill=(70, 40, 24))
    d.polygon([(480, 145), (480, 245), (560, 195)], fill=GOLD_HI)
    for i in range(4):
        d.arc([120 + i * 90, 250, 190 + i * 90, 330], 200, 340, fill=(200, 100, 50), width=4)
    save(img, "lab_heatexp.jpg")


def art_emind():
    img, d = base("em", (10, 8, 6), (16, 10, 6))
    # kumparan + garis fluks + jarum galvanometer
    for i in range(5):
        x0 = 90 + i * 62
        d.arc([x0, 120, x0 + 56, 240], 270, 90, fill=GOLD, width=5)
        d.arc([x0, 120, x0 + 56, 240], 90, 270, fill=GOLD, width=5)
    d.ellipse([470, 150, 590, 270], outline=GOLD_HI, width=5)
    d.line([(530, 210), (575, 160)], fill=GOLD_HI, width=4)
    save(img, "lab_emind.jpg")


if __name__ == "__main__":
    art_integral()
    art_matrix()
    art_ode()
    art_stats()
    art_umb_stats()
    art_thermo()
    art_qm()
    art_es()
    art_rel()
    art_umb_rel()
    art_proj()
    art_umb_newton()
    art_hydro()
    art_umb_hydro()
    art_complex()
    art_umb_complex()
    art_taylor()
    art_umb_real()
    art_modmath()
    art_umb_discrete()
    art_entropy()
    art_umb_info()
    art_poly()
    art_schwartz()
    art_umb_gr()
    art_optics()
    art_shm()
    art_umb_wave()
    art_heatexp()
    art_emind()
    print("done")
