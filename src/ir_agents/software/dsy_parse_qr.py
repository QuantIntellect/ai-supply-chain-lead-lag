"""Parse investor.3ds.com quarterly-results page(s) into a list of (year, quarter, label, title, url)."""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(__file__))
import fetch_util as fu
from bs4 import BeautifulSoup

BASE = "https://investor.3ds.com"

def parse(html):
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    # find all acc-title (quarter) and their following acc-body
    for t in soup.select(".acc-title"):
        q = t.get_text(strip=True)
        body = t.find_next_sibling(class_="acc-body")
        if body is None:
            continue
        # year: nearest preceding heading containing a 4-digit year
        yr = None
        prev = t.find_previous(string=re.compile(r"^\s*(19|20)\d{2}\s*$"))
        if prev:
            yr = prev.strip()
        for a in body.find_all("a"):
            href = a.get("href", "")
            if href.startswith("/"):
                href = BASE + href
            rows.append({"year": yr, "q": q, "label": a.get_text(strip=True),
                         "title": a.get("title", ""), "url": href})
    return rows

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else BASE + "/financial-information/quarterly-results"
    h = fu.cached_html(url)
    rows = parse(h)
    for r in rows:
        print(r["year"], r["q"], "|", r["label"][:40], "|", r["title"][:70], "|", r["url"][-60:])
