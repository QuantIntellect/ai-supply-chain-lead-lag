"""Fetch EDGAR filing-index pages for earnings 8-Ks (item 2.02) and quarterly 6-Ks.

The submissions JSON acceptanceDateTime is not reliable (offset varies by filing), so we
read the authoritative ET 'Accepted' stamp from each filing's -index.htm, and record the
exhibit table (EX-99.1 press release, EX-99.2 CFO commentary, ...) for document download.

Output: data/processed/edgar_earnings_index.parquet (one row per filing),
        data/processed/edgar_exhibits.parquet       (one row per document in those filings)
"""
import os
import re
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import requests
from bs4 import BeautifulSoup
from common import RAW, PROC, SEC_UA, ensure, polite_sleep

S = requests.Session()
S.headers.update({"User-Agent": SEC_UA, "Accept-Encoding": "gzip, deflate"})
CACHE = ensure(os.path.join(RAW, "edgar", "index_pages"))


def fetch_index(cik, acc):
    path = os.path.join(CACHE, f"{acc}-index.htm")
    if os.path.exists(path) and os.path.getsize(path) > 500:
        return open(path, encoding="utf-8", errors="ignore").read()
    url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc.replace('-', '')}/{acc}-index.htm"
    for _ in range(3):
        r = S.get(url, timeout=30)
        polite_sleep(0.12)
        if r.status_code == 200:
            with open(path, "w") as f:
                f.write(r.text)
            return r.text
    return ""


def parse_index(html):
    soup = BeautifulSoup(html, "html.parser")
    accepted = None
    for div in soup.find_all("div", class_="infoHead"):
        if div.get_text(strip=True) == "Accepted":
            accepted = div.find_next_sibling("div").get_text(strip=True)
    docs = []
    table = soup.find("table", class_="tableFile")
    if table:
        for tr in table.find_all("tr")[1:]:
            td = tr.find_all("td")
            if len(td) >= 4:
                a = td[2].find("a")
                docs.append({"seq": td[0].get_text(strip=True), "description": td[1].get_text(" ", strip=True),
                             "document": td[2].get_text(strip=True), "href": a["href"] if a else None,
                             "doc_type": td[3].get_text(strip=True)})
    return accepted, docs


def main():
    f = pd.read_parquet(os.path.join(PROC, "edgar_filings.parquet"))
    f = f[f.filingDate >= "2014-01-01"]
    is_earn = f.form.str.startswith("8-K") & f["items"].fillna("").str.contains("2.02")
    # 6-K filers: keep all 6-Ks; earnings ones are identified later by exhibit descriptions / dates
    is_6k = f.form.eq("6-K")
    mode = sys.argv[1] if len(sys.argv) > 1 else "8k"
    sel = f[is_earn].copy() if mode == "8k" else f[is_6k].copy()
    suffix = "" if mode == "8k" else "_6k"
    print("filings to index:", len(sel), "(8-K 2.02:", int(is_earn.sum()), ", 6-K:", int(is_6k.sum()), ")")
    rows, docs = [], []
    from concurrent.futures import ThreadPoolExecutor
    recs = list(sel.itertuples())
    with ThreadPoolExecutor(max_workers=3) as ex:
        pages = list(ex.map(lambda r: fetch_index(r.cik, r.accessionNumber), recs))
    for i, (r, html) in enumerate(zip(recs, pages)):
        acc_time, d = parse_index(html) if html else (None, [])
        rows.append({"ticker": r.ticker, "cik": r.cik, "form": r.form, "filingDate": r.filingDate,
                     "items": r.items, "accessionNumber": r.accessionNumber, "accepted_et": acc_time,
                     "primaryDocument": r.primaryDocument})
        for x in d:
            x.update({"ticker": r.ticker, "accessionNumber": r.accessionNumber, "form": r.form, "filingDate": r.filingDate})
            docs.append(x)
        if i % 250 == 0:
            print(i, r.ticker, r.filingDate, acc_time, flush=True)
    pd.DataFrame(rows).to_parquet(os.path.join(PROC, f"edgar_earnings_index{suffix}.parquet"), index=False)
    pd.DataFrame(docs).to_parquet(os.path.join(PROC, f"edgar_exhibits{suffix}.parquet"), index=False)
    print("done", len(rows), "filings,", len(docs), "documents")


if __name__ == "__main__":
    main()
