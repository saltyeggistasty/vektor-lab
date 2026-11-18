/* Replikasi spawn sidecar persis seperti main.js — diagnosis. */
const { spawn } = require("child_process");
const path = require("path");
const base = "G:\\vektor-lab(1)\\vektor-lab";
const sc = path.join(base, "Nabla Workspace x64 Offline", "Nabla Workspace (Native)",
  "resources", "sidecar", "NablaWorkspace.exe");
const child = spawn(sc, [], {
  cwd: path.dirname(sc),
  env: Object.assign({}, process.env, { NABLA_HEADLESS: "1" }),
  windowsHide: true,
  stdio: ["ignore", "pipe", "pipe"],
});
let out = "", err = "";
child.stdout.on("data", (c) => { out += c; process.stdout.write("[OUT] " + c); });
child.stderr.on("data", (c) => { err += c; process.stdout.write("[ERR] " + c); });
child.on("exit", (code) => process.stdout.write("\n[EXIT] code=" + code + "\n"));
setTimeout(() => {
  process.stdout.write("\n=== ringkasan setelah 15s ===\n");
  process.stdout.write("NABLA_URL diterima: " + (out.match(/NABLA_URL=\S+/) || ["TIDAK ADA"])[0] + "\n");
  process.stdout.write("stderr len: " + err.length + "\n");
  process.exit(0);
}, 15000);
