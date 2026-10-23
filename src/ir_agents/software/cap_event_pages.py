"""Fetch Capgemini event detail pages (2014-2026 results/CMD/M&A) and parse publication lists with times."""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(__file__))
import fetch_util as fu
from bs4 import BeautifulSoup

IN = os.path.join(fu.RAW_IR, "CAP.PA", "calendar_events.json")
OUT = os.path.join(fu.RAW_IR, "CAP.PA", "event_pages.json")
MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December"
KEEP = re.compile(r"(results|revenues|capital market|analyst day|acquisition|investor day|webinar)", re.I)

def parse_event(html):
    soup = BeautifulSoup(html, "html.parser")
    for t in soup(["script", "style", "noscript"]):
        t.decompose()
    text = re.sub(r"\s+", " ", soup.get_text(" ", strip=True))
    i = text.find("Search Switch sites")
    body = text[i + 60:] if i >= 0 else text
    j = body.find("On this site")
    body = body[:j] if j > 0 else body
    m = re.search(r"(%s) (\d{1,2}), (\d{4})(?: Starts at (\d{1,2}:\d{2} [ap]m))?" % MONTHS, body)
    pubs = []
    for pm in re.finditer(r"(Press release|Press Release|Presentation|Infographic|Report|Video|Other document|Webcast|Audio|Transcript|Podcast) (.{3,160}?) ((?:%s) \d{1,2}, \d{4})(?: (\d{1,2}:\d{2} [ap]m) \(CET\))?" % MONTHS, body):
        pubs.append({"type": pm.group(1), "title": pm.group(2).strip(), "date": pm.group(3), "time": pm.group(4)})
    links = sorted(set(a["href"] for a in soup.find_all("a", href=True)
                       if re.search(r"/publication/|\.pdf|uploads", a["href"])))
    return {"head": body[:900], "date": (" ".join(m.groups()[:3]) if m else None),
            "starts": (m.group(4) if m else None), "pubs": pubs, "links": links}

def main():
    evs = json.load(open(IN))
    out = []
    for e in evs:
        txt = e["card_text"]
        y = re.search(r"\b(19|20)\d{2}\b(?=[^\d]*Add to Calendar)", txt)
        yr = int(re.search(r"(?:%s) \d{1,2}, (\d{4})" % MONTHS, txt).group(1)) if re.search(r"(?:%s) \d{1,2}, (\d{4})" % MONTHS, txt) else 0
        if yr < 2014 or not KEEP.search(txt):
            continue
        h = fu.cached_html(e["url"])
        if not h:
            print("NOFETCH", e["url"]); continue
        d = parse_event(h)
        d["url"] = e["url"]; d["card_text"] = txt
        out.append(d)
        print(e["url"].split("/event/")[1][:40], d["date"], d["starts"], len(d["pubs"]))
    json.dump(out, open(OUT, "w"), indent=1)

if __name__ == "__main__":
    main()
