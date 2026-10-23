"""Scrape investor.3ds.com news releases (2015-2026) incl. publication datetime for results-related items.
Output: data/raw/ir/DSY.PA/ir_news_releases.json
"""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(__file__))
import fetch_util as fu
from bs4 import BeautifulSoup
from urllib.parse import quote

BASE = "https://investor.3ds.com"
OUT = os.path.join(fu.RAW_IR, "DSY.PA", "ir_news_releases.json")
YEARPARAM = "aac2c52233ec9ed03e44a98dd9028c83ac2c52a24dacec95b3c1757c0d59015b_year[value]"
REL = re.compile(r"(quarter|results|outlook|guidance|objective|capital markets|preliminary|first half|half-year|"
                 r"full year|fiscal|revenue|earnings|targets|growth plan|reports|financial|investor)", re.I)
NEG = re.compile(r"(declaration of the number|share buyback|liquidity contract|availability of|"
                 r"annual general|shareholders.? meeting|dividend|bond)", re.I)

def list_year(y):
    out = []
    for p in range(0, 15):
        u = BASE + "/news-releases?" + quote(YEARPARAM) + "=%d&page=%d" % (y, p)
        h = fu.cached_html(u)
        if not h:
            break
        soup = BeautifulSoup(h, "html.parser")
        arts = [a for a in soup.select("article") if a.find("a", href=re.compile("news-release-details"))]
        got = 0
        for a in arts:
            link = a.find("a", href=re.compile("news-release-details"))["href"]
            txt = re.sub(r"\s+", " ", a.get_text(" ", strip=True))
            m = re.search(r"([A-Z][a-z]+ \d{1,2}, (19|20)\d{2})", txt)
            title = txt.replace("News ", "", 1)
            if m:
                title = title[:title.find(m.group(1))].strip()
            rec = {"year": y, "title": title, "date": m.group(1) if m else "", "link": BASE + link if link.startswith("/") else link}
            if rec not in out:
                out.append(rec); got += 1
        if got == 0 or not soup.select_one(".pager__item--next"):
            break
    return out

def detail(rec):
    h = fu.cached_html(rec["link"])
    if not h:
        return
    soup = BeautifulSoup(h, "html.parser")
    d = soup.select_one(".field--name-field-nir-news-date")
    rec["datetime_text"] = d.get_text(" ", strip=True) if d else ""
    body = soup.select_one(".node__content") or soup.select_one("article") or soup
    links = sorted(set(a.get("href") for a in body.find_all("a") if a.get("href") and
                       re.search(r"(static-files|globenewswire|\.pdf)", a.get("href"), re.I)))
    rec["links"] = links[:20]

def main():
    allrec = []
    for y in range(2015, 2027):
        recs = list_year(y)
        print(y, len(recs))
        allrec.extend(recs)
    for r in allrec:
        if REL.search(r["title"]) and not NEG.search(r["title"]):
            detail(r)
    json.dump(allrec, open(OUT, "w"), indent=1, ensure_ascii=False)

if __name__ == "__main__":
    main()
