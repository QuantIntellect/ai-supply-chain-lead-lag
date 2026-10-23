"""Scrape investor.3ds.com events calendar (all pages) -> data/raw/ir/DSY.PA/ir_calendar_events.json"""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(__file__))
import fetch_util as fu
from bs4 import BeautifulSoup

BASE = "https://investor.3ds.com"
OUT = os.path.join(fu.RAW_IR, "DSY.PA", "ir_calendar_events.json")

def parse(html):
    soup = BeautifulSoup(html, "html.parser")
    out = []
    for art in soup.select("article.ds-card"):
        t = art.select_one(".field-nir-event-title")
        d = art.select_one(".ds-card__info span")
        s = art.select_one(".nir-widget--event--summary")
        a = art.select_one(".ds-card__links a")
        out.append({"title": t.get_text(" ", strip=True) if t else "",
                    "date": d.get_text(" ", strip=True) if d else "",
                    "summary": s.get_text(" ", strip=True) if s else "",
                    "link": (BASE + a["href"]) if a and a.get("href", "").startswith("/") else (a["href"] if a else "")})
    return out

def main():
    allev = []
    for p in range(0, 12):
        u = BASE + "/events-presentations/calendar?page=%d%%2C0" % p
        h = fu.cached_html(u)
        if not h:
            break
        ev = parse(h)
        if not ev:
            break
        new = [e for e in ev if e not in allev]
        if not new:
            break
        allev.extend(new)
    # event detail pages
    for e in allev:
        if not e["link"]:
            continue
        h = fu.cached_html(e["link"])
        if not h:
            continue
        soup = BeautifulSoup(h, "html.parser")
        main_ = soup.select_one("main") or soup
        txt = re.sub(r"\s+", " ", main_.get_text(" ", strip=True))
        i = txt.find(e["title"][:15])
        e["detail"] = txt[i:i + 700] if i >= 0 else txt[:700]
        e["detail_links"] = sorted(set(a.get("href") for a in main_.find_all("a") if a.get("href") and
                                       re.search(r"(static-files|globenewswire|pdf|news-release|press)", a.get("href"), re.I)))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(allev, open(OUT, "w"), indent=1, ensure_ascii=False)
    for e in allev:
        print(e["date"], "|", e["title"][:70], "|", e["summary"][-80:])

if __name__ == "__main__":
    main()
