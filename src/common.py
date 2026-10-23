"""Shared paths and helpers for the AI supply-chain project."""
import os
import time
import json
import pandas as pd

# repository root (the folder that contains src/); override with AIMAPPING_ROOT if data lives elsewhere
ROOT = os.environ.get("AIMAPPING_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG = os.path.join(ROOT, "config")
RAW = os.path.join(ROOT, "data", "raw")
PROC = os.path.join(ROOT, "data", "processed")
REPORTS = os.path.join(ROOT, "reports")

SEC_UA = "aimapping-research research@example.org"
WEB_UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 "
          "(KHTML, like Gecko) Chrome/126 Safari/537.36")

# Benchmarks used for abnormal returns, keyed by region / exchange suffix
BENCHMARKS = ["SPY", "QQQ", "SMH", "SOXX", "XLK", "XLU", "XLI", "IGV", "RSP",
              "^STOXX", "^STOXX50E", "^GDAXI", "^FCHI", "^FTSE", "^AEX", "^SSMI",
              "^TWII", "^KS11", "^N225", "EURUSD=X", "^VIX"]
# Second listings worth keeping (ADRs of EU companies; useful for US-hours reactions)
EXTRA_LISTINGS = ["ASML", "STM", "NOK", "SAP"]


def load_universe():
    return pd.read_csv(os.path.join(CONFIG, "universe.csv"), dtype=str).fillna("")


def load_edges():
    return pd.read_csv(os.path.join(CONFIG, "edges.csv"), dtype=str).fillna("")


def market_benchmark(ticker: str, region: str) -> str:
    """Local broad-market benchmark used for market-adjusted returns."""
    if region == "US":
        return "SPY"
    if ticker.endswith(".TW"):
        return "^TWII"
    if ticker.endswith(".KS"):
        return "^KS11"
    if ticker.endswith(".T"):
        return "^N225"
    return "^STOXX"


def ensure(path):
    os.makedirs(path, exist_ok=True)
    return path


def dump_json(obj, path):
    ensure(os.path.dirname(path))
    with open(path, "w") as f:
        json.dump(obj, f, indent=1, default=str)


def polite_sleep(sec=0.12):
    time.sleep(sec)
