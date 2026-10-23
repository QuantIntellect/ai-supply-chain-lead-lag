"""Scrape Capgemini investor calendar (past + upcoming) into a raw JSON list."""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(__file__))
import fetch_util as fu
from bs4 import BeautifulSoup

OUT = os.path.join(fu.RAW_IR, "CAP.PA", "calendar_events.json")

def parse(html):
    soup = BeautifulSoup(html, "html.parser")
    out = []
    # each event card contains a 'View event details' link to /event/<slug>/
    for a in soup.find_all("a", href=re.compile(r"/en/event/[^/]+/?$")):
        card = a
        # climb to a container that has the date text
        for _ in range(6):
            if card.parent is None:
                break
            card = card.parent
            txt = card.get_text(" ", strip=True)
            if re.search(r"(January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4}", txt):
                break
        txt = re.sub(r"\s+", " ", card.get_text(" ", strip=True))
        out.append({"url": a["href"], "card_text": txt[:400]})
    return out

def main():
    allev = {}
    pages = ["https://investors.capgemini.com/en/calendar-past/"] + \
            ["https://investors.capgemini.com/en/calendar-past/page/%d/" % i for i in range(2, 30)] + \
            ["https://investors.capgemini.com/en/calendar/"]
    for u in pages:
        h = fu.cached_html(u)
        if not h:
            print("stop at", u); 
            if "calendar-past" in u:
                continue
            else:
                continue
        evs = parse(h)
        if not evs and "calendar-past/page" in u:
            print("empty", u); break
        for e in evs:
            allev.setdefault(e["url"], e)
        print(u.split("/en/")[1], len(evs), len(allev))
    with open(OUT, "w") as f:
        json.dump(list(allev.values()), f, indent=1)

if __name__ == "__main__":
    main()
