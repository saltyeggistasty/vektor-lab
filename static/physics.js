/* ============================================================
   PHYSICS TAB — Simulasi Fluks Listrik Monte Carlo
   Modul frontend terpisah; memakai helper global dari app.js:
   $, post, getVal, esc, show, layout(), theme(), css(), renderLatex()
   ============================================================ */

const PHYS_HELP = {
  catalog: {
    t: "Katalog Simulasi",
    b: "Kumpulan eksperimen siap pakai. Tiap item mengisi otomatis bentuk permukaan, medan, dan domain, lalu lu bebas utak-atik lagi. <b>ELI5:</b> seperti menu paket di restoran, tinggal pilih, bisa dimodifikasi sesuai selera.",
  },
  surface: {
    t: "Permukaan z = f(x,y)",
    b: "Bentuk \"topografi\" permukaan yang dilewati medan listrik. <b>ELI5:</b> bayangkan selembar kain yang ditarik naik-turun; f(x,y) adalah tinggi kain itu di setiap titik (x,y). Permukaan datar berarti f = 0, bukit berarti f = exp(-x^2-y^2), dst. Matematikanya disebut <i>manifold 2D di ruang 3D</i>.",
  },
  domain: {
    t: "Domain (meter)",
    b: "Hamparan tanah di bawah permukaan tempat Monte Carlo \"melempar dadu\" menaruh titik sampel. <b>Satuan meter (SI)</b>, jadi luas domain dx·dy langsung dalam m².<br><b>ELI5:</b> ini peta area yang lu pilih untuk percobaan; makin luas makin banyak fluks yang kena.",
  },
  field: {
    t: "Medan Listrik E(x,y,z)",
    b: "Medan listrik = \"angin\" yang mendorong muatan +1 C kecil. Satuannya <b>N/C</b> (newton per coulomb), sama dengan <b>V/m</b>.<br><b>ELI5:</b> kalau lu taruh muatan 1 C di suatu titik, medan 500 N/C berarti ia ditarik/ditekan sebesar 500 newton.",
  },
  fieldmode: {
    t: "Jenis Medan",
    b: "<b>Seragam (uniform):</b> kuat &amp; arah sama di mana-mana, seperti angin konstan, mudah dipahami, bagus buat belajar fluks dasar.<br><b>Muatan titik:</b> medan menyebar radial dari satu muatan, kuat menurun 1/r² (hukum Coulomb).<br><b>Rumus bebas:</b> lu tulis sendiri komponen medan P, Q, R sebagai fungsi x, y, z.",
  },
  strength: {
    t: "Kuat Medan E₀ (N/C)",
    b: "Seberapa \"keras\" medannya, dalam newton per coulomb.<br><b>ELI5:</b> anggap E₀ = tebal hujan (lebat/tipis). Referensi: cuaca berawan ~100 N/C, rumah ~100 sampai 300 N/C, kolконdor... eh, petir badai dapat ribuan N/C. <b>Makin kuat medan, makin banyak fluks menembus permukaan (Φ ∝ E).</b>",
  },
  direction: {
    t: "Arah Medan & Flux",
    b: "Arah panah medan listrik (3D). <b>ELI5:</b> hujan bisa jatuh lurus ke atas kepala (+z), miring dari depan, atau dari samping. Fluks paling besar kalau medan <i>tegak lurus</i> permukaan; kalau medan <i>selari</i> permukaan (menggeser), fluksnya nol karena tak ada yang \"menembus\". Rumus: Φ pakai komponen medan yang searah normal permukaan.",
  },
  charge: {
    t: "Muatan Sumber Q (nC)",
    b: "Besar muatan titik yang jadi sumber medan, dalam <b>nano-coulomb</b> (10⁻⁹ C). Medannya E = kQ/r² dengan k = 8,99×10⁹ N·m²/C².<br><b>ELI5:</b> muatan seperti keran air; makin besar Q makin deras aliran medan keluar. 5 nC masih \"aman\", tapi ingat 5 C itu besar banget (petir level).",
  },
  chargepos: {
    t: "Posisi Muatan (x₀,y₀,z₀)",
    b: "Lokasi muatan sumber dalam meter. <b>Penting:</b> jangan letakkan di (atau di dalam) permukaan, medan 1/r² meledak tak hingga, Monte Carlo bisa jadi tidak valid.<br><b>ELI5:</b> letakkan balon listrik itu di udara, jangan nempel di tengah permukaannya.",
  },
  customfield: {
    t: "Komponen Medan P, Q, R (N/C)",
    b: "Medan vektor bebas: E = ⟨P, Q, R⟩ fungsi (x,y,z), satuan N/C. Contoh: ⟨−y, x, 0⟩ medan berputar; ⟨0, 0, 1⟩ angin ke atas; medan muatan di (0,0,2): ⟨k(x−x₀), k(y−y₀), k(z−z₀)⟩/r³ dirikan sendiri.<br><b>ELI5:</b> ini papan kontrol pro: lu bisa bikin medan munter bentuk apa pun, sepanjang dalam N/C.",
  },
  flip: {
    t: "Arah Flux / Normal n̂",
    b: "Fluks punya tanda tergantung orientasi permukaan. Normal +z berarti keluar \"ke atas\".<br><b>ELI5:</b> seperti memilih menghadapkan jendela ke dalam atau ke luar: hujan masuk jadi +, keluar jadi −. Total nilai Φ berubah tanda, tapi \"seberapa banyak\" garis medan menembus tetap sama besarnya.",
  },
  mc: {
    t: "Mesin Monte Carlo",
    b: "Alih-alih menghitung integral simbolik (susah untuk permukaan rumit), kita <b>lempar N titik acak</b> di domain, hitung kontribusi fluks masing-masing g = −P·fₓ − Q·f_y + R di titik itu, lalu rata-rata: Φ ≈ (Luas domain)·mean(g).<br><b>ELI5:</b> mau tahu banyaknya air yang jatuh di taman berbentuk aneh? Titipin N ember acak di seluruh taman, ukur, terus rata-rata.",
  },
  samples: {
    t: "Jumlah Sampel N",
    b: "Berapa banyak titik acak. Error menurun ~<b>1/√N</b>: 100× N berarti error hanya turun 10×.<br><b>ELI5:</b> makin banyak lemparan dadu, makin dekat hasil ke kebenaran. 100.000 lemparan biasanya cukup akurat ~0,3%; butuh sangat akurat? naikin N.",
  },
  seed: {
    t: "Seed (benih acak)",
    b: "Angka awal mesin acak. Dengan seed sama, hasil simulasi bisa diulang persis.<br><b>ELI5:</b> seperti film yang bisa di-<i>rewind</i>: percobaan jadi bisa direplikasi ilmiah. Kosongkan kalau mau hasil beda tiap jalan.",
  },
  ai: {
    t: "Cara kerja AI di sini",
    b: "Lu tulis skenario bebas → teks dikirim ke LLM (OpenRouter, key ada di <code>config.json</code>) → AI mengembalikan JSON konfigurasi (permukaan, medan, domain, arah flux) → backend memvalidasi rumus &amp; angka secara matematis (AI tidak bisa menyuntik kode) → parameter diisi ke form → simulasi Monte Carlo dijalankan modul Python.<br><b>ELI5:</b> AI itu asisten juru ketik pintar; yang menghitung tetap kalkulator fisika di backend.",
  },
};

