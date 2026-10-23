"""Download FY2015 Siemens earnings releases (event dating/timing evidence) and append to downloaded.json."""
import os, sys, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import *
T = "SIE.DE"; RAW = os.path.join(RAW_IR, T)
urls = json.load(open(os.path.join(RAW, "pages", "doc_links_fy15.json")))
dl = json.load(open(os.path.join(RAW, "pages", "downloaded.json")))
have = {d["url"] for d in dl}
f = Fetcher(min_gap=1.0)
for u in urls:
    href = "https:" + u if u.startswith("//") else u
    m = re.search(r"/2015-q([1-4])-earnings-release-e\.pdf$", href)
    if not m or href in have:
        continue
    p = f"2015Q{m.group(1)}"
    out = os.path.join(RAW, f"{p}_earnings_release.pdf")
    ok, st, _ = f.download(href, out)
    if ok and is_pdf(out):
        to_text(out, T, p, "earnings_release")
        dl.append({"local_path": out, "url": href, "doc_type": "earnings_release", "fiscal_period": p, "pub_date": ""})
        print("ok", p)
    else:
        print("fail", p, st)
json.dump(dl, open(os.path.join(RAW, "pages", "downloaded.json"), "w"), indent=1)
