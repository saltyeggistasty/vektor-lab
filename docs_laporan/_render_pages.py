# -*- coding: utf-8 -*-
import fitz, os
doc = fitz.open(r"G:\vektor-lab(1)\vektor-lab\Laporan_Akhir_Nabla_Workspace.pdf")
out = r"G:\vektor-lab(1)\vektor-lab\docs_laporan\qa_pages"
os.makedirs(out, exist_ok=True)
for i, page in enumerate(doc):
    pix = page.get_pixmap(dpi=100)
    pix.save(os.path.join(out, f"page_{i+1:02d}.png"))
print("rendered", len(doc), "pages")
