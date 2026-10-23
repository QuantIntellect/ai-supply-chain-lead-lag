"""Page through the EQS company news widget for Siemens Energy AG (newsType ADHOC / ANNOUNCEMENT / ALL)
and write a TSV of (data-current-time [UTC per EQS], shown time, date group, category, heading, url)."""
import sys; sys.path.insert(0, "/Users/sinamirzaei/Documents/aimapping/src/ir_agents/energy"); import irlib
import re, os
from urllib.parse import urlencode
from bs4 import BeautifulSoup
SP = "/private/tmp/claude-501/-Users-sinamirzaei-Documents-aimapping/57e0a0d0-6441-40ef-828b-57eeb87e7b21/scratchpad/enr"
CID = "72871984-b098-1014-985c-772d05d60f5f"
news_type = sys.argv[1] if len(sys.argv) > 1 else "ADHOC"
maxpages = int(sys.argv[2]) if len(sys.argv) > 2 else 10
rows = []
for p in range(1, maxpages + 1):
    q = {"lang": "en", "action": "fetch_eqs_financial_news_data", "newsType": news_type, "pageLimit": 30,
         "pageNo": p, "additional[is_new]": "false", "loadFrom": "mysql", "companyName": "Siemens Energy AG",
         "companyId": CID, "parseBy": "newsgrouping"}
    r = irlib.fetch("https://www.eqs-news.com/wp/wp-admin/admin-ajax.php?" + urlencode(q))
    s = BeautifulSoup(r.text, "html.parser")
    n = 0
    cur_date = ""
    cur_ts = ""
    for el in s.find_all(True):
        if el.has_attr("data-financial-news-hidden"):
            cur_ts = el.get("data-current-time", "")
        if el.has_attr("data-financial-news-date-grouped"):
            cur_date = el.get_text(strip=True)
        if el.name == "a" and el.get("data-wio") == "news-feed-list-item":
            t = el.select_one(".news__time")
            h = el.select_one(".news__heading")
            rows.append([cur_ts, t.get_text(strip=True) if t else "", cur_date, el.get("data-news-category", ""),
                         (h.get_text(" ", strip=True) if h else "").replace("\t", " "), el.get("href", "")])
            n += 1
    print(f"page {p}: {n} items; last date {cur_date}")
    if n < 30:
        break
out = os.path.join(SP, f"eqs_{news_type}.tsv")
with open(out, "w") as f:
    for r_ in rows:
        f.write("\t".join(r_) + "\n")
print("wrote", len(rows), out)
