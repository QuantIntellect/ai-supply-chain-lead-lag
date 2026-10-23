"""DT: enumerate archived financial-calendar detail pages (Wayback CDX) and extract the announced publication time."""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(__file__))
import fetch_util as fu

OUT = os.path.join(fu.RAW_IR, "DTE.DE", "dte_calendar_detail.json")

def main():
    urls = {}
    for pre in ["www.telekom.com/en/investor-relations/financial-calendar/details/",
                "www.telekom.com/en/investor-relations/service/financial-calendar/details/",
                "www.telekom.com/de/investor-relations/finanzkalender/details/"]:
        try:
            r = fu.get("http://web.archive.org/cdx/search/cdx?url=%s&matchType=prefix&output=json&filter=statuscode:200&collapse=urlkey&limit=3000" % pre, timeout=180, gap=1.5)
            js = r.json()
        except Exception as e:
            print("CDXERR", pre, repr(e)[:100]); continue
        for x in js[1:]:
            urls[x[2].split("?")[0]] = x[1]
        print(pre, len(js) - 1, flush=True)
    res = json.load(open(OUT)) if os.path.exists(OUT) else {}
    for u, ts in sorted(urls.items()):
        if u in res:
            continue
        h = fu.cached_html("http://web.archive.org/web/%sid_/%s" % (ts, u), timeout=90, gap=1.5)
        if not h:
            res[u] = {"ts": ts, "err": True}; continue
        from bs4 import BeautifulSoup
        s = BeautifulSoup(h, "html.parser"); main = s.find("main") or s
        t = re.sub(r"\s+", " ", main.get_text(" "))
        title = s.title.get_text(strip=True) if s.title else ""
        times = re.findall(r".{0,90}\b\d{1,2}[:.]\d{2}\s*(?:a\.m\.|p\.m\.|CET|CEST|MEZ|MESZ|Uhr|GMT|h\b).{0,60}", t)
        dates = re.findall(r"(?:January|February|March|April|May|June|July|August|September|October|November|December|Mai) \d{1,2},? \d{4}|\d{2}\.\d{2}\.\d{4}|\d{1,2}\. \w+ \d{4}", t)
        res[u] = {"ts": ts, "title": title[:150], "dates": dates[:4], "times": times[:6]}
        print(ts, u.split("details/")[-1][:70], "|", dates[:1], "|", (times[0][:120] if times else None), flush=True)
        json.dump(res, open(OUT, "w"), indent=1)

if __name__ == "__main__":
    main()
