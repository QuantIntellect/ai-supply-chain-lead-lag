"""Regex KPI extraction from US earnings press releases (8-K EX-99.x text).

Extracts per release: backlog ($bn), book-to-bill, orders growth (%), organic orders growth (%),
AI orders / AI backlog / AI shipments ($bn, e.g. Dell, HPE, SMCI), RPO ($bn), and the next-quarter
revenue guidance midpoint ($bn) when phrased as "revenue is expected to be $X billion ±Y%" or
"between $A and $B".
Output: data/processed/press_release_kpis.csv (one row per ticker x release date; first match per field)
"""
import os
import re
import sys
import glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd
from common import PROC

MONEY = r"\$\s?([\d,]+(?:\.\d+)?)\s?(billion|million|B|M)\b"
PAT = {
    "backlog_bn": re.compile(r"\bbacklog\b[^.]{0,80}?" + MONEY, re.I),
    "book_to_bill": re.compile(r"book[- ]to[- ]bill(?: ratio)?[^.\d]{0,40}?(\d\.\d{1,2})", re.I),
    "orders_growth_pct": re.compile(r"\borders\b[^.]{0,60}?(?:increased|grew|were up|up|rose)\s(?:by\s)?(?:approximately\s)?(\d{1,3}(?:\.\d)?)\s?%", re.I),
    "organic_orders_pct": re.compile(r"organic orders[^.]{0,40}?(?:increased|grew|were up|up|rose)?\s?(?:by\s)?(?:approximately\s)?(\d{1,3}(?:\.\d)?)\s?%", re.I),
    "ai_orders_bn": re.compile(r"\bAI(?:[- ]optimized)?(?: server| systems?)? orders\b[^.]{0,60}?" + MONEY, re.I),
    "ai_backlog_bn": re.compile(r"\bAI(?:[- ]optimized)?(?: server| systems?)? backlog\b[^.]{0,60}?" + MONEY, re.I),
    "ai_shipments_bn": re.compile(r"\bAI(?:[- ]optimized)?(?: server| systems?)? (?:shipments|revenue)\b[^.]{0,60}?" + MONEY, re.I),
    "rpo_bn": re.compile(r"remaining performance obligations?[^.]{0,80}?" + MONEY, re.I),
}
GUIDE_PM = re.compile(r"revenue (?:is|are) expected to be\s+" + MONEY + r",?\s+plus or minus\s+(\d+(?:\.\d)?)\s?%", re.I)
GUIDE_RANGE = re.compile(r"(?:revenue|net sales)[^.]{0,80}?(?:expected|guidance|outlook)[^.]{0,60}?(?:between|of|range of)\s+" + MONEY + r"\s+(?:and|to)\s+" + MONEY, re.I)


def to_bn(v, unit):
    v = float(v.replace(",", ""))
    return v / 1000 if unit.lower() in ("million", "m") else v


def main():
    rows = []
    for f in glob.glob(os.path.join(PROC, "edgar_text", "*", "*_8K_*.txt")):
        tk = os.path.basename(os.path.dirname(f))
        date = os.path.basename(f)[:10]
        text = re.sub(r"\s+", " ", open(f, encoding="utf-8", errors="ignore").read())
        if len(text) < 2000:
            continue
        rec = {"ticker": tk, "date": date, "doc": os.path.basename(f)}
        for k, rx in PAT.items():
            m = rx.search(text)
            if not m:
                continue
            g = m.groups()
            rec[k] = to_bn(g[0], g[1]) if k.endswith("_bn") else float(g[0])
            rec[k + "_ctx"] = text[max(0, m.start() - 60): m.end() + 40]
        m = GUIDE_PM.search(text)
        if m:
            rec["guide_rev_mid_bn"] = to_bn(m.group(1), m.group(2))
        else:
            m = GUIDE_RANGE.search(text)
            if m:
                rec["guide_rev_mid_bn"] = (to_bn(m.group(1), m.group(2)) + to_bn(m.group(3), m.group(4))) / 2
        rows.append(rec)
    K = pd.DataFrame(rows)
    # one row per ticker/date: keep the document with the most fields found
    K["nf"] = K.drop(columns=["ticker", "date", "doc"]).notna().sum(axis=1)
    K = K.sort_values("nf").drop_duplicates(["ticker", "date"], keep="last").sort_values(["ticker", "date"])
    K.to_csv(os.path.join(PROC, "press_release_kpis.csv"), index=False)
    cov = K.drop(columns=[c for c in K.columns if c.endswith("_ctx")] + ["doc", "nf"]).groupby("ticker").count()
    print("releases parsed:", len(K))
    print(cov[[c for c in cov.columns if c != "date"]].loc[lambda d: d.sum(axis=1) > 0].to_string())


if __name__ == "__main__":
    main()
