"""Crawl Aixtron IR news listing (all pages) -> data/raw/ir/AIXA.DE/listing/*.html and a parsed CSV of items."""
import os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import irlib
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd

T = "AIXA.DE"
MONTHS = {m: i for i, m in enumerate(["januar", "februar", "märz", "april", "mai", "juni", "juli", "august",
                                       "september", "oktober", "november", "dezember"], 1)}
MONTHS.update({m: i for i, m in enumerate(["january", "february", "march", "april", "may", "june", "july", "august",
                                            "september", "october", "november", "december"], 1)})


def parse_date(s):
    m = re.search(r"(\d{1,2})\.\s*([A-Za-zäÄ]+)\s+(\d{4})", s)
    if not m:
        return ""
    mo = MONTHS.get(m.group(2).lower())
    return f"{m.group(3)}-{mo:02d}-{int(m.group(1)):02d}" if mo else ""


def main(base="https://www.aixtron.com/en/investors/news", tag="all", maxpage=40):
    d = irlib.ensure(os.path.join(irlib.raw_dir(T), "listing"))
    rows, seen_pages = [], set()
    for p in range(0, maxpage + 1):
        url = base if p == 0 else f"{base}?page={p}"
        path = os.path.join(d, f"{tag}_p{p:02d}.html")
        st, b = irlib.fetch(url, path)
        if st != 200:
            print("stop", p, st); break
        soup = BeautifulSoup(b, "html.parser")
        items = soup.select("div.box-press")
        if not items:
            print("no items page", p); break
        sig = tuple(a.get("href") for a in soup.select("div.box-press h2 a"))
        if sig in seen_pages:
            print("repeat page", p)
            if p > 2:
                break
            continue
        seen_pages.add(sig)
        for it in items:
            sm = it.find("small")
            a = it.select_one("h2 a")
            if not a:
                continue
            meta = " ".join(sm.get_text(" ", strip=True).split()) if sm else ""
            date = parse_date(meta)
            cat = meta.split("|", 1)[1].strip() if "|" in meta else ""
            rows.append({"date": date, "category": cat, "title": " ".join(a.get_text(" ", strip=True).split()),
                         "url": urljoin(url, a["href"]), "page": p})
    df = pd.DataFrame(rows).drop_duplicates("url")
    out = os.path.join(irlib.raw_dir(T), f"listing_{tag}.csv")
    df.to_csv(out, index=False)
    print(len(df), df.date.min(), df.date.max())
    print(df.category.value_counts().to_string())


if __name__ == "__main__":
    main(*(sys.argv[1:3])) if len(sys.argv) > 2 else main()
