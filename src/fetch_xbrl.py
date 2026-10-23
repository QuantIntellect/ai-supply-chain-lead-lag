"""Quarterly fundamentals from SEC XBRL companyfacts (US-GAAP filers).

Derives discrete quarterly values from YTD cash-flow facts by differencing within a fiscal year.
Output: data/processed/fundamentals_q.parquet  (ticker, concept, period_start, period_end, value, filed)
"""
import os
import sys
import json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import requests
from common import RAW, PROC, SEC_UA, ensure, polite_sleep

S = requests.Session()
S.headers.update({"User-Agent": SEC_UA, "Accept-Encoding": "gzip, deflate"})

CONCEPTS = {
    "revenue": ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet",
                "RevenueFromContractWithCustomerIncludingAssessedTax"],
    "capex": ["PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsToAcquireProductiveAssets",
              "PaymentsForCapitalImprovements"],
    "finance_lease_principal": ["FinanceLeasePrincipalPayments"],
    "gross_profit": ["GrossProfit"],
    "operating_income": ["OperatingIncomeLoss"],
    "rpo": ["RevenueRemainingPerformanceObligation"],
    "inventory": ["InventoryNet"],
    "deferred_revenue": ["ContractWithCustomerLiabilityCurrent", "DeferredRevenueCurrent"],
}
INSTANT = {"rpo", "inventory", "deferred_revenue"}


def companyfacts(cik):
    path = os.path.join(ensure(os.path.join(RAW, "edgar", "companyfacts")), f"CIK{cik:010d}.json")
    if not os.path.exists(path):
        r = S.get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json", timeout=90)
        polite_sleep(0.2)
        if r.status_code != 200:
            return None
        with open(path, "w") as f:
            f.write(r.text)
    return json.load(open(path))


def facts_frame(cf, tags):
    """All USD facts for the first tag list members present; prefer later-listed tags only when earlier missing."""
    gaap = cf.get("facts", {}).get("us-gaap", {})
    frames = []
    for pri, tag in enumerate(tags):
        if tag not in gaap:
            continue
        for unit, vals in gaap[tag]["units"].items():
            if unit != "USD":
                continue
            df = pd.DataFrame(vals)
            df["tag"], df["pri"] = tag, pri
            frames.append(df)
    if not frames:
        return None
    df = pd.concat(frames, ignore_index=True)
    df["end"] = pd.to_datetime(df["end"])
    if "start" in df:
        df["start"] = pd.to_datetime(df["start"])
    df["filed"] = pd.to_datetime(df["filed"])
    return df


def quarterly_flow(df):
    """Discrete quarter values from duration facts (direct 3-month facts or YTD differences)."""
    df = df.dropna(subset=["start"]).copy()
    df["days"] = (df.end - df.start).dt.days
    # for each (start,end) keep the best tag (lowest pri) and the earliest filing (first public)
    df = df.sort_values(["pri", "filed"]).drop_duplicates(["start", "end"], keep="first")
    first_filed = df.groupby(["start", "end"]).filed.min()
    val = {(r.start, r.end): r.val for r in df.itertuples()}
    out = {}
    q = df[(df.days >= 80) & (df.days <= 100)]
    for r in q.itertuples():
        out[r.end] = (r.start, r.val, first_filed[(r.start, r.end)])
    ytd = df[df.days > 100].sort_values("end")
    for r in ytd.itertuples():
        if r.end in out:
            continue
        # find the YTD fact with the same start ending ~one quarter earlier
        prev = [(s, e) for (s, e) in val if s == r.start and 75 <= (r.end - e).days <= 100]
        if prev:
            s, e = prev[0]
            out[r.end] = (e + pd.Timedelta(days=1), r.val - val[(s, e)], first_filed[(r.start, r.end)])
    return pd.DataFrame([{"period_start": v[0], "period_end": k, "value": v[1], "filed": v[2]} for k, v in out.items()])


def instant_values(df):
    df = df.sort_values(["pri", "filed"]).drop_duplicates(["end"], keep="first")
    return pd.DataFrame({"period_start": pd.NaT, "period_end": df.end, "value": df.val, "filed": df.filed})


def main():
    cikmap = pd.read_csv(os.path.join(PROC, "sec_cik_map.csv"))
    out = []
    for r in cikmap.itertuples():
        cf = companyfacts(int(r.cik))
        if cf is None:
            print("no companyfacts", r.ticker)
            continue
        got = []
        for concept, tags in CONCEPTS.items():
            df = facts_frame(cf, tags)
            if df is None:
                continue
            q = instant_values(df) if concept in INSTANT else quarterly_flow(df)
            if len(q):
                q["ticker"], q["concept"] = r.ticker, concept
                out.append(q)
                got.append(f"{concept}:{len(q)}")
        print(f"{r.ticker:9s}", " ".join(got))
    F = pd.concat(out, ignore_index=True).sort_values(["ticker", "concept", "period_end"])
    F.to_parquet(os.path.join(PROC, "fundamentals_q.parquet"), index=False)
    print("rows", len(F))


if __name__ == "__main__":
    main()