const PHYS_PRESETS = {
  plate: {
    name: "Pelat Ombak sin(x²+y²) + Medan Seragam",
    desc: "Permukaan z = sin(x²+y²) di domain x, y dari -1 sampai 1 m, ditembus medan 1 N/C arah komponen (1,1,1). Suku kemiringan ganjil (2x, 2y) habis saat integrasi simetris, jadi fluks = E₀·(A/√3) = 4/√3 ≈ 2,31 N·m²/C, pas buat cek akurasi Monte Carlo.",
    f: "sin(x^2+y^2)", x0: "-1", x1: "1", y0: "-1", y1: "1",
    mode: "uniform", e0: "1", dir: "custom", da: "1", db: "1", dc: "1",
    flip: false, cat: "",
  },
  wave: {
    name: "Permukaan Gelombang + Medan Vertikal",
    desc: "Laut bergelombang z = 0.5·sin(x)·cos(y) di pesona angin ke atas 300 N/C. Fluks ≈ E₀·A proyeksi = 300×36 = 10800 N·m²/C, gelombang tak mengubah total (teorema proyeksi), tapi puncak/lautan lembah terlihat lebih keramat di peta warna.",
    f: "0.5*sin(x)*cos(y)", x0: "-3", x1: "3", y0: "-3", y1: "3",
    mode: "uniform", e0: "300", dir: "zplus", da: "0", db: "0", dc: "1",
    flip: false, cat: "",
  },
  point: {
    name: "Muatan Titik di Atas Pelat",
    desc: "Muatan 5 nC menggantung 2 m di atas pelat 16×16 m. Hukum Gauss: fluks pelat = Q/(2ε₀)·(fraksi sudut padat) ≈ 220 N·m²/C untuk domain ini; muatan setengah ruang penuh = Q/(2ε₀).",
    f: "0", x0: "-8", x1: "8", y0: "-8", y1: "8",
    mode: "point", qnc: "5", qx: "0", qy: "0", qz: "2",
    flip: false, cat: "",
  },
  parab: {
    name: "Cekungan Paraboloid + Medan Miring",
    desc: "Cekung z = 0.35(x²+y²) kena medan 200 N/C miring arah (1,1,1). Lihat suku −P·fₓ dan −Q·f_y ikut bermain: kemiringan permukaan menangkap komponen medan horizontal.",
    f: "0.35*(x^2+y^2)", x0: "-2", x1: "2", y0: "-2", y1: "2",
    mode: "uniform", e0: "200", dir: "custom", da: "1", db: "1", dc: "1",
    flip: false, cat: "",
  },
  hill: {
    name: "Bukit Gaussian + Hujan Medan Vertikal",
    desc: "Bukit z = 3·exp(−x²−y²) hujan medan 100 N/C vertikal. Teorema proyeksi: tanpa komponen horizontal, Φ = E₀·(luas proyeksi) = 100·36 = 3600 N·m²/C, tinggi bukit tak pengaruh total!",
    f: "3*exp(-(x^2+y^2))", x0: "-3", x1: "3", y0: "-3", y1: "3",
    mode: "uniform", e0: "100", dir: "zplus", da: "0", db: "0", dc: "1",
    flip: false, cat: "",
  },
};

/* ---------- angka ---------- */
const SI_PREF = [
  [1e9, "G"], [1e6, "M"], [1e3, "k"], [1, ""],
  [1e-3, "m"], [1e-6, "\u00b5"], [1e-9, "n"], [1e-12, "p"],
];

function fmtSI(v, unit) {
  if (v === null || v === undefined || !isFinite(v)) return "";
  const rnd = (x) => {
    let s = (+x.toPrecision(4)).toString();
    if (s.includes("e")) s = plainNum(+s);
    return s;
  };
  const a = Math.abs(v);
  if (a === 0) return `0 ${unit || ""}`.trim();
  for (const [f, p] of SI_PREF) {
    if (a >= f) return `${rnd(v / f)} ${p}${unit || ""}`.trim();
  }
  return `${rnd(v)} ${unit || ""}`.trim();
}

