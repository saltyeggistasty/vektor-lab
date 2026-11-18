# -*- coding: utf-8 -*-
"""qm_wave.jpg â€” backdrop HOVER kartu Mekanika Kuantum.
Crop band gelombang biru di bawah QM.png (bukan band hitam-gelap atas),
sedikit dicerahkan supaya latar blur hover terang, tak menjegal batas kartu."""
from PIL import Image, ImageEnhance, ImageOps

src = Image.open("menu_screen/QM.png").convert("RGB")
W, H = src.size                                  # 1400x784
wave = src.crop((0, 300, W, H))                  # band gelombang penuh lebar
wave = ImageEnhance.Brightness(wave).enhance(1.42)
wave = ImageEnhance.Color(wave).enhance(1.18)
# +40% gamma-lift (sama dgn cover lain): bayangan naik, sorotan tak ketos
LIFT = 1.4
wave = wave.point(lambda v: round(255 * (v / 255) ** (1 / LIFT)))
wave.save("menu_screen/qm_wave.jpg", "JPEG", quality=88, optimize=True)
print("qm_wave.jpg", wave.size)

