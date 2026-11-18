# -*- coding: utf-8 -*-
"""Builder PDF Laporan Proyek Akhir, Nabla Workspace.
Output: Laporan_Akhir_Nabla_Workspace.pdf (di root proyek) + skrip_narasi_video.md
"""
import io, os, sys, hashlib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
sys.path.insert(0, BASE)
import laporan_content as C

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
                                Spacer, Table, TableStyle, Image, PageBreak,
                                KeepTogether, Preformatted, CondPageBreak)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.pdfgen import canvas as pdfcanvas
from PIL import Image as PILImage

# ── Palet (hasil palette.cascade) ─────────────────────────────
PAGE_BG = colors.HexColor("#f7f7f6")
CARD_BG = colors.HexColor("#e8e7e3")
TABLE_STRIPE = colors.HexColor("#f2f2f0")
HEADER_FILL = colors.HexColor("#686048")
COVER_BLOCK = colors.HexColor("#857b5c")
BORDER = colors.HexColor("#d9d3c0")
ICON = colors.HexColor("#836f34")
ACCENT = colors.HexColor("#2c90b2")
TEXT_PRIMARY = colors.HexColor("#1f1f1c")
TEXT_MUTED = colors.HexColor("#8d8a83")

# ── Font (DejaVu dari matplotlib; unicode lengkap) ────────────
import matplotlib
FDIR = os.path.join(matplotlib.get_data_path(), "fonts", "ttf")
pdfmetrics.registerFont(TTFont("DVS", os.path.join(FDIR, "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("DVS-B", os.path.join(FDIR, "DejaVuSans-Bold.ttf")))
pdfmetrics.registerFont(TTFont("DVS-I", os.path.join(FDIR, "DejaVuSans-Oblique.ttf")))
pdfmetrics.registerFont(TTFont("DVS-BI", os.path.join(FDIR, "DejaVuSans-BoldOblique.ttf")))
pdfmetrics.registerFont(TTFont("DVM", os.path.join(FDIR, "DejaVuSansMono.ttf")))
pdfmetrics.registerFontFamily("DVS", normal="DVS", bold="DVS-B", italic="DVS-I", boldItalic="DVS-BI")

PAGE_W, PAGE_H = A4
MARGIN = 2.2 * cm
AVAIL = PAGE_W - 2 * MARGIN

def st(name, **kw):
    base = dict(fontName="DVS", fontSize=10, leading=15, textColor=TEXT_PRIMARY,
                alignment=TA_JUSTIFY, spaceAfter=6)
    base.update(kw)
    return ParagraphStyle(name, **base)

S_TITLE  = st("Title", fontName="DVS-B", fontSize=24, leading=30, alignment=TA_CENTER)
S_SUB    = st("Sub", fontSize=13, leading=18, alignment=TA_CENTER, textColor=TEXT_MUTED)
S_H1     = st("H1", fontName="DVS-B", fontSize=16, leading=21, spaceBefore=14, spaceAfter=8, alignment=TA_LEFT, textColor=HEADER_FILL)
S_H2     = st("H2", fontName="DVS-B", fontSize=12.5, leading=17, spaceBefore=10, spaceAfter=6, alignment=TA_LEFT, textColor=TEXT_PRIMARY)
S_BODY   = st("Body")
S_BULLET = st("Bullet", leftIndent=14, bulletIndent=4, spaceAfter=3)
S_CAP    = st("Cap", fontSize=8.5, leading=12, alignment=TA_CENTER, textColor=TEXT_MUTED, spaceAfter=4)
S_CELL   = st("Cell", fontSize=9, leading=13, alignment=TA_LEFT, spaceAfter=0)
S_CELLB  = st("CellB", fontName="DVS-B", fontSize=9, leading=13, alignment=TA_LEFT, spaceAfter=0, textColor=colors.white)
S_PART   = st("Part", fontName="DVS-B", fontSize=22, leading=28, alignment=TA_CENTER, textColor=HEADER_FILL)
S_PARTS  = st("PartS", fontSize=12, leading=17, alignment=TA_CENTER, textColor=TEXT_MUTED)
S_CODE   = ParagraphStyle("Code", fontName="DVM", fontSize=8, leading=11, textColor=TEXT_PRIMARY, backColor=TABLE_STRIPE, borderPadding=6, leftIndent=6, rightIndent=6)
S_MARKER = st("Marker", fontName="DVS-B", fontSize=10.5, leading=15, textColor=ICON, spaceBefore=10, spaceAfter=4, alignment=TA_LEFT)

# ── DocTemplate dengan TOC ────────────────────────────────────
class LaporanDoc(BaseDocTemplate):
    def afterFlowable(self, fl):
        if isinstance(fl, Paragraph):
            if fl.style.name == "H1":
                txt = fl.getPlainText()
                key = "h1-%s" % hashlib.md5(txt.encode()).hexdigest()[:8]
                self.canv.bookmarkPage(key)
                self.canv.addOutlineEntry(txt, key, level=0, closed=False)
                self.notify("TOCEntry", (0, txt, self.page))
            elif fl.style.name == "H2":
                txt = fl.getPlainText()
                key = "h2-%s" % hashlib.md5(txt.encode()).hexdigest()[:8]
                self.canv.bookmarkPage(key)
                self.canv.addOutlineEntry(txt, key, level=1, closed=False)
                self.notify("TOCEntry", (1, txt, self.page))

def on_page(canv, doc):
    canv.saveState()
    # header tipis
    canv.setStrokeColor(BORDER); canv.setLineWidth(0.6)
    canv.line(MARGIN, PAGE_H - 1.35 * cm, PAGE_W - MARGIN, PAGE_H - 1.35 * cm)
    canv.setFont("DVS", 7.5); canv.setFillColor(TEXT_MUTED)
    canv.drawString(MARGIN, PAGE_H - 1.15 * cm, "Laporan Proyek Akhir, Nabla Workspace | Rekayasa Perangkat Lunak (TIKB2503021)")
    canv.drawRightString(PAGE_W - MARGIN, PAGE_H - 1.15 * cm, "STMIK IKMI Cirebon")
    # footer nomor halaman
    canv.setFont("DVS", 8.5); canv.setFillColor(TEXT_PRIMARY)
    canv.drawCentredString(PAGE_W / 2, 1.1 * cm, str(canv.getPageNumber()))
    canv.restoreState()

doc = LaporanDoc(os.path.join(ROOT, "Laporan_Akhir_Nabla_Workspace.pdf"), pagesize=A4,
                 leftMargin=MARGIN, rightMargin=MARGIN, topMargin=1.9 * cm, bottomMargin=1.8 * cm,
                 title="Laporan Proyek Akhir, Nabla Workspace",
                 author="Mahasiswa STMIK IKMI Cirebon",
                 subject="PRD/SRS + SDD (Pemodelan UML & UI/UX) + Laporan Pengujian",
                 creator="Nabla Workspace Docs Builder")
frame = Frame(MARGIN, 1.8 * cm, AVAIL, PAGE_H - 1.9 * cm - 1.8 * cm, id="main")
doc.addPageTemplates([PageTemplate(id="body", frames=[frame], onPage=on_page)])

story = []

# ── Helpers ───────────────────────────────────────────────────
def P(txt, style=S_BODY):
    story.append(Paragraph(txt, style))

def B(txt):
    story.append(Paragraph("•  " + txt, S_BULLET))

def H1(num, txt):
    story.append(CondPageBreak(4.5 * cm))
    story.append(Paragraph(f"{num}.  {txt}" if num else txt, S_H1))

def H2(txt):
    story.append(CondPageBreak(3.2 * cm))
    story.append(Paragraph(txt, S_H2))

def tbl(headers, rows, widths, fs=9, header_fs=9):
    data = [[Paragraph(h, S_CELLB) for h in headers]]
    for r in rows:
        data.append([Paragraph(c, S_CELL) for c in r])
    t = Table(data, colWidths=widths, hAlign="CENTER", repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HEADER_FILL),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, TABLE_STRIPE]),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t

def img_fit(path, max_w=AVAIL, max_h=24 * cm):
    im = PILImage.open(path)
    w, h = im.size
    scale = min(max_w / w, max_h / h, 1.0)
    return Image(path, width=w * scale, height=h * scale)

def diagram(name, max_w=AVAIL):
    story.append(KeepTogether([
        img_fit(os.path.join(BASE, "diagrams", name), max_w=max_w),
        Spacer(1, 4),
    ]))

def ui_grid():
    cells, row = [], []
    for fn, cap in C.UI_SHOTS:
        path = os.path.join(BASE, fn.replace("/", os.sep))
        im = PILImage.open(path)
        w, h = im.size
        cw = (AVAIL - 0.6 * cm) / 2.0
        scale = cw / w
        img = Image(path, width=w * scale, height=h * scale)
        cell = [img, Spacer(1, 2), Paragraph(cap, S_CAP)]
        row.append(cell)
        if len(row) == 2:
            cells.append(row); row = []
    if row:
        row.append("")
        cells.append(row)
    t = Table(cells, colWidths=[(AVAIL - 0.6 * cm) / 2.0 + 0.3 * cm] * 2, hAlign="CENTER")
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t)