function stripTrail(s) {
  if (s.includes(".")) return s.replace(/(\.\d*?)0+$/, "$1").replace(/\.$/, "");
  return s;
}

function num0(id, dflt) {
  const v = parseFloat($(id)?.value ?? "");
  return isFinite(v) ? v : dflt;
}

/* desimal murni (tanpa notasi e) supaya backend aman */
function plainNum(v) {
  const n = (typeof v === "number") ? v : parseFloat(v);
  if (!isFinite(n)) return "0";
  let s = String(n);
  if (!s.includes("e")) return s;
  const [man, exp] = s.split("e");
  const E = parseInt(exp, 10);
  const [int, frac = ""] = man.replace("-", "").split(".");
  let sign = man.startsWith("-") ? "-" : "";
  let digits = (int + frac).replace(/^0+/, "");
  let pt = int.replace(/^0+/, "").length + E;
  if (pt <= 0) {
    // 0.000xxx
    let zeros = "";
    for (let i = 0; i < -pt; i++) zeros += "0";
    return sign + "0." + zeros + digits;
  }
  if (pt >= digits.length) {
    for (let i = digits.length; i < pt; i++) digits += "0";
    return sign + digits;
  }
  return sign + digits.slice(0, pt) + "." + digits.slice(pt);
}

/* ---------- help pop-up (ELI5) ---------- */
const helpPop = document.createElement("div");
helpPop.className = "help-pop hidden";
document.body.appendChild(helpPop);

function openHelp(key, btn) {
  const h = PHYS_HELP[key];
  if (!h) return;
  const head = t9("help." + key + ".t", h.t);
  const body = t9("help." + key + ".b", h.b);
  helpPop.innerHTML = `<div class="hp-h"><span>${head}</span><button class="hp-x">✕</button></div><div class="hp-b">${body}</div>`;
  helpPop.classList.remove("hidden");
  const r = btn.getBoundingClientRect();
  helpPop.style.visibility = "hidden";
  helpPop.style.display = "block";
  const w = helpPop.offsetWidth, hh = helpPop.offsetHeight;
  let left = Math.min(Math.max(8, r.left), window.innerWidth - w - 12);
  let top = r.bottom + 8;
  if (top + hh > window.innerHeight - 12) top = Math.max(8, r.top - hh - 8);
  helpPop.style.left = left + "px";
  helpPop.style.top = top + "px";
  helpPop.style.visibility = "";
  helpPop.querySelector(".hp-x").onclick = () => helpPop.classList.add("hidden");
  if (window.katex) {
    try { window.renderMathInElement?.(helpPop, {delimiters: [
      {left: "\\(", right: "\\)", display: false},
      {left: "\\[", right: "\\]", display: true},
    ]}); } catch (e) {}
  }
}

document.addEventListener("click", (e) => {
  const tip = e.target.closest(".help-tip");
  if (tip) { openHelp(tip.dataset.help, tip); e.preventDefault(); return; }
  if (!e.target.closest(".help-pop")) helpPop.classList.add("hidden");
});

/* ---------- UI sink .......... ---------- */
function syncPhysMode() {
  const m = $("fmode").value;
  show("u-in", m === "uniform");
  show("pt-in", m === "point");
  show("cu-in", m === "custom");
  show("dirCustom", $("pdir").value === "custom");
  // Kontrak detail dua arah: konten aktif = detail terbuka.
  const advC = $("advCustom"), advD = $("advDir");
  if (advC) {
    advC.classList.toggle("hidden", m !== "custom"); // mode lain: jangan tinggalkan kotak kosong
    if (m === "custom") advC.open = true;
  }
  if (advD) {
    if ($("pdir").value === "custom") advD.open = true;
    else advD.open = false;
  }
}

/* Detail jadi pintu dua arah: MEMBUKANYA = memakai mode itu,
   jadi tidak pernah ada detail terbuka dengan isian tersembunyi. */
if ($("advDir")) {
  $("advDir").addEventListener("toggle", () => {
    if ($("advDir").open && $("pdir").value !== "custom") {
      $("pdir").value = "custom";
      syncPhysMode();
    }
  });
}
if ($("advCustom")) {
  $("advCustom").addEventListener("toggle", () => {
    if ($("advCustom").open && $("fmode").value !== "custom") {
      $("fmode").value = "custom";
      syncPhysMode();
    }
  });
}
if ($("fmode")) {
  $("fmode").onchange = syncPhysMode;
  $("pdir").onchange = syncPhysMode;
  syncPhysMode();
}

/* ---------- katalog: desc kecil di bawah select dibuang per request ---------- */
function applyPreset(id) {
  const p = PHYS_PRESETS[id];
  if (!p) return;
  $("pf").value = p.f;
  $("px0").value = p.x0; $("px1").value = p.x1;
  $("py0").value = p.y0; $("py1").value = p.y1;
  $("fmode").value = p.mode;
  if (p.mode === "uniform") {
    $("pe0").value = p.e0;
    $("pdir").value = p.dir;
    $("pda").value = p.da; $("pdb").value = p.db; $("pdc").value = p.dc;
  } else if (p.mode === "point") {
    $("pq").value = p.qnc;
    $("ppx").value = p.qx; $("ppy").value = p.qy; $("ppz").value = p.qz;
  }
  $("pflip").checked = !!p.flip;
  syncPhysMode();
}
if ($("pcat")) {
  $("pcat").onchange = () => { applyPreset($("pcat").value); };
}

/* ---------- susun request sesuai mode medan ---------- */
const DIRS = {
  zplus: [0, 0, 1], zminus: [0, 0, -1],
  xplus: [1, 0, 0], xminus: [-1, 0, 0],
  yplus: [0, 1, 0], yminus: [0, -1, 0],
};

