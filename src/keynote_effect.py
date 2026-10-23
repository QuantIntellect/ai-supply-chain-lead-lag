"""Do stocks react when NVIDIA names them in a keynote / keynote press kit?

For each keynote with a known start time and each tradeable universe stock: reaction session on the
stock's own exchange = first session closing after the keynote start. Compare named vs not-named
stocks: AR (vs local index), AR vs AI basket, CAR[+1,+5]. Clustered by keynote. Small sample (~20 keynotes).
Output: reports/tables/keynote_effect.csv, reports/tables/keynote_effect_obs.csv
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd
import statsmodels.api as sm
from common import PROC, REPORTS, load_universe
from events import Calendar

OUT = os.path.join(REPORTS, "tables")


def main():
    K = pd.read_csv(os.path.join(PROC, "keynotes", "keynote_events.csv"))
    K = K[K.keynote_time_et.notna()].copy()
    K["ts"] = pd.to_datetime(K.keynote_time_et, utc=True)
    M = pd.read_csv(os.path.join(PROC, "keynotes", "keynote_mentions.csv"))
    uni = load_universe()
    trade = [t for t in uni[uni.tradeable == "1"].ticker]
    ret = pd.read_parquet(os.path.join(PROC, "panel", "ret.parquet"))
    ar = pd.read_parquet(os.path.join(PROC, "panel", "abret.parquet"))
    ari = pd.read_parquet(os.path.join(PROC, "panel", "abret_ind.parquet"))
    E = pd.read_parquet(os.path.join(PROC, "events.parquet"))
    cal = Calendar(ret[[t for t in trade if t in ret.columns]])
    rows = []
    for k in K.itertuples():
        named = M[(M.event_slug == k.event_slug) & M.ticker.isin(trade)]
        types = named.groupby("ticker").mention_type.agg(lambda s: "|".join(sorted(set(s))))
        counts = named.groupby("ticker").size()
        for t in cal.days:
            if t == "NVDA":
                continue
            d, partial = cal.reaction_day(t, k.ts)
            if d is None:
                continue
            idx = cal.days[t]
            j = idx.get_loc(d)
            # skip if the stock had its own earnings within +-2 sessions
            own = E[(E.ticker == t) & (E.react_date >= idx[max(0, j - 2)]) & (E.react_date <= idx[min(len(idx) - 1, j + 2)])]
            if len(own):
                continue
            a = ar[t].reindex(idx)
            ai = ari[t].reindex(idx)
            rows.append({"event": k.event_slug, "date": d, "ticker": t, "named": int(t in types.index),
                         "n_mentions": int(counts.get(t, 0)), "types": types.get(t, ""),
                         "ar0": a.iloc[j] + (a.iloc[j + 1] if partial and j + 1 < len(a) else 0),
                         "ar0_ind": ai.iloc[j] + (ai.iloc[j + 1] if partial and j + 1 < len(ai) else 0),
                         "car_1_5": a.iloc[j + 1 + int(partial): j + 6 + int(partial)].sum() if j + 6 < len(a) else np.nan,
                         "car_1_5_ind": ai.iloc[j + 1 + int(partial): j + 6 + int(partial)].sum() if j + 6 < len(ai) else np.nan})
    X = pd.DataFrame(rows)
    X.to_csv(os.path.join(OUT, "keynote_effect_obs.csv"), index=False)
    res = []
    for sub, d in [("all named", X), ("partnership/investment", X.assign(named=X.types.str.contains("partnership|investment").astype(int))),
                   ("customer/deployment", X.assign(named=X.types.str.contains("customer").astype(int))),
                   ("2+ mentions", X.assign(named=(X.n_mentions >= 2).astype(int)))]:
        for y in ["ar0", "ar0_ind", "car_1_5", "car_1_5_ind"]:
            dd = d.dropna(subset=[y])
            m = sm.OLS(dd[y] * 100, sm.add_constant(dd.named)).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(dd.event)[0]})
            res.append({"named_definition": sub, "y": y, "n_named": int(dd.named.sum()), "n_obs": len(dd), "keynotes": dd.event.nunique(),
                        "diff_pct": m.params["named"], "t": m.tvalues["named"]})
    R = pd.DataFrame(res)
    R.to_csv(os.path.join(OUT, "keynote_effect.csv"), index=False)
    pd.set_option("display.width", 200)
    print(R.round(3).to_string(index=False))
    top = X[X.named == 1].groupby("ticker").agg(n=("event", "count"), mean_ar0=("ar0", "mean"), mean_ar0_ind=("ar0_ind", "mean")).sort_values("n", ascending=False)
    print((top.head(15) * [1, 100, 100]).round(2).to_string())


if __name__ == "__main__":
    main()
