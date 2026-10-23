"""Build wide daily panels: returns (close-close, overnight, intraday), abnormal returns, abnormal volume.

Saved to data/processed/panel/*.parquet (index = calendar date, columns = tickers).
Each ticker keeps its own trading calendar (NaN on days its exchange is closed).
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd
from common import PROC, load_universe, market_benchmark, ensure, EXTRA_LISTINGS

# exchange sessions: suffix -> (tz, open, close)
EXCHANGES = {
    "": ("America/New_York", "09:30", "16:00"),
    ".DE": ("Europe/Berlin", "09:00", "17:30"),
    ".PA": ("Europe/Paris", "09:00", "17:30"),
    ".AS": ("Europe/Amsterdam", "09:00", "17:30"),
    ".MI": ("Europe/Rome", "09:00", "17:30"),
    ".L": ("Europe/London", "08:00", "16:30"),
    ".SW": ("Europe/Zurich", "09:00", "17:30"),
    ".CO": ("Europe/Copenhagen", "09:00", "17:00"),
    ".ST": ("Europe/Stockholm", "09:00", "17:30"),
    ".HE": ("Europe/Helsinki", "10:00", "18:30"),
    ".TW": ("Asia/Taipei", "09:00", "13:30"),
    ".KS": ("Asia/Seoul", "09:00", "15:30"),
    ".T": ("Asia/Tokyo", "09:00", "15:00"),
}
INDEX_EXCH = {"^STOXX": ".DE", "^STOXX50E": ".DE", "^GDAXI": ".DE", "^FCHI": ".PA", "^FTSE": ".L", "^AEX": ".AS",
              "^SSMI": ".SW", "^TWII": ".TW", "^KS11": ".KS", "^N225": ".T"}


def exchange_of(ticker):
    if ticker in INDEX_EXCH:
        return EXCHANGES[INDEX_EXCH[ticker]]
    for suf in sorted([s for s in EXCHANGES if s], key=len, reverse=True):
        if ticker.endswith(suf):
            return EXCHANGES[suf]
    return EXCHANGES[""]


def load_prices():
    p = pd.read_parquet(os.path.join(PROC, "prices", "prices_long.parquet"))
    p["date"] = pd.to_datetime(p["date"])
    return p


def build():
    out = ensure(os.path.join(PROC, "panel"))
    p = load_prices()
    p = p[p.close > 0].copy()
    p["adj_factor"] = p.adj_close / p.close
    p["adj_open"] = p.open * p.adj_factor
    wide = {c: p.pivot_table(index="date", columns="ticker", values=c) for c in ["adj_close", "adj_open", "volume", "close"]}
    close, opn, vol = wide["adj_close"], wide["adj_open"], wide["volume"]
    rets, ovn, intra = {}, {}, {}
    for tk in close.columns:
        c = close[tk].dropna()
        o = opn[tk].reindex(c.index)
        rets[tk] = c.pct_change()
        ovn[tk] = o / c.shift(1) - 1
        intra[tk] = c / o - 1
    R = pd.DataFrame(rets).sort_index()
    ON = pd.DataFrame(ovn).sort_index()
    ID = pd.DataFrame(intra).sort_index()
    # bad opens (open==prev close exactly, or missing) make overnight/intraday unreliable: flag share
    bad_open = (ON.abs() < 1e-12) | ON.isna()
    q = (bad_open & R.notna()).sum() / R.notna().sum()
    # clip absurd values (data errors)
    for df in (R, ON, ID):
        df[(df > 3) | (df < -0.9)] = np.nan

    uni = load_universe()
    region = dict(zip(uni.ticker, uni.region))
    # drop pre-listing / predecessor history (SPAC shells, tracking stocks, unrelated predecessors)
    for tk, hs in zip(uni.ticker, uni.history_start):
        if hs and tk in R.columns:
            for df in (R, ON, ID, vol):
                df.loc[df.index < pd.Timestamp(hs), tk] = np.nan
    for tk in EXTRA_LISTINGS:
        region[tk] = "US"
    # rolling market beta vs local benchmark (250d window, lagged 21d), market-model abnormal return
    AR = pd.DataFrame(index=R.index, columns=R.columns, dtype=float)
    BETA = pd.DataFrame(index=R.index, columns=R.columns, dtype=float)
    for tk in R.columns:
        if tk.startswith("^") or tk in ("SPY", "QQQ", "SMH", "SOXX", "XLK", "XLU", "XLI", "IGV", "RSP", "EURUSD=X"):
            continue
        bm = market_benchmark(tk, region.get(tk, "US"))
        y = R[tk].dropna()
        x = R[bm].reindex(y.index)
        # if benchmark closed on a stock trading day, treat its return as 0 for that day
        x = x.fillna(0.0)
        cov = (y * x).rolling(250, min_periods=120).mean() - y.rolling(250, min_periods=120).mean() * x.rolling(250, min_periods=120).mean()
        var = x.rolling(250, min_periods=120).var(ddof=0)
        b = (cov / var).shift(21).clip(0, 3).fillna(1.0)
        BETA[tk] = b.reindex(R.index)
        AR[tk] = (y - b * x).reindex(R.index)
    # industry-adjusted abnormal return: vs equal-weight basket of the tradeable AI universe in the same region
    ABI = pd.DataFrame(index=R.index, columns=R.columns, dtype=float)
    trade = uni[uni.tradeable == "1"]
    for reg in ["US", "EU"]:
        names = [t for t in trade[trade.region == reg].ticker if t in R.columns]
        basket = R[names].mean(axis=1, skipna=True)
        for tk in names:
            y = R[tk].dropna()
            x = basket.reindex(y.index).fillna(0.0)
            cov = (y * x).rolling(250, min_periods=120).mean() - y.rolling(250, min_periods=120).mean() * x.rolling(250, min_periods=120).mean()
            var = x.rolling(250, min_periods=120).var(ddof=0)
            b = (cov / var).shift(21).clip(0, 3).fillna(1.0)
            ABI[tk] = (y - b * x).reindex(R.index)
        R[f"AIEW_{reg}"] = basket
    # abnormal volume: volume / trailing 60d median (lagged 1d)
    AV = vol / vol.rolling(60, min_periods=20).median().shift(1)
    AV = AV.replace([np.inf, -np.inf], np.nan)

    R.to_parquet(os.path.join(out, "ret.parquet"))
    ON.to_parquet(os.path.join(out, "ret_overnight.parquet"))
    ID.to_parquet(os.path.join(out, "ret_intraday.parquet"))
    AR.to_parquet(os.path.join(out, "abret.parquet"))
    ABI.to_parquet(os.path.join(out, "abret_ind.parquet"))
    BETA.to_parquet(os.path.join(out, "beta.parquet"))
    AV.to_parquet(os.path.join(out, "abvol.parquet"))
    wide["close"].to_parquet(os.path.join(out, "close_raw.parquet"))
    close.to_parquet(os.path.join(out, "close_adj.parquet"))
    print("panel shapes", R.shape)
    print("share of days with unreliable open (overnight==0 or NaN):")
    print(q.sort_values(ascending=False).head(25).round(3).to_string())


if __name__ == "__main__":
    build()
