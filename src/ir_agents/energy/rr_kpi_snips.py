"""Print compact KPI snippets per results period (helper for manual KPI compilation)."""
import sys; sys.path.insert(0, "/Users/sinamirzaei/Documents/aimapping/src/ir_agents/energy"); import irlib
import re
T = "data/processed/ir_text/RR.L/"
periods = sys.argv[1].split(",")
pats = sys.argv[2:]
for p in periods:
    f = T + p + ".txt"
    t = re.sub(r"\s+", " ", open(irlib.ROOT + "/" + f, encoding="utf-8").read())
    print("########", p)
    for pat in pats:
        n = 0
        for m in re.finditer(pat, t, re.I):
            print("  [%s] .. %s" % (pat[:25], t[max(0, m.start() - 60):m.end() + 420]))
            n += 1
            if n >= 2:
                break
