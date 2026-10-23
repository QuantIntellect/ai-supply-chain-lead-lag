"""Print release dateline + conference-call / publication-time statements from each extracted press release."""
import sys; sys.path.insert(0, "/Users/sinamirzaei/Documents/aimapping/src/ir_agents/energy"); import irlib
import csv, re, os
rows = list(csv.DictReader(open(os.path.join(irlib.RAW_IR, "PRY.MI", "docs_index.csv"))))
for r in rows:
    if r["doctype"] != "press_release" or not r["text_path"]:
        continue
    t = open(os.path.join(irlib.ROOT, r["text_path"]), encoding="utf-8", errors="replace").read()
    t = re.sub(r"\s+", " ", t)
    m = re.search(r"(Milan[^.]{0,40}?\d{1,2}(st|nd|rd|th)? [A-Z][a-z]+,? \d{4}|Milan[^.]{0,30}?[A-Z][a-z]+ \d{1,2}(st|nd|rd|th)?,? \d{4})", t)
    dl = m.group(0)[:70] if m else "?"
    cc = []
    for mm in re.finditer(r"(conference call|webcast|call will be held|will be presented|presentation will)", t, re.I):
        cc.append(t[max(0, mm.start() - 60): mm.end() + 170])
        if len(cc) >= 1: break
    print(r["period"], "|", dl, "|", cc[0] if cc else "-")