def part_divider(no, judul, isi):
    story.append(PageBreak())
    story.append(Spacer(1, 5.2 * cm))
    story.append(Paragraph(no, S_SUB))
    story.append(Spacer(1, 8))
    story.append(Paragraph(judul, S_PART))
    story.append(Spacer(1, 14))
    story.append(Paragraph(isi, S_PARTS))
    story.append(PageBreak())

def narration_blocks(script_text):
    """Pecah skrip: baris [m:s–m:s] jadi marker tebal, sisanya paragraf dialog."""
    for block in script_text.strip().split("\n\n"):
        lines = block.strip().split("\n")
        if lines[0].startswith("VIDEO ") or lines[0].startswith(("(", "Tips", "Ketentuan")):
            if lines[0].startswith("VIDEO "):
                story.append(Paragraph(lines[0], S_TITLE if False else S_H2))
                if len(lines) > 1:
                    story.append(Paragraph(lines[1], S_CAP))
                continue
            for ln in lines:
                P(ln)
            continue
        story.append(Paragraph(lines[0], S_MARKER))
        for ln in lines[1:]:
            P("\u201C" + ln.strip().strip('"') + "\u201D")

# ============================================================
# KATA PENGANTAR + DAFTAR ISI
# ============================================================
story.append(Spacer(1, 3 * cm))
P("KATA PENGANTAR", S_TITLE)
story.append(Spacer(1, 12))
P("Laporan ini disusun sebagai pemenuhan tugas Proyek Akhir Mandiri mata kuliah Rekayasa Perangkat Lunak (TIKB2503021), Program Studi S1 Teknik Informatika STMIK IKMI Cirebon. Sesuai ketentuan panduan proyek, seluruh dokumen, PRD/SRS, SDD (Pemodelan UML & UI/UX), dan Laporan Pengujian/CI-CD, dijilid menjadi satu berkas PDF, dilengkapi skrip narasi video presentasi per tahapan dengan penanda menit sesuai durasi yang ditentukan.")
P("Aplikasi yang dibangun, Nabla Workspace, adalah aplikasi web edukasi fisika dan matematika dengan fitur kecerdasan artifisial yang tertanam pada alur kerja komputasi. Seluruh perancangan, konstruksi kode, dan pengujian dilakukan secara mandiri end-to-end.")
story.append(Spacer(1, 24))
t = tbl(["Keterangan", "Isi"], [
    ["Mata Kuliah", C.META["mk"]],
    ["Tema Topik Kelompok", C.META["tema"]],
    ["Dosen Pengampu", C.META["dosen"]],
    ["Nama Mahasiswa", "Afif Sheva Ramdhani"],
    ["NIM", "41257083"],
    ["Kelas", "1A-2025"],
    ["Program Studi", C.META["prodi"]],
], [5 * cm, AVAIL - 5 * cm])
story.append(t)
story.append(PageBreak())

