"""List pdf links on Wayback snapshots of the rolls-royce.com financial-results page (year-end
snapshots list that year's results documents)."""
import sys; sys.path.insert(0, "/Users/sinamirzaei/Documents/aimapping/src/ir_agents/energy"); import irlib
import re, json, os
from bs4 import BeautifulSoup
SCR = "/private/tmp/claude-501/-Users-sinamirzaei-Documents-aimapping/57e0a0d0-6441-40ef-828b-57eeb87e7b21/scratchpad/rr"
PAGE = sys.argv[1]
stamps = sys.argv[2:]
res = {}
for st in stamps:
    url = f"https://web.archive.org/web/{st}/{PAGE}"
    try:
        r = irlib.fetch(url, min_interval=2.0, timeout=90)
    except RuntimeError as e:
        print("ERR", st, e); continue
    print("##", st, r.status_code, r.url[:110])
    if r.status_code != 200:
        continue
    soup = BeautifulSoup(r.text, "html.parser")
    # walk the results list: capture date headings + links in document order
    txt_items = []
    for a in soup.find_all("a", href=True):
        h = a["href"]
        if ".pdf" in h.lower() and "vulnerab" not in h.lower():
            m = re.search(r"(/~/media/.*?\.pdf)", h, re.I) or re.search(r"(https?://www\.rolls-royce\.com/.*?\.pdf)", h, re.I)
            p = m.group(1) if m else h
            txt_items.append(p)
    seen = []
    for p in txt_items:
        if p not in seen:
            seen.append(p)
    res[st] = seen
    for p in seen:
        print("    ", p[:170])
json.dump(res, open(os.path.join(SCR, f"wayback_{abs(hash(PAGE))%1000}_{stamps[0]}.json"), "w"), indent=1)
