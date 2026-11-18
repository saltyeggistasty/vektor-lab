const $ = (id) => document.getElementById(id);
const post = async (url, body) => {
  const r = await fetch(url, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(body),
  });
  const j = await r.json();
  if (!j.ok) {
    // bawa errKey/errArgs biar pesan bisa diterjemahkan & di-translate ulang
    const e = new Error(j.error || ((window.I18N && window.I18N.t("graph.error", "Terjadi kesalahan")) || "Terjadi kesalahan"));
    e.errKey = j.errKey;
    e.errArgs = j.errArgs;
    throw e;
  }
  return j.data;
};
const esc = (s) =>
  String(s).replace(/[&<>]/g, (c) => ({"&": "&amp;", "<": "&lt;", ">": "&gt;"}[c]));
const show = (id, on) => $(id).classList.toggle("hidden", !on);

// Helper to clean styling macros (like bold \bm, \mathbf, \mathrm, etc.)
const cleanLatex = (s) => {
  if (!s) return "";
  let res = s;
  const stylePattern =
    /\\(?:bm|boldsymbol|mathbf|textbf|mathit|textit|mathrm|textrm|text|mathsf|mathtt|mathbb|mathcal|mathscr|mathfrak|operatorname)\{([^{}]*)\}/g;
  while (stylePattern.test(res)) {
    res = res.replace(stylePattern, "$1");
  }
  return res
    .replace(
      /\\(?:boldmath|displaystyle|textstyle|scriptstyle|scriptscriptstyle|bf|it|rm|sf|tt)\b/g,
      ""
    )
    .replace(/\\,/g, " ")
    .replace(/\\:/g, " ")
    .replace(/\\;/g, " ")
    .trim();
};

// Helper to extract value from math-field or standard input
const getVal = (id) => {
  const el = $(id);
  if (!el) return "";
  const raw = (el.value || el.getValue?.() || el.textContent || "").trim();
  return cleanLatex(raw);
};

// ==================== COLOR PRESETS ====================
const COLOR_PRESETS = {
  gold: {
    name: "Golden Amber (Default)",
    scale: [
      [0, "#5b300d"],
      [0.35, "#a8662a"],
      [0.7, "#e0b04a"],
      [1, "#fff1b8"],
    ],
    curve: "#e0b04a",
    arrow: "#a8662a",
  },
  viridis: {
    name: "Viridis Multivariabel",
    scale: [
      [0, "#440154"],
      [0.25, "#3b528b"],
      [0.5, "#21918c"],
      [0.75, "#5ec962"],
      [1, "#fde725"],
    ],
    curve: "#21918c",
    arrow: "#5ec962",
  },
  plasma: {
    name: "Plasma Sunset",
    scale: [
      [0, "#0d0887"],
      [0.25, "#6a00a8"],
      [0.5, "#b12a90"],
      [0.75, "#e16462"],
      [1, "#fca636"],
    ],
    curve: "#b12a90",
    arrow: "#fca636",
  },
  rainbow: {
    name: "Rainbow / Turbo",
    scale: [
      [0, "#30123b"],
      [0.2, "#4686fb"],
      [0.4, "#1ae4b6"],
      [0.6, "#a2fc3c"],
      [0.8, "#faba39"],
      [1, "#7a0403"],
    ],
    curve: "#1ae4b6",
    arrow: "#4686fb",
  },
  neon: {
    name: "Cyberpunk Neon",
    scale: [
      [0, "#2b0938"],
      [0.3, "#3a0ca3"],
      [0.6, "#4361ee"],
      [0.85, "#4cc9f0"],
      [1, "#72efdd"],
    ],
    curve: "#4cc9f0",
    arrow: "#72efdd",
  },
  coolwarm: {
    name: "Coolwarm",
    scale: [
      [0, "#3b4cc0"],
      [0.35, "#8cb2e9"],
      [0.5, "#dddcdc"],
      [0.65, "#f49a7b"],
      [1, "#b40426"],
    ],
    curve: "#3b4cc0",
    arrow: "#b40426",
  },
  desmos: {
    name: "Desmos Crimson",
    scale: [
      [0, "#5e1515"],
      [0.5, "#b32a2a"],
      [1, "#e66060"],
    ],
    curve: "#b32a2a",
    arrow: "#e66060",
  },
};

