# -*- coding: utf-8 -*-
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
base = r"G:\vektor-lab(1)\vektor-lab\static"
# cuma file kecil relevan; skip mathlive.min.js
for fn in ["app.js", "donation.js", "menu.js", "tools.js", "physics.js", "loading.js"]:
    src = open(base + "\\" + fn, encoding="utf-8").read()
    for i, l in enumerate(src.splitlines(), 1):
        if re.search(r"auditBox|<details|\.open\b\s*=|querySelectorAll\(['\"]details|getElementsByTagName\(['\"]details", l):
            print(f"{fn}:{i}: {l.strip()[:130]}")
