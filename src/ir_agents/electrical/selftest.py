import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import *
print(classify_timing("07:00"), classify_timing("17:45"), classify_timing("12:00"), classify_timing(""))
import pymupdf, bs4
print("pymupdf", pymupdf.__doc__[:40] if pymupdf.__doc__ else "ok", "bs4", bs4.__version__)
f = Fetcher()
ok, st, p = f.download("https://www.se.com/ww/en/assets/pdf/release-Q3-revenues-2026", os.path.join(RAW_IR, "SU.PA", "2026Q3_release.pdf"))
print(ok, st, p, is_pdf(p), os.path.getsize(p))
out, n = to_text(p, "SU.PA", "2026Q3", "release")
print(out, n)
print(grep(out, r"data cent", maxhits=3))
