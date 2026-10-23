"""Daily cross-sectional 'supply-chain news' model with walk-forward evaluation.

For each tradeable stock B and trading day t, features summarise other companies' earnings
reactions that became known by B's close on t (entry_date <= t), bucketed by relation and age:
  rel ∈ {cust (A is B's customer), supp (A is B's supplier), layer (same layer), other}
  age ∈ {0 (became known today), 1-4, 5-19 sessions ago}
  value = sum of winsorised AR_A (pct)
plus B's own last earnings reaction (age buckets, PEAD) and own-return controls (1d, 5d, 20d AR).
Target: B's cumulative abnormal return over t+1..t+5.
Walk-forward: for each test year Y (2019..2026) fit OLS on the previous 4 years, predict Y.
Portfolio: each day weight_B ∝ prediction (event features only, and full model), hold 5 days
(1/5 of book rebalanced daily), net of costs on turnover.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd
from common import PROC, REPORTS, load_universe, ensure

OUT = ensure(os.path.join(REPORTS, "tables"))
H = 5
AGE = [(0, 0), (1, 4), (5, 19)]
RELMAP = {"B_supplies_A": "cust", "A_supplies_B": "supp", "same_layer": "layer", "other": "other"}
COST_BP = {"US": 10, "EU": 15}  # one-way, per unit of turnover


def build_features():
    S = pd.read_parquet(os.path.join(PROC, "spill.parquet"))
    E = pd.read_parquet(os.path.join(PROC, "events.parquet"))
    ar = pd.read_parquet(os.path.join(PROC, "panel", "abret.parquet"))
    uni = load_universe()
    trade = uni[uni.tradeable == "1"]
    tickers = [t for t in trade.ticker if t in ar.columns]
    lo, hi = S.arA.quantile([0.01, 0.99])
    S = S[S.B.isin(tickers) & S.entry_date.notna() & S.arA.notna()].copy()
    S["x"] = S.arA.clip(lo, hi) * 100
    S["g"] = S.rel.map(RELMAP)
    frames = []
    for B in tickers:
        a = ar[B].dropna()
        a = a[a.index >= "2014-06-01"]
        days = a.index
        n = len(days)
        F = pd.DataFrame(index=days)
        sb = S[S.B == B]
        pos = days.searchsorted(sb.entry_date.values)
        for g in ["cust", "supp", "layer", "other"]:
            m = (sb.g == g).values
            impulse = np.zeros(n + 1)
            np.add.at(impulse, pos[m], sb.x.values[m])
            impulse = impulse[:n]
            c = np.concatenate([[0.0], np.cumsum(impulse)])
            for lo_a, hi_a in AGE:
                # sum of impulses with age in [lo_a, hi_a]  -> impulses at t-hi_a .. t-lo_a
                idx = np.arange(n)
                top = idx - lo_a + 1
                bot = np.maximum(idx - hi_a, 0)
                F[f"{g}_{lo_a}_{hi_a}"] = np.where(top > 0, c[np.clip(top, 0, n)] - c[bot], 0.0)
        # own earnings reaction (PEAD): own AR on reaction day, by age
        eb = E[E.ticker == B]
        p2 = days.searchsorted(eb.react_date.values)
        imp = np.zeros(n + 1)
        np.add.at(imp, p2, eb.ar.fillna(0).clip(-0.3, 0.3).values * 100)
        imp = imp[:n]
        c = np.concatenate([[0.0], np.cumsum(imp)])
        idx = np.arange(n)
        for lo_a, hi_a in [(1, 4), (5, 19), (20, 59)]:
            top, bot = idx - lo_a + 1, np.maximum(idx - hi_a, 0)
            F[f"own_{lo_a}_{hi_a}"] = np.where(top > 0, c[np.clip(top, 0, n)] - c[bot], 0.0)
        av = a.values * 100
        cs = np.concatenate([[0.0], np.cumsum(av)])
        F["r1"] = av
        F["r5"] = cs[idx + 1] - cs[np.maximum(idx - 4, 0)]
        F["r20"] = cs[idx + 1] - cs[np.maximum(idx - 19, 0)]
        F["y"] = np.where(idx + H < n, cs[np.minimum(idx + 1 + H, n)] - cs[idx + 1], np.nan)
        F["ticker"] = B
        frames.append(F.reset_index().rename(columns={"index": "date", "Date": "date"}))
    X = pd.concat(frames, ignore_index=True)
    X = X.rename(columns={X.columns[0]: "date"})
    X["region"] = X.ticker.map(dict(zip(uni.ticker, uni.region)))
    X.to_parquet(os.path.join(PROC, "network_features.parquet"), index=False)
    return X


def fit_ols(D, cols):
    A = D[cols].values
    A = np.column_stack([np.ones(len(A)), A])
    beta, *_ = np.linalg.lstsq(A, D.y.values, rcond=None)
    return beta


def predict(D, cols, beta):
    return beta[0] * 0 + D[cols].values @ beta[1:]  # drop intercept: cross-sectional bets only


def portfolio(P, col, neutral=True, arfile="abret.parquet", baseline=False):
    """Daily book: weights ∝ prediction (gross 1), 1/H of book rebalanced each day; P&L on next-day AR.

    neutral   demean weights across names with a valid return that day (dollar-neutral vs the AI universe)
    arfile    abret.parquet (vs local index) or abret_ind.parquet (vs equal-weight AI basket of the region)
    baseline  replace the signal by 1 for every name with a nonzero signal (tests "just long the names")
    """
    W = P.pivot_table(index="date", columns="ticker", values=col).fillna(0.0)
    if baseline:
        W = (W != 0).astype(float)
    ar = pd.read_parquet(os.path.join(PROC, "panel", arfile))
    A0 = ar.reindex(index=W.index, columns=W.columns)
    if neutral:
        live = A0.notna()
        mu = W.where(live).mean(axis=1)
        W = W.sub(mu, axis=0).where(live, 0.0)
    W = W.div(W.abs().sum(axis=1).replace(0, np.nan), axis=0).fillna(0.0)
    W = W.rolling(H, min_periods=1).mean()  # overlapping holdings
    R = A0.shift(-1).fillna(0.0)  # next-day AR
    gross = (W * R).sum(axis=1)
    reg = P.drop_duplicates("ticker").set_index("ticker").region
    cost = pd.Series([COST_BP.get(reg.get(c, "US"), 10) for c in W.columns], index=W.columns) / 1e4
    turn = W.diff().abs().fillna(W.abs())
    net = gross - (turn * cost).sum(axis=1)
    return gross, net, turn.sum(axis=1)


def summarize(x):
    x = x.dropna()
    ann, vol = x.mean() * 252, x.std() * np.sqrt(252)
    eq = (1 + x).cumprod()
    return {"ann_ret": ann, "ann_vol": vol, "sharpe": ann / vol if vol else np.nan,
            "t_stat": x.mean() / x.std() * np.sqrt(len(x)) if x.std() else np.nan, "max_dd": (eq / eq.cummax() - 1).min()}


def main():
    X = build_features()
    ev_cols = [c for c in X.columns if c.split("_")[0] in ("cust", "supp", "layer", "other")]
    own_cols = [c for c in X.columns if c.startswith("own_")]
    ctrl = ["r1", "r5", "r20"]
    full_cols = ev_cols + own_cols + ctrl
    X = X.dropna(subset=["y"])
    X["y"] = X.y.clip(X.y.quantile(0.005), X.y.quantile(0.995))
    X["year"] = X.date.dt.year
    preds, coefs = [], []
    for Y in range(2019, 2027):
        tr = X[(X.year >= Y - 4) & (X.year < Y)]
        # gap of H days to avoid label overlap with the test year
        tr = tr[tr.date < pd.Timestamp(f"{Y}-01-01") - pd.Timedelta(days=10)]
        te = X[X.year == Y].copy()
        b_ev = fit_ols(tr, ev_cols)
        b_full = fit_ols(tr, full_cols)
        te["pred_event"] = predict(te, ev_cols, b_ev)
        te["pred_full"] = predict(te, full_cols, b_full)
        te["pred_own"] = predict(te, own_cols, fit_ols(tr, own_cols))
        preds.append(te[["date", "ticker", "region", "y", "pred_event", "pred_full", "pred_own"]])
        coefs.append(pd.Series(b_full[1:], index=full_cols, name=Y))
    P = pd.concat(preds)
    C = pd.concat(coefs, axis=1)
    C.to_csv(os.path.join(OUT, "network_model_coefs.csv"))
    print("walk-forward coefficients (full model, % AR over next 5d per 1% feature):")
    print(C.round(4).to_string())
    rows = []
    for col in ["pred_event", "pred_own", "pred_full"]:
        ic = P.groupby("date").apply(lambda d: d[col].corr(d.y, method="spearman") if d[col].std() > 0 else np.nan)
        gross, net, turn = portfolio(P, col)
        for per, lo, hi in [("2019-2022", "2019-01-01", "2023-01-01"), ("2023-2024", "2023-01-01", "2025-01-01"),
                            ("2025-2026", "2025-01-01", "2026-12-31"), ("all", "2019-01-01", "2026-12-31")]:
            g, n_ = gross[(gross.index >= lo) & (gross.index < hi)], net[(net.index >= lo) & (net.index < hi)]
            icp = ic[(ic.index >= lo) & (ic.index < hi)]
            rows.append({"signal": col, "period": per, "mean_IC": icp.mean(), "IC_t": icp.mean() / icp.std() * np.sqrt(icp.count()),
                         **{f"gross_{k}": v for k, v in summarize(g).items()}, **{f"net_{k}": v for k, v in summarize(n_).items()},
                         "turnover_daily": turn[(turn.index >= lo) & (turn.index < hi)].mean()})
        pd.DataFrame({"gross": gross, "net": net}).to_parquet(os.path.join(PROC, f"network_pnl_{col}.parquet"))
    R = pd.DataFrame(rows)
    R.to_csv(os.path.join(OUT, "network_model_perf.csv"), index=False)
    pd.set_option("display.width", 250)
    print(R[["signal", "period", "mean_IC", "IC_t", "gross_sharpe", "net_sharpe", "net_ann_ret", "net_t_stat", "net_max_dd", "turnover_daily"]].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