const getActivePreset = () => {
  const p = $("colorPreset")?.value || localStorage.getItem("colorPreset") || "gold";
  return COLOR_PRESETS[p] || COLOR_PRESETS.gold;
};

// ==================== TABS ====================
document.querySelectorAll(".tab").forEach((b) => {
  b.onclick = () => {
    // layar bahasa (mode buka-ulang dr bar atas) masih aktif? cancel dulu,
    // tab yang diklik user harus langsung menang, overlay mengalah
    const ls = $("langSel");
    if (ls && ls.classList.contains("active") && window.I18N && I18N.cancelLangScreen)
      I18N.cancelLangScreen();
    // tombol bahasa: balik ke layar pemilih bahasa, bukan pindah panel
    if (b.id === "langTab") {
      if (window.warDonation) window.warDonation.close();  // jangan ketutupan overlay donasi
      if (window.warAbout) window.warAbout.close();
      if (window.I18N && window.I18N.openLangScreen) window.I18N.openLangScreen();
      return;
    }
    // tombol donasi: buka layar donasi (overlay), bukan pindah panel
    if (b.id === "donBtn") {
      if (window.warDownload) window.warDownload.close();  // jangan tumpuk overlay download
      if (window.warAbout) window.warAbout.close();        // ...atau overlay about
      if (window.warDonation) window.warDonation.open();
      return;
    }
    // tombol offline: toggle panel unduh (X di panel dihapus, jadi
    // klik tombol ini lagi = tutup)
    if (b.id === "dlBtn") {
      if (window.warDonation) window.warDonation.close();  // jangan tumpuk overlay donasi
      if (window.warAbout) window.warAbout.close();        // ...atau overlay about
      if (window.warDownload) window.warDownload.toggle();
      return;
    }
    // tombol about: toggle layar about us + form kritik/lapor bug
    if (b.id === "aboutBtn") {
      if (window.warDonation) window.warDonation.close();  // jangan tumpuk overlay donasi
      if (window.warDownload) window.warDownload.close();  // ...atau panel unduhan
      if (window.warAbout) window.warAbout.toggle();
      return;
    }
    const apply = () => {
      if (window.warDonation) window.warDonation.close();  // pindah tab = keluar dr page donasi
      if (window.warDownload) window.warDownload.close();  // ...dan dr panel unduhan
      if (window.warAbout) window.warAbout.close();        // ...dan dr layar about
      document.querySelectorAll(".tab").forEach((x) => x.classList.toggle("active", x === b));
      document
        .querySelectorAll(".panel-wrap")
        .forEach((p) => p.classList.toggle("active", p.id === b.dataset.tab));
      document.body.classList.remove("hud-show");
      // tab Matematika/Fisika = War Menu; reset subview balik ke menu
      if (window.warMath) window.warMath.resetMenu();
      if (window.warPhys) window.warPhys.resetMenu();
      document.body.classList.toggle("warfs",
        b.dataset.tab === "math" || b.dataset.tab === "physics");
      if (b.dataset.tab === "graph") Plotly.Plots.resize($("plot"));
      if (b.dataset.tab === "physics" && $("ppplot") && window.Plotly)
        Plotly.Plots.resize($("ppplot"));
    };
    // transisi ringan antar bidang (lightSwipe dr menu.js) — warp penuh
    // di panel war menu yang berat = stutter; ini swipe simpel + fade
    if (window.lightSwipe) window.lightSwipe(apply);
    else if (window.warpTo) window.warpTo(apply);
    else apply();
  };
});

