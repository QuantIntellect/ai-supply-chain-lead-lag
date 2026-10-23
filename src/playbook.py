"""Forward playbook: for each upcoming reporter, which stocks historically move with it on its release day.

Pair beta (B's AR on A's release day per 1% of A's AR) shrunk toward the layer-pair beta with weight
n/(n+20); typical move = beta x median |AR_A| over A's last 12 releases. Also lists the current season's
completed releases. Output: reports/tables/playbook.csv, reports/tables/season_now.csv
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd
from common import PROC, REPORTS, load_universe

OUT = os.path.join(REPORTS, "tables")


def main():
    P = pd.read_csv(os.path.join(OUT, "pair_map.csv"))
    L = pd.read_csv(os.path.join(OUT, "spill_contemp_layers_ai.csv"))
    Lall = pd.read_csv(os.path.join(OUT, "spill_contemp_layers_pre.csv"))
    lb = pd.concat([Lall.assign(era="pre"), L.assign(era="ai")]).groupby(["layerA", "layerB"]).beta.mean().rename("beta_layer").reset_index()
    P = P.merge(lb, on=["layerA", "layerB"], how="left")
    w = P.n_all / (P.n_all + 20)
    P["beta_shrunk"] = np.where(P.beta_all.notna(), w * P.beta_all + (1 - w) * P.beta_layer.fillna(0), P.beta_layer)
    E = pd.read_parquet(os.path.join(PROC, "events.parquet"))
    typ = E.sort_values("react_date").groupby("ticker").ar.apply(lambda s: s.tail(12).abs().median() * 100).rename("typical_abs_ar_pct")
    uni = load_universe()
    name = dict(zip(uni.ticker, uni.name))
    trade = set(uni[uni.tradeable == "1"].ticker)
    y = pd.read_parquet(os.path.join(PROC, "yahoo_earnings_dates.parquet"))
    y["ts"] = pd.to_datetime(y.earn_ts_utc, utc=True)
    up = y[(y.ts >= "2026-10-23") & (y.ts <= "2026-12-31") & y.ticker.isin(uni.ticker)].sort_values("ts").drop_duplicates("ticker")
    rows = []
    for r in up.itertuples():
        c = P[(P.A == r.ticker) & P.B.isin(trade) & (P.n_all >= 14)].copy()
        cand = c.sort_values("corr_lo_all", ascending=False).head(6)   # rank by lower 95% bound of the correlation
        t = typ.get(r.ticker, np.nan)
        rows.append({"reporter": r.ticker, "name": name.get(r.ticker, r.ticker), "date_et": r.ts.tz_convert("America/New_York").strftime("%Y-%m-%d %H:%M"),
                     "typical_abs_ar_pct": t,
                     "movers": "; ".join(f"{b} β={x:.2f} ρ={rho:.2f} [lo {lo:.2f}, n={n:.0f}] (~{x * t:.1f}%)" for b, x, rho, lo, n in zip(cand.B, cand.beta_shrunk, cand.corr_all, cand.corr_lo_all, cand.n_all)),
                     "n_pairs_ok": int(len(c)),
                     "movers_short": " · ".join(f"{b} β{x:.2f} ρ{rho:.2f}" for b, x, rho in zip(cand.B[:5], cand.beta_shrunk[:5], cand.corr_all[:5])),
                     "ai_era_betas": "; ".join(f"{b} {x:.2f}" if pd.notna(x) else f"{b} n/a" for b, x in zip(cand.B, cand.beta_ai))})
    PB = pd.DataFrame(rows)
    PB.to_csv(os.path.join(OUT, "playbook.csv"), index=False)
    pd.set_option("display.width", 250)
    pd.set_option("display.max_colwidth", 120)
    print(PB[PB.reporter.isin(["NVDA", "MSFT", "GOOGL", "AMZN", "AMD", "AVGO", "ORCL", "MU", "VRT", "GEV", "ETN", "ANET", "SIE.DE",
                               "ENR.DE", "ASM.AS", "000660.KS", "005930.KS", "AMAT", "KLAC", "CRWV", "NBIS", "DELL", "MRVL"])].to_string(index=False))
    S = E[E.react_date >= "2026-10-01"].sort_values("react_date")[["ticker", "react_date", "ar", "av", "surprise_pct", "source"]]
    S["name"] = S.ticker.map(name)
    S.to_csv(os.path.join(OUT, "season_now.csv"), index=False)


if __name__ == "__main__":
    main()
