"""Print short datacenter / guidance snippets per Legrand release (for manual note-writing)."""
import os, sys, re, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import *
for p in sorted(glob.glob(os.path.join(TEXT_IR, "LR.PA", "20*Q*_release.txt"))):
    fp = os.path.basename(p).replace("_release.txt", "")
    t = re.sub(r"\s+", " ", open(p, encoding="utf-8").read())
    print("##", fp)
    hits = []
    for m in re.finditer(r"[^.]{0,140}(data ?cent(er|re)s?|hyperscal|artificial intelligence|\bAI\b)[^.]{0,160}", t, re.I):
        s = m.group(0).strip()
        if re.search(r"\d", s) and s[:60] not in [h[:60] for h in hits]:
            hits.append(s)
    for h in hits[:3]:
        print("  DC:", h[:300])
    g = re.search(r"(targeting for (full-year )?20\d\d|20\d\d targets?)[^:]{0,80}:(.{0,420})", t, re.I)
    if g:
        print("  GUID:", g.group(0)[:480])
