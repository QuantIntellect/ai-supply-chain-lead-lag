"""Pull SEC EDGAR submission histories for every SEC-registered company in the universe.

Outputs
  data/raw/edgar/submissions/CIK##########*.json   raw submission JSON (incl. older pages)
  data/processed/edgar_filings.parquet             one row per filing (8-K, 10-Q, 10-K, 6-K, 20-F, 40-F)
"""
import os
import sys
import json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import requests
from common import RAW, PROC, SEC_UA, load_universe, ensure, polite_sleep

KEEP_FORMS = {"8-K", "8-K/A", "10-Q", "10-K", "10-K/A", "6-K", "20-F", "40-F", "10-KT"}
# SEC tickers for universe members (ADR / US line where the home listing is abroad)
SEC_TICKER = {"ASML.AS": "ASML", "STMPA.PA": "STM", "NOKIA.HE": "NOK", "SAP.DE": "SAP"}

S = requests.Session()
S.headers.update({"User-Agent": SEC_UA, "Accept-Encoding": "gzip, deflate"})


def get_json(url, path):
    if os.path.exists(path):
        return json.load(open(path))
    r = S.get(url, timeout=60)
    polite_sleep(0.15)
    r.raise_for_status()
    ensure(os.path.dirname(path))
    with open(path, "w") as f:
        f.write(r.text)
    return r.json()


def frame_from_block(block):
    df = pd.DataFrame(block)
    return df


def main():
    raw = ensure(os.path.join(RAW, "edgar", "submissions"))
    tick = get_json("https://www.sec.gov/files/company_tickers.json", os.path.join(raw, "company_tickers.json"))
    t2c = {v["ticker"].upper(): int(v["cik_str"]) for v in tick.values()}
    uni = load_universe()
    rows, cikmap = [], []
    for _, u in uni.iterrows():
        sec_tk = SEC_TICKER.get(u.ticker, u.ticker if u.region == "US" else None)
        if not sec_tk:
            continue
        cik = t2c.get(sec_tk.upper())
        if cik is None:
            print("no CIK for", u.ticker, sec_tk)
            continue
        cikmap.append({"ticker": u.ticker, "sec_ticker": sec_tk, "cik": cik})
        cik10 = f"{cik:010d}"
        sub = get_json(f"https://data.sec.gov/submissions/CIK{cik10}.json", os.path.join(raw, f"CIK{cik10}.json"))
        blocks = [sub["filings"]["recent"]]
        for extra in sub["filings"].get("files", []):
            nm = extra["name"]
            blocks.append(get_json(f"https://data.sec.gov/submissions/{nm}", os.path.join(raw, nm)))
        df = pd.concat([frame_from_block(b) for b in blocks], ignore_index=True)
        df = df[df["form"].isin(KEEP_FORMS)].copy()
        df["ticker"] = u.ticker
        df["cik"] = cik
        df["company"] = sub.get("name")
        rows.append(df)
        print(f"{u.ticker:9s} cik={cik:<8d} {sub.get('name')[:40]:40s} filings_kept={len(df)} forms={dict(df.form.value_counts())}")
    allf = pd.concat(rows, ignore_index=True)
    keep = ["ticker", "cik", "company", "form", "filingDate", "reportDate", "acceptanceDateTime", "items",
            "accessionNumber", "primaryDocument", "primaryDocDescription", "size"]
    allf = allf[[c for c in keep if c in allf.columns]]
    allf.to_parquet(os.path.join(PROC, "edgar_filings.parquet"), index=False)
    pd.DataFrame(cikmap).to_csv(os.path.join(PROC, "sec_cik_map.csv"), index=False)
    print("total filings", len(allf))


if __name__ == "__main__":
    main()
