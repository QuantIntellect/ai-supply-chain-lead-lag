"""DT: collect scheduled quarterly results dates from telekom.com year pages + newsroom meta dates."""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(__file__))
import fetch_util as fu

OUT = os.path.join(fu.RAW_IR, "DTE.DE", "dte_release_dates.json")

def main():
    rows = {}
    for y in range(2014, 2027):
        h = fu.cached_html("https://www.telekom.com/en/investor-relations/publications/financial-results/%d" % y)
        links = sorted(set(re.findall(r'href="(https://www\.telekom\.com/en/newsroom/latest-updates/media-information/(\d{4})/(\d{1,2})/[^"]+)"', h)))
        for (link, ly, lm) in links:
            ly, lm = int(ly), int(lm)
            if lm in (1, 2, 3, 4) and ly == y + 1:
                q = "%dQ4" % y
            elif lm in (4, 5, 6) and ly == y:
                q = "%dQ1" % y
            elif lm in (7, 8, 9) and ly == y:
                q = "%dQ2" % y
            elif lm in (10, 11, 12) and ly == y:
                q = "%dQ3" % y
            else:
                continue
            hh = fu.cached_html(link)
            m = re.search(r'<meta name="date" content="([0-9-]+)"', hh or "")
            t = re.search(r"<title>(.*?)</title>", hh or "", re.S)
            rows.setdefault(q, []).append({"q": q, "link": link, "meta_date": m.group(1) if m else None,
                                           "title": re.sub(r"\s+", " ", t.group(1)).strip()[:150] if t else None})
    with open(OUT, "w") as f:
        json.dump(rows, f, indent=1)
    for q in sorted(rows):
        for r in rows[q]:
            print(q, r["meta_date"], r["title"][:90] if r["title"] else None)

if __name__ == "__main__":
    main()