// ==================== ACTIVE FIELD & MATHLIVE ====================
let activeField = $("f");
const fieldLabels = {
  f: "f(x, y, z)",
  P: "P(x, y, z)",
  Q: "Q(x, y, z)",
  R: "R(x, y, z)",
  gf: "z = f(x, y)",
  gP: "P",
  gQ: "Q",
  gR: "R",
  cx: "x(t)",
  cy: "y(t)",
  cz: "z(t)",
  pf: "f(x,y) permukaan",
  pP: "P(x,y,z)",
  pQ: "Q(x,y,z)",
  pR: "R(x,y,z)",
};

function setupActiveFields() {
  document.querySelectorAll("math-field").forEach((mf) => {
    const markActive = () => {
      activeField = mf;
      if ($("activeFieldName")) {
        $("activeFieldName").textContent = fieldLabels[mf.id] || mf.id;
      }
    };
    mf.addEventListener("focus", markActive);
    mf.addEventListener("click", markActive);
    mf.addEventListener("input", markActive);
    /* buang "Insert matrix" dari menu konteks: matriks di field kalkulus
       (integral/turunan/limit) cumalah bikin error — matriks pakai Matrix
       Calculator. Divider gantung di depannya ikut dibuang. */
    try {
      if (Array.isArray(mf.menuItems)) {
        let items = mf.menuItems.filter((it) => it && it.id !== "insert-matrix");
        items = items.filter((it, i) =>
          !(it && it.type === "divider" && items[i - 1] &&
            items[i - 1].type === "divider"));
        mf.menuItems = items;
      }
    } catch (e) { /* menu customization tidak tersedia: biarkan */ }
  });
}

// ==================== DESMOS VIRTUAL KEYPAD ====================
const keypad = $("mathKeypad");
const keypadToggle = $("keypadToggle");
const closeKeypad = $("closeKeypad");

function toggleKeypad(open) {
  const isCollapsed = keypad.classList.contains("collapsed");
  const shouldOpen = open !== undefined ? open : isCollapsed;
  keypad.classList.toggle("collapsed", !shouldOpen);
  keypadToggle.classList.toggle("active", shouldOpen);
}

if (keypadToggle) keypadToggle.onclick = () => toggleKeypad();
if (closeKeypad) closeKeypad.onclick = () => toggleKeypad(false);

// Keypad Tabs (123 / Functions)
document.querySelectorAll(".kp-tab").forEach((tab) => {
  tab.onclick = () => {
    document.querySelectorAll(".kp-tab").forEach((t) => t.classList.remove("active"));
    tab.classList.add("active");
    const target = tab.dataset.panel;
    document.querySelectorAll(".kp-panel").forEach((p) => {
      p.classList.toggle("active", p.id === "panel-" + target);
    });
  };
});

// Keypad Button Actions
document.querySelectorAll(".kbtn").forEach((btn) => {
  btn.addEventListener("click", (e) => {
    e.preventDefault();
    if (!activeField) {
      activeField = $("f") || $("gf");
    }
    activeField.focus();

    const ins = btn.dataset.insert;
    const cmd = btn.dataset.cmd;

    if (ins) {
      activeField.executeCommand(["insert", ins]);
    } else if (cmd === "power") {
      activeField.executeCommand(["insert", "^{#?}"]);
    } else if (cmd === "fraction") {
      activeField.executeCommand(["insert", "\\frac{#@}{#?}"]);
    } else if (cmd === "sqrt") {
      activeField.executeCommand(["insert", "\\sqrt{#?}"]);
    } else if (cmd === "abs") {
      activeField.executeCommand(["insert", "\\left|#?\\right|"]);
    } else if (cmd === "nroot") {
      activeField.executeCommand(["insert", "\\sqrt[#?]{#@}"]);
    } else if (cmd === "def_int") {
      activeField.executeCommand(["insert", "\\int_{#?}^{#?} #@ \\, d#?"]);
    } else if (cmd === "indef_int") {
      activeField.executeCommand(["insert", "\\int #@ \\, d#?"]);
    } else if (cmd === "deleteBackward") {
      activeField.executeCommand(["deleteBackward"]);
    } else if (cmd === "clear") {
      activeField.setValue("");
    } else if (cmd === "moveToPreviousChar") {
      activeField.executeCommand(["moveToPreviousChar"]);
    } else if (cmd === "moveToNextChar") {
      activeField.executeCommand(["moveToNextChar"]);
    }
  });
});

