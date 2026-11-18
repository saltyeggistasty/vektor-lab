# -*- coding: utf-8 -*-
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
js = open(r"G:\vektor-lab(1)\vektor-lab\static\donation.js", encoding="utf-8").read()
i = js.find("Escape")
print(js[max(0, i-700):i+500])
