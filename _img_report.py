from PIL import Image
import os, glob

base = r"G:\vektor-lab(1)\vektor-lab\menu_screen"
dirs = [base, os.path.join(base, "tools_card_art"), os.path.join(base, "new_math_menu"),
        os.path.join(base, "new_phys_menu"), os.path.join(base, "wm")]
for d in dirs:
    if not os.path.isdir(d):
        continue
    print("==", os.path.basename(d) or "menu_screen")
    for f in sorted(glob.glob(os.path.join(d, "*.jpg")) + glob.glob(os.path.join(d, "*.png")) + glob.glob(os.path.join(d, "*.jpeg"))):
        n = os.path.basename(f)
        if n.startswith(("mc_", "lab_umb", "wm_", "_sheet", "gen_")) and d == base:
            continue
        try:
            im = Image.open(f)
            mp = im.size[0] * im.size[1] / 1e6
            print(f"  {n:36} {im.size[0]:5}x{im.size[1]:<5} {mp:5.2f} MP  {os.path.getsize(f)/1024:7.0f} KB")
        except Exception as e:
            print("  ", n, "ERR", e)
