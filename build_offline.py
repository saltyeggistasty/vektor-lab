# -*- coding: utf-8 -*-
"""Build versi offline Nabla Workspace -> exe Windows (PyInstaller onedir).

Hasil:
  "Nabla Workspace x64 Offline/Nabla Workspace/"   (folder aplikasi, klik exe)
  "Nabla Workspace x64 Offline/NablaWorkspace-x64.zip"  (untuk diunduh dari web)
  "Nabla Workspace x64 Offline/download-info.json"      (dibaca /download/info)

Catatan:
- Secret TIDAK diikutkan: config.json asli tidak pernah masuk bundle; launcher
  menyalin config.example.json -> config.json di samping exe saat first-run.
- Opsi --include-config: build PERSONAL (memakai config.json asli). Jangan
  dibagikan kalau dipakai, karena berisi API key/email kamu."""
import io
import os
import sys
import json
import shutil
import hashlib
import subprocess

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = os.path.dirname(os.path.abspath(__file__))
VENV_PY = os.path.join(BASE, "venv", "Scripts", "python.exe")
TARGET = os.path.join(BASE, "Nabla Workspace x64 Offline")
WORK = os.path.join(BASE, "_build_offline")
DIST = os.path.join(WORK, "dist")
APPDIR_NAME = "Nabla Workspace"
ZIP_NAME = "NablaWorkspace-x64.zip"

VENDOR_REQUIRED = [
    os.path.join("static", "vendor", "katex", "katex.min.css"),
    os.path.join("static", "vendor", "katex", "katex.min.js"),
    os.path.join("static", "vendor", "plotly.min.js"),
    os.path.join("static", "vendor", "gsap.min.js"),
]
DATA_DIRS = ["templates", "static", "i18n", "loading_screen", "menu_screen",
             "language_select_backdrop", "about_us_menu"]
DATA_FILES = ["address.json", "config.example.json"]
# potongan folder yang tidak perlu ikut bundle
STRIP_IN_DIST = [
    os.path.join("menu_screen", "_orig_backup"),
    os.path.join("i18n", "backup"),
]
EXCLUDE_MODULES = ["PIL", "setuptools", "pip", "wheel", "tkinter"]
# pywebview: bawa SEMUA aset backend Windows (Edge WebView2 + pythonnet)
COLLECT_ALL = ["webview"]
HIDDEN_IMPORTS = ["symengine", "mpmath", "clr_loader", "pythonnet"]


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    # 0) prasyarat
    for rel in VENDOR_REQUIRED:
        p = os.path.join(BASE, rel)
        if not os.path.exists(p) or os.path.getsize(p) == 0:
            raise SystemExit("vendor hilang: %s — jalankan _vendor.py dulu" % rel)
    for d in DATA_DIRS:
        if not os.path.isdir(os.path.join(BASE, d)):
            raise SystemExit("folder data hilang: " + d)

    # 1) bersihkan area kerja & hasil lama
    for p in [DIST, os.path.join(TARGET, APPDIR_NAME),
              os.path.join(TARGET, ZIP_NAME),
              os.path.join(WORK, "build"), os.path.join(WORK, "NablaWorkspace.spec")]:
        if os.path.isdir(p):
            shutil.rmtree(p, ignore_errors=True)
        elif os.path.exists(p):
            os.remove(p)
    os.makedirs(TARGET, exist_ok=True)

    # 2) pyinstaller
    cmd = [VENV_PY, "-m", "PyInstaller", "--noconfirm", "--clean", "--noconsole",
           "--name", "NablaWorkspace",
           "--icon", os.path.join(BASE, "desktop", "icon.ico"),
           "--distpath", DIST,
           "--workpath", os.path.join(WORK, "build"),
           "--specpath", WORK]
    for d in DATA_DIRS:
        cmd += ["--add-data", os.path.join(BASE, d) + os.pathsep + d]
    for f in DATA_FILES:
        cmd += ["--add-data", os.path.join(BASE, f) + os.pathsep + "."]
    for m in EXCLUDE_MODULES:
        cmd += ["--exclude-module", m]
    for m in HIDDEN_IMPORTS:
        cmd += ["--hidden-import", m]
    for pkg in COLLECT_ALL:
        cmd += ["--collect-all", pkg]
    cmd.append("run.py")
    print(">> pyinstaller ...")
    r = subprocess.run(cmd, cwd=BASE)
    if r.returncode != 0:
        raise SystemExit("pyinstaller gagal (code %d)" % r.returncode)

    # 3) rapikan hasil: nama folder + buang potongan tak perlu
    src = os.path.join(DIST, "NablaWorkspace")
    appdir = os.path.join(TARGET, APPDIR_NAME)
    shutil.move(src, appdir)
    for rel in STRIP_IN_DIST:
        p = os.path.join(appdir, "_internal", rel)
        if os.path.isdir(p):
            shutil.rmtree(p, ignore_errors=True)
            print("strip:", rel)

    # 4) README
    readme = (
        "Nabla Workspace - Versi Offline (Windows x64)\n"
        "==============================================\n\n"
        "Cara pakai:\n"
        "  1. Double-click  NablaWorkspace.exe\n"
        "  2. Lab terbuka di browser/jendela aplikasi. Semua alat jalan\n"
        "     tanpa internet.\n\n"
        "Fitur AI (opsional):\n"
        "  AI hanya tersambung ke internet saat kamu memang menggunakannya\n"
        "  (centang AI lalu tekan tombolnya). Butuh API key: buka config.json\n"
        "  di folder ini dan isi openrouter_api_key (config contoh otomatis\n"
        "  dibuat saat pertama kali dijalankan).\n\n"
        "How to use (EN):\n"
        "  1. Double-click  NablaWorkspace.exe\n"
        "  2. The lab opens locally. All tools work without internet.\n"
        "  3. Optional AI: edit config.json next to this exe and fill in\n"
        "     openrouter_api_key.\n\n"
        "Nabla Workspace - " + r"https://github.com/ - personal project\n"
    )
    with open(os.path.join(appdir, "README.txt"), "w", encoding="utf-8") as f:
        f.write(readme)

    # 5) zip (folder dalam zip = "Nabla Workspace")
    zip_base = os.path.join(TARGET, "NablaWorkspace-x64")
    print(">> zip ...")
    final = shutil.make_archive(zip_base, "zip", root_dir=TARGET, base_dir=APPDIR_NAME)
    zip_path = final if final.endswith(".zip") else final + ".zip"

    # 6) info unduhan
    info = {"file": os.path.basename(zip_path),
            "size": os.path.getsize(zip_path),
            "sha256": sha256_of(zip_path),
            "mtime": int(os.path.getmtime(zip_path))}
    with open(os.path.join(TARGET, "download-info.json"), "w", encoding="utf-8") as f:
        json.dump(info, f, indent=2)
    # salin juga ke app.py yang dibaca /download/info: server mencari
    # file ZIP bernama NablaWorkspace-x64.zip di folder target ✓ (sudah sama)

    print()
    print("== BUILD SELESAI ==")
    print("folder :", appdir, "(%.0f MB)" % (
        sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(appdir) for f in fs) / 1048576))
    print("zip    :", zip_path, "(%.1f MB)" % (info["size"] / 1048576))
    print("sha256 :", info["sha256"][:16], "...")


if __name__ == "__main__":
    main()
