"""Second pass: month-level Wayback CDX queries (with retries) for SAP News results posts in
years where the year-level query failed. Merges into news_sap_wayback_posts.json."""
import sys, os, re, json, time
sys.path.insert(0, os.path.dirname(__file__))
import fetch_util as fu
from sap_wayback_posts import KEEP, DROP, OUT

def cdx_month(y, m):
    u = ("https://web.archive.org/cdx/search/cdx?url=news.sap.com/%d/%02d/*&filter=statuscode:200"
         "&fl=original,timestamp&collapse=urlkey&limit=5000" % (y, m))
    for attempt in range(5):
        try:
            r = fu.get(u, timeout=120, gap=2.0)
            if r.status_code == 200:
                return [l.split(" ") for l in r.text.splitlines() if len(l.split(" ")) == 2]
        except Exception as e:
            pass
        time.sleep(8 * (attempt + 1))
    print("CDX fail", y, m)
    return []

def main():
    res = json.load(open(OUT))
    have = {r["url"] for r in res}
    targets = [(2014, 12), (2015, 1)] + [(y, m) for y in (2016, 2017, 2019, 2021, 2022) for m in (1, 2, 4, 5, 7, 10, 11)]
    cands = {}
    for y, m in targets:
        if y == 2022 and m > 7:
            continue
        rows = cdx_month(y, m)
        for orig, ts in rows:
            base = re.sub(r"/amp/?$", "/", orig.split("?")[0].split("#")[0]).replace("http://", "https://").replace(":80/", "/")
            if not base.endswith("/"):
                base += "/"
            mm = re.match(r"https://news\.sap\.com/(\d{4})/(\d{2})/([^/]+)/$", base)
            if not mm or not KEEP.search(mm.group(3)) or DROP.search(mm.group(3)):
                continue
            if base in have:
                continue
            if base not in cands or ts < cands[base]:
                cands[base] = ts
        print(y, m, len(rows), len(cands))
    for base, ts in sorted(cands.items()):
        snap = "https://web.archive.org/web/%sid_/%s" % (ts, base)
        try:
            r = fu.get(snap, timeout=90, gap=1.5)
            h = r.text if r.status_code == 200 else ""
        except Exception:
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
