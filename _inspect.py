"""Inspeksi: referensi gambar math vs physics menu + ukuran file."""
import re

h = open(r"G:\vektor-lab(1)\vektor-lab\templates\index.html", encoding="utf-8").read()
m = h.find('id="mathMenu"')
p = h.find('id="physMenu"')
math_sec, phys_sec = h[m:p], h[p:]

import os
BASE = r"G:\vektor-lab(1)\vektor-lab"

def refs(sec):
    return sorted(set(re.findall(r'(?:data-img|src)="([^"]+)"', sec)))

def size(url):
    path = os.path.join(BASE, url.lstrip("/").replace("/", os.sep))
    if not os.path.exists(path):
        return None
    return os.path.getsize(path)

print("=== MATH MENU ===")
tot = 0
for u in refs(math_sec):
    s = size(u)
    mark = ""
    if s is None:
        mark = "  <<< GAK ADA FILENYA!"
        s = 0
    tot += s
    print(f"{(s/1024/1024):7.2f} MB  {u}{mark}")
print(f"  total: {tot/1024/1024:.2f} MB")

print("=== PHYSICS MENU ===")
tot = 0
for u in refs(phys_sec):
    s = size(u)
    mark = ""
    if s is None:
        mark = "  <<< GAK ADA FILENYA!"
        s = 0
    tot += s
    print(f"{(s/1024/1024):7.2f} MB  {u}{mark}")
print(f"  total: {tot/1024/1024:.2f} MB")

# folder optimized untuk pembanding
opt = os.path.join(BASE, "menu_screen", "new_math_menu", "optimized")
if os.path.isdir(opt):
    print("=== new_math_menu/optimized ===")
    for f in sorted(os.listdir(opt)):
        fp = os.path.join(opt, f)
        print(f"{(os.path.getsize(fp)/1024/1024):7.2f} MB  {f}")
