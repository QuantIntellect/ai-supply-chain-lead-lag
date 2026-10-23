"""Parse Siemens IR results pages (current + archive) into a document link list."""
import os, sys, re, html, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import *
from bs4 import BeautifulSoup

PAGES = ["financial_results", "financial_results_archive"]
rows = []
for pg in PAGES:
    h = open(os.path.join(RAW_IR, "SIE.DE", "pages", pg + ".html"), encoding="utf-8", errors="ignore").read()
    h2 = h
    for _ in range(3):
        h2 = html.unescape(h2.replace('\\"', '"').replace('\\u002F', '/').replace('\\/', '/'))
    # find all richText tables
    for tm in re.finditer(r"<table>.*?</table>", h2, re.S):
        soup = BeautifulSoup(tm.group(0), "html.parser")
        for tr in soup.find_all("tr"):
            tds = tr.find_all("td")
            if not tds:
                continue
            label = tds[0].get_text(" ", strip=True)
            for a in tr.find_all("a"):
                href = a.get("href", "")
                if not href:
                    continue
                rows.append({"page": pg, "label": label, "text": a.get_text(" ", strip=True), "href": href})
seen = set(); out = []
for r in rows:
    k = r["href"]
    if k in seen:
        continue
    seen.add(k); out.append(r)
json.dump(out, open(os.path.join(RAW_IR, "SIE.DE", "pages", "doc_links.json"), "w"), indent=1)
print(len(out))
from collections import Counter
print(Counter(r["label"] for r in out).most_common(80))
