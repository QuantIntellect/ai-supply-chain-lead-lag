"""Crawl VAT Group news listing (news?year=YYYY&page=N) and build an index of all news items.
Output: data/raw/ir/VACN.SW/news_index.json (list of {date, tags, title, teaser, url})."""
import os
import sys
import json
import re
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import fetch, raw_dir
from bs4 import BeautifulSoup

T = "VACN.SW"
BASE = "https://www.vatgroup.com"
listdir = os.path.join(raw_dir(T), "listing")
os.makedirs(listdir, exist_ok=True)


def parse(html):
    soup = BeautifulSoup(html, "html.parser")
    out = []
    for art in soup.find_all("article", class_="little-article"):
        a = art.find("a", href=True)
        if not a:
            continue
        tags = [" ".join(s.get_text(" ", strip=True).split()) for s in art.find_all("span", class_="tag")]
        date = None
        if tags:
            try:
                date = datetime.strptime(tags[0], "%b %d, %Y").strftime("%Y-%m-%d")
            except ValueError:
                date = None
        title = art.find(class_="little-article__title")
        teaser = art.find(class_="little-article__text")
        href = a["href"]
        if href.startswith("/"):
            href = BASE + href
        out.append({"date": date, "tags": tags[1:], "title": title.get_text(" ", strip=True) if title else "",
                    "teaser": teaser.get_text(" ", strip=True) if teaser else "", "url": href})
    pages = set(int(x) for x in re.findall(r"page=(\d+)", html))
    return out, pages


def main():
    items = []
    for year in range(2016, 2027):
        page = 1
        maxpage = 1
        while page <= maxpage:
            url = f"{BASE}/news?year={year}" + (f"&page={page}" if page > 1 else "")
            path = os.path.join(listdir, f"news_{year}_p{page}.html")
            st, b = fetch(url, path)
            html = b.decode("utf-8", "ignore")
            its, pages = parse(html)
            if pages:
                maxpage = max(maxpage, max(pages))
            print(year, page, st, len(its), "maxpage", maxpage)
            items.extend(its)
            page += 1
    seen, uniq = set(), []
    for it in items:
        if it["url"] in seen:
            continue
        seen.add(it["url"])
        uniq.append(it)
    json.dump(uniq, open(os.path.join(raw_dir(T), "news_index.json"), "w"), indent=1)
    print("items", len(uniq), "investor items", sum('Investors' in i['tags'] for i in uniq))


if __name__ == "__main__":
    main()
