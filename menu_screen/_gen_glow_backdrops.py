# -*- coding: utf-8 -*-
"""GLOW versi cover war menu — khusus BACKDROP (.wm-bg), kartu tetap pakai
file lift biasa. Resep tiap file:
  1) gamma-lift total ~1.4 x 1.3 (biar luminance naik jauh, sorotan tak ketos)
  2) bloom: area terang ditandai, di-blur, lalu screen-blend = nyala emas
     (screen blend: out = 255-(255-a)(255-b)/255 -> hemat, tak pernah over)
Pemakaian: data-img tile menunjuk file .jpg glow ini (lihat index.html)."""
import os
from PIL import Image, ImageChops, ImageFilter

FOLDER = os.path.dirname(os.path.abspath(__file__))
BACKUP = os.path.join(FOLDER, "_orig_backup")

# name: (strength bloom, gamma tambahan, radius relatif min-dim)
PARAMS = {
    "mc_calc.jpg":              (0.70, 1.30, .055),   # golden utama, glow paling gede
    "mc_graph.jpg":             (0.55, 1.30, .045),
    "mc_lin.jpg":               (0.55, 1.30, .045),
    "mc_ode.jpg":               (0.55, 1.30, .045),
    "magnetic_field_cover.jpg": (0.50, 1.25, .040),
    "solar_flare.jpg":          (0.45, 1.25, .040),
}


def lift(im, gamma):
    return im.point(lambda v: round(255 * (v / 255) ** (1 / gamma)))


def apply(im, w, h, srcname):
    strength, extra, rfrac = PARAMS[srcname]
    im = lift(im, 1.4)          # lift dasar (sama dgn file kartu)
    im = lift(im, extra)        # lift tambahan khusus backdrop glow

    # mask area terang (bloom diambil dari highlight saja)
    g = im.convert("L")
    mask = g.point(lambda v: 0 if v < 82 else min(255, int((v - 82) * 255 / (255 - 82))))
    r = max(14, int(min(w, h) * rfrac))
    bloom = im.filter(ImageFilter.GaussianBlur(r))
    # bloom diredam pakai strength: dari hitam ke bloom sebesar 'strength'
    bloom = ImageChops.multiply(bloom, Image.new("RGB", bloom.size,
        tuple(int(255 * strength) for _ in range(3))))
    glow = ImageChops.screen(im, bloom)
    return glow


for name in PARAMS:
    src = os.path.join(BACKUP, name)
    if not os.path.exists(src):
        src = os.path.join(FOLDER, name)        # fallback file aktif
    im = Image.open(src).convert("RGB")
    w, h = im.size
    out = apply(im, w, h, name)
    dst = os.path.join(FOLDER, name.replace(".jpg", "_glow.jpg"))
    out.save(dst, "JPEG", quality=85, optimize=True)

    # ukur rata2 luminance utk laporan (sampel 48x48)
    small = out.resize((48, 48))
    px = list(small.convert("RGB").getdata())
    lum = round(sum(0.2126 * r + 0.7152 * g + 0.0722 * b for r, g, b in px) / len(px))
    print(f"{name} -> {os.path.basename(dst)} {out.size} luminance ~{lum}")
print("beres.")
