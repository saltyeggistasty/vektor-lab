# -*- coding: utf-8 -*-
import json
import urllib.request

BASE = "http://127.0.0.1:5000"
fail = 0

# 1) CSS mobile mode ter-serve
css = urllib.request.urlopen(BASE + "/static/style.css", timeout=30).read().decode()
for marker in ("MOBILE MODE (≤900px / zoom >150%)",
               "body.warfs #math.panel-wrap,",
               "flex: 0 0 100%; height: clamp(260px, 68vw, 470px)",
               "body.mcols-2 .wm-grid .wtile { flex: 0 0 calc(50% - 6px);",
               ".wm-cols-btn { display: none;",
               "#fieldSel { position: fixed; inset: 0; z-index: 39;"):
    ok = marker in css
    print(("CSS OK  " if ok else "CSS MISS") + marker)
    fail += 0 if ok else 1
ob, cb = css.count("{"), css.count("}")
print(f"CSS braces {ob}/{cb}", "OK" if ob == cb else "MISMATCH")
fail += 0 if ob == cb else 1

# 2) QM img -> dim_QM.png
html = urllib.request.urlopen(BASE + "/", timeout=30).read().decode("utf-8")
ok = 'src="/menu_screen/dim/dim_QM.png"' in html and 'src="/menu_screen/QM.png"' not in html
print(("HTML OK " if ok else "HTML MISS") + " QM cover dim_QM.png")
fail += 0 if ok else 1

# 3) i18n menu.cols ×7
for lang in ["indonesia", "english", "russia", "arab"]:
    d = json.loads(urllib.request.urlopen(f"{BASE}/i18n/{lang}.json", timeout=30).read())
    ok = "cols_1" in d.get("menu", {}) and "cols_2" in d.get("menu", {})
    print(("i18n OK  " if ok else "i18n MISS") + f" menu.cols {lang}")
    fail += 0 if ok else 1

# 4) regresi: API + kartu
body = json.dumps({"tool": "gdomain", "data": {}}).encode()
req = urllib.request.Request(BASE + "/api/lab", body, {"Content-Type": "application/json"})
with urllib.request.urlopen(req, timeout=60) as r:
    j = json.loads(r.read())
print("API gdomain:", "OK" if j.get("ok") else "BAD")
fail += 0 if j.get("ok") else 1
for probe in ('data-tool="sslope"', 'data-tool="gdist"', 'data-umbrella="qm"'):
    ok = probe in html
    print(("HTML OK " if ok else "HTML MISS") + probe)
    fail += 0 if ok else 1
print("FAIL =", fail)