P("DAFTAR ISI", S_TITLE)
story.append(Spacer(1, 10))
toc = TableOfContents()
toc.levelStyles = [
    st("TOC1", fontName="DVS-B", fontSize=10.5, leading=16, alignment=TA_LEFT),
    st("TOC2", fontSize=9.5, leading=14, alignment=TA_LEFT, leftIndent=16, textColor=TEXT_PRIMARY),
]
story.append(toc)
story.append(PageBreak())

# ============================================================
# BAGIAN I, PRD/SRS
# ============================================================
part_divider("BAGIAN I", "DOKUMEN PRD / SRS",
             "Product Requirement Document / Software Requirements Specification<br/>"
             "Standar IEEE 830-1998 &amp; ISO/IEC/IEEE 29148<br/>Bab 1 – 5")

H1(1, "Pendahuluan")
H2("1.1  Latar Belakang Masalah")
P(C.LATAR_BELAKANG)
H2("1.2  Tujuan dan Ruang Lingkup")
P(C.TUJUAN_LINGKUP)
H2("1.3  Definisi, Istilah, dan Singkatan")
story.append(tbl(["Istilah", "Definisi"], [[a, b] for a, b in C.DEFINISI], [4.4 * cm, AVAIL - 4.4 * cm]))
H2("1.4  Referensi")
for r in C.REFERENSI:
    B(r)

