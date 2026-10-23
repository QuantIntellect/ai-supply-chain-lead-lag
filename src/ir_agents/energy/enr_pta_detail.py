"""Fetch pressetext (pta) ad-hoc / news pages for Siemens Energy, save to raw dir, print dateline + lead."""
import sys; sys.path.insert(0, "/Users/sinamirzaei/Documents/aimapping/src/ir_agents/energy"); import irlib
import re
for nid in sys.argv[1:]:
    url = f"https://www.pressetext.com/news/{nid}"
    rel = irlib.download(url, "ENR.DE", f"pta_{nid}.html")
    if not rel:
        print("FAIL", nid); continue
    t = re.sub(r"\s+", " ", irlib.html_to_text(rel))
    m = re.search(r"\((pta\d+/\d{2}\.\d{2}\.\d{4}/\d{2}:\d{2} UTC[+-]\d)\)", t)
    i = m.start() if m else 0
    title_m = re.search(r"pta\d{11}\s+(.{0,300}?)\s+(München|Munich|Berlin)", t)
    print("=====", nid, "|", m.group(1) if m else "NO DATELINE", "|", rel)
    print(t[max(0, i - 250): i + 900])
