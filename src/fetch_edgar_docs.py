"""Download EDGAR documents: earnings press releases (8-K EX-99.x), foreign-filer earnings 6-K exhibits,
and the latest annual reports (10-K / 20-F) for customer-concentration / supplier disclosures.

Raw files: data/raw/edgar/docs/<TICKER>/<accession>_<document>
Text:      data/processed/edgar_text/<TICKER>/<filingDate>_<form>_<document>.txt
Index:     data/processed/edgar_docs_index.csv
"""
import os
import re
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from common import RAW, PROC, SEC_UA, ensure, polite_sleep

S = requests.Session()
S.headers.update({"User-Agent": SEC_UA, "Accept-Encoding": "gzip, deflate"})


def fetch(job):
    tk, cik, acc, doc, fdate, form = job
    raw = os.path.join(ensure(os.path.join(RAW, "edgar", "docs", tk)), f"{acc}_{doc}")
    txt_path = os.path.join(ensure(os.path.join(PROC, "edgar_text", tk)), f"{fdate}_{form}_{os.path.splitext(doc)[0]}.txt")
    if os.path.exists(txt_path):
        return (tk, acc, doc, fdate, form, txt_path, "cached")
    if not os.path.exists(raw):
        url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc.replace('-', '')}/{doc}"
        try:
            r = S.get(url, timeout=60)
        except requests.RequestException:
            return (tk, acc, doc, fdate, form, "", "error")
        polite_sleep(0.3)
        if r.status_code != 200:
            return (tk, acc, doc, fdate, form, "", f"http{r.status_code}")
        with open(raw, "wb") as f:
            f.write(r.content)
    if doc.lower().endswith(".pdf"):
        return (tk, acc, doc, fdate, form, raw, "pdf")
    html = open(raw, encoding="utf-8", errors="ignore").read()
    text = BeautifulSoup(html, "html.parser").get_text("\n")
    text = re.sub(r"\n\s*\n+", "\n", text)
    with open(txt_path, "w") as f:
        f.write(text)
    return (tk, acc, doc, fdate, form, txt_path, "ok")


def main():
    jobs = []
    cik = pd.read_csv(os.path.join(PROC, "sec_cik_map.csv")).set_index("ticker").cik.to_dict()
    # 1) earnings 8-K exhibits (EX-99.x) since 2014
    x8 = pd.read_parquet(os.path.join(PROC, "edgar_exhibits.parquet"))
    x8 = x8[x8.doc_type.str.upper().str.startswith("EX-99") & x8.document.str.lower().str.endswith((".htm", ".html", ".txt"))]
    for r in x8.itertuples():
        jobs.append((r.ticker, cik[r.ticker], r.accessionNumber, r.document, r.filingDate, "8K"))
    # 2) foreign filers: 6-K exhibits within 3 days of an earnings event
    x6 = pd.read_parquet(os.path.join(PROC, "edgar_exhibits_6k.parquet"))
    ev = pd.read_parquet(os.path.join(PROC, "events.parquet"))
    x6["fd"] = pd.to_datetime(x6.filingDate)
    keep = []
    for tk, g in x6.groupby("ticker"):
        d = ev[ev.ticker == tk].react_date
        if d.empty:
            continue
        near = g.fd.apply(lambda t: (abs(d - t) <= pd.Timedelta(days=3)).any())
        keep.append(g[near])
    if keep:
        x6 = pd.concat(keep)
        x6 = x6[x6.doc_type.str.upper().str.match(r"^(EX-99|EX-1|6-K)") & x6.document.str.lower().str.endswith((".htm", ".html", ".txt"))]
        for r in x6.itertuples():
            jobs.append((r.ticker, cik[r.ticker], r.accessionNumber, r.document, r.filingDate, "6K"))
    # 3) latest two annual reports per company (10-K or 20-F primary documents)
    f = pd.read_parquet(os.path.join(PROC, "edgar_filings.parquet"))
    ann = f[f.form.isin(["10-K", "20-F"])].sort_values("filingDate").groupby("ticker").tail(2)
    for r in ann.itertuples():
        jobs.append((r.ticker, r.cik, r.accessionNumber, r.primaryDocument, r.filingDate, r.form.replace("-", "")))
    jobs = list(dict.fromkeys(jobs))
    print("documents to fetch:", len(jobs), flush=True)
    with ThreadPoolExecutor(max_workers=8) as ex:
        res = list(ex.map(fetch, jobs))
    R = pd.DataFrame(res, columns=["ticker", "accession", "document", "filingDate", "kind", "path", "status"])
    R.to_csv(os.path.join(PROC, "edgar_docs_index.csv"), index=False)
    print(R.status.value_counts().to_string())
    print(R.groupby("kind").size().to_string())


if __name__ == "__main__":
    main()
