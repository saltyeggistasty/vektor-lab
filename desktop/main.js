/* =================================================================
   Nabla Workspace — shell desktop (Electron).
   Arsitektur ala VS Code/Discord: shell Chromium ter-bundle dgn GPU
   acceleration + server Python (sympy/numpy) sebagai HIDDEN SIDECAR.
   Shell menampilkan UI dari server localhost — semua tool tetap
   identik dgn versi web; tanpa internet sama sekali.
   ================================================================= */
const { app, BrowserWindow, Menu, shell, dialog } = require("electron");
const { spawn, exec } = require("child_process");
const path = require("path");
const fs = require("fs");

/* ---------- GPU acceleration: paksa pipeline hardware ---------- */
app.commandLine.appendSwitch("enable-gpu-rasterization");
app.commandLine.appendSwitch("enable-zero-copy");
app.commandLine.appendSwitch("ignore-gpu-blocklist");
app.commandLine.appendSwitch("enable-features", "CanvasOopRasterization");

let win = null;
let sidecar = null;
let sidecarUrl = null;
let quitting = false;

/* ---------- path sidecar (dev vs packaged) ---------- */
function sidecarDir() {
  if (app.isPackaged) {
    return path.join(process.resourcesPath, "sidecar");
  }
  // dev: folder build offline di root proyek
  return path.join(__dirname, "..", "Nabla Workspace x64 Offline", "Nabla Workspace");
}

function sidecarExe() {
  return path.join(sidecarDir(), "NablaWorkspace.exe");
}

/* ---------- jalankan sidecar server ---------- */
function startSidecar() {
  const exe = sidecarExe();
  if (!fs.existsSync(exe)) {
    dialog.showErrorBox(
      "Nabla Workspace",
      "Server lokal tidak ditemukan:\n" + exe +
      "\n\nPastikan seluruh folder utuh (jangan dipisah-pisah).");
    app.quit();
    return;
  }
  // NABLA_HEADLESS=1 -> sidecar hanya jadi server, tanpa jendela sendiri
  sidecar = spawn(exe, [], {
    cwd: sidecarDir(),
    env: Object.assign({}, process.env, { NABLA_HEADLESS: "1" }),
    windowsHide: true,
    stdio: ["ignore", "pipe", "pipe"],
  });
  /* stdout/stderr sidecar di-tee ke file log (diagnosa) + diparse */
  const logPath = path.join(sidecarDir(), "sidecar_log.txt");
  const logStream = fs.createWriteStream(logPath, { flags: "a" });
  logStream.write("\n=== sidecar start " + new Date().toISOString() + " ===\n");
  sidecar.stdout.on("data", (chunk) => {
    logStream.write(chunk);
    const line = String(chunk);
    const m = line.match(/NABLA_URL=(\S+)/);
    if (m && !sidecarUrl) {
      sidecarUrl = m[1];
      logStream.write(">>> shell menangkap URL: " + sidecarUrl + "\n");
      if (win && !win.isDestroyed()) win.loadURL(sidecarUrl);
    }
  });
  sidecar.stderr.on("data", (c) => logStream.write(c));
  sidecar.on("error", (e) => logStream.write(">>> spawn error: " + e + "\n"));
  sidecar.on("exit", (code) => {
    logStream.write(">>> sidecar exit code=" + code + "\n");
    logStream.end();
    if (!quitting && win && !win.isDestroyed()) {
      dialog.showErrorBox("Nabla Workspace",
        "Server lokal berhenti (code " + code + "). Tutup aplikasi lalu jalankan lagi.");
      app.quit();
    }
  });
}

/* ---------- GPU status -> file (verifikasi/penelusuran) ---------- */
function dumpGpuStatus() {
  try {
    const st = app.getGPUFeatureStatus();
    const dir = app.isPackaged ? path.dirname(app.getPath("exe")) : __dirname;
    fs.writeFileSync(path.join(dir, "gpu-status.json"),
      JSON.stringify({ status: st, version: app.getVersion(),
        electron: process.versions.electron, chrome: process.versions.chrome },
        null, 2));
  } catch (e) { /* tidak kritis */ }
}