H1(2, "Deskripsi Umum")
H2("2.1  Perspektif Produk")
P(C.PERSPEKTIF)
H2("2.2  Fungsi Utama Produk")
for f in C.FUNGSI_UTAMA:
    B(f)
H2("2.3  Karakteristik Pengguna")
P(C.KARAKTERISTIK_PENGGUNA)
H2("2.4  Batasan dan Asumsi")
for chunk in C.BATASAN.split("\n"):
    chunk = chunk.strip()
    if not chunk:
        continue
    if chunk.startswith("•"):
        B(chunk[1:].strip())
    else:
        P(chunk)
H2("2.5  Antarmuka Eksternal Sistem (Ringkas)")
story.append(tbl(["Endpoint", "Fungsi"], [[a, b] for a, b in C.API_TABLE], [8.2 * cm, AVAIL - 8.2 * cm]))

H1(3, "Kebutuhan Fungsional (User Stories &amp; Acceptance Criteria)")
P("Delapan belas kebutuhan fungsional didefinisikan dalam format user story beserta kriteria penerimaan yang terukur. Setiap kebutuhan dipetakan ke kasus uji pada Bagian III.")
rows = [[i, us, ac] for i, us, ac in C.KEBUTUHAN_FUNGSIONAL]
story.append(tbl(["ID", "User Story", "Acceptance Criteria"], rows,
                 [1.5 * cm, 7.3 * cm, AVAIL - 8.8 * cm]))

H1(4, "Kebutuhan Non-Fungsional")
rows = [[i, k, d] for i, k, d in C.KEBUTUHAN_NF]
story.append(tbl(["ID", "Kategori", "Kebutuhan &amp; Metrik"], rows,
                 [1.7 * cm, 3.0 * cm, AVAIL - 4.7 * cm]))

H1(5, "Spesifikasi Fitur AI Utama")
for para in C.FITUR_AI_DETAIL.split("\n\n"):
    if para.strip().startswith(("A.", "B.", "C.")):
        lines = para.split("\n")
        H2(lines[0])
        for ln in lines[1:]:
            P(ln)
    else:
        P(para)

# ============================================================
# BAGIAN II, SDD
# ============================================================
part_divider("BAGIAN II", "DOKUMEN SDD",
             "Software Design Document, Pemodelan UML &amp; UI/UX<br/>"
             "Arsitektur · Use Case · Activity · Class · Sequence · ERD · UI/UX<br/>Bab 6 – 12")

H1(6, "Arsitektur Sistem")
P(C.ARSITEKTUR_NARASI)
diagram("arsitektur.png")

H1(7, "Use Case Diagram &amp; Skenario")
P(C.USECASE_NARASI)
diagram("usecase.png")
for judul, nama, rows in C.SKENARIO_TABEL:
    H2(nama)
    story.append(tbl(["Elemen", "Uraian"], [[a, b] for a, b in rows], [3.2 * cm, AVAIL - 3.2 * cm]))
    story.append(Spacer(1, 8))

H1(8, "Activity Diagram")
P(C.ACTIVITY_NARASI)
diagram("activity.png", max_w=11.5 * cm)

H1(9, "Class Diagram (Berorientasi Objek, Prinsip SOLID)")
P(C.CLASS_NARASI)
diagram("class.png")

H1(10, "Sequence Diagram (Alur Pertukaran Pesan)")
P(C.SEQ_NARASI)
diagram("seq_ai.png")
diagram("seq_lab.png")

