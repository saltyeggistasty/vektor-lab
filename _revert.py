# -*- coding: utf-8 -*-
p = r"G:\vektor-lab(1)\vektor-lab\static\menu.js"
mj = open(p, encoding="utf-8").read()
block = open(r"G:\vektor-lab(1)\vektor-lab\_block.txt", encoding="utf-8").read()
assert block in mj, "block tidak persis ditemukan"
mj = mj.replace(block, "", 1)
open(p, "w", encoding="utf-8", newline="\n").write(mj)
print("syncGlow module dihapus. sisa ref:", mj.count("syncGlow") + mj.count("queueGlow") + mj.count("--glow-"))

# revert CSS: var -> statis (top + subtle bottom, tanpa middle)
p2 = r"G:\vektor-lab(1)\vektor-lab\static\style.css"
css = open(p2, encoding="utf-8").read()
gold_old = '''  background:
    radial-gradient(var(--glow-w, 62%) 24% at var(--glow-x, 50%) 21%,
      rgba(224, 176, 74, .5), transparent 70%),
    radial-gradient(calc(var(--glow-w, 62%) * .5) 22% at var(--glow-x, 50%) 92%,
      rgba(224, 176, 74, .18), transparent 70%);'''
gold_new = '''  background:
    radial-gradient(70% 24% at 50% 21%,
      rgba(224, 176, 74, .5), transparent 70%),
    radial-gradient(36% 22% at 50% 92%,
      rgba(224, 176, 74, .18), transparent 70%);'''
black_old = '''  background:
    radial-gradient(var(--glow-w, 62%) 24% at var(--glow-x, 50%) 21%,
      rgba(255, 200, 61, .4), transparent 70%),
    radial-gradient(calc(var(--glow-w, 62%) * .5) 22% at var(--glow-x, 50%) 92%,
      rgba(255, 200, 61, .14), transparent 70%);'''
black_new = '''  background:
    radial-gradient(70% 24% at 50% 21%,
      rgba(255, 200, 61, .4), transparent 70%),
    radial-gradient(36% 22% at 50% 92%,
      rgba(255, 200, 61, .14), transparent 70%);'''
assert gold_old in css and black_old in css
css = css.replace(gold_old, gold_new).replace(black_old, black_new)
# update komentar blok (buang referensi JS sync)
css = css.replace('''   Lebar & pusat blob DIATUR JS (menu.js) lewat --glow-w/--glow-x biar
   ngikutin lebar kartu yang tampil — kartu 3 biji = glow ramping,
   kartu penuh = glow lebar. Hanya gold & black: di light mode batas
   kartu sudah jelas sendiri. */''', '''   Hanya gold & black: di light mode batas kartu sudah jelas sendiri. */''')
open(p2, "w", encoding="utf-8", newline="\n").write(css)
print("CSS revert:", "--glow-" not in css)