// Sanitasi copy-paste ke clipboard agar tidak ada koma sebelum simbol diferensial (misal saat paste ke Desmos)
document.addEventListener("copy", (e) => {
  const active = document.activeElement;
  if (active && active.tagName === "MATH-FIELD") {
    const val = active.value;
    if (val) {
      const cleaned = val
        .replace(/\s*(,|\\,)\s*(?=d[a-zA-Z]\b)/g, " ");
      if (e.clipboardData) {
        e.clipboardData.setData("text/plain", cleaned);
        e.clipboardData.setData("application/x-latex", cleaned);
        e.preventDefault();
      }
    }
  }
});

if ($("kpSubmit")) {
  $("kpSubmit").onclick = () => {
    // rute per panel aktif di DOM (bukan per tab, subview War Menu memindah panel)
    const vp = document.querySelector(".panel-wrap.active")?.id;
    if (vp === "physics") {
      if (!$("physLab").classList.contains("hidden") && window.physRun) window.physRun();
    } else if (vp === "graph") $("runGraph").click();
    else if (vp === "calc") $("runCalc").click();
    else if (vp === "tool") $("toolRun").click();
  };
}

// ==================== KALKULATOR ====================
const VECTOR_OPS = ["divergence", "curl", "jacobian"];
function syncOp() {
  const op = $("op").value;
  const vec = VECTOR_OPS.includes(op);
  show("vectorIn", vec);
  show("scalarIn", !vec);
  show("partialIn", op === "partial");
  show("dirIn", op === "directional");
}
$("op").onchange = syncOp;
syncOp();

const fmtNum = (v) => (v === null
  ? ((window.I18N && window.I18N.t("calc.undefined", "tidak terdefinisi")) || "tidak terdefinisi")
  : (+v.toPrecision(8)).toString());

/* terjemahkan potongan pesan error dari backend (app.py bahasa Indonesia);
   sisa daftar model/teks en API GAK disentuh */
/* error terakhir per elemen: ganti bahasa -> pesan ke-translate ulang */
const lastAppErr = new Map();          // el -> Error (dgn errKey/errArgs)
if (window.I18N && window.I18N.onChange) {
  window.I18N.onChange(() => {
    lastAppErr.forEach((e, el) => {
      if (!el || !el.isConnected) { lastAppErr.delete(el); return; }
      el.textContent = errText(e);
    });
  });
}

function errText(msgOrErr) {
  const tOrFail = (key, fb) => {
    try { return (window.I18N && window.I18N.t(key, fb)) || fb; } catch (e) { return fb; }
  };
  let m = "";
  let key = null, args = null;
  if (msgOrErr && typeof msgOrErr === "object") {
    m = String(msgOrErr.message || "");
    key = msgOrErr.errKey;
    args = msgOrErr.errArgs;
  } else {
    m = String(msgOrErr || "");
  }
  if (key) {
    let s = tOrFail(key, m);
    (args || []).forEach((a, i) => { s = s.split("{" + i + "}").join(a); });
    return s;
  }
  const RULES = [
    ["Input tidak valid:", "err.err_invalid", "Input tidak valid:"],
    ["Semua model gagal menafsirkan hasil.", "err.err_models", "Semua model gagal menafsirkan hasil."],
  ];
  for (const [ru, key2, fb] of RULES) {
    const i = m.indexOf(ru);
    if (i >= 0) m = m.slice(0, i) + tOrFail(key2, fb) + m.slice(i + ru.length);
  }
  return m;
}

function renderLatex(tex, display = true) {
  if (window.katex) {
    try {
      return window.katex.renderToString(tex, {
        displayMode: display,
        throwOnError: false,
      });
    } catch (e) {}
  }
  return `<span class="expr">${esc(tex)}</span>`;
}

