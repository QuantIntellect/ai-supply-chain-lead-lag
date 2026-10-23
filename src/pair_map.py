"""Pairwise sympathy map: for every reporter A and responder B, how B moves on A's release day.

Outputs
  reports/tables/pair_map.csv          per (A,B): n, beta, corr (+95% CI) for 2015+, pre-2023 and 2023+
  reports/tables/h1_oos.csv            H1 test: betas fit <=2024 predict 2025-26 sympathy moves
  reports/tables/partial_share.csv     share of partial-session reactions by region pair
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd
import statsmodels.api as sm
from common import PROC, REPORTS, ensure
from analyze_spill import wins

OUT = ensure(os.path.join(REPORTS, "tables"))


def pair_stats(d):
    n = len(d)
    if n < 6 or d.arA.std() == 0:
        return dict(n=n)
    x, y = d.arA.values, d.ar0.values
    beta = np.cov(x, y, ddof=1)[0, 1] / np.var(x, ddof=1)
    r = np.corrcoef(x, y)[0, 1]
    z, se = np.arctanh(np.clip(r, -0.999, 0.999)), 1 / np.sqrt(max(n - 3, 1))
    return dict(n=n, beta=beta, corr=r, corr_lo=np.tanh(z - 1.96 * se), corr_hi=np.tanh(z + 1.96 * se))


def main():
    S = pd.read_parquet(os.path.join(PROC, "spill.parquet"))
    S = S[~S.own_near & S.arA.notna() & S.ar0.notna()].copy()
    S["arA"] = wins(S.arA) * 100
    S["ar0"] = wins(S.ar0) * 100
    ps = S.groupby(["regionA", "regionB"]).partial.mean().unstack().round(3)
    ps.to_csv(os.path.join(OUT, "partial_share.csv"))
    print("share of partial-session reactions (row=reporter region, col=responder region):\n", ps)

    rows = []
    for (a, b), d in S.groupby(["A", "B"]):
        rec = {"A": a, "B": b, "layerA": d.layerA.iat[0], "layerB": d.layerB.iat[0], "rel": d.rel.iat[0]}
        for tag, dd in [("all", d), ("pre", d[d.t0A < "2023-01-01"]), ("ai", d[d.t0A >= "2023-01-01"])]:
            for k, v in pair_stats(dd).items():
                rec[f"{k}_{tag}"] = v
        rows.append(rec)
    P = pd.DataFrame(rows)
    P.to_csv(os.path.join(OUT, "pair_map.csv"), index=False)
    strong = P[(P.n_all >= 20)].sort_values("corr_all", ascending=False)
    print("\nstrongest sympathy pairs 2015+ (n>=20):")
    print(strong[["A", "B", "rel", "n_all", "beta_all", "corr_all", "corr_lo_all", "beta_pre", "beta_ai", "n_ai"]].head(40).round(2).to_string(index=False))

    # H1: out-of-sample stability. Fit pair beta on <=2024, layer-pair beta as fallback / benchmark.
    tr = S[S.t0A < "2025-01-01"]
    te = S[S.t0A >= "2025-01-01"].copy()
    pb = pd.DataFrame([{"A": a, "B": b, **pair_stats(d)} for (a, b), d in tr.groupby(["A", "B"])])
    pb = pb[pb.n >= 8][["A", "B", "beta", "n"]].rename(columns={"beta": "beta_pair", "n": "n_train"})
    lb = pd.DataFrame([{"layerA": a, "layerB": b, "beta_layer": np.cov(d.arA, d.ar0)[0, 1] / np.var(d.arA, ddof=1)}
                       for (a, b), d in tr.groupby(["layerA", "layerB"])])
    te = te.merge(pb, on=["A", "B"], how="left").merge(lb, on=["layerA", "layerB"], how="left")
    # shrink pair beta toward layer beta (n/(n+20))
    w = te.n_train / (te.n_train + 20)
    te["beta_shrunk"] = np.where(te.beta_pair.notna(), w * te.beta_pair + (1 - w) * te.beta_layer, te.beta_layer)
    out = []
    for model in ["beta_layer", "beta_pair", "beta_shrunk"]:
        d = te.dropna(subset=[model])
        pred = d[model] * d.arA
        X = sm.add_constant(pred.rename("pred"))
        m = sm.OLS(d.ar0, X).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(d.t0A)[0]})
        hit = (np.sign(pred) == np.sign(d.ar0))[pred.abs() > 0.25].mean()
        out.append({"model": model, "n": len(d), "corr": np.corrcoef(pred, d.ar0)[0, 1], "slope": m.params["pred"],
                    "t": m.tvalues["pred"], "sign_hit_|pred|>0.25%": hit})
    H1 = pd.DataFrame(out)
    H1.to_csv(os.path.join(OUT, "h1_oos.csv"), index=False)
    print("\nH1 out-of-sample (train <=2024, test 2025-26):\n", H1.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
