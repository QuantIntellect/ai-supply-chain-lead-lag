"""Scrape Capgemini 'financial news' listing (all pages): title, date, time, publication link, file link."""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(__file__))
import fetch_util as fu
from bs4 import BeautifulSoup

OUT = os.path.join(fu.RAW_IR, "CAP.PA", "financial_news_list.json")
MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December"

def parse(html):
    soup = BeautifulSoup(html, "html.parser")
    items = []
    # Each item: has a date string and links (View online -> /publication/, Download -> /file/)
    for a in soup.find_all("a", href=re.compile(r"/en/(publication|file)/")):
        pass
    # generic approach: find elements containing 'View online' or 'Download pdf' and climb to item container
    seen = set()
    for a in soup.find_all("a", href=re.compile(r"/en/(publication/|file/)")):
        node = a
        for _ in range(5):
            if node.parent is None: break
            node = node.parent
            txt = node.get_text(" ", strip=True)
            if re.search(r"(%s) \d{1,2}, \d{4}" % MONTHS, txt) and len(txt) < 600:
                break
        key = id(node)
        if key in seen: continue
        seen.add(key)
        txt = re.sub(r"\s+", " ", node.get_text(" ", strip=True))
        m = re.search(r"^(.*?) ((?:%s) \d{1,2}, \d{4})(?: (\d{1,2}:\d{2} [ap]m) \(CET\))?" % MONTHS, txt)
        pubs = [x["href"] for x in node.find_all("a", href=re.compile(r"/en/publication/"))]
        files = [x["href"] for x in node.find_all("a", href=re.compile(r"/en/file/"))]
        items.append({"title": m.group(1) if m else txt[:150], "date": m.group(2) if m else None,
                      "time": m.group(3) if m else None, "pub": pubs[0] if pubs else None,
                      "file": files[0] if files else None, "raw": txt[:250]})
    return items

def main():
    out = []
    for p in range(1, 40):
        u = "https://investors.capgemini.com/en/financial-news/" + ("" if p == 1 else "page/%d/" % p)
        h = fu.cached_html(u)
        if not h:
            print("stop", p); break
        it = parse(h)
        if not it:
            print("empty", p); break
        out.extend(it)
        print(p, len(it), it[-1]["date"])
    json.dump(out, open(OUT, "w"), indent=1)

if __name__ == "__main__":
    main()
