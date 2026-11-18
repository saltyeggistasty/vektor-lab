# -*- coding: utf-8 -*-
# cache-busting sekali pakai: tambah v=asset_v ke semua url_for static
# di templates/index.html. Dipanggil manual; hasilnya permanen di template.
import io
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(BASE, "templates", "index.html")

with io.open(p, encoding="utf-8") as f:
    s = f.read()

pat = re.compile(
    r"url_for\((['\"])static\1, filename=(['\"'][^'\"]+['\"])\)"
)


def _add_v(m):
    q1, fn = m.group(1), m.group(2)
    return "url_for(%sstatic%s, filename=%s, v=asset_v)" % (q1, q1, fn)


s2, n = pat.subn(_add_v, s)

with io.open(p, "w", encoding="utf-8", newline="") as f:
    f.write(s2)

print("%d tag aset di-versioning dengan ?v=asset_v" % n)