H1(11, "ERD Basis Data")
P(C.ERD_NARASI)
diagram("erd.png")

H1(12, "Perancangan UI/UX")
P(C.UIUX_NARASI)
ui_grid()
P("Catatan UI/UX: seluruh layar di atas direkam langsung dari aplikasi yang berjalan (bukan mockup) pada resolusi 1600×900, tema Golden, Bahasa Indonesia. Prototipe interaktif Figma tidak diwajibkan; walkthrough antarmuka pada video presentasi memakai aplikasi asli sehingga keaslian rancangan dapat diverifikasi.", S_CAP)

# ============================================================
# BAGIAN III, PENGUJIAN
# ============================================================
part_divider("BAGIAN III", "LAPORAN PENGUJIAN &amp; CI/CD",
             "Strategi, Hasil, Temuan &amp; Perbaikan, Rencana CI/CD<br/>Bab 13 – 17")

H1(13, "Strategi &amp; Lingkungan Pengujian")
P(C.STRATEGI_UJI)

H1(14, "Hasil Pengujian Otomatis")
H2("14.1  Ringkasan Suite")
rows = [[a, b, c, d] for a, b, c, d in C.SUITE_TABLE]
story.append(tbl(["Skrip", "Cakupan", "Volume", "Hasil Akhir"], rows,
                 [3.6 * cm, 4.6 * cm, 4.6 * cm, AVAIL - 12.8 * cm]))
H2("14.2  Contoh Kasus Regresi (bug_reports2.md)")
rows = [[i, la, ex, hs] for i, la, ex, hs in C.CONTOH_KASUS]
story.append(tbl(["Kasus", "Ekspresi (LaTeX)", "Hasil Diharapkan", "Status"], rows,
                 [1.9 * cm, 7.6 * cm, 4.6 * cm, 1.6 * cm]))
P("Kode kasus: L = limit, D = derivatif, S = deret/produk, I = integral tak tentu, DI = integral tentu, C = operasi bersarang, P = pangkat fungsi, V = varian input/paste. Status tiap kasus diuji ganda pada mode native dan mode auto.", S_CAP)

H1(15, "Temuan &amp; Perbaikan Cacat")
P(C.BUG_NARASI)

H1(16, "Rencana CI/CD Pipeline")
P(C.CI_CD_NARASI)
story.append(Preformatted(C.CI_CD_NARASI.split("name: ci")[1].rsplit("Implementasi", 1)[0].strip(), S_CODE))

H1(17, "Kesimpulan Pengujian")
P(C.KESIMPULAN_UJI)

# ============================================================
# LAMPIRAN
# ============================================================
part_divider("LAMPIRAN", "INVENTARIS LENGKAP ALAT KOMPUTASI",
             "20 Tool Matematika &amp; Fisika · 10 Simulasi · 15 Grapher")

H1(None, "Lampiran A, Inventaris Alat Komputasi")
story.append(tbl(["Alat", "Fungsi"], [[a, b] for a, b in C.LAMPIRAN_TOOL], [5.4 * cm, AVAIL - 5.4 * cm]))

# ── Build ─────────────────────────────────────────────────────
doc.multiBuild(story)
print("PDF utama selesai:", doc.filename)

# ============================================================
# COVER (ReportLab canvas, vector) + merge
# ============================================================
cover_path = os.path.join(BASE, "_cover.pdf")
c = pdfcanvas.Canvas(cover_path, pagesize=A4)
W, Hh = A4

