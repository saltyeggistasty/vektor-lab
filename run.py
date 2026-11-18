# -*- coding: utf-8 -*-
"""Nabla Workspace — launcher versi offline (entry PyInstaller).

Server Flask di localhost (port bebas otomatis), seed config.json
first-run di samping exe (user-editable utk API key AI). GUI: JENDELA
NATIVE — bukan tab browser:
  1) pywebview (Edge WebView2) — jendela aplikasi asli;
  2) fallback: Edge/Chrome "--app=URL" (jendela standalone tanpa
     address bar/tab, tetap terlihat seperti aplikasi);
  3) terakhir: browser default.
Tidak ada koneksi internet yang dibuat sendiri — semua fitur lokal;
AI hanya aktif saat user eksplisit memakainya."""
import os
import sys
import socket
import threading
import time
import subprocess
import webbrowser

FROZEN = getattr(sys, "frozen", False)


def _free_port(start=5000, tries=50):
    """Cari port bebas mulai dari `start` (NABLA_PORT env = preferensi Electron)."""
    pref = os.environ.get("NABLA_PORT")
    if pref and pref.isdigit():
        start = max(2, int(pref))
    for p in range(start, start + tries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", p))
                return p
            except OSError:
                continue
    return 0          # praktis tidak terjadi (50 port cadangan)


def _seed_config():
    """First-run: salin config bawaan ke samping exe supaya user bisa mengisi
    API key AI sendiri. TIDAK PERNAH membawa secret apa pun dari build."""
    try:
        if not FROZEN:
            return
        exe_dir = os.path.dirname(sys.executable)
        dst = os.path.join(exe_dir, "config.json")
        if os.path.exists(dst):
            return
        src = os.path.join(getattr(sys, "_MEIPASS", exe_dir), "config.example.json")
        if os.path.exists(src):
            with open(src, "rb") as f:
                data = f.read()
            with open(dst, "wb") as f:
                f.write(data)
    except Exception:
        pass                      # launcher tidak boleh gagal karena ini


def _start_server(port):
    import app as webapp
    webapp.app.run(host="127.0.0.1", port=port,
                   debug=False, use_reloader=False, threaded=True)


def _wait_ready(port, timeout=12):
    for _ in range(int(timeout / 0.2)):
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.2):
                return True
        except OSError:
            time.sleep(0.2)
    return False


def _find_browser_exe(candidates):
    for c in candidates:
        if os.path.exists(c):
            return c
    # cek registry App Paths sebagai cadangan
    try:
        import winreg
        for key in candidates:
            name = os.path.basename(key)
            for hive in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
                try:
                    with winreg.OpenKey(hive,
                                        r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\\" + name) as k:
                        val, _ = winreg.QueryValueEx(k, "")
                        if val and os.path.exists(val.strip('"')):
                            return val.strip('"')
                except OSError:
                    continue
    except Exception:
        pass
    return None


def _open_app_window(url):
    """Buka URL di jendela aplikasi. Return True kalau berhasil lewat
    pywebview ATAU Edge/Chrome app-mode; False = hanya browser default."""
    # 1) pywebview: jendela native (Edge WebView2)
    try:
        import webview
        webview.create_window("Nabla Workspace", url,
                              width=1366, height=768, min_size=(900, 600))
        webview.start()
        return True              # jendela ditutup user = selesai
    except Exception:
        pass                     # backend tidak jalan di mesin ini -> fallback

    # 2) Edge / Chrome app-mode: jendela standalone tanpa address bar/tab
    local = os.environ.get("LOCALAPPDATA", "")
    pf = os.environ.get("PROGRAMFILES", r"C:\Program Files")
    pf86 = os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)")
    edge = _find_browser_exe([
        os.path.join(local, r"Microsoft\Edge\Application\msedge.exe"),
        os.path.join(pf, r"Microsoft\Edge\Application\msedge.exe"),
        os.path.join(pf86, r"Microsoft\Edge\Application\msedge.exe"),
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ])
    chrome = _find_browser_exe([
        os.path.join(pf, r"Google\Chrome\Application\chrome.exe"),
        os.path.join(pf86, r"Google\Chrome\Application\chrome.exe"),
        os.path.join(local, r"Google\Chrome\Application\chrome.exe"),
    ])
    for exe in (edge, chrome):
        if exe:
            try:
                subprocess.Popen(
                    [exe, "--app=" + url,
                     "--window-size=1366,768",
                     "--user-data-dir=" + os.path.join(
                         os.environ.get("TEMP", "."), "NablaWorkspaceProfile")],
                    creationflags=0x08000000)   # CREATE_NO_WINDOW
                return True
            except Exception:
                continue

    # 3) pilihan terakhir: browser default
    webbrowser.open(url)
    return False


def main():
    _seed_config()
    port = _free_port()
    t = threading.Thread(target=_start_server, args=(port,), daemon=True)
    t.start()

    url = "http://127.0.0.1:%d/" % port
    ready = _wait_ready(port)
    # marker utk shell desktop (Electron): parse stdout, bukan tebak port
    print("NABLA_URL=%s" % url, flush=True)

    # mode headless: dipakai shell desktop (Electron) — server saja, tanpa
    # jendela; shell yang menampilkan GUI-nya. Server mati saat shell mati.
    if os.environ.get("NABLA_HEADLESS") == "1":
        try:
            while True:
                time.sleep(3600)
        except KeyboardInterrupt:
            pass
        return

    if not ready:
        # server gak siap-siap: tetap coba tampilkan (halaman error-nya pun UI)
        pass
    opened = _open_app_window(url)
    if not opened:
        # hanya browser default yang berhasil: tetap jaga server hidup
        try:
            while True:
                time.sleep(3600)
        except KeyboardInterrupt:
            pass
    # pywebview / app-mode: server thread daemon ikut mati saat proses selesai


if __name__ == "__main__":
    main()
