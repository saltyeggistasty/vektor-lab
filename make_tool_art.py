# -*- coding: utf-8 -*-
# make_tool_art.py — generator cover art tool card gaya "Nagai-fy"
# ================================================================
# Ngubah foto sumber di menu_screen/lab_<tool>.jpg jadi flat-poster
# twilight ala Hiroshi Nagai (city-pop): smoothing lukisan (bilateral
# filter), posterisasi warna flat, tint shadow navy + highlight peach
# (midtone hue asli dipertahankan), saturasi tinggi, grain tipis.
#
# Pakai:  venv\Scripts\python.exe make_tool_art.py
# Output: menu_screen/tools_card_art/<tool>.jpg (800x1280, 5:8 portrait)
#
# Parameter yang bisa dimainkan:
#   TARGET_LUM  — kecerahan dasar rata-rata (naikin kalau hasil gelap)
#   QUANT       — jumlah warna (makin kecil makin flat/poster)
#   ALPHA_GRADE — kekuatan tint twilight (0 = foto asli, 1 = full duotone)
#   SAT/BRIGHT  — saturasi & brightness akhir
#   GRAIN       — tekanan grain tekstur kanvas
import os
import numpy as np
import cv2
from PIL import Image

SRC = r"G:\vektor-lab(1)\vektor-lab\menu_screen"
OUT = os.path.join(SRC, "tools_card_art")
os.makedirs(OUT, exist_ok=True)

TOOLS = ["integral", "matrix", "poly", "ode", "stats", "complex", "taylor",
         "modmath", "entropy", "es", "emind", "thermo", "heatexp", "qm",
         "rel", "proj", "hydro", "schwartz", "optics", "shm"]

W, H = 800, 1280         # 5:8 portrait — mendekati rasio frame kartu (tinggi),
                         # minim overzoom saat object-fit: cover
TARGET_LUM = 0.42
QUANT = 28
ALPHA_GRADE = 0.55
SAT, BRIGHT = 2.0, 1.04  # SAT 2.0 = permintaan user: +50% dari 1.35
GRAIN = 5.0

SHADOW_RGB = np.array([14, 18, 62]) / 255.0        # deep navy
HIGHLIGHT_RGB = np.array([255, 216, 182]) / 255.0  # peach hangat
S_EDGE, H_EDGE = 0.34, 0.72                        # ambang mulai tint

def build_lut():
    xs = np.linspace(0, 1, 256)
    out = np.stack([xs, xs, xs], axis=1)  # abu-abu luminance murni
    t_s = (np.clip((S_EDGE - xs) / S_EDGE, 0, 1) ** 1.2)[:, None]
    t_h = (np.clip((xs - H_EDGE) / (1 - H_EDGE), 0, 1) ** 1.2)[:, None]
    out = out * (1 - t_s) + SHADOW_RGB[None, :] * t_s
    out = out * (1 - t_h) + HIGHLIGHT_RGB[None, :] * t_h
    return (np.clip(out, 0, 1) * 255).astype(np.uint8)

LUT = build_lut()

def split_tone(bgr):
    lum = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY).astype(np.uint8)
    graded = LUT[lum][:, :, ::-1].astype(np.float32)  # -> BGR
    return bgr.astype(np.float32) * (1 - ALPHA_GRADE) + graded * ALPHA_GRADE

def normalize_lum(bgr):
    lum = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
    med = max(float(np.median(lum)), 0.02)
    gain = min(max(TARGET_LUM / med, 0.85), 2.2)
    return np.clip(bgr.astype(np.float32) * gain, 0, 255)

def crop_frame(im):
    """Center-crop ke rasio output (W:H) — potong sisi yang kepanjangan saja."""
    w, h = im.size
    target = W / H
    if w / h > target:                      # kelebaran -> potong kiri-kanan
        tw, th = int(h * target), h
    else:                                   # kepanjangan -> potong atas-bawah
        tw, th = w, int(w / target)
    left, top = (w - tw) // 2, (h - th) // 2
    return im.crop((left, top, left + tw, top + th)).resize((W, H), Image.LANCZOS)

def stylize(name):
    im = Image.open(os.path.join(SRC, f"lab_{name}.jpg")).convert("RGB")
    im = crop_frame(im)
    bgr = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR).astype(np.float32)

    bgr = normalize_lum(bgr)
    bgr = cv2.bilateralFilter(bgr.astype(np.uint8), 9, 60, 60)
    bgr = cv2.bilateralFilter(bgr, 9, 60, 60)
    bgr = cv2.bilateralFilter(bgr, 7, 40, 40).astype(np.float32)
    bgr = split_tone(bgr)

    hsv = cv2.cvtColor(np.clip(bgr, 0, 255).astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * SAT, 0, 255)
    hsv[:, :, 2] = np.clip(hsv[:, :, 2] * BRIGHT, 0, 255)
    bgr = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

    rgb = Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))
    rgb = rgb.quantize(colors=QUANT, method=Image.MEDIANCUT, dither=Image.Dither.NONE).convert("RGB")

    arr = np.array(rgb).astype(np.float32)
    rng = np.random.default_rng(42 + abs(hash(name)) % 999)
    noise = rng.normal(0, GRAIN, arr.shape[:2])[:, :, None]
    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)

    out = os.path.join(OUT, f"{name}.jpg")
    Image.fromarray(arr).save(out, "JPEG", quality=90)
    print(f"{name}.jpg  {os.path.getsize(out)} bytes")

if __name__ == "__main__":
    for t in TOOLS:
        stylize(t)
    print("DONE ->", OUT)
