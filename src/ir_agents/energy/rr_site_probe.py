"""Probe rolls-royce.com per-results pages and list document links (pdf) found on each."""
import sys; sys.path.insert(0, "/Users/sinamirzaei/Documents/aimapping/src/ir_agents/energy"); import irlib
import re, json, os
from bs4 import BeautifulSoup
SCR = "/private/tmp/claude-501/-Users-sinamirzaei-Documents-aimapping/57e0a0d0-6441-40ef-828b-57eeb87e7b21/scratchpad/rr"
BASE = "https://www.rolls-royce.com/investors/results-reports-and-presentations/financial-results/"
slugs = sys.argv[1:]
out = {}
for s in slugs:
    url = s if s.startswith("http") else BASE + s
    r = irlib.fetch(url)
    links = []
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.title.get_text(strip=True) if soup.title else ""
        for a in soup.find_all("a", href=True):
            h = a["href"]
            if ".pdf" in h.lower() or "webcast" in h.lower() or "transcript" in h.lower():
                links.append((a.get_text(" ", strip=True)[:60], h))
        # dates shown on page
        txt = re.sub(r"\s+", " ", soup.get_text(" ", strip=True))
        m = re.findall(r"\d{1,2} (?:January|February|March|April|May|June|July|August|September|October|November|December) 20\d\d", txt)
    else:
        title, m = "", []
    print("##", r.status_code, url[-90:], "|", title[:60], "|", sorted(set(m))[:6])
    seen = set()
    for t, h in links:
        if h in seen or "vulnerability" in h:
            continue
        seen.add(h)
        print("    ", t, "|", h[:170])
    out[url] = {"status": r.status_code, "links": links}
json.dump(out, open(os.path.join(SCR, "site_probe_%d.json" % (abs(hash(" ".join(slugs))) % 10000)), "w"))
