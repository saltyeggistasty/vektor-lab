# Nabla Workspace — Versi Offline Executable + Download Page

## Context
Web edukasi (Flask + vanilla JS) mau dibungkus jadi aplikasi Windows offline yang bisa diunduh dari situsnya sendiri. Eksplorasi menemukan fakta kunci:
- Semua path backend relatif ke `__file__` (6 lokasi di app.py + `physics.py:44-45`) → perlu frozen-mode handling.
- **Blocker offline utama**: index.html memuat 4 library dari CDN — KaTeX CSS+JS (jsdelivr), Plotly (cdn.plot.ly), GSAP (cdnjs). Harus di-vendor ke `static/vendor/` atau UI rusak offline. MathLive sudah lokal.
- **`config.json` berisi secret asli** (OpenRouter key + Gmail app password) → TIDAK BOLEH ikut ke bundle. Aplikasi sudah degrade elegan tanpa config (PhysError jelas, tanpa crash startup).
- AI: `#pai` & `#aiAutoRun` checked-by-default (index.html:1171/1190), tapi AI hanya pernah dipanggil saat aksi user eksplisit (physics.js:655, 804) — boot pakai `physSimulate(false)` ✓.
- Frontend 100% relative fetch, tanpa absolute URL ✓. Venv Python 3.14.7, PyInstaller belum terpasang. Folder `Nabla Workspace x64 Offline/` kosong & siap.

## Keputusan desain
- **Format**: ZIP berisi build **onedir** (bukan onefile) — alasan: onefile mengekstrak ~150MB ke temp SETIAP launch (N4020 = boot 10-20s); onedir = unzip sekali, klik exe langsung cepat. Zip berisi folder `Nabla Workspace/` + README singkat.
- **Window**: launcher coba `pywebview` (jendela native); kalau WebView2 tidak ada → fallback otomatis buka browser default. Port: cari port bebas otomatis.
- **Secrets**: tidak pernah di-bundle. Launcher menyalin `config.example.json` → `config.json` di samping exe saat first-run agar user bisa isi API key sendiri untuk fitur AI.

## Implementasi

### 1. Vendor CDN → lokal (menguntungkan web juga)
- Download ke `static/vendor/`: `katex/katex.min.css`, `katex/katex.min.js`, `katex/fonts/*` (font KaTeX direferensikan relatif oleh css), `plotly.min.js`, `gsap.min.js`.
- `templates/index.html`: 4 tag CDN (baris 8/10/12/1377) → `url_for('static', ...)` vendor. Perilaku UI/engines tidak berubah.

### 2. Frozen-mode backend
- `app.py`: helper `_base()` (`sys._MEIPASS` saat frozen, else dirname `__file__`) dipakai 6 lokasi path + `render_template` tetap jalan (Flask root via _MEIPASS). Route baru: `GET /download/info` (JSON: ada/ukuran/sha256/mtime dari folder build) & `GET /download/offline` (send_file zip dari `Nabla Workspace x64 Offline/`).
- `physics.py:44-45`: `CONFIG_PATH` frozen-aware → saat frozen baca `config.json` dari folder exe (user-editable), fallback bawaan.
- NEW `run.py` (entry PyInstaller): `debug=False, use_reloader=False`, pilih port bebas (mulai 5000), seed `config.json` first-run, lalu `pywebview` window → fallback `webbrowser.open()`. Dev flow `app.py` tidak berubah.

### 3. AI opsional di build offline (web tidak berubah)
- Route `GET /api/appinfo` → `{frozen: bool}`.
- `physics.js`: kecil saja — saat `frozen`: default-uncheck `#pai` & `#aiAutoRun` + tampilkan note i18n di panel AI ("AI butuh internet + API key di config.json di samping exe; koneksi hanya saat kamu menekan tombol AI"). Web version: tidak berubah sama sekali (non-frozen → skip).

### 4. Download panel di web
- Header: tombol `<button class="tab" id="dlBtn">⬇ Offline</button>` di `.hright`; branch kecil di handler `.tab` app.js:142-182.
- NEW `<section id="dlSel">` overlay (pola #donSel: fixed z-9000, .active, body class utk header) tapi **pakai CSS vars tema** (adaptif gold/light/black sesuai permintaan). Isi: judul + deskripsi, info file (nama, ukuran, sha256 dari `/download/info`, tombol Unduh disabled + pesan bila build belum ada), langkah install (unzip → double-click exe), catatan fitur online (AI opsional).
- NEW `static/download.js` (IIFE pola donation.js: open/close/ESC). 
- `static/style.css`: blok `#dlSel` bertema var(--*).
- i18n: grup `"download"` baru ×7 bahasa (terjemahan gw tulis).

### 5. Build pipeline
- NEW `build_offline.py`: cek vendor files → jalankan PyInstaller (onedir, --noconsole, add-data: templates, static, i18n, loading_screen, menu_screen, language_select_backdrop, address.json, config.example.json; hiddenimports symengine/mpmath; exclude PIL & file sampah `_*.py`, `__pycache__`, `menu_screen/_orig_backup`, `i18n/backup`) → output ke `Nabla Workspace x64 Offline/Nabla Workspace x64/` → ZIP + sha256 → tulis `download-info.json` (dibaca /download/info). Opsi `--include-config` untuk build personal dgn config asli (tidak dipakai default).
- Prasyarat: `pip install pyinstaller` (Python 3.14 butuh PyInstaller terbaru; kalau gagal → fallback embeddable-python, akan dilaporkan).

### 6. Verifikasi (airtight, sesuai permintaan)
1. **Web**: E2E ulang setelah vendoring — KaTeX/Plotly/GSAP load lokal (cek 0 request eksternal), semua tool masih jalan, regresi graph 36/36, download panel terbuka di 3 tema + ganti bahasa.
2. **Build**: `build_offline.py` sukses → zip + sha256 di folder target.
3. **Offline exe**: launch exe → dapat port-nya → sweep otomatis via browser: SEMUA tool math (10), graph (15), sim (10), lab fisika Monte Carlo, menu math/physics/fieldsel, 7 bahasa, 3 tema, donasi, audit form (pesan elegan tanpa config), AI tanpa key (pesan jelas), AI checkbox default unchecked di build offline.
4. **Isolasi secret**: pastikan zip TIDAK berisi config.json asli (grep sk-or-v1 / app_password di isi zip).

File dimodifikasi: `app.py`, `physics.py`, `templates/index.html`, `static/app.js`, `static/physics.js`, `static/style.css`, `i18n/*.json` ×7. File baru: `run.py`, `build_offline.py`, `static/download.js`, `static/vendor/*`, `#dlSel` markup. UI/scripts/engines tools & menu TIDAK disentuh (kecuali 4 URL CDN + 3 penambahan kecil ter-gating frozen).