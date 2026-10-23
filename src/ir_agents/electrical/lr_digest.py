"""Compact KPI digest of Legrand release texts (for manual verification)."""
import os, sys, re, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import *
NUM = r"[\d][\d,\. ]*\d"
for p in sorted(glob.glob(os.path.join(TEXT_IR, "LR.PA", "20*Q*_release.txt"))):
    fp = os.path.basename(p).split("_")[0]
    t = re.sub(r"\s+", " ", open(p, encoding="utf-8").read())
    m = re.search(r"Key figures.{0,200}?Sales (" + NUM + r") (" + NUM + r") ([+\-−]?\d+[\.,]\d+ ?%)", t)
    sales = m.groups() if m else None
    m2 = re.search(r"Adjusted operating profit (" + NUM + r") (" + NUM + r") [+\-−]?\d+[\.,]\d+ ?% As % of sales (\d+[\.,]\d+ ?%) (\d+[\.,]\d+ ?%)", t)
    marg = m2.groups()[2:] if m2 else None
    org = re.findall(r"[^.]{0,90}organic[^.]{0,120}(?:quarter)[^.]{0,60}", t[:9000], re.I)[:2]
    print(f"## {fp} sales={sales} adjOPmargin={marg}")
    for o in org:
        print("   ORG:", o.strip()[:230])