function physBody() {
  const f = getVal("pf");
  const mode = $("fmode").value;
  let F;
  if (mode === "uniform") {
    const e0 = num0("pe0", 500);
    let d = $("pdir").value === "custom"
      ? [num0("pda", 0), num0("pdb", 0), num0("pdc", 1)]
      : DIRS[$("pdir").value] || [0, 0, 1];
    const n = Math.hypot(d[0], d[1], d[2]) || 1;
    F = d.map((c) => plainNum((e0 * c) / n));
  } else if (mode === "point") {
    const k = 8987551792.3;              // Coulomb (desimal murni)
    const q = plainNum(num0("pq", 0) * 1e-9);
    const x0 = plainNum(num0("ppx", 0));
    const y0 = plainNum(num0("ppy", 0));
    const z0 = plainNum(num0("ppz", 0));
    const r2 = `((x-${x0})^2+(y-${y0})^2+(z-${z0})^2)^1.5`;
    F = [
      `${k}*${q}*(x-${x0})/${r2}`,
      `${k}*${q}*(y-${y0})/${r2}`,
      `${k}*${q}*(z-${z0})/${r2}`,
    ];
  } else {
    F = [getVal("pP"), getVal("pQ"), getVal("pR")];
  }
  return {
    f, F,
    xmin: $("px0").value, xmax: $("px1").value,
    ymin: $("py0").value, ymax: $("py1").value,
    n: $("pn").value,
    seed: $("pseed").value,
    flip_normal: $("pflip").checked,
    show_samples: $("pshowSamples").checked,
    max_points: 1200,
  };
}

/* ---------- render 3D ---------- */
// Warna konsisten dengan tab Grafik 3D: surface & sampel pakai getActivePreset().scale,
// panah konus pakai preset.arrow. Flukso densitas ber-tanda → cmin/cmax simetris di 0.
function physScale() {
  try { return getActivePreset().scale; } catch (e) { return COLOR_PRESETS.gold.scale; }
}
function physArrowColor() {
  try { return getActivePreset().arrow; } catch (e) { return COLOR_PRESETS.gold.arrow; }
}

let lastPhys = null; // {graph, samples, stats, flip}

function physLayout() {
  const L = layout();
  L.scene.aspectmode = "cube";
  // range manual: antisipasi permukaan datar (z konstan) biar kamera tidak bius
  if (lastPhys) {
    const g = lastPhys.graph;
    const flat = (a) => a.flat ? a.flat() : a;
    const vals = (arr) => arr.filter((v) => v !== null && v !== undefined && isFinite(v));
    const pad = (lo, hi) => {
      const d = (hi - lo) || 1;
      return [lo - d * 0.12, hi + d * 0.12];
    };
    const [xlo, xhi] = pad(Math.min(...g.surface.x), Math.max(...g.surface.x));
    const [ylo, yhi] = pad(Math.min(...g.surface.y), Math.max(...g.surface.y));
    const zv = vals(flat(g.surface.z));
    const zlo0 = Math.min(...zv), zhi0 = Math.max(...zv);
    const [zlo, zhi] = pad(zlo0, zhi0);
    // pelat datar? beri ruang vertikal utk cone (tail-anchored, ~diag*0.05)
    // supaya panah tidak ter-clip jadi "dinding" pad sumbu z yang terlampau pipih
    const dx0 = Math.max(...g.surface.x) - Math.min(...g.surface.x);
    const dy0 = Math.max(...g.surface.y) - Math.min(...g.surface.y);
    const diag0 = Math.hypot(dx0, dy0, zhi0 - zlo0) || 1;
    const room = diag0 * 0.13;
    const zr = [Math.min(zlo, zlo0 - room), Math.max(zhi, zhi0 + room)];
    L.scene.xaxis = {...L.scene.xaxis, range: [xlo, xhi]};
    L.scene.yaxis = {...L.scene.yaxis, range: [ylo, yhi]};
    L.scene.zaxis = {...L.scene.zaxis, range: zr};
    L.scene.camera = {eye: {x: 1.55, y: 1.35, z: 1.05}};
  }
  return L;
}

function nestedFlat(mats, cols) {
  const out = cols ? {} : [];
  if (cols) {
    cols.forEach((k) => (out[k] = []));
    for (let i = 0; i < mats[0].length; i++)
      for (let j = 0; j < mats[0][i].length; j++) {
        let ok = true;
        for (const m of mats) {
          if (m[i] === undefined || m[i][j] === undefined || m[i][j] === null || !isFinite(m[i][j])) { ok = false; break; }
        }
        if (ok) for (const k of cols) out[k].push(mats[cols.indexOf(k)][i][j]);
      }
    return out;
  }
  return null;
}

