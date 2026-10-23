"""Pooled spillover regressions on the responder-event panel.

Contemporaneous:  ar0_B      = a + b * arA          (sympathy beta, by layer pair / relation)
Drift:            car_1_k_B  = a + g * arA (+ c * ar0_B)  (does B keep moving after A's news?)
SEs clustered by reporter reaction date (all responders to one release share the shock).
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd
import statsmodels.api as sm
from common import PROC, REPORTS, ensure

OUT = ensure(os.path.join(REPORTS, "tables"))
LAYERS = ["ENERGY", "DCINFRA", "SEMICAP", "FOUNDRY_MEM", "CHIPS", "NETWORK", "SYSTEMS", "AIFACTORY", "HYPERSCALER", "APPS"]


def wins(s, p=0.01):
    lo, hi = s.quantile(p), s.quantile(1 - p)
    return s.clip(lo, hi)


def ols(df, y, xs, cluster="t0A"):
    d = df.dropna(subset=[y] + xs)
    if len(d) < 30 or d[cluster].nunique() < 8:
        return None
    X = sm.add_constant(d[xs])
    m = sm.OLS(d[y], X).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(d[cluster])[0]})
    return m, len(d), d[cluster].nunique()


def load(start="2023-01-01", end=None):
    S = pd.read_parquet(os.path.join(PROC, "spill.parquet"))
    S = S[S.t0A >= start]
    if end:
        S = S[S.t0A < end]
    S = S[~S.own_near & S.arA.notna()].copy()
    for c in ["arA", "ar0", "ar0_raw", "gap0", "id0", "car_m5_m1"] + [c for c in S if c.startswith("car_1_")]:
        S[c] = wins(S[c].astype(float)) * 100  # percent
    return S


def layer_matrix(S, y, x="arA"):
    rows = []
    for la in LAYERS:
        for lb in LAYERS:
            d = S[(S.layerA == la) & (S.layerB == lb)]
            r = ols(d, y, [x])
            if r is None:
                continue
            m, n, g = r
            rows.append({"layerA": la, "layerB": lb, "beta": m.params[x], "t": m.tvalues[x], "n": n, "clusters": g})
    return pd.DataFrame(rows)


def main():
    for era, start, end in [("ai", "2023-01-01", None), ("pre", "2015-01-01", "2023-01-01")]:
        S = load(start, end)
        print(f"===== {era} era: rows={len(S)} events={S.event_id.nunique()}")
        M0 = layer_matrix(S, "ar0")
        M0.to_csv(os.path.join(OUT, f"spill_contemp_layers_{era}.csv"), index=False)
        piv = M0.pivot(index="layerA", columns="layerB", values="beta").reindex(index=LAYERS, columns=LAYERS)
        print("contemporaneous sympathy beta (row = reporter layer, col = responder layer):")
        print(piv.round(2).to_string())
        # drift by relation type
        rows = []
        D = S[~S.own_in_30]
        for rel in ["A_supplies_B", "B_supplies_A", "same_layer", "other", "ALL"]:
            d = D if rel == "ALL" else D[D.rel == rel]
            for k in [1, 2, 5, 10, 20, 40]:
                y = f"car_1_{k}"
                r = ols(d, y, ["arA"])
                r2 = ols(d, y, ["arA", "ar0"])
                if r is None:
                    continue
                m, n, g = r
                row = {"rel": rel, "k": k, "g_arA": m.params["arA"], "t": m.tvalues["arA"], "n": n, "clusters": g}
                if r2:
                    row.update({"g_arA_ctrl": r2[0].params["arA"], "t_ctrl": r2[0].tvalues["arA"],
                                "c_ar0": r2[0].params["ar0"], "t_ar0": r2[0].tvalues["ar0"]})
                rows.append(row)
        DR = pd.DataFrame(rows)
        DR.to_csv(os.path.join(OUT, f"spill_drift_rel_{era}.csv"), index=False)
        print("drift regressions car[+1,+k] on arA (and controlling for responder's own day-0 move):")
        print(DR.round(3).to_string(index=False))
        # contemporaneous by relation
        rows = []
        for rel in ["A_supplies_B", "B_supplies_A", "same_layer", "other"]:
            r = ols(S[S.rel == rel], "ar0", ["arA"])
            if r:
                rows.append({"rel": rel, "beta": r[0].params["arA"], "t": r[0].tvalues["arA"], "n": r[1]})
        CR = pd.DataFrame(rows)
        CR.to_csv(os.path.join(OUT, f"spill_contemp_rel_{era}.csv"), index=False)
        print(CR.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
