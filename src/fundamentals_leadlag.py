"""Demand cascade in fundamentals + H5 (TSMC monthly revenue -> AI basket returns).

1. Calendar-quarter panel of revenue / capex (XBRL) + TSMC quarterly revenue (sum of monthly).
2. Lead-lag correlations of YoY growth: hyperscaler capex vs supplier revenue at leads -2..+4 quarters.
3. H5: TSMC monthly YoY acceleration -> AI-chip basket abnormal return over next 20 sessions (US),
   and -> NVDA next reported quarterly revenue growth.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd
import statsmodels.api as sm
from common import PROC, REPORTS, ensure

OUT = ensure(os.path.join(REPORTS, "tables"))
HYPER = ["MSFT", "GOOGL", "AMZN", "META", "ORCL"]
SUPPLIERS = ["NVDA", "AVGO", "AMD", "MU", "MRVL", "ANET", "SMCI", "DELL", "VRT", "ETN", "GEV", "PWR", "CLS", "FN",
             "COHR", "LITE", "CIEN", "AMAT", "LRCX", "KLAC", "TSMC", "CRWV", "MPWR", "CRDO", "ALAB", "STX", "WDC", "CSCO"]


def quarterly_panel():
    F = pd.read_parquet(os.path.join(PROC, "fundamentals_q.parquet"))
    F = F[F.concept.isin(["revenue", "capex", "finance_lease_principal"])].copy()
    mid = F.period_start + (F.period_end - F.period_start) / 2
    F["cq"] = mid.dt.to_period("Q")
    P = F.pivot_table(index="cq", columns=["concept", "ticker"], values="value", aggfunc="last")
    tsmc = pd.read_csv(os.path.join(PROC, "tsmc_monthly.csv"), parse_dates=["month"])
    tq = tsmc.groupby(tsmc.month.dt.to_period("Q")).revenue_ntd_bn.agg(["sum", "count"])
    P[("revenue", "TSMC")] = tq["sum"].where(tq["count"] == 3)
    return P


def main():
    P = quarterly_panel()
    capex = P["capex"][HYPER].copy()
    # finance leases are a large part of MSFT/AMZN/META/ORCL data-center spend: include them
    fl = P["finance_lease_principal"].reindex(columns=HYPER).fillna(0)
    hyper_capex = capex.sum(axis=1, min_count=5)
    hyper_capex_fl = (capex + fl).sum(axis=1, min_count=5)
    rev = P["revenue"]
    Q = pd.DataFrame({"hyper_capex": hyper_capex, "hyper_capex_incl_leases": hyper_capex_fl})
    for s in SUPPLIERS:
        if s in rev:
            Q[f"rev_{s}"] = rev[s]
    Q = Q[Q.index >= pd.Period("2015Q1")]
    yoy = (Q.pct_change(4, fill_method=None) * 100).replace([np.inf, -np.inf], np.nan)
    Q.to_csv(os.path.join(OUT, "quarterly_capex_revenue.csv"))
    yoy.to_csv(os.path.join(OUT, "quarterly_capex_revenue_yoy.csv"))
    print("hyperscaler capex (USD bn, cash capex incl. finance-lease principal), last 12 quarters:")
    print((Q[["hyper_capex", "hyper_capex_incl_leases"]].tail(12) / 1e9).round(1).T.to_string())
    print("\nYoY % last 8 quarters:")
    print(yoy[["hyper_capex", "rev_NVDA", "rev_AVGO", "rev_MU", "rev_TSMC", "rev_VRT", "rev_ETN", "rev_ANET", "rev_DELL"]].tail(8).round(0).to_string())

    # lead-lag: corr(capex_yoy(t), rev_yoy(t+k))
    rows = []
    for s in [c for c in yoy.columns if c.startswith("rev_")]:
        for k in range(-2, 5):
            a = yoy["hyper_capex"]
            b = yoy[s].shift(-k)
            d = pd.concat([a, b], axis=1).dropna()
            if len(d) >= 12:
                rows.append({"supplier": s[4:], "lead_q": k, "corr": d.corr().iloc[0, 1], "n": len(d)})
            if len(d) >= 12:
                d2 = d[d.index >= pd.Period("2021Q1")]
                if len(d2) >= 8:
                    rows[-1]["corr_2021plus"] = d2.corr().iloc[0, 1]
                # first differences of YoY growth remove the shared 2023-26 up-trend
                dd = pd.concat([a.diff(), yoy[s].diff().shift(-k)], axis=1).dropna()
                if len(dd) >= 12:
                    rows[-1]["corr_diff"] = dd.corr().iloc[0, 1]
                    rows[-1]["n_diff"] = len(dd)
    LL = pd.DataFrame(rows)
    LL.to_csv(os.path.join(OUT, "capex_leadlag.csv"), index=False)
    piv = LL.pivot(index="supplier", columns="lead_q", values="corr").round(2)
    print("\ncorr(hyperscaler capex YoY at t, supplier revenue YoY at t+k), 2015+ :")
    print(piv.sort_values(0, ascending=False).to_string())
    best = LL.loc[LL.groupby("supplier")["corr"].idxmax()][["supplier", "lead_q", "corr"]]
    print("\npeak lead (quarters) by supplier:", dict(zip(best.supplier, best.lead_q)))
    if "corr_diff" in LL:
        print("\nfirst-difference version (d capex YoY vs d revenue YoY at t+k):")
        print(LL.pivot(index="supplier", columns="lead_q", values="corr_diff").round(2).to_string())
        bd = LL.dropna(subset=["corr_diff"])
        bd = bd.loc[bd.groupby("supplier")["corr_diff"].idxmax()][["supplier", "lead_q", "corr_diff", "n_diff"]]
        print("peak lead (differences):", dict(zip(bd.supplier, zip(bd.lead_q, bd.corr_diff.round(2)))))
        bd.to_csv(os.path.join(OUT, "capex_leadlag_peaks_diff.csv"), index=False)
        # nowcast: suppliers whose revenue acceleration lags capex acceleration by k>=1 quarters (corr_diff >= 0.3)
        dcap = yoy["hyper_capex"].diff()
        last_cap = dcap.dropna().index.max()
        rows = []
        for r in bd[(bd.lead_q >= 1) & (bd.corr_diff >= 0.3)].itertuples():
            k = int(r.lead_q)
            y = yoy[f"rev_{r.supplier}"].diff()
            d = pd.concat([dcap.rename("x"), y.shift(-k).rename("y")], axis=1).dropna()
            m = sm.OLS(d.y, sm.add_constant(d.x)).fit()
            last_rev = yoy[f"rev_{r.supplier}"].dropna().index.max()
            for h in range(1, k + 1):
                tq = last_rev + h
                src_q = tq - k
                if src_q > last_cap or src_q not in dcap.index or pd.isna(dcap.get(src_q)):
                    continue
                x = dcap[src_q]
                pred = m.params["const"] + m.params["x"] * x
                se = np.sqrt(m.scale)
                rows.append({"supplier": r.supplier, "lead_q": k, "corr_diff": r.corr_diff, "n": int(m.nobs), "slope": m.params["x"],
                             "target_quarter": str(tq), "capex_quarter": str(src_q), "capex_accel_pp": x,
                             "pred_rev_growth_change_pp": pred, "resid_sd_pp": se,
                             "last_rev_yoy_pct": yoy[f"rev_{r.supplier}"].dropna().iloc[-1], "last_rev_quarter": str(last_rev)})
        NC = pd.DataFrame(rows)
        NC.to_csv(os.path.join(OUT, "capex_nowcast.csv"), index=False)
        print("\nnowcast (change in supplier revenue YoY growth, pp; from hyperscaler capex acceleration k quarters earlier):")
        print(NC.round(2).to_string(index=False))

    # ---------- H5: TSMC monthly revenue -> AI basket ----------
    tsmc = pd.read_csv(os.path.join(PROC, "tsmc_monthly.csv"), parse_dates=["month", "release_date"]).sort_values("month")
    tsmc["yoy"] = tsmc.yoy_pct
    tsmc["accel"] = tsmc.yoy - tsmc.yoy.shift(1).rolling(3).mean()
    # seasonal MoM surprise: MoM minus average MoM of same calendar month in prior 3 years
    tsmc["cal_m"] = tsmc.month.dt.month
    tsmc["mom_norm"] = tsmc.groupby("cal_m").mom_pct.transform(lambda s: s.shift(1).rolling(3, min_periods=2).mean())
    tsmc["mom_surp"] = tsmc.mom_pct - tsmc.mom_norm
    ar = pd.read_parquet(os.path.join(PROC, "panel", "abret.parquet"))
    basket = ["NVDA", "AMD", "AVGO", "MRVL", "MU", "TSM"]
    B = ar[basket].mean(axis=1)
    smh = pd.read_parquet(os.path.join(PROC, "panel", "ret.parquet"))["SMH"] - pd.read_parquet(os.path.join(PROC, "panel", "ret.parquet"))["SPY"]
    rows = []
    for r in tsmc.itertuples():
        d = r.release_date
        idx = B.dropna().index
        j = idx.searchsorted(d)  # release ~13:30 Taipei = before US open: day d is the reaction day
        if j + 21 >= len(idx):
            continue
        rows.append({"month": r.month, "release": d, "yoy": r.yoy, "accel": r.accel, "mom_surp": r.mom_surp,
                     "ar_d0": B.loc[idx[j]], "car_1_5": B.loc[idx[j + 1]: idx[j + 5]].sum(),
                     "car_1_20": B.loc[idx[j + 1]: idx[j + 20]].sum(),
                     "smh_1_20": smh.loc[idx[j + 1]: idx[j + 20]].sum()})
    H = pd.DataFrame(rows).dropna(subset=["accel"])
    out = []
    for era, d in [("all", H), ("2015-2022", H[H.release < "2023-01-01"]), ("2023+", H[H.release >= "2023-01-01"])]:
        for x in ["accel", "mom_surp"]:
            for y in ["ar_d0", "car_1_5", "car_1_20", "smh_1_20"]:
                dd = d.dropna(subset=[x, y])
                m = sm.OLS(dd[y] * 100, sm.add_constant(dd[x])).fit(cov_type="HAC", cov_kwds={"maxlags": 2})
                out.append({"era": era, "x": x, "y": y, "n": len(dd), "b": m.params[x], "t": m.tvalues[x]})
    H5 = pd.DataFrame(out)
    H5.to_csv(os.path.join(OUT, "h5_tsmc_monthly.csv"), index=False)
    print("\nH5: TSMC monthly revenue surprise -> AI-chip basket abnormal return (%, per 1pp of surprise):")
    print(H5.pivot_table(index=["era", "x"], columns="y", values=["b", "t"]).round(3).to_string())
    H.to_csv(os.path.join(OUT, "h5_tsmc_monthly_obs.csv"), index=False)


if __name__ == "__main__":
    main()
