# -*- coding: utf-8 -*-
"""Inject key terjemahan baris 'note' LaTeX backend (graphlab.py) ke grup graph.*.
   - graph.note_gsurf3d : catatan bidang singgung (gsurf3d)
   - graph.note_gfrenet : catatan frame Frenet (gfrenet)
   Indonesia = teks asli backend (identitas). Irish = English."""
import json, io, os

GS = r"z = f(x,y)\ +\ \text{bidang singgung di } (x_0, y_0)"
FR = r"\mathbf{T}, \mathbf{N}, \mathbf{B} = \text{frame Frenet},\ \kappa, \tau \text{ numerik}"

EN_GS = r"z = f(x,y)\ +\ \text{tangent plane at } (x_0, y_0)"
EN_FR = r"\mathbf{T}, \mathbf{N}, \mathbf{B} = \text{Frenet frame},\ \kappa, \tau \text{ numeric}"

# file -> [note_gsurf3d, note_gfrenet]
TR = {
    "indonesia.json": [GS, FR],
    "english.json":   [EN_GS, EN_FR],
    "irish.json":     [EN_GS, EN_FR],
    "melayu.json":    [r"z = f(x,y)\ +\ \text{satah sesentuh di } (x_0, y_0)",
                       r"\mathbf{T}, \mathbf{N}, \mathbf{B} = \text{bingkai Frenet},\ \kappa, \tau \text{ berangka}"],
    "russia.json":    [r"z = f(x,y)\ +\ \text{касательная плоскость в } (x_0, y_0)",
                       r"\mathbf{T}, \mathbf{N}, \mathbf{B} = \text{репер Френе},\ \kappa, \tau \text{ численно}"],
    "ukraina.json":   [r"z = f(x,y)\ +\ \text{дотична площина в } (x_0, y_0)",
                       r"\mathbf{T}, \mathbf{N}, \mathbf{B} = \text{ріпер Френе},\ \kappa, \tau \text{ числово}"],
    "arab.json":      [r"z = f(x,y)\ +\ \text{المستوى المماسي عند } (x_0, y_0)",
                       r"\mathbf{T}, \mathbf{N}, \mathbf{B} = \text{إطار فرينه},\ \kappa, \tau \text{ عددياً}"],
}

ok, skip = 0, 0
for fn, (vgs, vfr) in TR.items():
    p = os.path.join("i18n", fn)
    d = json.load(io.open(p, encoding="utf-8"))
    g = d["graph"]
    changed = False
    for k, v in (("note_gsurf3d", vgs), ("note_gfrenet", vfr)):
        if k in g:
            if g[k] != v:
                g[k] = v; changed = True  # timpa kalau beda (sinkron dgn backend)
            else:
                skip += 1
        else:
            g[k] = v; changed = True; ok += 1
    if changed:
        io.open(p, "w", encoding="utf-8", newline="\n").write(
            json.dumps(d, ensure_ascii=False, indent=2) + "\n")

print("INJECTED:", ok, "| SAME:", skip)
# validasi ulang
for fn, (vgs, vfr) in TR.items():
    d = json.load(io.open(os.path.join("i18n", fn), encoding="utf-8"))
    assert d["graph"]["note_gsurf3d"] == vgs and d["graph"]["note_gfrenet"] == vfr, fn
print("VALIDASI LULUS")
