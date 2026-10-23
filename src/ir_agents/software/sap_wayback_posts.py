"""Recover pre-2022-07 SAP News Center results posts via the Wayback CDX API and read
article:published_time from archived snapshots."""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(__file__))
import fetch_util as fu

OUT = os.path.join(fu.RAW_IR, "SAP.DE", "news_sap_wayback_posts.json")
KEEP = re.compile(r"(sap-announces|sap-reports|preliminary|outlook|sap-to-release|sap-to-announce|"
                  r"ambition|capital-markets|guidance|quarter|half-year|full-year|year-end|ad-hoc|adhoc|"
                  r"results|financial-analyst|investor-day|restructuring|share-buyback|repurchase)", re.I)
DROP = re.compile(r"(customer|partner|award|study|survey|business-results|cpq|black-friday|employee-experience|"
                  r"podcast|webinar|-cloud-data-business|retail|insurer|sapphire-now|teched)", re.I)

def cdx(year):
    u = ("https://web.archive.org/cdx/search/cdx?url=news.sap.com/%d/*&filter=statuscode:200"
         "&fl=original,timestamp&collapse=urlkey&limit=20000" % year)
    r = fu.get(u, timeout=120, gap=2.0)
    if r.status_code != 200:
        print("CDX fail", year, r.status_code); return []
    rows = []
    for line in r.text.splitlines():
        parts = line.split(" ")
        if len(parts) == 2:
            rows.append(parts)
    return rows

def main():
    cands = {}
    for y in range(2014, 2023):
        rows = cdx(y)
        for orig, ts in rows:
            base = orig.split("?")[0].split("#")[0]
            base = re.sub(r"/amp/?$", "/", base)
            base = base.replace("http://", "https://").replace(":80/", "/")
            if not base.endswith("/"):
                base += "/"
            m = re.match(r"https://news\.sap\.com/(\d{4})/(\d{2})/([^/]+)/$", base)
            if not m:
                continue
            slug = m.group(3)
            if KEEP.search(slug) and not DROP.search(slug):
                if base not in cands or ts < cands[base]:
                    cands[base] = ts
        print(y, len(rows), "cands so far", len(cands))
    res = []
    for base, ts in sorted(cands.items()):
        snap = "https://web.archive.org/web/%sid_/%s" % (ts, base)
        try:
            r = fu.get(snap, timeout=90, gap=1.5)
            h = r.text if r.status_code == 200 else ""
        except Exception as e:
            h = ""
        pt = re.search(r'article:published_time"\s+content="([^"]+)"', h)
        title = re.search(r"<title>(.*?)</title>", h, re.S)
        body = re.sub(r"\s+", " ", fu.html_to_text(h)) if h else ""
        i = body.find("WALLDORF")
        res.append({"url": base, "snapshot_ts": ts, "published_time": pt.group(1) if pt else None,
                    "title": re.sub(r"\s+", " ", title.group(1)).strip() if title else None,
                    "dateline": body[i:i + 400] if i >= 0 else body[:200]})
        print(res[-1]["published_time"], base[22:110])
    with open(OUT, "w") as f:
        json.dump(res, f, indent=1)

if __name__ == "__main__":
    main()
