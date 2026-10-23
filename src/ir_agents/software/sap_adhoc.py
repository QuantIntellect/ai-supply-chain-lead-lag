"""Fetch SAP ad hoc announcements (sap.com IR mirror of EQS/DGAP) and extract EQS timestamps."""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(__file__))
import fetch_util as fu

SRC = os.path.join(fu.RAW_IR, "SAP.DE", "adhoc_urls_wayback.txt")
OUT = os.path.join(fu.RAW_IR, "SAP.DE", "adhoc_parsed.json")

def main(extra=()):
    urls = [u for u in open(SRC).read().split("\n") if u.endswith(".html")]
    urls += list(extra)
    res = []
    for u in urls:
        m = re.search(r"/(\d{4})/\d{2}/", u)
        if not m or int(m.group(1)) < 2014:
            continue
        h = fu.cached_html(u)
        if not h:
            print("NOFETCH", u); continue
        t = re.sub(r"\s+", " ", fu.html_to_text(h))
        ts = re.search(r"(\d{1,2}[-.](?:[A-Za-z]{3}|\d{2})[-.]\d{4}) ?/ ?(\d{1,2}:\d{2})( ?CET/CEST| ?CET| ?CEST)?", t)
        title = re.search(r"<title>(.*?)</title>", h, re.S)
        kw = re.search(r"Key word\(s\): ([^/]{0,80})", t)
        res.append({"url": u, "eqs_date": ts.group(1) if ts else None, "eqs_time": ts.group(2) if ts else None,
                    "title": re.sub(r"\s+", " ", title.group(1)).strip()[:160] if title else None,
                    "keywords": kw.group(1).strip() if kw else None})
        print(res[-1]["eqs_date"], res[-1]["eqs_time"], "|", (res[-1]["keywords"] or "")[:30], "|", (res[-1]["title"] or "")[:90])
    with open(OUT, "w") as f:
        json.dump(res, f, indent=1)

if __name__ == "__main__":
    main(sys.argv[1:])
