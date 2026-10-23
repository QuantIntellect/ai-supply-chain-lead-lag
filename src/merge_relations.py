"""Fold relationships stated on earnings calls (us_notes/relations_*.csv) into config/edges.csv.

customer:  counterparty buys from ticker   -> edge ticker -> counterparty
supplier:  counterparty sells to ticker    -> edge counterparty -> ticker
partner:   partner edge;  investor: counterparty invested in ticker -> investment edge counterparty -> ticker
Existing edges confirmed on a call are upgraded to confidence "high"; new edges between two universe
companies are added with confidence "med" and the call date as evidence. Original file kept as edges_v1.csv.
"""
import os
import re
import sys
import glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
from common import CONFIG, PROC, load_universe

ALIASES = {
    "nvidia": "NVDA", "microsoft": "MSFT", "azure": "MSFT", "google": "GOOGL", "alphabet": "GOOGL", "gcp": "GOOGL",
    "amazon": "AMZN", "aws": "AMZN", "meta": "META", "facebook": "META", "oracle": "ORCL", "oci": "ORCL",
    "tsmc": "TSM", "taiwan semiconductor": "TSM", "samsung": "005930.KS", "sk hynix": "000660.KS", "hynix": "000660.KS",
    "micron": "MU", "intel": "INTC", "broadcom": "AVGO", "amd": "AMD", "advanced micro devices": "AMD", "marvell": "MRVL",
    "arm": "ARM", "dell": "DELL", "super micro": "SMCI", "supermicro": "SMCI", "hpe": "HPE", "hewlett packard enterprise": "HPE",
    "cisco": "CSCO", "arista": "ANET", "foxconn": "2317.TW", "hon hai": "2317.TW", "quanta computer": "2382.TW", "wistron": "3231.TW",
    "wiwynn": "6669.TW", "celestica": "CLS", "jabil": "JBL", "coreweave": "CRWV", "nebius": "NBIS", "iren": "IREN",
    "applied digital": "APLD", "cipher": "CIFR", "terawulf": "WULF", "equinix": "EQIX", "digital realty": "DLR",
    "asml": "ASML.AS", "applied materials": "AMAT", "lam research": "LRCX", "kla": "KLAC", "teradyne": "TER",
    "coherent": "COHR", "lumentum": "LITE", "ciena": "CIEN", "fabrinet": "FN", "credo": "CRDO", "astera": "ALAB",
    "vertiv": "VRT", "eaton": "ETN", "schneider": "SU.PA", "siemens energy": "ENR.DE", "siemens": "SIE.DE", "abb": "ABBN.SW",
    "ge vernova": "GEV", "constellation": "CEG", "vistra": "VST", "talen": "TLN", "nrg": "NRG", "oklo": "OKLO", "nuscale": "SMR",
    "bloom energy": "BE", "bloom": "BE", "quanta services": "PWR", "hubbell": "HUBB", "nvent": "NVT", "modine": "MOD",
    "sap": "SAP.DE", "servicenow": "NOW", "salesforce": "CRM", "adobe": "ADBE", "snowflake": "SNOW", "palantir": "PLTR",
    "nokia": "NOKIA.HE", "deutsche telekom": "DTE.DE", "softbank": "9984.T", "infineon": "IFX.DE", "stmicroelectronics": "STMPA.PA",
    "monolithic power": "MPWR", "seagate": "STX", "western digital": "WDC", "sandisk": "SNDK", "tokyo electron": "8035.T",
    "advantest": "6857.T", "asm international": "ASM.AS", "besi": "BESI.AS", "rolls-royce": "RR.L", "prysmian": "PRY.MI",
    "dassault": "DSY.PA", "capgemini": "CAP.PA", "delta electronics": "2308.TW",
}


def resolve(x, tickers):
    s = str(x).strip()
    if s in tickers:
        return s
    if s.upper() in tickers:
        return s.upper()
    k = s.lower()
    k = re.sub(r"\b(inc|corp|corporation|ltd|plc|n\.v\.|nv|group|holdings|technologies|technology|co)\b\.?", "", k).strip(" ,.")
    if k in ALIASES:
        return ALIASES[k]
    for a, t in ALIASES.items():
        if re.fullmatch(a + r"( .*)?", k):
            return t
    return None


def main():
    uni = load_universe()
    tickers = set(uni.ticker)
    p = os.path.join(CONFIG, "edges.csv")
    v1 = os.path.join(CONFIG, "edges_v1.csv")
    if not os.path.exists(v1):
        pd.read_csv(p, dtype=str).to_csv(v1, index=False)
    E = pd.read_csv(v1, dtype=str).fillna("")
    R = pd.concat([pd.read_csv(f, dtype=str) for f in glob.glob(os.path.join(PROC, "us_notes", "relations_*.csv"))], ignore_index=True).fillna("")
    R["cp"] = R.counterparty.apply(lambda x: resolve(x, tickers))
    R["tk"] = R.ticker.apply(lambda x: resolve(x, tickers))
    R = R[R.cp.notna() & R.tk.notna() & (R.cp != R.tk)]
    rows = []
    for r in R.itertuples():
        if r.relation == "customer":
            rows.append((r.tk, r.cp, "supply_call"))
        elif r.relation == "supplier":
            rows.append((r.cp, r.tk, "supply_call"))
        elif r.relation == "partner":
            rows.append((r.tk, r.cp, "partner"))
        elif r.relation == "investor":
            rows.append((r.cp, r.tk, "investment"))
    C = pd.DataFrame(rows, columns=["src", "dst", "kind"])
    C["n_calls"] = 1
    C = C.groupby(["src", "dst", "kind"], as_index=False).n_calls.sum()
    have = {(a, b): i for i, (a, b) in enumerate(zip(E.src, E.dst))}
    added = upgraded = 0
    for r in C.itertuples():
        key = (r.src, r.dst)
        rev = (r.dst, r.src)
        if key in have or (r.kind == "partner" and rev in have):
            i = have.get(key, have.get(rev))
            if E.at[i, "confidence"] != "high" and r.kind != "partner":
                E.at[i, "confidence"] = "high"
                upgraded += 1
            if "earnings call" not in E.at[i, "evidence"]:
                E.at[i, "evidence"] = (E.at[i, "evidence"] + "; earnings call").strip("; ")
            continue
        rel = {"supply_call": "customer_stated", "partner": "partner", "investment": "investment"}[r.kind]
        conf = "high" if r.n_calls >= 2 else "med"
        E.loc[len(E)] = [r.src, r.dst, rel, f"earnings call ({r.n_calls} mention{'s' if r.n_calls > 1 else ''})", conf, ""]
        have[key] = len(E) - 1
        added += 1
    E.to_csv(p, index=False)
    print(f"call relations resolved: {len(R)}; unique pairs: {len(C)}; edges added: {added}; upgraded to high: {upgraded}; total edges now {len(E)}")
    print(E.rel.value_counts().to_string())


if __name__ == "__main__":
    main()
