# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
fp = r"G:\vektor-lab(1)\vektor-lab\static\tools.js"
src = open(fp, encoding="utf-8").read()
old = """    /* --- integral (satu per ekspresi; nested -> sentinel) --- */
    {
      const m = /\\\\int(?:_\\{([^{}]*)\\}\\^\\{([^{}]*)\\})?/.exec(s);
      if (m) {"""
new = """    /* --- integral (satu per ekspresi; nested -> sentinel) ---
       Kalau ada \\sum/\\prod SEBELUM \\int (C05: integral = body dari
       sum), skip cabang ini -> sum branch yang memproses dgn integral
       sbg nested body. */
    {
      const m = /\\\\int(?:_\\{([^{}]*)\\}\\^\\{([^{}]*)\\})?/.exec(s);
      const hasOuterSum = m && /\\\\(sum|prod)_/.test(s.slice(0, m.index));
      if (m && !hasOuterSum) {"""
assert old in src, "MISS"
src = src.replace(old, new)
open(fp, "w", encoding="utf-8", newline="\n").write(src)
print("ok")
