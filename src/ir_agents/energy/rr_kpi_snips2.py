"""Targeted KPI snippets per results period (helper)."""
import sys; sys.path.insert(0, "/Users/sinamirzaei/Documents/aimapping/src/ir_agents/energy"); import irlib
import re
T = irlib.ROOT + "/data/processed/ir_text/RR.L/"
mode = sys.argv[1]
for p in sys.argv[2].split(","):
    t = re.sub(r"\s+", " ", open(T + p + ".txt", encoding="utf-8").read())
    print("########", p)
    if mode == "table":
        m = re.search(r"(Group financial performance|Group continuing operations|Group financial summary|Group £ million)", t)
        if m: print(t[m.start():m.start() + 1100])
    elif mode == "ps":
        ms = list(re.finditer(r"Power Systems.{0,300}?order intake", t, re.I))
        for m in ms[:3]:
            print("  ..", t[m.start():m.start() + 950])
    elif mode == "dc":
        for m in list(re.finditer(r"data cent|SMR|small modular", t, re.I))[:int(sys.argv[3]) if len(sys.argv) > 3 else 6]:
            print("  ..", t[max(0, m.start() - 200):m.end() + 250])
    elif mode == "guid":
        for m in list(re.finditer(r"Outlook|guidance", t))[:5]:
            print("  ..", t[max(0, m.start() - 50):m.end() + 450])
