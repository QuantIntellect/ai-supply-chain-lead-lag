"""Print short snippets around a regex for a list of Schneider periods."""
import os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import *
T = "SU.PA"
pat, pers = sys.argv[1], sys.argv[2].split(",")
kind = sys.argv[3] if len(sys.argv) > 3 else "release"
before, after, maxhits = (int(x) for x in (sys.argv[4:7] if len(sys.argv) > 6 else (60, 300, 1)))
for per in pers:
    p = os.path.join(TEXT_IR, T, f"{per}_{kind}.txt")
    if not os.path.exists(p):
        print(per, "NOFILE"); continue
    t = open(p, encoding="utf-8", errors="ignore").read()
    t = re.sub(r"\s+", " ", t).replace("’", "'").replace("–", "-")
    hits = [m for m in re.finditer(pat, t, re.I)][:maxhits]
    if not hits:
        print(per, "NOHIT")
    for m in hits:
        print(per, "|", t[max(0, m.start() - before): m.end() + after])
