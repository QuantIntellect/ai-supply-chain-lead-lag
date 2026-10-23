"""Download daily OHLCV (raw + adjusted) for the universe and benchmarks via yfinance."""
import os
import sys
import time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import yfinance as yf
from common import PROC, BENCHMARKS, EXTRA_LISTINGS, load_universe, ensure

START = "2014-06-01"


def fetch_one(tk, tries=3):
    for i in range(tries):
        try:
            df = yf.Ticker(tk).history(start=START, auto_adjust=False, actions=True)
            if df is not None and len(df):
                df.index = pd.to_datetime(df.index).tz_localize(None).normalize()
                df = df.rename(columns=str.lower).rename(columns={"adj close": "adj_close", "stock splits": "splits"})
                df["ticker"] = tk
                return df
        except Exception as e:  # network hiccups / throttling
            print(f"  retry {tk}: {type(e).__name__} {e}")
        time.sleep(2 + 3 * i)
    return None


def main():
    out = ensure(os.path.join(PROC, "prices"))
    uni = load_universe()
    tickers = list(uni.ticker) + EXTRA_LISTINGS + BENCHMARKS
    frames, missing = [], []
    for tk in tickers:
        df = fetch_one(tk)
        if df is None:
            missing.append(tk)
            print(f"MISSING {tk}")
            continue
        frames.append(df)
        print(f"{tk:10s} {df.index.min().date()} -> {df.index.max().date()} rows={len(df)}")
        time.sleep(0.3)
    allp = pd.concat(frames).reset_index().rename(columns={"Date": "date", "index": "date"})
    allp.to_parquet(os.path.join(out, "prices_long.parquet"), index=False)
    print("saved", len(allp), "rows; missing:", missing)


if __name__ == "__main__":
    main()
