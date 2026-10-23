"""Responder-event panel: how every other stock moves around each company's earnings release.

For each reporter event (A, ts_utc) and each responder B != A:
  t0_B      first session of B's exchange closing after the release (cross-time-zone correct)
  ar0       B's market-model abnormal return on t0_B
  car_1_k   B's cumulative abnormal return over sessions t0+1 .. t0+k (drift; tradeable after A's reaction)
  gap0/id0  B's overnight gap and intraday (open->close) return on t0 minus benchmark's
Plus reporter info (AR_A on its own reaction day, EPS surprise), layers and the edge relation.

Output: data/processed/spill.parquet
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd
from common import PROC, load_universe, load_edges, market_benchmark
from events import Calendar

PANEL = os.path.join(PROC, "panel")
SAME_CO = [{"TSM", "2330.TW"}]
HORIZONS = [1, 2, 5, 10, 20, 40]


def main(start="2015-01-01"):
    ret = pd.read_parquet(os.path.join(PANEL, "ret.parquet"))
    ar = pd.read_parquet(os.path.join(PANEL, "abret.parquet"))
    on = pd.read_parquet(os.path.join(PANEL, "ret_overnight.parquet"))
    idr = pd.read_parquet(os.path.join(PANEL, "ret_intraday.parquet"))
    E = pd.read_parquet(os.path.join(PROC, "events.parquet"))
    E = E[E.react_date >= start].copy()
    uni = load_universe()
    layer = dict(zip(uni.ticker, uni.layer))
    region = dict(zip(uni.ticker, uni.region))
    tickers = [t for t in uni.ticker if t in ret.columns]
    cal = Calendar(ret[tickers])
    edges = load_edges()
    # supply-type edges only (partnerships / equity stakes are kept on the map, not as supply links)
    sup = edges[~edges.rel.isin(["partner", "investment"])]
    down = set(zip(sup.src, sup.dst))   # (supplier, customer)

    # per-ticker arrays on own trading days
    arr = {}
    for tk in tickers:
        d = cal.days[tk]
        a = ar[tk].reindex(d).fillna(0.0).values
        bm = market_benchmark(tk, region[tk])
        g = (on[tk].reindex(d) - on[bm].reindex(d).fillna(0)).values
        i = (idr[tk].reindex(d) - idr[bm].reindex(d).fillna(0)).values
        arr[tk] = (d, a, np.concatenate([[0.0], np.cumsum(a)]), g, i)
    own_dates = E.groupby("ticker").react_date.apply(lambda s: np.array(sorted(s.values), dtype="datetime64[ns]")).to_dict()

    rows = []
    for ev in E.itertuples():
        A = ev.ticker
        if A not in arr:
            continue
        # time at which A's own reaction-day abnormal return is fully known (close of A's reaction session)
        iA = cal.days[A].get_indexer([ev.react_date])[0]
        if iA < 0:
            continue
        T_A = cal.closes[A][iA]
        for B in tickers:
            if B == A or any({A, B} <= s for s in SAME_CO):
                continue
            d, a, cs, g, i = arr[B]
            t0, partial = cal.reaction_day(B, ev.ts_utc)
            if t0 is None:
                continue
            j = d.get_loc(t0)
            if j < 260:  # need history for beta
                continue
            # partial session (release during B's session): reaction spans t0..t0+1, drift starts after t0+1
            je = j + 1 if partial else j
            if je >= len(a):
                continue
            rec = {"event_id": ev.event_id, "A": A, "B": B, "t0A": ev.react_date, "t0B": t0, "partial": partial,
                   "arA": ev.ar, "surpA": ev.surprise_pct, "avA": ev.av, "ar0_raw": a[j], "ar0": cs[je + 1] - cs[j],
                   "gap0": g[j], "id0": i[j], "car_m5_m1": cs[j] - cs[max(0, j - 5)]}
            # tradeable drift starts at the first B close at/after T_A (no look-ahead across time zones)
            ie = je
            cB = cal.closes[B]
            if cB[ie] < T_A:
                ie = int(cB.searchsorted(T_A, side="left"))
            rec["entry_lag"] = ie - je
            rec["entry_date"] = d[ie] if ie < len(d) else pd.NaT
            for k in HORIZONS:
                rec[f"car_1_{k}"] = (cs[ie + 1 + k] - cs[ie + 1]) if ie + k < len(a) else np.nan
            # contamination: B's own earnings near t0 or inside drift window
            od = own_dates.get(B)
            if od is not None and len(od):
                t0n = np.datetime64(t0)
                diffs = (od - t0n).astype("timedelta64[D]").astype(int)
                rec["own_near"] = bool(np.any(np.abs(diffs) <= 1))
                rec["own_in_30"] = bool(np.any((diffs >= 1) & (diffs <= 30)))
            else:
                rec["own_near"] = rec["own_in_30"] = False
            rows.append(rec)
    S = pd.DataFrame(rows)
    S["layerA"] = S.A.map(layer)
    S["layerB"] = S.B.map(layer)
    S["regionA"] = S.A.map(region)
    S["regionB"] = S.B.map(region)
    S["rel"] = np.where([(a, b) in down for a, b in zip(S.A, S.B)], "A_supplies_B",
                np.where([(b, a) in down for a, b in zip(S.A, S.B)], "B_supplies_A",
                np.where(S.layerA == S.layerB, "same_layer", "other")))
    S.to_parquet(os.path.join(PROC, "spill.parquet"), index=False)
    print("spill rows", len(S), "events", S.event_id.nunique())
    print(S.rel.value_counts())


if __name__ == "__main__":
    main()
