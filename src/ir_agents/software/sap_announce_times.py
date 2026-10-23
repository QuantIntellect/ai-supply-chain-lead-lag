"""Fetch SAP 'to release ... results' / timing posts and print sentences mentioning times."""
import sys, json, os, re
sys.path.insert(0, os.path.dirname(__file__))
import fetch_util as fu

js = json.load(open(os.path.join(fu.RAW_IR, "SAP.DE", "news_sap_posts.json")))
pat = re.compile(r"(to Release|to Announce|Updated Tim)", re.I)
for p in js:
    if not pat.search(p["title"]):
        continue
    h = fu.cached_html(p["link"])
    if not h:
        print("NOFETCH", p["link"]); continue
    txt = fu.html_to_text(h)
    i = txt.find(p["title"][:20])
    body = re.sub(r"\s+", " ", txt)
    sents = re.findall(r"[^.]*?(?:a\.m\.|p\.m\.|CET|CEST|EDT|EST|\d{1,2}:\d{2})[^.]*\.", body)
    print("==", p["date_gmt"][:16], p["title"][:70])
    for s in sents[:4]:
        print("   ", s.strip()[:260])
