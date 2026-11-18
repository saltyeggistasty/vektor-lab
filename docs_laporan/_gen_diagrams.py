# -*- coding: utf-8 -*-
"""Generator diagram UML + ERD + Arsitektur untuk Laporan Nabla Workspace.
Output: docs_laporan/diagrams/*.png (DPI 220, palet low-saturation).
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Ellipse, FancyArrowPatch, Rectangle, Circle
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "diagrams")
os.makedirs(OUT, exist_ok=True)

# Palet low-saturation (isi pucat, border jenuh sedang)
C_BLUE_F, C_BLUE_E = "#EFF6FF", "#3B6FB5"
C_GREEN_F, C_GREEN_E = "#F0FDF4", "#2F8F5B"
C_AMBER_F, C_AMBER_E = "#FFFBEB", "#B58318"
C_RED_F, C_RED_E = "#FEF2F2", "#B54242"
C_PURP_F, C_PURP_E = "#F5F3FF", "#6D5BB5"
C_GRAY_F, C_GRAY_E = "#F8FAFC", "#64748B"
TXT = "#1E293B"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "text.color": TXT,
    "axes.edgecolor": TXT,
})


def newfig(w, h):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")
    return fig, ax


def box(ax, x, y, w, h, lines, fc=C_BLUE_F, ec=C_BLUE_E, fs=9, bold_first=True,
        rounded=True, align="center", lw=1.4):
    """Kotak (opsi 3-sekat jika lines = (judul, attrs[], methods[]))."""
    style = "round,pad=0.6,rounding_size=1.2" if rounded else "square,pad=0.6"
    p = FancyBboxPatch((x, y), w, h, boxstyle=style, fc=fc, ec=ec, lw=lw, zorder=2)
    ax.add_patch(p)
    if lines is None:
        return (x, y, w, h)
    if isinstance(lines, tuple):
        title, attrs, methods = lines
        n_a, n_m = len(attrs), len(methods)
        # proporsi tinggi: judul fix, sisanya proporsional
        h_t = h * 0.22
        h_a = h * 0.78 * (n_a / max(n_a + n_m, 1)) if (n_a + n_m) else 0
        h_m = h * 0.78 - h_a
        ax.text(x + w / 2, y + h - h_t / 2, title, ha="center", va="center",
                fontsize=fs + 1, fontweight="bold", zorder=3)
        ax.plot([x, x + w], [y + h - h_t, y + h - h_t], color=ec, lw=lw, zorder=3)
        if n_a:
            ax.plot([x, x + w], [y + h_m, y + h_m], color=ec, lw=lw, zorder=3)
            for i, a in enumerate(attrs):
                ax.text(x + 1.5, y + h_m + h_a - (i + 0.5) * h_a / n_a, a,
                        ha="left", va="center", fontsize=fs - 1.5, zorder=3)
        for i, m in enumerate(methods):
            ax.text(x + 1.5, y + h_m - (i + 0.5) * h_m / n_m if n_m else y, m,
                    ha="left", va="center", fontsize=fs - 1.5, zorder=3)
    else:
        n = len(lines)
        if n == 1:
            ax.text(x + w / 2, y + h / 2, lines[0], ha="center", va="center",
                    fontsize=fs, fontweight="bold" if bold_first else "normal", zorder=3)
        else:
            for i, t in enumerate(lines):
                fw = "bold" if (i == 0 and bold_first) else "normal"
                ha = "center" if align == "center" else "left"
                tx = x + w / 2 if ha == "center" else x + 1.5
                ax.text(tx, y + h - (i + 0.5) * h / n, t, ha=ha, va="center",
                        fontsize=fs if i == 0 else fs - 1, fontweight=fw, zorder=3)
    return (x, y, w, h)


def arrow(ax, p1, p2, label="", dashed=False, color="#475569", fs=8,
          label_dxy=(0, 2), style="-|>", lw=1.3, conn="arc3,rad=0"):
    a = FancyArrowPatch(p1, p2, arrowstyle=style, mutation_scale=14,
                        color=color, lw=lw, linestyle="--" if dashed else "-",
                        connectionstyle=conn, zorder=4)
    ax.add_patch(a)
    if label:
        mx, my = (p1[0] + p2[0]) / 2 + label_dxy[0], (p1[1] + p2[1]) / 2 + label_dxy[1]
        ax.text(mx, my, label, ha="center", va="center", fontsize=fs, color="#334155",
                bbox=dict(fc="white", ec="none", alpha=0.85, pad=1.2), zorder=5)


def actor(ax, x, y, name, scale=1.0):
    """Stick figure actor, kepala di (x, y), menghadap ke bawah."""
    s = scale
    ax.add_patch(Circle((x, y), 2.2 * s, fc="#FDE68A", ec="#92400E", lw=1.4, zorder=3))
    ax.plot([x, x], [y - 2.2 * s, y - 8 * s], color="#92400E", lw=1.6, zorder=3)   # badan
    ax.plot([x - 3 * s, x + 3 * s], [y - 4.5 * s, y - 4.5 * s], color="#92400E", lw=1.6, zorder=3)  # tangan
    ax.plot([x, x - 2.5 * s], [y - 8 * s, y - 12 * s], color="#92400E", lw=1.6, zorder=3)  # kaki
    ax.plot([x, x + 2.5 * s], [y - 8 * s, y - 12 * s], color="#92400E", lw=1.6, zorder=3)
    ax.text(x, y - 14.5 * s, name, ha="center", va="top", fontsize=9, fontweight="bold", zorder=3)
    return (x, y)


def diamond(ax, x, y, w, h, text, fs=8.5):
    ax.add_patch(plt.Polygon([(x, y + h / 2), (x + w / 2, y), (x, y - h / 2), (x - w / 2, y)],
                             fc="#FFFBEB", ec="#B58318", lw=1.4, zorder=3))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, zorder=4)


def oval(ax, x, y, w, h, text, fc=C_GREEN_F, ec=C_GREEN_E, fs=8.5):
    ax.add_patch(Ellipse((x, y), w, h, fc=fc, ec=ec, lw=1.4, zorder=2))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, zorder=3)
    return (x, y, w, h)


def save(fig, name):
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("OK", path)


# ============================================================
# 1. USE CASE DIAGRAM
# ============================================================
fig, ax = newfig(15, 10.5)
ax.add_patch(Rectangle((17, 6), 66, 90, fc="#FAFCFF", ec="#334155", lw=1.6, zorder=1))
ax.text(50, 97.5, "Nabla Workspace, Sistem Aplikasi Web Edukasi Fisika & Matematika",
        ha="center", fontsize=11, fontweight="bold")

uc = {}
uc["lang"]  = oval(ax, 33, 88, 27, 8.5, "Memilih bahasa (×7)\n& tema tampilan")
uc["calc"]  = oval(ax, 33, 72, 27, 9, "Melakukan kalkulasi kalkulus\n(∇f, ∇·F, Hessian, dsb.)")
uc["tools"] = oval(ax, 33, 55.5, 27, 9, "Menggunakan tool matematika\n& fisika (45 kartu tool)")
uc["mc"]    = oval(ax, 33, 39, 27, 9, "Menjalankan simulasi\nMonte Carlo flux Gauss")
uc["dl"]    = oval(ax, 33, 23, 27, 9, "Mengunduh aplikasi\nversi offline (exe)")
uc["copy"]  = oval(ax, 33, 12, 27, 7.5, "Melihat & menyalin\nalamat donasi", fs=8)

uc["aicfg"] = oval(ax, 67, 88, 27, 9, "Mengonfigurasi simulasi via\nbahasa natural  «AI»", fc=C_PURP_F, ec=C_PURP_E)
uc["aiint"] = oval(ax, 67, 72, 27, 9, "Memperoleh interpretasi\nhasil simulasi  «AI»", fc=C_PURP_F, ec=C_PURP_E)
uc["cfg"]   = oval(ax, 67, 55.5, 27, 9, "Mengelola konfigurasi\n(config.json)", fc=C_GRAY_F, ec=C_GRAY_E, fs=8)
uc["addr"]  = oval(ax, 67, 39, 27, 9, "Mengelola alamat donasi\n(address.json)", fc=C_GRAY_F, ec=C_GRAY_E, fs=8)
uc["mail"]  = oval(ax, 67, 23, 27, 9, "Mengirim kritik/saran &\nformulir audit donasi", fc=C_AMBER_F, ec=C_AMBER_E)

a_user = actor(ax, 8, 62, "Pengguna\n(Pelajar / Guru)")
a_adm  = actor(ax, 92, 47, "Pemilik\nAplikasi")
a_llm  = actor(ax, 92, 84, "LLM OpenRouter\n(sistem eksternal)")
a_mail = actor(ax, 92, 11, "SMTP Gmail\n(sistem eksternal)")

for k in ["lang", "calc", "tools", "mc", "dl", "copy"]:
    arrow(ax, (12.5, 58 if k != "copy" else 20), (uc[k][0] - 13.5, uc[k][1]), "", lw=1.0)
# asosiasi actor kanan (jalur vertikal bersih)
arrow(ax, (uc["aicfg"][0] + 13.5, 88), (a_llm[0] - 6, 86), "", lw=1.0)
arrow(ax, (uc["aiint"][0] + 13.5, 72), (a_llm[0] - 6, 81.5), "", lw=1.0)
arrow(ax, (uc["cfg"][0] + 13.5, 57), (a_adm[0] - 6, 49), "", lw=1.0)
arrow(ax, (uc["addr"][0] + 13.5, 40.5), (a_adm[0] - 6, 45), "", lw=1.0)
arrow(ax, (uc["mail"][0] + 13.5, 23.5), (a_mail[0] - 6.5, 13), "", lw=1.0)

# include / extend (koridor tengah antar kolom, tanpa menembus elips)
arrow(ax, (uc["mc"][0] + 13, uc["mc"][1] + 2.5), (uc["aicfg"][0] - 13.5, uc["aicfg"][1] - 1),
      "«extend» auto-run", dashed=True, fs=7.5, conn="arc3,rad=-0.22")
arrow(ax, (uc["aiint"][0] - 13.5, uc["aiint"][1] - 2), (uc["mc"][0] + 13, uc["mc"][1] + 1.5),
      "«include» opsional (#pai)", dashed=True, fs=7.5, conn="arc3,rad=-0.18")

ax.set_title("Gambar 7.1, Use Case Diagram Nabla Workspace", fontsize=13, fontweight="bold", pad=14)
save(fig, "usecase.png")

# ============================================================
# 2. ACTIVITY DIAGRAM, alur perhitungan tool matematika
# ============================================================
fig, ax = newfig(11, 15)

def abox(x, y, w, h, text, fc=C_BLUE_F, ec=C_BLUE_E, fs=9):
    return box(ax, x - w / 2, y - h / 2, w, h, [text] if isinstance(text, str) else text, fc=fc, ec=ec, fs=fs)

def start_node(x, y):
    ax.add_patch(Circle((x, y), 1.6, fc=TXT, ec=TXT, zorder=3))

def end_node(x, y):
    ax.add_patch(Circle((x, y), 2.1, fc="white", ec=TXT, lw=1.4, zorder=3))
    ax.add_patch(Circle((x, y), 1.2, fc=TXT, ec=TXT, zorder=4))

X = 42
start_node(X, 97)
arrow(ax, (X, 95.3), (X, 93))
abox(X, 89.5, 44, 6.5, "CalcGuard: validasi cooldown tombol (5 dtk)")
arrow(ax, (X, 86.2), (X, 84.2))
diamond(ax, X, 81, 30, 6, "Dalam cooldown?")
arrow(ax, (X + 15, 81), (77, 81), "Ya", fs=8)
abox(87, 81, 20, 7, "Tampilkan pesan\nerr.calc_wait (i18n)", fc=C_RED_F, ec=C_RED_E, fs=8)
arrow(ax, (87, 77.5), (87, 71.2), "", lw=1.0)
end_node(87, 68.5)  # akhir jalur cooldown (flow-final terpisah)
arrow(ax, (X, 78), (X, 76), "Tidak", fs=8, label_dxy=(-6, 0))
abox(X, 72.5, 46, 6.5, "Pengguna memasukkan ekspresi LaTeX pada math-field")
arrow(ax, (X, 69.2), (X, 67.2))
abox(X, 63.5, 46, 7, "tools.js: calculus2sympy() membangun op_data\n(JSON terstruktur, tanpa evaluasi mentah)")
arrow(ax, (X, 60), (X, 58))
abox(X, 54.5, 46, 7, "Deteksi otomatis jenis operasi:\nintegral / derivatif / limit / Σ deret / ∏ produk")
arrow(ax, (X, 51), (X, 49))
diamond(ax, X, 45.5, 34, 7.5, "Mode manual cocok dgn\ndeteksi?")
arrow(ax, (X + 17, 45.5), (80, 45.5), "Tidak", fs=8)
abox(87, 45.5, 20, 8.5, "Auto-switch mode\n+ re-render form\n+ re-collect payload", fc=C_AMBER_F, ec=C_AMBER_E, fs=8)
arrow(ax, (87, 41.2), (87, 34), "", lw=1.0)
arrow(ax, (87, 34), (X + 1, 34), "", lw=1.0, style="-")
arrow(ax, (X, 42), (X, 34), "Ya", fs=8, label_dxy=(-5, 0))
ax.add_patch(Circle((X, 34), 1.2, fc=TXT, ec=TXT, zorder=4))  # merge
arrow(ax, (X, 32.8), (X, 31))
abox(X, 27.5, 44, 6.5, "POST /api/lab  →  Flask dispatch → mathlab.run_tool()")
arrow(ax, (X, 24.2), (X, 22.2))
abox(X, 18.5, 46, 7.5, "_build_op(): membangun objek SymPy\ntak-evaluasi (Integral/Sum/Limit/Derivative/Product)")
arrow(ax, (X, 14.7), (X, 12.9))
diamond(ax, X, 9.5, 32, 6.5, "Sentinel error\n__NABLA_ERR__?")
arrow(ax, (X - 16, 9.5), (23, 9.5), "Ya", fs=8, label_dxy=(0, 2.4))
abox(11.5, 9.5, 21, 8, "Pesan i18n ramah:\nerr.int_missing_dx,\nerr.bound_invalid, dst.", fc=C_RED_F, ec=C_RED_E, fs=7.5)
arrow(ax, (11.5, 5.5), (11.5, 4.4), "", lw=1.0)
end_node(11.5, 1.8)  # akhir jalur error (flow-final terpisah)
arrow(ax, (X, 6.2), (X, 4.9), "Tidak", fs=8, label_dxy=(-7, 0))
abox(X, 1.5, 46, 6.5, "_best_form() + _pretty_latex() → render KaTeX + plain")
arrow(ax, (66, 1.5), (84.8, 1.5), "", lw=1.0)
end_node(87, 1.5)  # akhir jalur sukses (flow-final terpisah)
ax.set_title("Gambar 8.1, Activity Diagram: Alur Perhitungan Tool Matematika",
             fontsize=12.5, fontweight="bold", pad=12)
save(fig, "activity.png")

# ============================================================
# 3. CLASS DIAGRAM
# ============================================================
fig, ax = newfig(17, 13)

# Baris 1
box(ax, 2, 64, 29, 34, ("«controller» MathLab (mathlab.py)",
    ["- TOOLS: dict[str, handler]",
     "- assume_int: simbol Σ/∏ integer"],
    ["+ run_tool(d)  [20 tool]", "+ tool_integral(d) [L/D/S/I/DI/C/P]",
     "+ tool_matrix / ode / taylor / poly", "+ tool_stats / complex / modmath",
     "+ tool_entropy / thermo / qm / es", "+ tool_rel / proj / hydro / …",
     "- _build_op(opd, int_syms)", "- _apply_opd(opd, d, mode)",
     "- _expr_int(s, assume_int)", "- _bound(v), _parse_matrix()",
     "- _pretty_latex(e), _best_form(e)", "- _abs_log(e)"]), fs=8)
box(ax, 36, 64, 29, 34, ("«boundary» FlaskApp (app.py)",
    ["- BASE_DIR: Path", "- MAX_CONTENT_LENGTH: 8MB",
     "- asset_v: boot timestamp"],
    ["+ route /  : render index.html", "+ api_calc / surface / field / curve",
     "+ api_lab()  [dispatcher]", "+ api_physics_simulate()",
     "+ api_physics_ai() [ai_configure]", "+ api_physics_interpret()",
     "+ api_audit() / api_feedback()", "  (SMTP STARTTLS Gmail)",
     "+ download_info / offline()", "+ _audit_cfg(), @api wrapper",
     "  → {ok, error, errKey, errArgs}"]), fs=8)
box(ax, 71, 64, 27, 34, ("«controller» PhysicsLab (physics.py)",
    ["- DEFAULTS: config AI",
     "- OPENROUTER_URL: const"],
    ["+ load_config()", "+ monte_carlo_flux(f,F,xr,yr,n,seed)",
     "+ phys_simulation(d)", "+ phys_surface_graph()",
     "+ mc_samples_cloud()", "+ ai_configure(desc,cur,lang)",
     "+ ai_interpret(stats,ctx,lang)", "- _call_model(messages)",
     "- _extract_json(txt) [toleran]", "- _validate_ai_config(cfg)",
     "- _clean_interp(text)"]), fs=8)

# Baris 2
box(ax, 2, 38, 29, 20, ("VectorCalc (vectorcalc.py)",
    ["- SCALAR_OPS: 8 operasi vektor"],
    ["+ calculate(d)  (∇f, ∇·F, curl,", "  Hessian, Jacobian, dst.)",
     "+ surface(d) / field(d) / curve(d)", "+ CalcError(bahasa-aware)"]), fs=8)
box(ax, 36, 38, 29, 20, ("GraphLab (graphlab.py), 15 grapher",
    ["- TOOLS: dict[str, spec]"],
    ["+ validasi input + readout numerik", "  (render kanvas di klien:",
     "   graphers.js / graphers2.js)", "  gdomain, gfractal, gising,",
     "  gfluid, ggeodesic, …"]), fs=8)
box(ax, 71, 38, 27, 20, ("SimLab (simlab.py), 10 simulasi",
    ["- TOOLS: dict[str, spec]",
     "- numpy RK4 / split-step"],
    ["+ slogistic / slorenz / sfourier", "+ swalk / sdblpend / sdrag",
     "+ skepler / sslit / sschrod", "+ smatrix (deterministik, seed)"]), fs=8)

# Baris 3: error + frontend
box(ax, 2, 21, 29, 13, ("«domain errors» Exception",
    ["LabError(errKey, args)", "PhysError  |  CalcError"],
    ["→ HTTP 400 {ok:false, error,", "   errKey, errArgs}",
     "→ diterjemahkan frontend", "   via i18n ×7"]), fc=C_RED_F, ec=C_RED_E, fs=7.5)

box(ax, 36, 2, 62, 32, ("«frontend»  Vanilla JS (static/)",
    ["ToolsPanel (tools.js): registry 10 tool mathfield;",
     "  la2plain/calculus2sympy LaTeX→op_data;",
     "  updateParamLocks auto-fill, deteksi operasi,",
     "  auto-switch mode; CalcGuard cooldown 5/10 dtk",
     "PhysicsUI (physics.js): form Monte Carlo, preset,",
     "  drawPhys() Plotly, #runAI + #pai + #aiAutoRun,",
     "  guardrail off-topic lokal (tanpa token)",
     "GraphEngines (graphers.js / graphers2.js):",
     "  15 engine kanvas & Plotly, pan-zoom HiDPI,",
     "  parser bilangan real & kompleks",
     "MenuWarStories (menu.js) · I18N (i18n.js, 7 bahasa,",
     "  RTL arab) · AboutPanel / DonationPanel / DownloadPanel"],
    []), fc=C_GRAY_F, ec=C_GRAY_E, fs=8)

# Relasi
arrow(ax, (31, 81), (36, 81), "/api/lab", fs=8)
arrow(ax, (65, 81), (71, 81), "/api/physics/*", fs=8)
arrow(ax, (42, 64), (24, 58), "/api/calc · surface ·", fs=7.5, label_dxy=(-9, 1.5))
ax.text(20, 61.2, "field · curve", fontsize=7.5, ha="center")
arrow(ax, (50.5, 64), (50.5, 58), "/api/lab", fs=8, label_dxy=(6.5, 0))
arrow(ax, (60, 64), (82, 58), "/api/lab", fs=8, label_dxy=(8, 1.5))
# frontend -> FlaskApp: konektor L-shape lewat koridor x=33.5
ax.plot([33.5, 33.5], [34, 61], color="#475569", lw=1.3, zorder=4)
ax.plot([33.5, 44], [61, 61], color="#475569", lw=1.3, zorder=4)
arrow(ax, (44, 61), (44, 64), "", fs=8)
ax.text(35.2, 46, "«HTTP/JSON» fetch", fontsize=7.5, rotation=90, ha="center",
        va="center", color="#334155")
arrow(ax, (33.5, 27.5), (31, 27.5), "", dashed=True, lw=1.0)  # error -> engines (implisit)

ax.text(50, -1.5, "Prinsip desain: SOLID, SRP (satu modul = satu tanggung jawab komputasi), OCP (registry TOOLS dict → tambah tool tanpa mengubah dispatcher),\nDIP (frontend hanya bergantung kontrak REST {ok, error, errKey}, bukan implementasi mesin komputasi).",
        ha="center", fontsize=8.5, style="italic")
ax.set_title("Gambar 9.1, Class Diagram Tingkat Modul (Backend Python + Frontend JS)",
             fontsize=13, fontweight="bold", pad=14)
save(fig, "class.png")

# ============================================================
# 4. SEQUENCE DIAGRAM, AI Monte Carlo
# ============================================================
fig, ax = newfig(14.5, 9.5)
LX = {"user": 7, "ui": 26, "flask": 46, "phy": 65, "llm": 88}
NAMES = [("Pengguna", "«aktor»"), ("UI Fisika\n(physics.js)", "«frontend»"),
         ("Flask app.py\n/api/physics/*", "«boundary»"),
         ("PhysicsLab\n(physics.py)", "«controller»"),
         ("OpenRouter LLM", "«sistem eksternal»")]
Y_TOP, Y_BOT = 88, 8
for k, (nm, st) in zip(LX, NAMES):
    box(ax, LX[k] - 9, Y_TOP, 18, 8, [nm, st], fc=C_BLUE_F, ec=C_BLUE_E, fs=8.5)
    ax.plot([LX[k], LX[k]], [Y_BOT, Y_TOP], color="#94A3B8", lw=1.1, ls="--", zorder=1)

def msg(a, b, y, text, ret=False, num=""):
    arrow(ax, (LX[a], y), (LX[b], y), f"{num}{text}", dashed=ret, fs=8,
          style="-|>" if not ret else "-|>", color="#334155" if not ret else "#64748B")

msg("user", "ui", 82, "1: isi deskripsi bahasa natural + klik [Konfigurasi AI]")
msg("ui", "ui", 76.5, "2: guardrail lokal regex off-topic (tanpa token)", ret=True)
ax.text(LX["ui"], 74.6, "   refus → #aiMsg", fontsize=7.5, color="#64748B")
msg("ui", "flask", 70.5, "3: POST /api/physics/ai {description, current, lang}")
msg("flask", "phy", 64.5, "4: ai_configure(description, current, lang)")
msg("phy", "llm", 58.5, "5: POST chat/completions (model utama)")
msg("llm", "phy", 52.5, "6: respons JSON (fallback model ×3 bila gagal)", ret=True)
msg("phy", "phy", 47.5, "7: _extract_json + validasi skema config", ret=True)
msg("phy", "flask", 42, "8: {ok, config, model}  |  PhysError → 400 errKey", ret=True)
msg("flask", "ui", 36.5, "9: applyAIConfig → isi form + kartu ringkasan AI", ret=True)
msg("ui", "user", 31, "10: form terisi (jika #aiAutoRun ✓ → langkah 11)", ret=True)
msg("ui", "flask", 25.5, "11: POST /api/physics/simulate {N, field, domain, seed}")
msg("flask", "phy", 20, "12: monte_carlo_flux() → Φ, CI95, trace konvergensi")
msg("phy", "flask", 15, "13: stats + surface graph + samples cloud", ret=True)
msg("ui", "flask", 11, "14: POST /api/physics/interpret (jika #pai ✓)", ret=False)
arrow(ax, (LX["flask"], 9.6), (LX["llm"], 9.6), "", dashed=True, style="-|>")
ax.text(56, 5.4, "15: interpretasi hasil ditampilkan pada #physInterp (model tercantum)",
        fontsize=8, ha="center")
ax.set_title("Gambar 10.1, Sequence Diagram: Konfigurasi & Interpretasi AI Simulasi Monte Carlo",
             fontsize=12.5, fontweight="bold", pad=12)
save(fig, "seq_ai.png")

# ============================================================
# 5. SEQUENCE DIAGRAM, /api/lab perhitungan tool
# ============================================================
fig, ax = newfig(13, 8)
LX2 = {"user": 8, "tools": 29, "flask": 50, "ml": 70, "sy": 89}
NAMES2 = [("Pengguna", "«aktor»"), ("ToolsPanel\n(tools.js)", "«frontend»"),
          ("Flask app.py", "«boundary»"), ("MathLab\n(mathlab.py)", "«controller»"),
          ("SymPy/SymEngine", "«pustaka komputasi»")]
for k, (nm, st) in zip(LX2, NAMES2):
    box(ax, LX2[k] - 9, 88, 18, 8, [nm, st], fc=C_GREEN_F, ec=C_GREEN_E, fs=8.5)
    ax.plot([LX2[k], LX2[k]], [8, 88], color="#94A3B8", lw=1.1, ls="--", zorder=1)

def msg2(a, b, y, text, ret=False):
    arrow(ax, (LX2[a], y), (LX2[b], y), text, dashed=ret, fs=8)

msg2("user", "tools", 82, "1: input LaTeX (math-field) + parameter opsional")
msg2("tools", "tools", 76.5, "2: updateParamLocks: auto-fill + deteksi operasi", ret=True)
msg2("tools", "flask", 71, "3: POST /api/lab {tool, op_data, mode}")
msg2("flask", "ml", 65.5, "4: run_tool(payload)")
msg2("ml", "ml", 60, "5: _build_op → objek tak-evaluasi", ret=True)
msg2("ml", "sy", 54.5, "6: doit()/diff/integrate/limit/series …")
msg2("sy", "ml", 49, "7: hasil simbolik", ret=True)
msg2("ml", "ml", 43.5, "8: _best_form() + _pretty_latex()", ret=True)
msg2("ml", "flask", 38, "9: {ok, rows: [{latex, plain, meta}]}", ret=True)
msg2("flask", "tools", 32.5, "10: HTTP 200 JSON", ret=True)
msg2("tools", "user", 27, "11: render KaTeX + nilai plain + tabel")
arrow(ax, (LX2["tools"], 22), (LX2["flask"], 22), "ALT: error domain", fs=8, style="-")
ax.text(46.5, 19.4, "", fontsize=7)
msg2("ml", "flask", 16.5, "12: LabError(errKey) → HTTP 400", ret=False)
msg2("flask", "tools", 11.5, "13: {ok:false, errKey} → pesan i18n ramah", ret=True)
ax.set_title("Gambar 10.2, Sequence Diagram: Perhitungan Tool via /api/lab (op_data pipeline)",
             fontsize=12.5, fontweight="bold", pad=12)
save(fig, "seq_lab.png")

# ============================================================
# 6. ERD
# ============================================================
fig, ax = newfig(15, 9.5)

def ent(x, y, w, name, attrs, pk_first=True):
    h = 5 + len(attrs) * 3.6
    p = FancyBboxPatch((x, y), w, h, boxstyle="square,pad=0", fc="white", ec="#3B6FB5", lw=1.4, zorder=2)
    ax.add_patch(p)
    # header
    p = FancyBboxPatch((x, y + h - 4.6), w, 4.6, boxstyle="square,pad=0", fc="#3B6FB5", ec="#3B6FB5", zorder=3)
    ax.add_patch(p)
    ax.text(x + w / 2, y + h - 2.3, name, ha="center", va="center", fontsize=9.5,
            fontweight="bold", color="white", zorder=4)
    for i, (a, tag) in enumerate(attrs):
        yy = y + h - 4.6 - (i + 0.5) * 3.6
        pre = "PK  " if tag == "pk" else ("FK  " if tag == "fk" else "      ")
        fw = "bold" if tag == "pk" else "normal"
        ax.text(x + 1.6, yy, pre + a, ha="left", va="center", fontsize=8.2, fontweight=fw, zorder=4)
    return (x, y, w, h)

e_user = ent(4, 58, 26, "PENGGUNA_PERANGKAT", [
    ("id_perangkat : UUID", "pk"), ("bahasa : VARCHAR(16)", ""), ("tema : VARCHAR(16)", ""),
    ("preset_warna : VARCHAR(16)", ""), ("dibuat_pada : DATETIME", "")])
e_log = ent(36, 64, 28, "LOG_SIMULASI", [
    ("id_log : BIGINT", "pk"), ("id_perangkat : UUID", "fk"),
    ("jenis_tool : VARCHAR(32)", ""), ("parameter_json : JSON", ""),
    ("ringkasan_hasil : TEXT", ""), ("durasi_ms : INT", ""), ("dibuat_pada : DATETIME", "")])
e_fb = ent(36, 26, 28, "UMPAN_BALIK", [
    ("id_umpan : BIGINT", "pk"), ("id_perangkat : UUID", "fk"),
    ("nama : VARCHAR(80)", ""), ("kontak : VARCHAR(120)", ""),
    ("jenis : ENUM(bug, saran)", ""), ("pesan : TEXT(5000)", ""), ("dibuat_pada : DATETIME", "")])
e_audit = ent(4, 12, 26, "AUDIT_DONASI", [
    ("id_audit : BIGINT", "pk"), ("id_perangkat : UUID", "fk"),
    ("nama_lengkap : VARCHAR(120)", ""), ("negara : VARCHAR(60)", ""),
    ("bidang_kemanusiaan : TEXT", ""), ("status_organisasi : VARCHAR(40)", ""),
    ("tampilkan_publik : BOOLEAN", ""), ("file_foto : BLOB", ""), ("status_verifikasi : ENUM", "")])
e_addr = ent(70, 52, 26, "ALAMAT_DONASI", [
    ("id_alamat : INT", "pk"), ("mata_uang : VARCHAR(16)", ""),
    ("jaringan : VARCHAR(24)", ""), ("alamat_wallet : VARCHAR(128)", ""),
    ("aktif : BOOLEAN", "")])
e_cfg = ent(70, 14, 26, "KONFIGURASI_APLIKASI", [
    ("id_konfig : INT", "pk"), ("modul : ENUM(ai, smtp)", ""),
    ("kunci : VARCHAR(40)", ""), ("nilai : TEXT", ""),
    ("terenkripsi : BOOLEAN", ""), ("diperbarui_pada : DATETIME", "")])

# relasi (crow's foot sederhana)
def rel(p1, p2, label, card="1 ── N"):
    arrow(ax, p1, p2, "", style="-", color="#64748B", lw=1.2)
    mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
    ax.text(mx, my + 1.4, label, fontsize=7.8, ha="center", color="#334155",
            bbox=dict(fc="white", ec="none", pad=1.0), zorder=5)
    ax.text(mx, my - 2.4, card, fontsize=7.5, ha="center", color="#B54242", zorder=5)

rel((30, 70), (36, 80), "mencatat")
rel((30, 64), (36, 48), "mengirim")
rel((30, 60), (23, 51.8), "mengajukan")
ax.text(50, 6.5, "Catatan: implementasi saat ini memakai persistensi file (config.json, address.json) + email SMTP langsung.",
        fontsize=8.5, style="italic", ha="center")
ax.text(50, 3, "ERD ini adalah perancangan basis data relasional (SQLite/PostgreSQL) untuk pengembangan lanjutan.",
        fontsize=8.5, style="italic", ha="center")
ax.set_title("Gambar 11.1, ERD Basis Data (Perancangan Relasional)", fontsize=13, fontweight="bold", pad=12)
save(fig, "erd.png")

# ============================================================
# 7. ARSITEKTUR SISTEM (3 tier)
# ============================================================
fig, ax = newfig(14.5, 9)
# Tier 1: Presentasi
box(ax, 2, 74, 96, 20, None, fc=C_GRAY_F, ec=C_GRAY_E)
ax.text(50, 91.5, "TIER 1, LAPISAN PRESENTASI (Klien)", fontsize=10.5, fontweight="bold", ha="center")
for i, (t, d) in enumerate([
    ("Peramban / Web", "MathLive · Plotly · KaTeX · GSAP (vendored)"),
    ("Aplikasi Offline", "PyInstaller onedir + pywebview / Electron shell"),
    ("Modul JS", "tools.js · physics.js · graphers*.js · i18n.js · calcguard.js")]):
    box(ax, 5 + i * 32, 76.5, 28, 11, [t, d], fs=8.5)
arrow(ax, (50, 74), (50, 68), "HTTPS / REST JSON {ok, error, errKey}", fs=9)
# Tier 2: Aplikasi
box(ax, 2, 44, 96, 24, None, fc=C_BLUE_F, ec=C_BLUE_E)
ax.text(50, 65.5, "TIER 2, LAPISAN APLIKASI (Flask, Python 3.14)", fontsize=10.5, fontweight="bold", ha="center")
for i, (t, d) in enumerate([
    ("Route UI & Aset", "/ · /i18n/* · /menu_screen/* · /download/*"),
    ("Route Komputasi", "/api/calc · /api/lab · /api/physics/simulate"),
    ("Route AI & Kontak", "/api/physics/ai · /interpret · /api/feedback · /api/audit")]):
    box(ax, 5 + i * 32, 46.5, 28, 15, [t, d], fs=8.5)
# Tier 3: Mesin + eksternal
box(ax, 2, 18, 58, 22, None, fc=C_GREEN_F, ec=C_GREEN_E)
ax.text(31, 37.5, "TIER 3a, MESIN KOMPUTASI (lokal, deterministik)", fontsize=10, fontweight="bold", ha="center")
for i, (t, d) in enumerate([
    ("mathlab.py", "20 tool · SymPy/SymEngine"),
    ("physics.py", "Monte Carlo flux · NumPy"),
    ("vectorcalc / graphlab / simlab", "8 ops · 15 grapher · 10 sim")]):
    box(ax, 5 + i * 18.5, 20, 17, 13, [t, d], fs=7.5)
box(ax, 64, 18, 34, 22, None, fc=C_PURP_F, ec=C_PURP_E)
ax.text(81, 37.5, "TIER 3b, LAYANAN EKSTERNAL (opsional)", fontsize=10, fontweight="bold", ha="center")
box(ax, 67, 28, 28, 7, ["OpenRouter LLM", "chat/completions · fallback ×3"], fs=8)
box(ax, 67, 20, 28, 6.5, ["SMTP Gmail :587", "STARTTLS, audit & feedback"], fs=8)
arrow(ax, (42, 44), (31, 40), "", fs=8, style="-")
arrow(ax, (75, 44), (78, 40), "", fs=8, style="-")
box(ax, 2, 3, 96, 10, ["PERSISTENSI, file JSON di sisi server: config.json (kunci AI/SMTP, tidak pernah dibundel) · address.json (wallet donasi) · NablaWorkspace-x64.zip (build offline)",
                       "PERSISTENSI KLIEN, localStorage: tema, bahasa, tata letak menu"], fs=8.5, fc=C_AMBER_F, ec=C_AMBER_E)
ax.set_title("Gambar 6.1, Arsitektur Sistem 3-Tier Nabla Workspace", fontsize=13, fontweight="bold", pad=12)
save(fig, "arsitektur.png")

print("SELESAI, 7 diagram dibuat di", OUT)
