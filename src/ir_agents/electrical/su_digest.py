"""Print a compact digest of a Schneider release text: highlights section and
lines with revenue/orders/margin/backlog/data-center/target keywords."""
import os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import *
T = "SU.PA"
per = sys.argv[1]
n = int(sys.argv[2]) if len(sys.argv) > 2 else 2200
mode = sys.argv[3] if len(sys.argv) > 3 else "hl"
p = os.path.join(TEXT_IR, T, f"{per}_release.txt")
txt = open(p, encoding="utf-8", errors="ignore").read()
flat = re.sub(r"[ \t]*\n[ \t]*", " ", txt)
flat = re.sub(r"\s{2,}", " ", flat)
if mode == "hl":
    i = flat.find("Highlights")
    print(flat[i:i + n])
else:
    pat = sys.argv[3]
    for m in re.finditer(pat, flat, re.I):
        print("-", flat[max(0, m.start() - 150): m.end() + 250])
