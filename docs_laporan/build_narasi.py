# -*- coding: utf-8 -*-
"""Builder PDF terpisah: Skrip Narasi Video Final — Nabla Workspace.
Output: Narasi.pdf (root proyek)."""
import io, os, sys
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
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, PageBreak, Preformatted)
import matplotlib

FDIR = os.path.join(matplotlib.get_data_path(), "fonts", "ttf")
pdfmetrics.registerFont(TTFont("DVS", os.path.join(FDIR, "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("DVS-B", os.path.join(FDIR, "DejaVuSans-Bold.ttf")))
pdfmetrics.registerFont(TTFont("DVS-I", os.path.join(FDIR, "DejaVuSans-Oblique.ttf")))
pdfmetrics.registerFontFamily("DVS", normal="DVS", bold="DVS-B", italic="DVS-I")

PAGE_W, PAGE_H = A4
MARGIN = 2.2 * cm
AVAIL = PAGE_W - 2 * MARGIN

PAGE_BG = colors.HexColor("#f7f7f6")
TABLE_STRIPE = colors.HexColor("#f2f2f0")
HEADER_FILL = colors.HexColor("#686048")
COVER_BLOCK = colors.HexColor("#857b5c")
BORDER = colors.HexColor("#d9d3c0")
ICON = colors.HexColor("#836f34")
ACCENT = colors.HexColor("#2c90b2")
TEXT_PRIMARY = colors.HexColor("#1f1f1c")
TEXT_MUTED = colors.HexColor("#8d8a83")

def st(name, **kw):
    base = dict(fontName="DVS", fontSize=10.5, leading=16, textColor=TEXT_PRIMARY,
                alignment=TA_JUSTIFY, spaceAfter=6)
    base.update(kw)
    return ParagraphStyle(name, **base)

S_TITLE = st("Title", fontName="DVS-B", fontSize=22, leading=28, alignment=TA_CENTER)
S_SUB   = st("Sub", fontSize=12, leading=17, alignment=TA_CENTER, textColor=TEXT_MUTED)
S_BODY  = st("Body")
S_MARKER = st("Marker", fontName="DVS-B", fontSize=11, leading=16, textColor=ICON,
              spaceBefore=12, spaceAfter=4, alignment=TA_LEFT)
S_DIALOG = st("Dialog", leftIndent=14)
S_CAP    = st("Cap", fontSize=8.5, leading=12, alignment=TA_CENTER, textColor=TEXT_MUTED, spaceAfter=4)

def on_page(canv, doc):
    canv.saveState()
    canv.setStrokeColor(BORDER); canv.setLineWidth(0.6)
    canv.line(MARGIN, PAGE_H - 1.35 * cm, PAGE_W - MARGIN, PAGE_H - 1.35 * cm)
    canv.setFont("DVS", 7.5); canv.setFillColor(TEXT_MUTED)
    canv.drawString(MARGIN, PAGE_H - 1.15 * cm, "Skrip Narasi Video Final | Nabla Workspace")
    canv.drawRightString(PAGE_W - MARGIN, PAGE_H - 1.15 * cm, "Afif Sheva Ramdhani | 41257083 | 1A-2025")
    canv.setFont("DVS", 8.5); canv.setFillColor(TEXT_PRIMARY)
    canv.drawCentredString(PAGE_W / 2, 1.1 * cm, str(canv.getPageNumber()))
    canv.restoreState()

doc = SimpleDocTemplate(os.path.join(ROOT, "Narasi.pdf"), pagesize=A4,
                        leftMargin=MARGIN, rightMargin=MARGIN, topMargin=1.9 * cm, bottomMargin=1.8 * cm,
                        title="Skrip Narasi Video Final | Nabla Workspace",
                        author="Afif Sheva Ramdhani",
                        subject="Skrip narasi video final (10 menit) | Proyek Akhir Rekayasa Perangkat Lunak",
                        creator="Nabla Workspace Docs Builder")

story = []

# ── Halaman pembuka ──
story.append(Spacer(1, 2.2 * cm))
story.append(Paragraph("SKRIP NARASI VIDEO FINAL", S_TITLE))
story.append(Spacer(1, 6))
story.append(Paragraph("Live Demo Aplikasi Web &amp; Sistem Utuh<br/>Nabla Workspace", S_SUB))
story.append(Spacer(1, 16))
ident = [["Nama Mahasiswa", "Afif Sheva Ramdhani"],
         ["NIM", "41257083"],
         ["Kelas", "1A-2025"],
         ["Mata Kuliah", C.META["mk"]],
         ["Tema Topik Kelompok", C.META["tema"]],
         ["Dosen Pengampu", C.META["dosen"]]]
t = Table([[a, b] for a, b in ident], colWidths=[5 * cm, AVAIL - 5 * cm], hAlign="CENTER")
t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (0, -1), COVER_BLOCK),
    ("ROWBACKGROUNDS", (1, 0), (1, -1), [colors.white, TABLE_STRIPE]),
    ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ("TOPPADDING", (0, 0), (-1, -1), 6),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
]))
story.append(t)
story.append(Spacer(1, 16))
story.append(Paragraph(C.VIDEO_KETENTUAN.replace(
    "Ketentuan umum (sesuai Panduan Proyek, diperbarui per instruksi dosen):",
    "<b>Ketentuan umum (sesuai Panduan Proyek, diperbarui per instruksi dosen):</b>"), S_BODY))
story.append(Spacer(1, 6))
story.append(Paragraph(C.VIDEO_TIPS, S_BODY))
story.append(Spacer(1, 8))
story.append(Paragraph("Marker [menit] hanya panduan ritme saat merekam, bukan teks yang dibacakan. Bagian dalam tanda kurung siku seperti [Buka aplikasi] adalah aksi screen recording, bukan dialog.", S_CAP))
story.append(PageBreak())

# ── Skrip ──
story.append(Paragraph("SKRIP NARASI (TARGET 10:00)", S_TITLE))
story.append(Spacer(1, 12))
for block in C.VIDEO_FINAL.strip().split("\n\n"):
    lines = block.strip().split("\n")
    if lines[0].startswith("SKRIP NARASI"):
        continue
    story.append(Paragraph(lines[0], S_MARKER))
    for ln in lines[1:]:
        story.append(Paragraph("\u201C" + ln.strip().strip('"') + "\u201D", S_DIALOG))

doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
print("Narasi.pdf selesai:", os.path.join(ROOT, "Narasi.pdf"))
