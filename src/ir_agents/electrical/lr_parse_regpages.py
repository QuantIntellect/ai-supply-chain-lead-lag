"""Parse Legrand regulated-information year pages -> JSON list of (year, section, title, href)."""
import os, sys, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import *
from bs4 import BeautifulSoup

out = []
pdir = os.path.join(RAW_IR, "LR.PA", "pages")
for y in range(2015, 2027):
    p = os.path.join(pdir, f"en_investors-and-shareholders_regulated-information_{y}.html")
    s = BeautifulSoup(open(p, "rb").read(), "html.parser")
    for ul in s.find_all("ul", class_="filter-list"):
        if "l3" not in (ul.get("class") or []):
            continue
        # section title = text of the parent li's first child text node
        sec_li = ul.find_parent("li")
        sec = ""
        if sec_li is not None:
            for ch in sec_li.children:
                t = ch.get_text(" ", strip=True) if hasattr(ch, "get_text") else str(ch).strip()
                if t:
                    sec = t[:60]
                    break
        for li in ul.find_all("li", recursive=False):
            title = re.sub(r"\s+", " ", li.get_text(" ", strip=True))
            hrefs = [a["href"] for a in li.find_all("a", href=True)]
            out.append({"page_year": y, "section": sec, "title": title, "hrefs": hrefs})
json.dump(out, open(os.path.join(RAW_IR, "LR.PA", "pages", "regpages_parsed.json"), "w"), indent=0, ensure_ascii=False)
print(len(out))
secs = {}
for o in out:
    secs.setdefault(o["section"], 0)
    secs[o["section"]] += 1
print(secs)
