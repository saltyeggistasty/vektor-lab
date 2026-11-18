# -*- coding: utf-8 -*-
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
src = open(r"G:\vektor-lab(1)\vektor-lab\static\tools.js", encoding="utf-8").read()
for m in re.finditer(r"const gb = grabBody\(rest\);", src):
    ln = src[:m.start()].count("\n") + 1
    print("tools.js line", ln)
src2 = open(r"G:\vektor-lab(1)\vektor-lab\mathlab.py", encoding="utf-8").read()
for m in re.finditer(r"_abs_log", src2):
    ln = src2[:m.start()].count("\n") + 1
    print("mathlab line", ln, src2.splitlines()[ln - 1][:90])
