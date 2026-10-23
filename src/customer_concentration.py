"""Extract customer-concentration and named-counterparty statements from the latest 10-K / 20-F texts.

Output: data/processed/customer_concentration.csv
  ticker, form, filingDate, pct, named (universe/private names found in the sentence), sentence
Used to verify / extend config/edges.csv with first-party evidence.
"""
import os
import re
import sys
import glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
from common import PROC, load_universe

NAMES = {
    "NVIDIA": "NVDA", "Microsoft": "MSFT", "Alphabet": "GOOGL", "Google": "GOOGL", "Amazon": "AMZN", "AWS": "AMZN",
    "Meta": "META", "Oracle": "ORCL", "Taiwan Semiconductor": "TSM", "TSMC": "TSM", "Samsung": "005930.KS",
    "SK hynix": "000660.KS", "SK Hynix": "000660.KS", "Micron": "MU", "Intel": "INTC", "Broadcom": "AVGO",
    "Advanced Micro Devices": "AMD", "AMD": "AMD", "Apple": "AAPL", "Dell": "DELL", "Super Micro": "SMCI",
    "Hewlett Packard": "HPE", "Cisco": "CSCO", "Arista": "ANET", "Foxconn": "2317.TW", "Hon Hai": "2317.TW",
    "Quanta": "2382.TW/PWR", "Wistron": "3231.TW", "Wiwynn": "6669.TW", "Celestica": "CLS", "Jabil": "JBL",
    "CoreWeave": "CRWV", "OpenAI": "OpenAI", "Anthropic": "Anthropic", "xAI": "xAI", "ASML": "ASML.AS",
    "Applied Materials": "AMAT", "Lam Research": "LRCX", "KLA": "KLAC", "Marvell": "MRVL", "Coherent": "COHR",
    "Lumentum": "LITE", "Ciena": "CIEN", "Fabrinet": "FN", "Vertiv": "VRT", "Eaton": "ETN", "Schneider": "SU.PA",
    "Siemens": "SIE.DE", "Nokia": "NOKIA.HE", "Equinix": "EQIX", "Digital Realty": "DLR", "Nebius": "NBIS",
    "Constellation": "CEG", "Talen": "TLN", "Vistra": "VST", "Crusoe": "Crusoe", "Lambda": "Lambda",
}
PCT = re.compile(r"(\d{1,2}(?:\.\d)?)\s?%\s+of\s+(?:our\s+)?(?:total\s+|net\s+|consolidated\s+)?(?:revenue|revenues|net sales|sales)", re.I)
CUST = re.compile(r"\b(customer [A-H]\b|largest customers?|direct customers?|significant customers?|ten largest|top (?:five|ten|10|5) customers?|accounted for)\b", re.I)


def main():
    rows = []
    for f in glob.glob(os.path.join(PROC, "edgar_text", "*", "*_10K_*.txt")) + glob.glob(os.path.join(PROC, "edgar_text", "*", "*_20F_*.txt")):
        tk = os.path.basename(os.path.dirname(f))
        base = os.path.basename(f)
        fdate, form = base[:10], base.split("_")[1]
        text = re.sub(r"\s+", " ", open(f, encoding="utf-8", errors="ignore").read())
        for sent in re.split(r"(?<=[.;])\s+", text):
            if len(sent) > 900:
                continue
            p = PCT.search(sent)
            if not (p and CUST.search(sent)) and not (CUST.search(sent) and any(n in sent for n in NAMES)):
                continue
            named = sorted({v for n, v in NAMES.items() if re.search(r"\b" + re.escape(n) + r"\b", sent) and v != tk})
            rows.append({"ticker": tk, "form": form, "filingDate": fdate, "pct": float(p.group(1)) if p else None,
                         "named": "|".join(named), "sentence": sent.strip()[:700]})
    C = pd.DataFrame(rows).drop_duplicates(["ticker", "sentence"])
    C.to_csv(os.path.join(PROC, "customer_concentration.csv"), index=False)
    print("statements:", len(C), "companies:", C.ticker.nunique())
    print("statements naming counterparties:", int((C.named != "").sum()))


if __name__ == "__main__":
    main()
