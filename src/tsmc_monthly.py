"""TSMC monthly revenue series from its SEC 6-K filings (released ~10th of each month).

Output: data/processed/tsmc_monthly.csv (month, revenue_ntd_bn, mom_pct, yoy_pct, release_date, accession)
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
S.headers.update({"User-Agent": SEC_UA})
CACHE = ensure(os.path.join(RAW, "edgar", "tsm_6k"))
PAT = re.compile(r"revenues? for ([A-Z][a-z]+)\s+(\d{4})\s+(?:were|was)\s+approximately\s+NT\$\s?([\d,\.]+)\s+(billion|million)", re.I)
CHG = re.compile(r"(increase|decrease) of\s+([\d\.]+)\s*(?:percent|%)\s+from\s+([A-Z][a-z]+)\s+(\d{4})", re.I)


def main():
    f = pd.read_parquet(os.path.join(PROC, "edgar_filings.parquet"))
    t = f[(f.ticker == "TSM") & (f.form == "6-K")].copy()
    t["day"] = pd.to_datetime(t.filingDate).dt.day
    t = t[(t.day <= 15) & (t.filingDate >= "2014-01-01")]
    rows = []
    for r in t.itertuples():
        path = os.path.join(CACHE, f"{r.accessionNumber}_{r.primaryDocument}")
        if not os.path.exists(path):
            url = f"https://www.sec.gov/Archives/edgar/data/{r.cik}/{r.accessionNumber.replace('-', '')}/{r.primaryDocument}"
            resp = S.get(url, timeout=30)
            polite_sleep(0.2)
            if resp.status_code != 200:
                continue
            with open(path, "w") as fh:
                fh.write(resp.text)
        txt = BeautifulSoup(open(path, encoding="utf-8", errors="ignore").read(), "html.parser").get_text(" ")
        txt = re.sub(r"\s+", " ", txt)
        m = PAT.search(txt)
        if not m:
            continue
        mon, yr, val, unit = m.groups()
        v = float(val.replace(",", "")) * (1 if unit.lower() == "billion" else 1e-3)
        rec = {"month": pd.Timestamp(f"1 {mon} {yr}"), "revenue_ntd_bn": v, "release_date": r.filingDate,
               "accession": r.accessionNumber}
        for c in CHG.finditer(txt[m.end(): m.end() + 400]):
            sign = 1 if c.group(1).lower() == "increase" else -1
            ref = pd.Timestamp(f"1 {c.group(3)} {c.group(4)}")
            months = (rec["month"].year - ref.year) * 12 + rec["month"].month - ref.month
            if months == 1:
                rec["mom_pct"] = sign * float(c.group(2))
            elif months == 12:
                rec["yoy_pct"] = sign * float(c.group(2))
        rows.append(rec)
    M = pd.DataFrame(rows).sort_values(["month", "release_date"]).drop_duplicates("month", keep="first")
    M.to_csv(os.path.join(PROC, "tsmc_monthly.csv"), index=False)
    print(len(M), "months", M.month.min().date(), "->", M.month.max().date())
    print(M.tail(14).to_string(index=False))


if __name__ == "__main__":
    main()
