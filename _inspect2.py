"""Cek dimensi piksel semua art yang direferensikan menu (data-img)."""
import os
import re

from PIL import Image

BASE = r"G:\vektor-lab(1)\vektor-lab"
h = open(os.path.join(BASE, "templates", "index.html"), encoding="utf-8").read()
m = h.find('id="mathMenu"')
p = h.find('id="physMenu"')

def dataimgs(sec):
    return sorted(set(re.findall(r'data-img="([^"]+)"', sec)))

for name, sec in (("MATH", h[m:p]), ("PHYS", h[p:])):
    print(f"=== {name} data-img dims ===")
    for u in dataimgs(sec):
        path = os.path.join(BASE, u.lstrip("/").replace("/", os.sep))
        try:
            img = Image.open(path)
            mp = img.width * img.height / 1e6
            flag = "  <<< BESAR!" if mp > 8 else ""
            print(f"{img.width:5d}x{img.height:<5d} {mp:6.1f} MP  {u}{flag}")
        except Exception as e:
            print(f"  ERROR {u}: {e}")