/* ---------- jendela utama ---------- */
function createWindow() {
  win = new BrowserWindow({
    width: 1366,
    height: 768,
    minWidth: 900,
    minHeight: 600,
    backgroundColor: "#0d0b08",      // sehangat loading screen: gak ada kilat putih
    show: false,
    icon: path.join(__dirname, "icon.ico"),
    title: "Nabla Workspace",
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
      backgroundThrottling: false,   // simulasi jalan terus saat window blur
    },
  });

  // server belum pasti siap? tunggu marker NABLA_URL dr sidecar
  if (sidecarUrl) win.loadURL(sidecarUrl);

  win.once("ready-to-show", () => win.show());
  win.webContents.on("did-fail-load", (e, code, desc, url) => {
    // server belum siap saat window loading -> coba lagi (maks ~20x)
    if (sidecarUrl && code === -3 && !win.webContents.__retried) {
      win.webContents.__retried = (win.webContents.__retried || 0) + 1;
      if (win.webContents.__retried < 20)
        setTimeout(() => win.loadURL(sidecarUrl), 500);
    }
  });

  // link eksternal (kalau suatu saat ada) -> browser sistem, bukan window ini
  win.webContents.setWindowOpenHandler(({ url }) => {
    if (url.startsWith("http://127.0.0.1")) return { action: "allow" };
    shell.openExternal(url);
    return { action: "deny" };
  });

  win.on("closed", () => { win = null; });
}

/* ---------- menu native Windows ---------- */
function buildMenu() {
  const template = [
    {
      label: "Nabla",
      submenu: [
        { label: "Tentang Nabla Workspace", click: () => {
            dialog.showMessageBox(win, { type: "info", title: "Tentang",
              message: "Nabla Workspace — Desktop",
              detail: "Laboratorium matematika & fisika offline.\n" +
                      "Electron " + process.versions.electron + " · Chromium " +
                      process.versions.chrome + "\nSeluruh alat berjalan lokal; " +
                      "fitur AI opsional (butuh internet saat dipakai)." });
          } },
        { type: "separator" },
        { label: "Keluar", accelerator: "Ctrl+Q", click: () => app.quit() },
      ],
    },
    {
      label: "Tampilan",
      submenu: [
        { label: "Muat Ulang", accelerator: "F5",
          click: () => win && win.webContents.reload() },
        { label: "Perbesar", accelerator: "Ctrl+Plus",
          click: () => { if (win) win.webContents.zoomLevel += 0.5; } },
        { label: "Perkecil", accelerator: "Ctrl+-",
          click: () => { if (win) win.webContents.zoomLevel -= 0.5; } },
        { label: "Ukuran Normal", accelerator: "Ctrl+0",
          click: () => { if (win) win.webContents.zoomLevel = 0; } },
        { type: "separator" },
        { label: "Layar Penuh", accelerator: "F11",
          click: () => win && win.setFullScreen(!win.isFullScreen()) },
        { label: "DevTools", accelerator: "F12", enabled: !app.isPackaged,
          click: () => win && win.webContents.toggleDevTools() },
      ],
    },
  ];
  Menu.setApplicationMenu(Menu.buildFromTemplate(template));
}

/* ---------- single instance: klik exe kedua = fokus jendela pertama ---------- */
if (!app.requestSingleInstanceLock()) {
  app.quit();
} else {
  app.on("second-instance", () => {
    if (win) {
      if (win.isMinimized()) win.restore();
      win.focus();
    }
  });

  app.whenReady().then(() => {
    // GPU status utk verifikasi (hardware acceleration aktif?)
    app.whenReady().then(() => setTimeout(dumpGpuStatus, 3000));
    startSidecar();
    createWindow();
    buildMenu();
  });

  app.on("window-all-closed", () => app.quit());
  app.on("before-quit", () => {
    quitting = true;
    if (sidecar) {
      try { exec("taskkill /PID " + sidecar.pid + " /T /F"); } catch (e) {}
    }
  });
}
