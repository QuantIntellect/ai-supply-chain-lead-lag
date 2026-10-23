"""Customer-news momentum strategy (fixed rule, no fitting) + region-pair drift table + live signals.

Signal for stock B on day t: sum of winsorised earnings-day abnormal returns (pct) of B's customers
(edges where B supplies A) that became known in the last 20 sessions (cust_0_0 + cust_1_4 + cust_5_19
from network_features). Book: weights ∝ signal (gross 1), H-day overlapping holding, next-day AR P&L,
10/15 bp one-way costs (US/EU).
Outputs: reports/tables/customer_momentum_perf.csv, data/processed/customer_momentum_pnl.parquet,
         reports/tables/live_signals.csv, reports/tables/region_drift.csv
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd
import network_model as nm
from common import PROC, REPORTS, load_universe, load_edges
from analyze_spill import load, ols

OUT = os.path.join(REPORTS, "tables")


def region_drift():
    rows = []
    for era, start, end in [("AI 2023-26", "2023-01-01", None), ("pre-AI 2015-22", "2015-01-01", "2023-01-01")]:
        S = load(start, end)
        D = S[~S.own_in_30]
        for (ra, rb), d in D.groupby(["regionA", "regionB"]):
            for rel in ["edge", "same_layer", "other"]:
                dd = d[d.rel.isin(["A_supplies_B", "B_supplies_A"])] if rel == "edge" else d[d.rel == rel]
                r0 = ols(dd, "ar0", ["arA"])
                rec = {"era": era, "reporter": ra, "responder": rb, "rel": rel}
                if r0:
                    rec.update({"sympathy_beta": r0[0].params["arA"], "sympathy_t": r0[0].tvalues["arA"], "n": r0[1]})
                for k in [1, 5, 20]:
                    r = ols(dd, f"car_1_{k}", ["arA"])
                    if r:
                        rec.update({f"drift{k}_g": r[0].params["arA"], f"drift{k}_t": r[0].tvalues["arA"]})
                rows.append(rec)
    R = pd.DataFrame(rows)
    R.to_csv(os.path.join(OUT, "region_drift.csv"), index=False)
    return R


def main():
    region_drift()
    X = pd.read_parquet(os.path.join(PROC, "network_features.parquet"))
    ar = pd.read_parquet(os.path.join(PROC, "panel", "abret.parquet"))
    X["sig_cust"] = X[["cust_0_0", "cust_1_4", "cust_5_19"]].sum(axis=1)
    rows, pnl = [], {}
    for H in [10, 20]:
        nm.H = H
        yH = []
        for B, g in X.groupby("ticker"):
            a = ar[B].reindex(g.date).fillna(0).values * 100
            cs = np.concatenate([[0], np.cumsum(a)])
            n = len(a)
            idx = np.arange(n)
            yH.append(pd.Series(np.where(idx + H < n, cs[np.minimum(idx + 1 + H, n)] - cs[idx + 1], np.nan), index=g.index))
        X["y"] = pd.concat(yH)
        P = X[X.date >= "2016-01-01"].copy()
        Pi = P.dropna(subset=["y"])
        ic = Pi[Pi.sig_cust != 0].groupby("date").apply(
            lambda d: d.sig_cust.corr(d.y, method="spearman") if d.sig_cust.std() > 0 and len(d) >= 5 else np.nan)
        VARIANTS = {  # name: (neutral, ar panel, baseline)
            "signal | net-long | vs index (original)": (False, "abret.parquet", False),
            "signal | dollar-neutral | vs index": (True, "abret.parquet", False),
            "signal | net-long | vs AI basket": (False, "abret_ind.parquet", False),
            "signal | dollar-neutral | vs AI basket": (True, "abret_ind.parquet", False),
            "baseline: long all signalled names | vs index": (False, "abret.parquet", True),
            "baseline: long all signalled names | vs AI basket": (False, "abret_ind.parquet", True),
        }
        for vname, (neu, arf, base) in VARIANTS.items():
            gross, net, turn = nm.portfolio(P, "sig_cust", neutral=neu, arfile=arf, baseline=base)
            pnl[f"H{H}|{vname}"] = net
            for per, lo, hi in [("2016-2022", "2016-01-01", "2023-01-01"), ("2023-2024", "2023-01-01", "2025-01-01"),
                                ("2025-2026", "2025-01-01", "2026-12-31"), ("2016-2026", "2016-01-01", "2026-12-31")]:
                g, n_ = gross[(gross.index >= lo) & (gross.index < hi)], net[(net.index >= lo) & (net.index < hi)]
                icp = ic[(ic.index >= lo) & (ic.index < hi)]
                sg, sn = nm.summarize(g), nm.summarize(n_)
                rows.append({"hold_days": H, "variant": vname, "period": per, "IC": icp.mean(),
                             "IC_t": icp.mean() / icp.std() * np.sqrt(icp.count()),
                             "gross_sharpe": sg["sharpe"], "net_sharpe": sn["sharpe"], "net_ann_ret": sn["ann_ret"],
                             "net_t": sn["t_stat"], "net_max_dd": sn["max_dd"],
                             "daily_turnover": turn[(turn.index >= lo) & (turn.index < hi)].mean()})
    R = pd.DataFrame(rows)
    R.to_csv(os.path.join(OUT, "customer_momentum_perf.csv"), index=False)
    pd.DataFrame(pnl).to_parquet(os.path.join(PROC, "customer_momentum_pnl.parquet"))
    pd.set_option("display.width", 250)
    print(R[R.hold_days == 20].round(3).to_string(index=False))

    # live signals at the last date: which customers drove them
    last = X.date.max()
    L = X[X.date == last][["ticker", "sig_cust", "cust_0_0", "cust_1_4", "cust_5_19", "own_1_4", "own_5_19"]]
    S = pd.read_parquet(os.path.join(PROC, "spill.parquet"))
    sess = sorted(X.date.unique())[-20]
    recent = S[(S.rel == "B_supplies_A") & (S.entry_date >= sess)]
    drivers = recent.groupby("B").apply(lambda d: ", ".join(f"{a} {x * 100:+.1f}%" for a, x in zip(d.A, d.arA))).rename("customer_reports")
    L = L.merge(drivers, left_on="ticker", right_index=True, how="left")
    uni = load_universe()
    L = L.merge(uni[["ticker", "name", "layer"]], on="ticker").sort_values("sig_cust", ascending=False)
    L.to_csv(os.path.join(OUT, "live_signals.csv"), index=False)
    print("live signals as of", pd.Timestamp(last).date())
    print(L[L.sig_cust != 0].round(2).to_string(index=False))


if __name__ == "__main__":
    main()
