"""Yahoo earnings dates (with EPS estimate / actual / surprise) for every universe ticker."""
import os
import sys
import time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import yfinance as yf
from common import PROC, EXTRA_LISTINGS, load_universe


def main():
    uni = load_universe()
    out = []
    for tk in list(uni.ticker) + EXTRA_LISTINGS:
        df = None
        for i in range(3):
            try:
                df = yf.Ticker(tk).get_earnings_dates(limit=100)
                break
            except Exception as e:
                print("retry", tk, type(e).__name__, str(e)[:80])
                time.sleep(3 + 3 * i)
        if df is None or not len(df):
            print(f"{tk:10s} none")
            continue
        df = df.reset_index()
        df.columns = ["earn_ts", "eps_est", "eps_act", "surprise_pct"]
        df["ticker"] = tk
        out.append(df)
        recent = df[df.earn_ts >= pd.Timestamp("2015-01-01", tz=df.earn_ts.dt.tz)]
        print(f"{tk:10s} rows={len(df):3d} since2015={len(recent):3d} first={df.earn_ts.min().date()}")
        time.sleep(0.4)
    allx = pd.concat(out, ignore_index=True)
    allx["earn_ts_utc"] = allx.earn_ts.apply(lambda t: t.tz_convert("UTC"))
    allx = allx.drop(columns=["earn_ts"])
    allx.to_parquet(os.path.join(PROC, "yahoo_earnings_dates.parquet"), index=False)
    print("saved", len(allx))


if __name__ == "__main__":
    main()
