"""Compact views of a Nexans release: key-figures table and selected phrases."""
import sys, re
sys.path.insert(0, "/Users/sinamirzaei/Documents/aimapping/src/ir_agents/energy"); import irlib
fp, mode = sys.argv[1], sys.argv[2]
t = re.sub(r"\s+", " ", open(f"{irlib.TEXT_IR}/NEX.PA/{fp}_press_release.txt", encoding="utf-8").read())
if mode == "table":
    i = t.find("KEY FIGURES")
    print(t[i:i + int(sys.argv[3]) if len(sys.argv) > 3 else i + 650] if i >= 0 else "no table")
else:
    for m in list(re.finditer(mode, t, re.I))[: int(sys.argv[3]) if len(sys.argv) > 3 else 2]:
        print("..", t[max(0, m.start() - 140): m.end() + 160])
