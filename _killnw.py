# -*- coding: utf-8 -*-
import io, sys, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
out = subprocess.run(
    ["wmic", "process", "where", "name='NablaWorkspace.exe'", "get", "ProcessId"],
    capture_output=True, text=True).stdout
for l in out.splitlines():
    pid = l.strip()
    if pid.isdigit():
        subprocess.run(["taskkill", "/F", "/PID", pid, "/T"], capture_output=True)
        print("killed", pid)
