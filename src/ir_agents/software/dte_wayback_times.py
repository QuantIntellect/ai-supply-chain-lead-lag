"""DT: look for the announced publication time of each quarterly release in Wayback snapshots
of telekom.com IR pages taken in the ~3 weeks before the release date."""
import sys, os, re, json, datetime as dt
sys.path.insert(0, os.path.dirname(__file__))
import fetch_util as fu

DATES = ["2015-02-26","2015-05-13","2015-08-06","2015-11-05","2016-02-25","2016-05-04","2016-08-11","2016-11-10",
         "2017-03-02","2017-05-11","2017-08-03","2017-11-09","2018-02-22","2018-05-09","2018-08-09","2018-11-08",
         "2019-02-21","2019-05-09","2019-08-08","2019-11-07","2020-02-19","2020-05-14","2020-08-13","2020-11-12",
         "2021-02-26","2021-05-12","2021-08-12","2021-11-12","2022-02-24","2022-05-13","2022-08-11","2022-11-10",
         "2023-02-23","2023-05-11","2023-08-10","2023-11-09","2024-02-23","2024-05-16","2024-08-08","2024-11-14",
         "2025-02-26","2025-05-15","2025-08-07","2025-11-13","2026-02-26","2026-05-13","2026-08-06"]
PAGES = ["www.telekom.com/en/investor-relations/publications/financial-results",
         "www.telekom.com/en/investor-relations/financial-calendar",
         "www.telekom.com/en/investor-relations/service/financial-calendar",
         "www.telekom.com/en/investor-relations",
         "www.telekom.com/de/investor-relations/finanzpublikationen/finanzergebnisse",
         "www.telekom.com/en/investor-relations/investor-relations"]
OUT = os.path.join(fu.RAW_IR, "DTE.DE", "dte_wayback_times.json")
PAT = re.compile(r"(?:Publication of the results[^:]{0,40}|Agenda|Document downloads|Publication|Veröffentlichung[^:]{0,40}|publish(?:es)? its results[^.]{0,80})[: ]{0,3}(?:at )?(\d{1,2}[:.]\d{2})\s*(?:a\.m\.|Uhr|CET|CEST|MEZ|MESZ|h)?", re.I)

def cdx(page, d):
    d0 = (dt.date.fromisoformat(d) - dt.timedelta(days=21)).strftime("%Y%m%d")
    d1 = (dt.date.fromisoformat(d) - dt.timedelta(days=0)).strftime("%Y%m%d") + "050000"
    u = ("http://web.archive.org/cdx/search/cdx?url=%s&output=json&from=%s&to=%s&filter=statuscode:200" % (page, d0, d1))
    try:
        r = fu.get(u, timeout=90, gap=1.5)
        js = r.json()
        return [x[1] for x in js[1:]]
    except Exception as e:
        return []

def main():
    res = json.load(open(OUT)) if os.path.exists(OUT) else {}
    for d in DATES:
        if d in res and res[d].get("hits"):
            continue
        hits, tried = [], 0
        for page in PAGES:
            snaps = cdx(page, d)
            for ts in snaps[::-1][:2]:
                tried += 1
                h = fu.cached_html("http://web.archive.org/web/%sid_/https://%s" % (ts, page), timeout=90, gap=1.5)
                if not h:
                    continue
                t = re.sub(r"\s+", " ", fu.html_to_text(h))
                # look only in windows that mention the release date's month/day
                dd = dt.date.fromisoformat(d)
                keys = [dd.strftime("%B %-d, %Y"), dd.strftime("%b %d, %Y"), dd.strftime("%d.%m.%Y"), dd.strftime("%-d. %B %Y"), dd.strftime("%B %-d")]
                for k in keys:
                    for m in re.finditer(re.escape(k), t):
                        win = t[m.start(): m.start() + 600]
                        mm = PAT.search(win)
                        if mm:
                            hits.append({"ts": ts, "page": page, "time": mm.group(1), "ctx": win[:300]})
                if hits:
                    break
            if hits:
                break
        res[d] = {"tried": tried, "hits": hits[:3]}
        print(d, tried, hits[0]["time"] if hits else None, flush=True)
        with open(OUT, "w") as f:
            json.dump(res, f, indent=1)

if __name__ == "__main__":
    main()
