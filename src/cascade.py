"""Cascade test: do earlier reporters in the same season predict a later reporter's own release?

Unit: each event of company B. Features use only information available at the close before B's
reaction day:
  f_edge     mean AR of edge-linked companies (suppliers or customers of B) released in prior 60 days
  f_layer    mean AR of same-layer companies released in prior 60 days
  f_up/down  mean AR of upstream / downstream layers released in prior 60 days
  f_surp_*   mean EPS surprise (%) of the same groups
  symp_car   sum of B's own AR on those reporters' reaction days (how much B already moved on peers' news)
  pre_car    B's CAR over [-20,-1]
  last_ar    B's own reaction at its previous release
Targets: B's release-day AR (ar_own) and EPS-surprise sign.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd
import statsmodels.api as sm
from common import PROC, REPORTS, load_universe, load_edges, ensure

OUT = ensure(os.path.join(REPORTS, "tables"))
ORDER = ["ENERGY", "SEMICAP", "FOUNDRY_MEM", "CHIPS", "NETWORK", "SYSTEMS", "DCINFRA", "AIFACTORY", "HYPERSCALER", "APPS"]
RANK = {l: i for i, l in enumerate(ORDER)}  # rough upstream -> downstream ordering of the build-out


def build(window_days=60):
    E = pd.read_parquet(os.path.join(PROC, "events.parquet"))
    S = pd.read_parquet(os.path.join(PROC, "spill.parquet"))
    ar = pd.read_parquet(os.path.join(PROC, "panel", "abret.parquet"))
    uni = load_universe()
    layer = dict(zip(uni.ticker, uni.layer))
    edges = load_edges()
    nbrs = {}
    edges = edges[~edges.rel.isin(["partner", "investment"])]
    for a, b in zip(edges.src, edges.dst):
        nbrs.setdefault(a, set()).add(b)
        nbrs.setdefault(b, set()).add(a)
    E = E[E.react_date >= "2015-01-01"].copy()
    E["layer"] = E.ticker.map(layer)
    E["ar_w"] = E.ar.clip(E.ar.quantile(0.01), E.ar.quantile(0.99))
    E["surp_w"] = E.surprise_pct.clip(-50, 50)
    # B's response on each reporter's day, from the spill panel (keyed by event_id of A and responder B)
    resp = S.set_index(["event_id", "B"]).ar0
    rows = []
    for ev in E.itertuples():
        B, tB = ev.ticker, ev.react_date
        prior = E[(E.react_date < tB) & (E.react_date >= tB - pd.Timedelta(days=window_days)) & (E.ticker != B)]
        if prior.empty:
            continue
        lb = layer.get(B)
        groups = {
            "edge": prior[prior.ticker.isin(nbrs.get(B, set()))],
            "layer": prior[prior.layer == lb],
            "up": prior[prior.layer.map(RANK) < RANK.get(lb, 0)],
            "down": prior[prior.layer.map(RANK) > RANK.get(lb, 0)],
            "all": prior,
        }
        rec = {"event_id": ev.event_id, "B": B, "date": tB, "layer": lb, "ar_own": ev.ar_w, "surp_own": ev.surp_w,
               "av_own": ev.av}
        for g, d in groups.items():
            rec[f"f_{g}"] = d.ar_w.mean() if len(d) else np.nan
            rec[f"n_{g}"] = len(d)
            rec[f"fs_{g}"] = d.surp_w.mean() if d.surp_w.notna().any() else np.nan
        # sympathy CAR: B's own AR on the prior reporters' reaction days (edge+layer group), already "priced in"
        ids = pd.concat([groups["edge"], groups["layer"]]).event_id.unique()
        vals = [resp.get((i, B), np.nan) for i in ids]
        vals = [v for v in vals if pd.notna(v)]
        rec["symp_car"] = float(np.sum(vals)) if vals else 0.0
        # weighted: sympathy CAR on all prior reporters
        ids_all = prior.event_id.unique()
        va = [resp.get((i, B), np.nan) for i in ids_all]
        rec["symp_car_all"] = float(np.nansum(va)) if len(va) else 0.0
        # B's pre-event CAR[-20,-1] and previous own reaction
        s = ar[B].dropna()
        j = s.index.searchsorted(tB)
        rec["pre_car"] = s.iloc[max(0, j - 20): j].sum() if j > 0 else np.nan
        prevB = E[(E.ticker == B) & (E.react_date < tB)]
        rec["last_ar"] = prevB.ar_w.iloc[-1] if len(prevB) else np.nan
        rows.append(rec)
    C = pd.DataFrame(rows)
    C.to_parquet(os.path.join(PROC, "cascade.parquet"), index=False)
    return C


def fit(C, y, xs, label):
    d = C.dropna(subset=[y] + xs)
    X = sm.add_constant(d[xs])
    m = sm.OLS(d[y], X).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(d.date.dt.to_period("W"))[0]})
    return {"model": label, "y": y, "n": len(d), **{f"b_{x}": m.params[x] for x in xs},
            **{f"t_{x}": m.tvalues[x] for x in xs}, "r2": m.rsquared}


def main():
    C = build()
    print("cascade rows", len(C))
    res = []
    for era, d in [("pre", C[C.date < "2023-01-01"]), ("ai", C[C.date >= "2023-01-01"])]:
        d = d.copy()
        for c in ["ar_own", "f_edge", "f_layer", "f_up", "f_down", "f_all", "symp_car", "symp_car_all", "pre_car", "last_ar"]:
            d[c] = d[c] * 100
        d["surp_pos"] = (d.surp_own > 0).astype(float).where(d.surp_own.notna())
        for spec, xs in [("peers", ["f_edge", "f_layer"]), ("layers", ["f_up", "f_down", "f_layer"]),
                         ("priced_in", ["f_layer", "symp_car", "pre_car"]), ("full", ["f_layer", "f_up", "f_down", "symp_car", "pre_car", "last_ar"])]:
            for y in ["ar_own", "surp_pos"]:
                try:
                    r = fit(d, y, xs, spec)
                    r["era"] = era
                    res.append(r)
                except Exception as e:
                    print("fail", era, spec, y, e)
        # surprise-on-surprise: do peers' EPS surprises predict B's surprise?
        for y, xs in [("surp_own", ["fs_layer", "fs_edge"]), ("surp_pos", ["fs_layer", "fs_up", "fs_down"])]:
            r = fit(d, y, xs, "surprise_on_surprise")
            r["era"] = era
            res.append(r)
    R = pd.DataFrame(res)
    R.to_csv(os.path.join(OUT, "cascade_regressions.csv"), index=False)
    pd.set_option("display.width", 250)
    for (era, y), g in R.groupby(["era", "y"]):
        print(f"\n== era={era} target={y}")
        cols = [c for c in g.columns if (c.startswith("b_") or c.startswith("t_")) and g[c].notna().any()]
        print(g[["model", "n", "r2"] + cols].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
