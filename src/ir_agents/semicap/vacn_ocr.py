"""OCR image-only VAT presentation PDFs (no text layer) with pymupdf + tesseract.
Usage: vacn_ocr.py <pdf_path> <period> <doctype>"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pymupdf
from irlib import write_text

os.environ.setdefault("TESSDATA_PREFIX", "/opt/homebrew/share/tessdata")
pdf, period, doctype = sys.argv[1], sys.argv[2], sys.argv[3]
out = []
with pymupdf.open(pdf) as doc:
    for page in doc:
        tp = page.get_textpage_ocr(language="eng", dpi=200, full=True)
        out.append(page.get_text(textpage=tp))
txt = "\n".join(out)
p = write_text("VACN.SW", period, doctype, txt)
print(p, len(txt))
