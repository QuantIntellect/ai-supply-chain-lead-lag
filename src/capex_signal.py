"""Exploratory: hyperscaler capex acceleration at earnings -> layer-basket drift.

Event = hyperscaler release (MSFT, GOOGL, AMZN, META, ORCL). Signal = YoY capex growth of the
reported quarter minus that of the previous quarter (pp). Response = equal-weight abnormal-return
basket of each layer's tradeable names over [+1,+20] and [+1,+60] sessions after the hyperscaler's
reaction day (US names; EU names enter the next EU session).
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd, statsmodels.api as sm
from common import PROC, REPORTS, load_universe

HYPER = ["MSFT", "GOOGL", "AMZN", "META", "ORCL"]


def main():
    F = pd.read_parquet(os.path.join(PROC, "fundamentals_q.parquet"))
    F = F[(F.concept == "capex") & F.ticker.isin(HYPER)].sort_values(["ticker", "period_end"])
    F["yoy"] = F.groupby("ticker").value.pct_change(4, fill_method=None) * 100
    F["accel"] = F.groupby("ticker").yoy.diff()
    E = pd.read_parquet(os.path.join(PROC, "events.parquet"))
    E = E[E.ticker.isin(HYPER)]
    # match each event to the latest period_end before the event (the quarter being reported)
    rows = []
    for e in E.itertuples():
        f = F[(F.ticker == e.ticker) & (F.period_end < e.react_date) & (F.period_end > e.react_date - pd.Timedelta(days=75))]
        if len(f):
            rows.append({"ticker": e.ticker, "date": e.react_date, "arA": e.ar, "capex_yoy": f.yoy.iloc[-1], "accel": f.accel.iloc[-1]})
    X = pd.DataFrame(rows).dropna()
    uni = load_universe()
    ar = pd.read_parquet(os.path.join(PROC, "panel", "abret.parquet"))
    trade = uni[(uni.tradeable == "1") & ~uni.layer.isin(["HYPERSCALER"])]
    out = []
    for L, g in trade.groupby("layer"):
        cols = [t for t in g.ticker if t in ar.columns]
        basket = ar[cols].mean(axis=1)
        b = basket.dropna()
        for k in [20, 60]:
            vals = []
            for r in X.itertuples():
                j = b.index.searchsorted(r.date)  # entry at close of hyperscaler reaction day
                vals.append(b.iloc[j + 1: j + 1 + k].sum() * 100 if j + k < len(b) else np.nan)
            X[f"{L}_{k}"] = vals
    res = []
    for era, d in [("2015-2022", X[X.date < "2023-01-01"]), ("2023+", X[X.date >= "2023-01-01"]), ("all", X)]:
        for c in [c for c in X.columns if c.endswith("_20") or c.endswith("_60")]:
            dd = d.dropna(subset=[c, "accel", "arA"])
            Z = dd[["accel"]].assign(arA=dd.arA * 100)
            m = sm.OLS(dd[c], sm.add_constant(Z)).fit(cov_type="HAC", cov_kwds={"maxlags": 3})
            res.append({"era": era, "layer_h": c, "n": len(dd), "b_accel": m.params["accel"], "t_accel": m.tvalues["accel"],
                        "b_arA": m.params["arA"], "t_arA": m.tvalues["arA"]})
    R = pd.DataFrame(res)
    R.to_csv(os.path.join(REPORTS, "tables", "capex_accel_layer_drift.csv"), index=False)
    pd.set_option("display.width", 200)
    print(R.pivot_table(index="layer_h", columns="era", values=["t_accel", "t_arA"]).round(2).to_string())
    print("n events:", len(X), "AI-era:", int((X.date >= "2023-01-01").sum()))


if __name__ == "__main__":
    main()