function drawPhys() {
  if (!lastPhys) return;
  const {graph, samples, stats, flip} = lastPhys;
  const raw = [];

  // permukaan: diwarnai densitas fluks (ber-tanda)
  raw.push({
    type: "surface",
    x: graph.surface.x,
    y: graph.surface.y,
    z: graph.surface.z,
    surfacecolor: graph.surface.fd_fill,
    colorscale: physScale(),
    cmin: -stats.colorMax,
    cmax: stats.colorMax,
    colorbar: {thickness: 12, title: {text: t9("physlab.cb_density", "densitas Φ<br>(N·m²/C)"), side: "right"}},
    contours: {
      x: {show: false, highlight: false},
      y: {show: false, highlight: false},
      z: {show: true, usecolormap: false, project: {x: false, y: false, z: false}, highlight: false},
    },
    hovertemplate: "<b>x:</b> %{x:.2f} m<br><b>y:</b> %{y:.2f} m<br><b>z:</b> %{z:.2f} m<br><i>" + t9("physlab.hover_density", "warna = densitas fluks (lihat colorbar)") + "</i><extra></extra>",
    _role: "surface",
  });

  if ($("pshowCones").checked) {
    const c = nestedFlat(
      [graph.cones.x, graph.cones.y, graph.cones.z, graph.cones.u, graph.cones.v, graph.cones.w, graph.cones.s],
      ["x", "y", "z", "u", "v", "w", "s"]
    );
    // panjang cone proporsional ukuran domain (vektor backend satuan arah)
    const zall = graph.surface.z.flat().filter((v) => v !== null && isFinite(v));
    const diag = Math.hypot(
      Math.max(...graph.surface.x) - Math.min(...graph.surface.x),
      Math.max(...graph.surface.y) - Math.min(...graph.surface.y),
      Math.max(...zall) - Math.min(...zall)
    ) || 1;
    raw.push({
      type: "cone",
      x: c.x, y: c.y, z: c.z,
      u: c.u, v: c.v, w: c.w,
      // Plotly TIDAK bisa memetakan warna cone dari customdata (colormap cone
      // = norm vektor) → satu warna panah dari preset Grafik 3D, mirip
      // vektor gradien di tab grafik. anchor "tail" + cone kecil supaya
      // panahnya seperti jarum, bukan blob raksasa.
      colorscale: [[0, physArrowColor()], [1, physArrowColor()]],
      cmin: 0,
      cmax: 1,
      showscale: false,
      sizemode: "scaled",
      sizeref: diag * 0.05,
      anchor: "tail",
      hovertemplate: "<b>" + t9("physlab.hover_local", "densitas fluks lokal:") + "</b> %{customdata:.2f} N·m²/C<extra></extra>",
      customdata: flip ? c.s.map((v) => -v) : c.s,
      _role: "cones",
    });
  }

  if ($("pshowSamples").checked && samples && samples.x.length) {
    raw.push({
      type: "scatter3d",
      mode: "markers",
      x: samples.x, y: samples.y, z: samples.z,
      marker: {
        size: 2.5,
        color: samples.g,
        colorscale: physScale(),
        cmin: -stats.colorMax,
        cmax: stats.colorMax,
        showscale: false,
        opacity: 0.75,
      },
      hovertemplate: "<b>" + t9("physlab.hover_sample", "sampel MC") + "</b><br>" + t9("physlab.hover_contrib", "kontribusi:") + " %{marker.color:.2f} N·m²/C<extra></extra>",
      _role: "samples",
    });
  }

  Plotly.react("ppplot", raw, physLayout(), {responsive: true, displaylogo: false});
}

/* ---------- render hasil statistik ---------- */
/* label UI via i18n (kunci physlab.*); cadangan = teks asli di bawah.
   Hanya teks yang ditampilkan, tidak menyentuh mesin hitung. */
const t9 = (key, fb) => {
  try {
    const v = window.I18N && window.I18N.t(key, fb);
    return (v === undefined || v === null) ? fb : v;
  } catch (e) { return fb; }
};

/* terjemahkan potongan pesan error dari backend (app.py bahasa Indonesia);
   sisa daftar model/en API GAK disentuh */
