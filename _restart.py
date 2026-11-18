# -*- coding: utf-8 -*-
import io, sys, subprocess, time, urllib.request
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
out = subprocess.run(
    ["wmic", "process", "where", "name='python.exe'", "get", "ProcessId,CommandLine"],
    capture_output=True, text=True).stdout
for l in out.splitlines():
    if "app.py" in l and "-I" not in l:
        pid = l.rsplit(None, 1)[-1].strip()
        if pid.isdigit():
            subprocess.run(["taskkill", "/F", "/PID", pid], capture_output=True)
time.sleep(2)
subprocess.Popen(
    [r"G:\vektor-lab(1)\vektor-lab\venv\Scripts\python.exe", "app.py"],
    cwd=r"G:\vektor-lab(1)\vektor-lab", creationflags=0x08000000)
for a in range(25):
    time.sleep(1)
    try:
        r = urllib.request.urlopen("http://127.0.0.1:5000/api/appinfo", timeout=10)
        print("server up:", r.read().decode()[:50])
        break
    except Exception:
        if a == 24:
            raise SystemExit("server gagal")