function renderResult(d) {
  let labelHtml = d.label_latex
    ? renderLatex(d.label_latex, false)
    : `<div class="res-label">${esc(d.label)}</div>`;

  let h = `<div class="res-label">${labelHtml}</div>`;

  if (d.kind === "scalar") {
    const tex = d.latex || d.result;
    h += `<div class="math-res-box">${renderLatex(tex, true)}</div>`;
  } else if (d.kind === "vector") {
    const comps = d.latex || d.result;
    const tex = `\\left\\langle ${comps.join(",\\; ")} \\right\\rangle`;
    h += `<div class="math-res-box">${renderLatex(tex, true)}</div>`;
  } else {
    // matrix
    const rows = d.latex || d.result;
    const tex = `\\begin{bmatrix} ${rows.map((r) => r.join(" & ")).join(" \\\\ ")} \\end{bmatrix}`;
    h += `<div class="math-res-box">${renderLatex(tex, true)}</div>`;
  }

  if (d.at_point !== undefined) {
    const p = d.at_point;
    let s;
    if (d.kind === "matrix") {
      const tex = `\\begin{bmatrix} ${p
        .map((r) => r.map(fmtNum).join(" & "))
        .join(" \\\\ ")} \\end{bmatrix}`;
      s = `<div class="math-res-box">${renderLatex(tex, true)}</div>`;
    } else if (d.kind === "vector") {
      const tex = `\\left\\langle ${p.map(fmtNum).join(",\\; ")} \\right\\rangle`;
      s = `<div class="math-res-box">${renderLatex(tex, true)}</div>`;
    } else {
      s = `<div class="math-res-box">${renderLatex(fmtNum(p), true)}</div>`;
    }
    h += `<div class="sub">${(window.I18N && window.I18N.t("calc.at_point", "Nilai di titik")) || "Nilai di titik"} (${[0, 1, 2]
      .map((i) => $("p" + i).value)
      .join(", ")}):</div>${s}`;
  }

  $("resultBody").className = "";
  $("resultBody").innerHTML = h;
}

$("runCalc").onclick = async () => {
  const op = $("op").value;
  const body = {
    op,
    f: getVal("f"),
    F: [getVal("P"), getVal("Q"), getVal("R")],
    var: $("pvar").value,
    order: +$("order").value,
    direction: [$("d0").value, $("d1").value, $("d2").value],
  };
  if ($("usePt").checked || op === "directional") {
    body.point = [$("p0").value, $("p1").value, $("p2").value];
  }
  if (op === "directional" && !$("usePt").checked) $("usePt").checked = true;

  try {
    renderResult(await post("/api/calc", body));
  } catch (e) {
    $("resultBody").className = "err";
    $("resultBody").textContent = errText(e);
    lastAppErr.set($("resultBody"), e);
  }
};

// ==================== GRAFIK 3D ====================
const theme = () => document.documentElement.dataset.theme || "gold";
const css = (v) => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
let last = null; // { traces, bounds }

// Layout bersih tanpa spikes / spikelines saat kursor diarahkan ke manifold
function layout() {
  const txt = css("--cream");
  const grid =
    theme() === "light" ? "#d8c9a6" : theme() === "black" ? "#444" : "#5a3f26";
  const bgc =
    theme() === "light" ? "#fbf3df" : theme() === "black" ? "#000" : "#1d130b";

  const ax = (k) => ({
    title: {text: k, font: {size: 16, color: txt}},
    backgroundcolor: bgc,
    gridcolor: grid,
    showbackground: true,
    zeroline: false,
    linecolor: txt,
    tickfont: {color: txt, size: 11},
    color: txt,
    // Garis penunjuk sumbu saat cursor mengarah ke manifold (rapi, terarah, tidak bloated):
    showspikes: true,
    spikesides: false,
    spikethickness: 1.5,
    spikecolor: theme() === "light" ? "#8a5a0c" : "#e0b04a",
    spikemode: "toaxis",
    showline: true,
  });

  return {
    paper_bgcolor: "rgba(0,0,0,0)",
    font: {color: txt},
    margin: {l: 0, r: 0, t: 10, b: 0},
    showlegend: false,
    hovermode: "closest",
    scene: {
      xaxis: ax("x"),
      yaxis: ax("y"),
      zaxis: ax("z"),
      aspectmode: "cube",
    },
  };
}

