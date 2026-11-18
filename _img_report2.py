from PIL import Image
import os, glob

for d in [r"G:\vektor-lab(1)\vektor-lab\menu_screen\dim",
          r"G:\vektor-lab(1)\vektor-lab\menu_screen\new_math_menu\optimized",
          r"G:\vektor-lab(1)\vektor-lab\language_select_backdrop"]:
    print("==", d)
    if not os.path.isdir(d):
        print("   MISSING")
        continue
    for f in sorted(glob.glob(os.path.join(d, "*"))):
        n = os.path.basename(f)
        sz = os.path.getsize(f) / 1024
        try:
            im = Image.open(f)
            mp = im.size[0] * im.size[1] / 1e6
            print(f"  {n:36} {im.size[0]:5}x{im.size[1]:<5} {mp:6.2f} MP  {sz:8.0f} KB  {im.format}")
        except Exception:
            print(f"  {n:36} (bukan gambar)  {sz:8.0f} KB")
