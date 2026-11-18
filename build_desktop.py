# -*- coding: utf-8 -*-
"""Build DESKTOP NATIVE (Electron shell + Python sidecar).

Hasil di "Nabla Workspace x64 Offline/":
  "Nabla Workspace (Native)/"  -> double-click NablaWorkspace.exe
  "NablaWorkspace-x64.zip"     -> zip unduhan (nama sama dgn route web)
  "download-info.json"

Struktur (ala VS Code/Discord):
  NablaWorkspace.exe           (runtime Electron, ikon NABLA via rcedit)
  resources/app/               (main.js shell + package.json)
  resources/sidecar/           (server Python PyInstaller, hidden child)
  resources/sidecar/... jalan dengan NABLA_HEADLESS=1
"""
import io
import os
import sys
import json
import shutil
import hashlib
import subprocess

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = os.path.dirname(os.path.abspath(__file__))
DESKTOP = os.path.join(BASE, "desktop")
TARGET = os.path.join(BASE, "Nabla Workspace x64 Offline")
APPNAME = "Nabla Workspace (Native)"
APPDIR = os.path.join(TARGET, APPNAME)
ZIP_NAME = "NablaWorkspace-x64.zip"
ELECTRON_DIST = os.path.join(DESKTOP, "node_modules", "electron", "dist")
RCEDIT = os.path.join(DESKTOP, "node_modules", "rcedit", "bin", "rcedit-x64.exe")


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def copytree(src, dst, ignore=None):
    shutil.copytree(src, dst, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns(*(ignore or [])))


def main():
    # 0) prasyarat
    assert os.path.isdir(ELECTRON_DIST), "npm install electron dulu di desktop/"
    assert os.path.exists(RCEDIT), "npm install rcedit dulu di desktop/"
    sidecar_src = os.path.join(TARGET, "Nabla Workspace")
    assert os.path.exists(os.path.join(sidecar_src, "NablaWorkspace.exe")), \
        "build sidecar dulu: python build_offline.py"

    # 1) bersihkan hasil lama
    if os.path.isdir(APPDIR):
        shutil.rmtree(APPDIR, ignore_errors=True)
    os.makedirs(APPDIR, exist_ok=True)

    # 2) runtime Electron
    print(">> salin runtime electron ...")
    copytree(ELECTRON_DIST, APPDIR)
    exe = os.path.join(APPDIR, "NablaWorkspace.exe")
    os.replace(os.path.join(APPDIR, "electron.exe"), exe)

    # 3) resources/app (shell) + resources/sidecar (server python)
    res = os.path.join(APPDIR, "resources")
    app_res = os.path.join(res, "app")
    os.makedirs(app_res, exist_ok=True)
    for f in ["main.js", "package.json", "icon.ico"]:
        shutil.copy2(os.path.join(DESKTOP, f), app_res)
    # package.json di app: minimal, main menunjuk main.js
    pkg = json.load(open(os.path.join(DESKTOP, "package.json"), encoding="utf-8"))
    json.dump({"name": pkg["name"], "productName": pkg["productName"],
               "version": pkg["version"], "main": "main.js"},
              open(os.path.join(app_res, "package.json"), "w", encoding="utf-8"),
              indent=2)
    print(">> salin sidecar python ...")
    copytree(sidecar_src, os.path.join(res, "sidecar"))

    # 4) ikon + metadata exe (rcedit)
    print(">> rcedit icon ...")
    r = subprocess.run([RCEDIT, exe, "--set-icon", os.path.join(DESKTOP, "icon.ico"),
                        "--set-version-string", "ProductName", "Nabla Workspace",
                        "--set-version-string", "FileDescription",
                        "Nabla Workspace - Laboratorium Offline",
                        "--set-version-string", "CompanyName", "Nabla Workspace"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print("rcedit warning:", r.stdout, r.stderr)

    # 5) README
    with open(os.path.join(APPDIR, "README.txt"), "w", encoding="utf-8") as f:
        f.write(
            "Nabla Workspace - Desktop (Windows x64)\n"
            "========================================\n\n"
            "Cara pakai:\n"
            "  1. Double-click  NablaWorkspace.exe\n"
            "  2. Aplikasi terbuka di jendelanya sendiri (GUI native).\n"
            "     Seluruh alat berjalan tanpa internet.\n\n"
            "Fitur AI (opsional):\n"
            "  AI hanya tersambung ke internet saat kamu memang menggunakannya.\n"
            "  Butuh API key: buka config.json di dalam folder resources/sidecar\n"
            "  dan isi openrouter_api_key.\n\n"
            "How to use (EN):\n"
            "  1. Double-click NablaWorkspace.exe - the app opens in its own\n"
            "     native window. All tools work offline.\n"
            "  2. Optional AI: edit resources/sidecar/config.json and fill in\n"
            "     openrouter_api_key.\n")

    # 6) zip unduhan (nama sama dgn route /download/offline)
    zip_base = os.path.join(TARGET, "NablaWorkspace-x64")
    if os.path.exists(zip_base + ".zip"):
        os.remove(zip_base + ".zip")
    print(">> zip ...")
    final = shutil.make_archive(zip_base, "zip", root_dir=TARGET, base_dir=APPNAME)
    zip_path = final if final.endswith(".zip") else final + ".zip"

    info = {"file": os.path.basename(zip_path),
            "size": os.path.getsize(zip_path),
            "sha256": sha256_of(zip_path),
            "mtime": int(os.path.getmtime(zip_path))}
    with open(os.path.join(TARGET, "download-info.json"), "w", encoding="utf-8") as f:
        json.dump(info, f, indent=2)

    size_mb = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(APPDIR) for f in fs) / 1048576
    print()
    print("== BUILD DESKTOP SELESAI ==")
    print("folder :", APPDIR, "(%.0f MB)" % size_mb)
    print("zip    :", zip_path, "(%.1f MB)" % (info["size"] / 1048576))
    print("sha256 :", info["sha256"][:16], "...")


if __name__ == "__main__":
    main()