// Layout 2D untuk tool plots: warna ikut tema web (light/dark/golden),
// dragmode PAN (bisa geser graph dgn cursor) + scrollZoom via config.
function layout2d() {
  const txt = css("--cream");
  const grid =
    theme() === "light" ? "#d8c9a6" : theme() === "black" ? "#444" : "#5a3f26";
  const bg =
    theme() === "light" ? "#fbf3df" : theme() === "black" ? "#0a0a0a" : "#1d130b";
  const axis = {
    gridcolor: grid,
    zerolinecolor: grid,
    linecolor: grid,
    tickfont: {color: txt, size: 11},
    title: {font: {size: 13, color: txt}},
  };
  return {
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: bg,
    font: {color: txt},
    margin: {l: 58, r: 18, t: 14, b: 46},
    showlegend: false,
    hovermode: "closest",
    dragmode: "pan",
    xaxis: {...axis},
    yaxis: {...axis},
  };
}

// ==================== 3D COORDINATE AXES WITH ARROWS ====================
function buildAxesArrows(bounds) {
  if (!$("showAxesArrows")?.checked) return [];

  const {xmin, xmax, ymin, ymax, zmin, zmax} = bounds;
  const lx = Math.max(Math.abs(xmin), Math.abs(xmax), 1) * 1.15;
  const ly = Math.max(Math.abs(ymin), Math.abs(ymax), 1) * 1.15;
  const lz = Math.max(Math.abs(zmin), Math.abs(zmax), 1) * 1.15;

  const axisCol = css("--gold") || "#e0b04a";
  const dimCol =
    theme() === "light" ? "#b39c6b" : theme() === "black" ? "#888" : "#845e36";

  // Sumbu garis (X, Y, Z) dengan hoverinfo: 'none'
  const axisLines = {
    type: "scatter3d",
    mode: "lines",
    x: [-lx * 0.95, lx, null, 0, 0, null, 0, 0],
    y: [0, 0, null, -ly * 0.95, ly, null, 0, 0],
    z: [0, 0, null, 0, 0, null, -lz * 0.95, lz],
    line: {color: dimCol, width: 4.5},
    hoverinfo: "none",
    _role: "axisLines",
  };

  // Panah kerucut 3D di ujung sumbu positif (+X, +Y, +Z)
  const axisCones = {
    type: "cone",
    x: [lx, 0, 0],
    y: [0, ly, 0],
    z: [0, 0, lz],
    u: [1, 0, 0],
    v: [0, 1, 0],
    w: [0, 0, 1],
    sizemode: "scaled",
    sizeref: 0.16,
    anchor: "tip",
    colorscale: [
      [0, axisCol],
      [1, axisCol],
    ],
    showscale: false,
    hoverinfo: "none",
    _role: "axisCones",
  };

  // Label huruf teks di ujung panah (X, Y, Z)
  const axisLabels = {
    type: "scatter3d",
    mode: "text",
    x: [lx * 1.14, 0, 0],
    y: [0, ly * 1.14, 0],
    z: [0, 0, lz * 1.14],
    text: ["<b>X</b>", "<b>Y</b>", "<b>Z</b>"],
    textposition: "middle center",
    textfont: {size: 15, color: axisCol, family: "Inter, sans-serif"},
    hoverinfo: "none",
    _role: "axisLabels",
  };

  return [axisLines, axisCones, axisLabels];
}