function trApiErr(msgOrErr) {
  const tOrFail = (key, fb) => {
    try { return t9(key, fb); } catch (e) { return fb; }
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
  for (const [ru, key, fb] of RULES) {
    const i = m.indexOf(ru);
    if (i >= 0) m = m.slice(0, i) + t9(key, fb) + m.slice(i + ru.length);
  }
  return m;
}

function pill(st) {
  const cls = st.converged ? "pill ok" : "pill warn";
  return `<span class="${cls}">${st.converged ? t9("physlab.pill_ok", "✔ terkonvergensi (rel.err < 2%)") : t9("physlab.pill_warn", "⚠ belum konvergen, naikkan N")}</span>`;
}

function termRows(st) {
  const tot = Math.abs(st.flux) || 1;
  /* kunci suku datang dari backend (physics.py) — dipetakan ke i18n di
     sini (layer UI), fallback = teks asli backend */
  const TERM_KEYS = {
    "R (komponen normal medan)": "physlab.term_r",
    "-P*fx (medan x vs kemiringan x)": "physlab.term_p",
    "-Q*fy (medan y vs kemiringan y)": "physlab.term_q",
  };
  const rows = Object.entries(st.terms)
    .map(([k, v]) => {
      const contrib = st.domain_area * v; // kontribusi suku utk fluks
      const pct = Math.round((Math.abs(contrib) / tot) * 100);
      return `<tr><td>${t9(TERM_KEYS[k] || "", k)}</td><td>${fmtSI(contrib, "N·m²/C")}</td><td>%${pct}</td></tr>`;
    });
  return `<table class="sterm">${rows.join("")}</table>`;
}

/* hasil terakhir yang tampil (untuk re-render saat bahasa diganti) */
let lastRenderedStat = null;

function renderPhysStats(st, aiSum) {
  lastRenderedStat = {st, aiSum: aiSum || null};
  const okv = (v, u) => (v === null || !isFinite(v)) ? "" : fmtSI(v, u);
  let h = `
  <div class="pstat-lead">${renderLatex(
    "\\Phi = \\iint_S \\mathbf{E}\\cdot d\\mathbf{A} = \\iint_D \\left(-P\\,f_x - Q\\,f_y + R\\right)\\,dx\\,dy"
  )}</div>
  <div class="pstat-grid">
    <div class="pstat big"><div class="pstat-k">${t9("physlab.stat_flux", "Φ, Fluks Total")}</div>
      <div class="pstat-v">${renderLatex("\\Phi \\approx " + (st.flux < 0 ? "-" : "") + "\\;" + stripTrail(String(+(Math.abs(st.flux).toPrecision(5)))) + "\\; \\text{N}\\cdot\\text{m}^2/\\text{C}")}</div></div>
    <div class="pstat big"><div class="pstat-k">${t9("physlab.stat_q", "Q terkurung (hukum Gauss, Q = ε₀·Φ)")}</div>
      <div class="pstat-v">${fmtSI(st.charge_enclosed, "C")}</div></div>
    <div class="pstat"><div class="pstat-k">${t9("physlab.stat_unc", "Ketidakpastian (95%)")}</div><div class="pstat-v">±${okv(st.ci95)} N·m²/C</div></div>
    <div class="pstat"><div class="pstat-k">${t9("physlab.stat_relerr", "Relatif error")}</div><div class="pstat-v">${st.rel_error < 1 ? "%" + (st.rel_error * 100).toPrecision(2) : t9("physlab.stat_relerr_high", "besar")}</div></div>
    <div class="pstat"><div class="pstat-k">${t9("physlab.stat_valid", "Sampel valid")}</div><div class="pstat-v">${st.n_valid.toLocaleString("de-DE")} / ${st.n.toLocaleString("de-DE")}</div></div>
    <div class="pstat"><div class="pstat-k">${t9("physlab.stat_area_domain", "Luas domain")}</div><div class="pstat-v">${okv(st.domain_area)} m²</div></div>
    <div class="pstat"><div class="pstat-k">${t9("physlab.stat_area_surf", "Luas permukaan (est. MC)")}</div><div class="pstat-v">${okv(st.surface_area)} ± ${okv(st.surface_area_err)} m²</div></div>
    <div class="pstat"><div class="pstat-k">${t9("physlab.stat_seed", "Seed")}</div><div class="pstat-v">${st.seed ?? t9("physlab.seed_random", "acak")}</div></div>
  </div>
  <div class="pstat-note">${pill(st)}${st.ci95 === 0 || st.ci95 === null
    ? ` <span class="muted">${t9("physlab.note_exact", "Galat 0 = suku integrand konstan di seluruh domain (permukaan datar atau medan tetap tegak lurus). Hasil Monte Carlo eksak, bukan bug.")}</span>` : ''} &nbsp; ${t9("physlab.term_note", "Padatan rata-rata suku integrand (per m²)")}: ${termRows(st)}</div>`;

  if (aiSum) {
    h += `<div class="ai-summary"><b>${t9("physlab.ai_res_head", "🤖 Penjelasan AI:")}</b><p>${esc(aiSum)}</p></div>`;
  }

  $("physStatBody").className = "";
  $("physStatBody").innerHTML = h;
}

/* ganti bahasa di tengah jalan -> render ulang hasil terakhir dengan
   dict bahasa baru (data perhitungan TIDAK disentuh, cuma labelnya) */
try {
  if (window.I18N) window.I18N.onChange(() => {
    if (lastRenderedStat) {
      // summary Penjelasan AI (teks bahasa lama) ikut dibuang saat render ulang
      renderPhysStats(lastRenderedStat.st, null);
    }
    if (lastPhys) drawPhys();           // label/colorbar/hover grafik ikut bahasa
    if (lastPhysErr && lastPhysErr.el) {
      try { lastPhysErr.el.textContent = trApiErr(lastPhysErr.e); } catch (e) {}
    }baru
    // ⚠️ semua output AI berbahasa lama direset, jangan menggantung:
    //  - panel tafsiran hasil
    if (lastInterp && lastInterp.kind !== "load") {
      lastInterp = null;
      const ip = $("physInterp");
      ip.classList.add("hidden");
      ip.innerHTML = "";
    }
    //  - "Penjelasan AI" di bawah tombol Susun Parameter
    lastAISummary = "";
    const ab = $("aiSummary");
    if (ab) { ab.classList.add("hidden"); ab.innerHTML = ""; }
  });
} catch (e) {}

/* ---------- jalankan simulasi ---------- */
let lastPhysErr = null;   // error terakhir (re-translate saat ganti bahasa)
let lastAISummary = "";        // penjelasan konfigurasi dari runAI (kalau ada)

function simContext() {
  // konteks skenario utk interpretasi hasil (angka nyata dikirim backend)
  const mode = $("fmode").value;
  return {
    surface: getVal("pf"),
    field_mode: mode,
    e0: mode === "uniform" ? num0("pe0", null) : null,
    charge: mode === "point" ? num0("pq", 0) * 1e-9 : null,
    src_point: mode === "point"
      ? [num0("ppx", 0), num0("ppy", 0), num0("ppz", 0)] : null,
    direction: mode === "uniform"
      ? ($("pdir").value === "custom"
        ? [num0("pda", 0), num0("pdb", 0), num0("pdc", 1)]
        : (DIRS[$("pdir").value] || null))
      : null,
    flip_normal: $("pflip").checked,
    xmin: $("px0").value, xmax: $("px1").value,
    ymin: $("py0").value, ymax: $("py1").value,
    ai_summary: lastAISummary,
  };
}

let lastInterp = null;   // {kind:"load"|"ok"|"fail", st, d, err} untuk re-render pas ganti bahasa

function renderInterp() {
  const box = $("physInterp");
  if (!box || !lastInterp) return;
  if (lastInterp.kind === "load") {
    box.innerHTML = `<b>${t9("physlab.ai_interp_head", "🤖 AI menafsirkan hasil simulasi…")}</b><p class='muted'>${t9("physlab.ai_sending", "mengirim angka hasil Monte Carlo ke tutor AI…")}</p>`;
  } else if (lastInterp.kind === "ok") {
    box.innerHTML = `<b>${t9("physlab.ai_result_head", "🤖 Interpretasi Hasil (tutor AI, model {m}):").replace("{m}", esc(lastInterp.d.model || "-"))}</b><p>${esc(lastInterp.d.text)}</p>`;
  } else {
    box.innerHTML = `<b>${t9("physlab.ai_interp_fail", "🤖 Interpretasi gagal:")}</b><p class="muted">${esc(trApiErr(lastInterp.err))}</p>`;
  }
}

async function aiInterpret(st) {
  const box = $("physInterp");
  if (!box) return;
  box.classList.remove("hidden");
  lastInterp = {kind: "load", st};
  renderInterp();
  try {
    const d = await post("/api/physics/interpret", {
      stats: st,
      context: simContext(),
      // 🌐 AI menjawab sesuai bahasa UI yang aktif saat tombol ditekan
      lang: (window.I18N && I18N.lang) || "indonesia",
    });
    lastInterp = {kind: "ok", st, d};
    renderInterp();
  } catch (e) {
    lastInterp = {kind: "fail", st, err: e.message};
    renderInterp();
  }
}

async function physSimulate(userRun = true) {
  const msg = $("physMsg");
  msg.textContent = t9("physlab.calc_msg", "Menghitung (Monte Carlo {n} titik...)").replace("{n}", (+($("pn").value || 0)).toLocaleString("de-DE"));
  msg.className = "hint";
  try {
    const d = await post("/api/physics/simulate", physBody());
    const st = d.stats;
    const fvals = d.graph.surface.fd.flat().filter((v) => v !== null && isFinite(v));
    st.colorMax = fvals.length ? Math.max(...fvals.map(Math.abs), 1e-9) : 1;
    lastPhys = {graph: d.graph, samples: d.samples, stats: st, flip: d.stats.sign < 0};
    drawPhys();
    renderPhysStats(st, null);
    msg.textContent = "";
    // interpretasi AI atas ANGKA hasil (toggle #pai);
    // HANYA saat user menekan tombol run — auto-run preset awal (boot) TIDAK
    // memanggil AI, supaya token gratis OpenRouter tidak terbakar diam-diam
    const ip = $("physInterp");
    if (userRun && $("pai") && $("pai").checked) {
      aiInterpret(st);
    } else if (ip) {
      ip.classList.add("hidden");
      ip.innerHTML = "";
    }
  } catch (e) {
    msg.textContent = trApiErr(e);
    lastPhysErr = { el: msg, e: e };
    msg.className = "hint err";
  }
}

window.physRun = physSimulate;
window.physOnShow = () => { if ($("ppplot") && lastPhys) Plotly.Plots.resize("ppplot"); };

/* ---------- sink preset warna Grafik 3D ↔ tab fisika ---------- */
window.physTheme = () => {            // dipanggil setTheme() di app.js saat ganti tema
  if (lastPhys) drawPhys();           // physLayout() baca tema terbaru
};
window.physPresetSync = (v) => {      // dipanggil saat #colorPreset (tab grafik) berubah
  if ($("ppreset")) $("ppreset").value = v;
  if (lastPhys) drawPhys();
};
if ($("ppreset") && $("colorPreset")) {
  $("colorPreset").querySelectorAll("option").forEach((o) => {
    $("ppreset").add(new Option(o.text, o.value));
  });
  $("ppreset").value = $("colorPreset").value;
  $("ppreset").onchange = () => {
    const v = $("ppreset").value;
    try { localStorage.setItem("colorPreset", v); } catch (e) {}
    $("colorPreset").value = v;      // tab grafik ikut (programmatically → draw manual)
    if (lastPhys) drawPhys();
    if (typeof draw === "function") draw();
  };
}
if ($("runPhys")) {
  $("runPhys").onclick = physSimulate;
  $("pshowSamples").onchange = drawPhys;
  $("pshowCones").onchange = drawPhys;
}

/* ---------- AI ---------- */
function currentConfigJSON() {
  return JSON.stringify({
    surface: getVal("pf"),
    xmin: $("px0").value, xmax: $("px1").value,
    ymin: $("py0").value, ymax: $("py1").value,
    field_mode: $("fmode").value,
    e0: $("pe0")?.value, direction: $("pdir")?.value === "custom"
      ? [num0("pda", 0), num0("pdb", 0), num0("pdc", 1)] : (DIRS[$("pdir").value] || null),
    charge_nc: $("pq")?.value,
    src_point: [$("ppx")?.value, $("ppy")?.value, $("ppz")?.value],
    custom_pqr: [getVal("pP"), getVal("pQ"), getVal("pR")],
    flip_normal: $("pflip").checked,
  });
}

function applyAIConfig(c) {
  // AI selalu MENIMPA: tandai katalog jadi "kustom" biar jelas bukan preset
  if ($("pcat") && [...$("pcat").options].some((o) => o.value === "custom")) {
    $("pcat").value = "custom";
  }
  $("pf").value = c.surface;
  if (c.xmin !== undefined) $("px0").value = plainNum(c.xmin);
  if (c.xmax !== undefined) $("px1").value = plainNum(c.xmax);
  if (c.ymin !== undefined) $("py0").value = plainNum(c.ymin);
  if (c.ymax !== undefined) $("py1").value = plainNum(c.ymax);
  $("fmode").value = c.field_mode || "uniform";

  if (c.field_mode === "point") {
    $("pq").value = plainNum(+c.charge * 1e9);
    $("ppx").value = plainNum(c.src_point?.[0] ?? 0);
    $("ppy").value = plainNum(c.src_point?.[1] ?? 0);
    $("ppz").value = plainNum(c.src_point?.[2] ?? 1);
  } else if (c.field_mode === "custom") {
    if (c.p) $("pP").value = c.p;
    if (c.q) $("pQ").value = c.q;
    if (c.r) $("pR").value = c.r;
  } else {
    $("pe0").value = plainNum(c.e0 ?? 500);
    const dv = (c.direction || [0, 0, 1]).map(Number);
    let best = Object.keys(DIRS).filter((k) =>
      k.match(/plus|minus/) && DIRS[k].every((v, i) => v === dv[i]))[0];
    if (best) {
      $("pdir").value = best;
    } else {
      $("pdir").value = "custom";
      $("pda").value = plainNum(dv[0]);
      $("pdb").value = plainNum(dv[1]);
      $("pdc").value = plainNum(dv[2]);
    }
  }
  $("pflip").checked = !!c.flip_normal;
  syncPhysMode();
  // AI mengisi range domain? buka collapsible-nya biar user bisa lihat isinya
  const advDom = document.getElementById("advDomain");
  if (advDom) advDom.open = true;
}

/* daftar kata yang jelas bukan konfigurasi simulasi fisika:
   kena -> langsung ditolak lokal, TIDAK dipanggil ke model (hemat token) */
const AI_OFFTOPIC_RX = new RegExp(
  [
    "python", "javascript", "javascripts", "\\bjava\\b", "\\bphp\\b",
    "\\bscript\\b", "\\bskrip\\b", "\\bkode program\\b", "program code",
    "\\bhtml\\b", "\\bcss\\b", "\\bwebsite\\b", "\\bweb\\s?page\\b", "\\bsitus\\b",
    "\\bweb\\b", "\\baplikasi\\b", "\\bapplication\\b", "resep masakan", "\\brecipe\\b",
    "\\bresep\\b", "\\blagu\\b", "\\bsong\\b", "\\bessay\\b", "\\besei\\b", "\\bjoke\\b",
    "\\bcandaan\\b", "install", "\\bwindows\\b", "\\blinux\\b", "\\bgame\\b",
    "\\bsql\\b", "\\bdatabase\\b", "\\bexcel\\b",
  ].join("|"),
  "i"
);

if ($("runAI")) {
  $("runAI").onclick = async () => {
    const msg = $("aiMsg");
    const desc = $("aiText").value.trim();
    if (!desc) { msg.textContent = t9("physlab.ai_empty_desc", "Tulis dulu deskripsi skenarionya 🙂"); msg.className = "hint err"; return; }
    // GUARDRAIL 1 (lokal): non-simulasi -> nolak tanpa memanggil AI
    if (AI_OFFTOPIC_RX.test(desc)) {
      msg.textContent = t9("physlab.ai_refuse", "🤖 Guardrail: permintaannya gak nyambung sama simulasi, jadi gak dikirim ke AI.");
      msg.className = "hint err";
      return;
    }
    msg.textContent = t9("physlab.ai_building", "🤖 AI sedang menyusun konfigurasi (biasanya 5 sampai 30 detik, model gratis semua)…");
    msg.className = "hint";
    try {
      const d = await post("/api/physics/ai", {
        description: desc,
        current: currentConfigJSON(),
        // 🌐 summary AI ikut bahasa UI yang aktif
        lang: (window.I18N && I18N.lang) || "indonesia",
      });
      // GUARDRAIL 2 (server prompt): model menolak -> {refusal:"..."}
      if (d.refusal) {
        const why = (d.reason && d.reason !== "off-topic") ? " — " + d.reason : "";
        msg.textContent = t9("physlab.ai_refuse", "🤖 Guardrail: permintaannya gak nyambung sama simulasi, jadi gak dikirim ke AI.") + why;
        msg.className = "hint err";
        return;
      }
      applyAIConfig(d.config);
      const box = $("aiSummary");
      lastAISummary = String(d.config.summary || d.raw_summary || "");
      box.classList.remove("hidden");
      box.innerHTML = `<b>${t9("physlab.ai_summary_head", "🤖 Penjelasan AI (model: {m}):").replace("{m}", esc(d.model))}</b><p>${esc(d.config.summary || d.raw_summary)}</p>`;
      msg.textContent = "";
      if ($("aiAutoRun").checked) physSimulate();
    } catch (e) {
      msg.textContent = trApiErr(e);
    lastPhysErr = { el: msg, e: e };
      msg.className = "hint err";
    }
  };
}

/* ---------- init: jalankan preset pelat dulu biar tak kosong ----------
   (false = BUKAN tekanan user: jangan panggil interpretasi AI sama sekali) */
if ($("ppplot")) {
  applyPreset("plate");
  physSimulate(false).then(() => {
    if (document.querySelector(".tab.active")?.dataset.tab !== "physics") {
      // biarkan resize diserahkan pada handler tab
    } else {
      Plotly.Plots.resize("ppplot");
    }
  });
}

/* ---------- versi exe offline: AI jadi OPT-IN ----------
   Saat jalan sebagai executable (frozen), checkbox AI TIDAK dicentang
   otomatis — user yang memutuskan memakai AI (butuh internet + API key
   di config.json di samping exe). Koneksi hanya terjadi saat tombol AI
   ditekan; tidak ada panggilan latar di waktu lain. Versi web: tidak
   berubah sama sekali. */
(async () => {
  try {
    const r = await fetch("/api/appinfo");
    const j = await r.json();
    if (!j.ok || !j.data || !j.data.frozen) return;
    const pai = $("pai"), ar = $("aiAutoRun");
    if (pai) pai.checked = false;
    if (ar) ar.checked = false;
    const adv = document.getElementById("advAI");
    if (adv && !document.getElementById("aiOfflineNote")) {
      const note = document.createElement("p");
      note.id = "aiOfflineNote";
      note.className = "hint";
      note.dataset.i18n = "physlab.ai_offline_note";
      note.textContent = t9("physlab.ai_offline_note",
        "Mode offline: AI butuh internet + API key di config.json (di samping exe). Koneksi hanya saat kamu menekan tombol AI.");
      adv.appendChild(note);
    }
  } catch (e) { /* appinfo tidak ada = versi web, biarkan */ }
})();
