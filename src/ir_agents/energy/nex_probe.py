"""Probe Nexans finance pages: list links (pdf / press / result) without printing whole pages."""
import sys, re, os
sys.path.insert(0, "/Users/sinamirzaei/Documents/aimapping/src/ir_agents/energy"); import irlib
from bs4 import BeautifulSoup
SCR = "/private/tmp/claude-501/-Users-sinamirzaei-Documents-aimapping/57e0a0d0-6441-40ef-828b-57eeb87e7b21/scratchpad/nex"
for u in sys.argv[1:]:
    r = irlib.fetch(u)
    fn = os.path.join(SCR, irlib.safe_name(u)[-80:] + ".html")
    open(fn, "w").write(r.text)
    s = BeautifulSoup(r.text, "html.parser")
    links = []
    for a in s.find_all("a", href=True):
        h = a["href"]; t = a.get_text(" ", strip=True)[:90]
        links.append((h, t))
    print("==", u, r.status_code, len(r.text), "links", len(links), "->", fn)
    pdf = [l for l in links if re.search(r"\.pdf|download|asset", l[0], re.I)]
    print(" pdf-ish:", len(pdf))
    for h, t in pdf[:40]: print("   ", h[:150], "|", t)