function draw() {
  if (!last) return;
  const preset = getActivePreset();
  const axisCol = css("--gold") || "#e0b04a";

  // Terapkan skema warna preset ke traces
  const mainTraces = last.rawTraces.map((t) => {
    if (t._role === "surface") {
      return {
        ...t,
        colorscale: preset.scale,
        // Garis penunjuk kontur ketinggian saat kursor menunjuk point
        contours: {
          x: {show: false, highlight: false},
          y: {show: false, highlight: false},
          z: {
            show: true,
            usecolormap: true,
            highlight: true,
            highlightcolor: "#ffffff",
            highlightwidth: 2.2,
            project: {x: false, y: false, z: false},
          },
        },
        hoverinfo: "x+y+z",
        hovertemplate: "<b>x:</b> %{x:.3f}<br><b>y:</b> %{y:.3f}<br><b>z:</b> %{z:.3f}<extra></extra>",
      };
    } else if (t._role === "field") {
      return {
        ...t,
        colorscale: preset.scale,
        hoverinfo: "x+y+z",
      };
    } else if (t._role === "curve") {
      return {
        ...t,
        line: {...t.line, color: preset.curve},
      };
    } else if (t._role === "grad") {
      return {
        ...t,
        colorscale: [
          [0, preset.arrow],
          [1, preset.arrow],
        ],
      };
    }
    return t;
  });

  const axisTraces = buildAxesArrows(last.bounds);
  const finalTraces = [...mainTraces, ...axisTraces];

  Plotly.react("plot", finalTraces, layout(), {
    responsive: true,
    displaylogo: false,
  });
}

function calculateBounds(traces, t) {
  let xmin = -5, xmax = 5, ymin = -5, ymax = 5, zmin = -5, zmax = 5;
  if (t === "surface") {
    xmin = +$("xmin").value || -6;
    xmax = +$("xmax").value || 6;
    ymin = +$("ymin").value || -6;
    ymax = +$("ymax").value || 6;
    const surf = traces.find((x) => x.type === "surface");
    if (surf && surf.z) {
      const flatZ = surf.z.flat().filter((v) => v !== null && isFinite(v));
      if (flatZ.length) {
        zmin = Math.min(...flatZ);
        zmax = Math.max(...flatZ);
      }
    }
  } else if (t === "field") {
    const fmin = +$("fmin").value || -2;
    const fmax = +$("fmax").value || 2;
    xmin = fmin; xmax = fmax;
    ymin = fmin; ymax = fmax;
    zmin = fmin; zmax = fmax;
  } else {
    // curve
    const c = traces.find((x) => x.type === "scatter3d");
    if (c) {
      const getMinMax = (arr) => {
        const f = arr.filter((v) => v !== null && isFinite(v));
        return f.length ? [Math.min(...f), Math.max(...f)] : [-2, 2];
      };
      [xmin, xmax] = getMinMax(c.x);
      [ymin, ymax] = getMinMax(c.y);
      [zmin, zmax] = getMinMax(c.z);
    }
  }
  return {xmin, xmax, ymin, ymax, zmin, zmax};
}

// Tema
function setTheme(t) {
  document.documentElement.dataset.theme = t;
  try {
    localStorage.setItem("theme", t);
  } catch (e) {}
  document
    .querySelectorAll("#themeSw button")
    .forEach((b) => b.classList.toggle("active", b.dataset.t === t));
  draw();
  if (window.physTheme) window.physTheme();   // tab fisika ikut re-render (#ppplot)
  if (window.toolThemeRefresh) window.toolThemeRefresh(); // tool plots ikut tema
}
document
  .querySelectorAll("#themeSw button")
  .forEach((b) => (b.onclick = () => setTheme(b.dataset.t)));

function syncGraph() {
  const t = $("gtype").value;
  ["surface", "field", "curve"].forEach((k) => show("g-" + k, k === t));
}
$("gtype").onchange = syncGraph;

// Preset Warna Listener
if ($("colorPreset")) {
  const savedPreset = localStorage.getItem("colorPreset");
  if (savedPreset && COLOR_PRESETS[savedPreset]) {
    $("colorPreset").value = savedPreset;
  }
  $("colorPreset").onchange = () => {
    try {
      localStorage.setItem("colorPreset", $("colorPreset").value);
    } catch (e) {}
    draw();
    if (window.physPresetSync) window.physPresetSync($("colorPreset").value);
  };
}

if ($("showAxesArrows")) {
  $("showAxesArrows").onchange = () => draw();
}

