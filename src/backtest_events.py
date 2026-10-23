"""Event-level backtests of supply-chain drift strategies (pre-registered H2 + exploratory).

Each trade: responder B, entered at the close of `entry_date` (first B close after the reporter's
reaction is fully known), direction = sign(AR_A) (or minus for reversal strategies), held k sessions,
P&L = market-model abnormal return (beta-hedged) minus round-trip cost.
Threshold |AR_A| >= theta is chosen on the training window (<= 2024) and evaluated on 2025-2026.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd
import statsmodels.api as sm
from common import PROC, REPORTS, load_universe, ensure

OUT = ensure(os.path.join(REPORTS, "tables"))
COST = {"US": 0.0020, "EU": 0.0030, "ASIA": 0.0040}   # round trip incl. hedge
STRATS = {
    # name: (relation filter, direction, hold sessions, pre-registered?)
    "H2a_customer_news_to_suppliers": (["B_supplies_A"], +1, 20, True),
    "H2b_supplier_news_to_customers": (["A_supplies_B"], +1, 2, True),
    "edge_both_5d": (["A_supplies_B", "B_supplies_A"], +1, 5, False),
    "same_layer_reversal_5d": (["same_layer"], -1, 5, False),
    "same_layer_reversal_20d": (["same_layer"], -1, 20, False),
}
THETAS = [0.0, 0.02, 0.04, 0.06]


SLOTS = 20  # fixed-fraction sizing: each trade uses 1/SLOTS of the book (exposure varies with trade count)
_CS = {}


def car_from_panel(d, arfile, k):
    """CAR over the k sessions after entry_date, from the chosen abnormal-return panel."""
    if arfile not in _CS:
        ar = pd.read_parquet(os.path.join(PROC, "panel", arfile))
        _CS[arfile] = {t: (ar[t].dropna().index, np.concatenate([[0.0], np.cumsum(ar[t].dropna().values)])) for t in ar.columns}
    out = np.full(len(d), np.nan)
    for i, (b, e) in enumerate(zip(d.B.values, d.entry_date.values)):
        if b not in _CS[arfile]:
            continue
        idx, cs = _CS[arfile][b]
        j = idx.searchsorted(e)
        if j < len(idx) and idx[j] == e and j + k < len(idx):
            out[i] = cs[j + 1 + k] - cs[j + 1]
    return out


def trades(S, rels, direction, k, theta, tradeable, arfile="abret.parquet"):
    d = S[S.rel.isin(rels) & S.B.isin(tradeable) & ~S.own_near & ~S.own_in_30 & S.arA.notna()]
    d = d[d.arA.abs() >= theta].dropna(subset=[f"car_1_{k}", "entry_date"]).copy()
    d["side"] = direction * np.sign(d.arA)
    car = d[f"car_1_{k}"].values if arfile == "abret.parquet" else car_from_panel(d, arfile, k)
    d["gross"] = d.side * car
    d = d[np.isfinite(d.gross)]
    d["cost"] = d.regionB.map(COST)
    d["net"] = d.gross - d.cost
    return d


def stats(d):
    if len(d) < 10:
        return {"n": len(d)}
    m = sm.OLS(d.net, np.ones(len(d))).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(d.t0A)[0]})
    return {"n": len(d), "events": d.event_id.nunique(), "mean_gross_bp": d.gross.mean() * 1e4,
            "mean_net_bp": d.net.mean() * 1e4, "t_net": m.tvalues.iloc[0], "hit": (d.gross > 0).mean()}


def daily_series(d, ar, k):
    """Fixed-fraction book: each open trade is 1/SLOTS of capital; costs spread over holding days.
    Returns (daily net return, daily gross exposure)."""
    contrib = []
    for r in d.itertuples():
        s = ar[r.B].dropna()
        j = s.index.searchsorted(r.entry_date)
        win = s.iloc[j + 1: j + 1 + k]
        contrib.append(pd.DataFrame({"date": win.index, "ret": (r.side * win.values - r.cost / k) / SLOTS, "w": 1 / SLOTS}))
    if not contrib:
        return pd.Series(dtype=float), pd.Series(dtype=float)
    c = pd.concat(contrib)
    return c.groupby("date").ret.sum(), c.groupby("date").w.sum()


def perf(x, start, end):
    idx = pd.bdate_range(start, end)
    x = x.reindex(idx).fillna(0.0)
    ann = x.mean() * 252
    vol = x.std() * np.sqrt(252)
    eq = (1 + x).cumprod()
    dd = (eq / eq.cummax() - 1).min()
    return {"ann_ret": ann, "ann_vol": vol, "sharpe": ann / vol if vol > 0 else np.nan, "max_dd": dd,
            "time_in_mkt": (x != 0).mean()}


def main():
    S = pd.read_parquet(os.path.join(PROC, "spill.parquet"))
    S = S[S.t0A >= "2015-01-01"]
    uni = load_universe()
    tradeable = set(uni[uni.tradeable == "1"].ticker)
    panels = {f: pd.read_parquet(os.path.join(PROC, "panel", f)) for f in ["abret.parquet", "abret_ind.parquet"]}
    rows, series = [], {}
    for (name, (rels, direction, k, prereg)), arfile in [(it, f) for it in STRATS.items() for f in panels]:
        ar = panels[arfile]
        # choose theta on training data (best mean net per trade, min 200 trades)
        tr = S[S.t0A < "2025-01-01"]
        cand = []
        for th in THETAS:
            st = stats(trades(tr, rels, direction, k, th, tradeable, arfile))
            if st.get("n", 0) >= 200:
                cand.append((st["mean_net_bp"], th))
        theta = max(cand)[1] if cand else 0.0
        for period, lo, hi in [("train_2015_2024", "2015-01-01", "2025-01-01"), ("pre_AI_2015_2022", "2015-01-01", "2023-01-01"),
                               ("AI_2023_2024", "2023-01-01", "2025-01-01"), ("OOS_2025_2026", "2025-01-01", "2026-12-31")]:
            d = trades(S[(S.t0A >= lo) & (S.t0A < hi)], rels, direction, k, theta, tradeable, arfile)
            st = stats(d)
            ds, ex = daily_series(d, ar, k) if len(d) else (pd.Series(dtype=float), pd.Series(dtype=float))
            pf = perf(ds, lo, min(pd.Timestamp(hi), pd.Timestamp("2026-10-22"))) if len(ds) else {}
            bench = "vs index" if arfile == "abret.parquet" else "vs AI basket"
            rows.append({"strategy": name, "primary": prereg, "benchmark": bench, "theta": theta, "hold": k, "period": period,
                         **st, **pf, "avg_exposure": ex.reindex(pd.bdate_range(lo, min(pd.Timestamp(hi), pd.Timestamp("2026-10-22")))).fillna(0).mean() if len(ex) else 0})
            if period in ("OOS_2025_2026", "train_2015_2024"):
                series[f"{name}|{bench}|{period}"] = ds
    R = pd.DataFrame(rows)
    R.to_csv(os.path.join(OUT, "backtest_events.csv"), index=False)
    pd.to_pickle(series, os.path.join(PROC, "backtest_event_series.pkl"))
    pd.set_option("display.width", 250)
    cols = ["strategy", "benchmark", "theta", "hold", "period", "n", "events", "mean_gross_bp", "mean_net_bp", "t_net", "hit", "sharpe", "ann_ret", "max_dd", "avg_exposure"]
    print(R[cols].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
