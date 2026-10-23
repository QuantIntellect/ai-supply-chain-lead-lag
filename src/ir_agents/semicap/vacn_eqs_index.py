"""Index all VAT Group news on EQS News (distribution service; times shown in CET/CEST local time).
Page 1 = company page HTML; further pages via the site's admin-ajax endpoint (same call the page's JS makes).
Output: data/raw/ir/VACN.SW/eqs_index.json  [{date, time, kind, title, url}]"""
import os
import sys
import re
import json
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import fetch, raw_dir, session, throttle
from bs4 import BeautifulSoup

T = "VACN.SW"
UUID = "5c28f07e-ea7c-11e8-902f-2c44fd856d8c"
COMPANY = f"https://www.eqs-news.com/company/vat-group-ag/news/{UUID}"
AJAX = "https://www.eqs-news.com/wp/wp-admin/admin-ajax.php?lang=en"
outdir = os.path.join(raw_dir(T), "eqs")
os.makedirs(outdir, exist_ok=True)


def parse(html):
    """Return list of items. Dates appear as group headers ('15 October 2026'); items carry HH:MM."""
    soup = BeautifulSoup(html, "html.parser")
    items = []
    cur_date = None
    # walk all elements in document order; date headers & news links
    for el in soup.find_all(True):
        txt = " ".join(el.get_text(" ", strip=True).split()) if el.name in ("h2", "h3", "h4", "div", "span", "p") else ""
        if el.name == "a" and el.get("href", "").startswith("https://www.eqs-news.com/news/") and el["href"].endswith("_en"):
            t = " ".join(el.get_text(" ", strip=True).split())
            m = re.match(r"^(?:(\d{1,2} [A-Z][a-z]+ \d{4}) )?(\d{2}:\d{2}) (\S+) (.*)$", t)
            if not m:
                continue
            if m.group(1):
                cur_date = m.group(1)
            title = m.group(4)
            title = re.sub(r"^VAT Group AG (Ad-hoc|Corporate|[A-Za-z-]+) ", "", title)
            items.append({"date_raw": cur_date, "time": m.group(2), "kind": m.group(3), "title": title,
                          "url": el["href"]})
        elif txt and re.fullmatch(r"\d{1,2} [A-Z][a-z]+ \d{4}", txt):
            cur_date = txt
    for it in items:
        try:
            it["date"] = datetime.strptime(it["date_raw"], "%d %B %Y").strftime("%Y-%m-%d") if it["date_raw"] else None
        except ValueError:
            it["date"] = None
    return items


def main():
    allitems = []
    st, b = fetch(COMPANY, os.path.join(outdir, "company_p1.html"))
    its = parse(b.decode("utf-8", "ignore"))
    print("p1", st, len(its), its[0] if its else None)
    allitems += its
    page = 2
    while page < 40:
        path = os.path.join(outdir, f"company_p{page}.html")
        if os.path.exists(path):
            html = open(path, encoding="utf-8", errors="ignore").read()
        else:
            data = {"action": "fetch_eqs_financial_news_data", "newsType": "ALL", "pageLimit": "30",
                    "pageNo": str(page), "additional[is_new]": "false", "loadFrom": "mysql",
                    "companyName": "VAT Group AG", "companyId": UUID, "parseBy": "newsgrouping", "time": ""}
            throttle(AJAX)
            r = session().post(AJAX, data=data, headers={"Referer": COMPANY, "X-Requested-With": "XMLHttpRequest"},
                               timeout=40)
            html = r.text
            open(path, "w").write(html)
        its = parse(html)
        print("page", page, len(its), its[-1]["date"] if its else None)
        if not its:
            break
        allitems += its
        page += 1
    seen, uniq = set(), []
    for it in allitems:
        if it["url"] in seen:
            continue
        seen.add(it["url"])
        uniq.append(it)
    json.dump(uniq, open(os.path.join(raw_dir(T), "eqs_index.json"), "w"), indent=1)
    print("total", len(uniq), "min date", min(i["date"] for i in uniq if i["date"]))


if __name__ == "__main__":
    main()