$("runGraph").onclick = async () => {
  const t = $("gtype").value;
  $("graphMsg").textContent = (window.I18N && window.I18N.t("graph.calculating", "Menghitung…")) || "Menghitung…";
  $("graphMsg").className = "hint";
  const preset = getActivePreset();

  try {
    let rawTraces = [];
    if (t === "surface") {
      const d = await post("/api/surface", {
        f: getVal("gf"),
        xmin: $("xmin").value,
        xmax: $("xmax").value,
        ymin: $("ymin").value,
        ymax: $("ymax").value,
        n: 70,
      });

      rawTraces = [
        {
          type: "surface",
          x: d.x,
          y: d.y,
          z: d.z,
          colorscale: preset.scale,
          contours: {
            x: {show: false, highlight: false},
            y: {show: false, highlight: false},
            z: {
              show: true,
              usecolormap: true,
              highlight: true,
              highlightcolor: "#ffffff",
              highlightwidth: 2.2,
              project: {x: false, y: false, z: false},
            },
          },
          colorbar: {thickness: 12},
          hoverinfo: "x+y+z",
          hovertemplate: "<b>x:</b> %{x:.3f}<br><b>y:</b> %{y:.3f}<br><b>z:</b> %{z:.3f}<extra></extra>",
          _role: "surface",
        },
      ];

      if ($("showGrad").checked) {
        const g = await gradField();
        if (g) rawTraces.push(g);
      }
    } else if (t === "field") {
      const d = await post("/api/field", {
        F: [getVal("gP"), getVal("gQ"), getVal("gR")],
        min: $("fmin").value,
        max: $("fmax").value,
        n: $("fn").value,
      });
      rawTraces = [
        {
          type: "cone",
          x: d.x,
          y: d.y,
          z: d.z,
          u: d.u,
          v: d.v,
          w: d.w,
          colorscale: preset.scale,
          sizemode: "scaled",
          sizeref: 0.8,
          anchor: "tail",
          colorbar: {thickness: 12},
          hoverinfo: "x+y+z",
          _role: "field",
        },
      ];
    } else {
      const d = await post("/api/curve", {
        r: [getVal("cx"), getVal("cy"), getVal("cz")],
        tmin: $("tmin").value,
        tmax: $("tmax").value,
        n: 600,
      });
      rawTraces = [
        {
          type: "scatter3d",
          mode: "lines",
          x: d.x,
          y: d.y,
          z: d.z,
          line: {width: 6, color: preset.curve},
          _role: "curve",
        },
      ];
    }

    const bounds = calculateBounds(rawTraces, t);
    last = {rawTraces, bounds};
    draw();
    $("graphMsg").textContent = "";
  } catch (e) {
    $("graphMsg").textContent = errText(e);
    lastAppErr.set($("graphMsg"), e);
    $("graphMsg").className = "hint err";
  }
};

async function gradField() {
  const f = getVal("gf");
  const g = await post("/api/calc", {op: "gradient", f});
  const lo = Math.max(+$("xmin").value, +$("ymin").value);
  const hi = Math.min(+$("xmax").value, +$("ymax").value);
  const d = await post("/api/field", {
    F: [g.result[0], g.result[1], "0"],
    min: lo,
    max: hi,
    n: 8,
  });
  const idx = d.z
    .map((z, i) => i)
    .filter((i) => Math.abs(d.z[i] - d.z[0]) < 1e-9);
  const pick = (k) => idx.map((i) => d[k][i]);
  const arrowCol = getActivePreset().arrow;
  return {
    type: "cone",
    x: pick("x"),
    y: pick("y"),
    z: pick("z"),
    u: pick("u"),
    v: pick("v"),
    w: pick("w"),
    colorscale: [
      [0, arrowCol],
      [1, arrowCol],
    ],
    showscale: false,
    sizemode: "scaled",
    sizeref: 0.6,
    anchor: "tail",
    _role: "grad",
  };
}

// Inisialisasi
setupActiveFields();
syncGraph();
setTheme(theme());
$("runGraph").click();