# latar
c.setFillColor(PAGE_BG); c.rect(0, 0, W, Hh, stroke=0, fill=1)
# top bar
c.setFillColor(HEADER_FILL); c.rect(0, Hh - 3.1 * cm, W, 3.1 * cm, stroke=0, fill=1)
c.setFillColor(colors.white)
c.setFont("DVS-B", 11); c.drawCentredString(W / 2, Hh - 1.25 * cm, "PROYEK AKHIR MANDIRI, REKAYASA PERANGKAT LUNAK (TIKB2503021)")
c.setFont("DVS", 9); c.drawCentredString(W / 2, Hh - 1.85 * cm, "Tema Topik Kelompok: E-Learning & Smart Education AI")
c.setFont("DVS", 9); c.drawCentredString(W / 2, Hh - 2.45 * cm, "STMIK IKMI CIREBON")
# watermark nabla kecil, pucat (tidak menembus blok identitas)
c.setFillColor(colors.Color(0.41, 0.38, 0.28, alpha=0.08))
c.setFont("DVS-B", 72)
c.drawCentredString(W / 2, Hh - 13.6 * cm, "∇")
# kicker
c.setFillColor(ICON); c.setFont("DVS-B", 12)
c.drawCentredString(W / 2, Hh - 5.6 * cm, "L  A  P  O  R  A  N    P  R  O  Y  E  K")
# hero title
c.setFillColor(TEXT_PRIMARY); c.setFont("DVS-B", 46)
c.drawCentredString(W / 2, Hh - 7.6 * cm, "Nabla Workspace")
c.setFont("DVS", 15); c.setFillColor(TEXT_MUTED)
c.drawCentredString(W / 2, Hh - 8.9 * cm, "Aplikasi Web Edukasi Fisika & Matematika")
c.drawCentredString(W / 2, Hh - 9.6 * cm, "Terintegrasi Fitur Kecerdasan Artifisial")
# accent line
c.setStrokeColor(ACCENT); c.setLineWidth(2)
c.line(W / 2 - 4 * cm, Hh - 10.5 * cm, W / 2 + 4 * cm, Hh - 10.5 * cm)
# summary drawer
c.setFillColor(TEXT_PRIMARY); c.setFont("DVS", 10.5)
summary = [
    "Gabungan Dokumen: PRD/SRS (IEEE 830 · ISO 29148) · SDD, Pemodelan UML (Use Case,",
    "Activity, Class, Sequence) · ERD Basis Data · Perancangan UI/UX · Laporan Pengujian",
    "& Rencana CI/CD (skrip narasi video final disajikan pada berkas terpisah: Narasi.pdf)",
]
yy = Hh - 11.9 * cm
for ln in summary:
    c.drawCentredString(W / 2, yy, ln); yy -= 0.62 * cm
# blok identitas
c.setFillColor(COVER_BLOCK)
c.roundRect(W / 2 - 7.4 * cm, 5.4 * cm, 14.8 * cm, 6.6 * cm, 10, stroke=0, fill=1)
c.setFillColor(colors.white); c.setFont("DVS", 11)
rows_id = [
    ("Nama Mahasiswa", "Afif Sheva Ramdhani"),
    ("NIM", "41257083"),
    ("Kelas", "1A-2025"),
    ("Dosen Pengampu", "Yudhistira Arie Wijaya, M.Kom., CDS."),
]
yy = 5.4 * cm + 6.6 * cm - 1.15 * cm
for k, v in rows_id:
    c.setFont("DVS-B", 10.5); c.drawString(W / 2 - 6.8 * cm, yy, k)
    c.setFont("DVS", 10.5); c.drawString(W / 2 - 0.2 * cm, yy, v)
    yy -= 1.25 * cm
# footer
c.setFillColor(TEXT_MUTED); c.setFont("DVS", 8.5)
c.drawCentredString(W / 2, 2.6 * cm, "Program Studi S1 Teknik Informatika, STMIK IKMI Cirebon")
c.drawCentredString(W / 2, 2.1 * cm, "Tahun Akademik 2025/2026, Dokumen dijilid menjadi satu berkas PDF sesuai ketentuan Bab V panduan proyek")
c.showPage(); c.save()

# merge cover + body
from pypdf import PdfReader, PdfWriter
body = PdfReader(os.path.join(ROOT, "Laporan_Akhir_Nabla_Workspace.pdf"))
cover = PdfReader(cover_path)
wr = PdfWriter()
wr.append(cover)
wr.append(body)
wr.add_metadata({"/Title": "Laporan Proyek Akhir, Nabla Workspace",
                 "/Author": "Mahasiswa STMIK IKMI Cirebon",
                 "/Subject": "PRD/SRS + SDD (UML & UI/UX) + Laporan Pengujian + Skrip Narasi Video",
                 "/Creator": "Nabla Workspace Docs Builder"})
final = os.path.join(ROOT, "Laporan_Akhir_Nabla_Workspace.pdf")
with open(final, "wb") as f:
    wr.write(f)
os.remove(cover_path)
print("COVER digabung. Final:", final)

# ============================================================
