"""Assemble every result the report shows into reports/report_data.json (one JSON bundle)."""
import os
import sys
import glob
import json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd
from common import PROC, REPORTS, CONFIG, load_universe, load_edges

T = os.path.join(REPORTS, "tables")
SMALL_MULT_ORDERS = ["ABBN.SW", "SIE.DE", "ENR.DE", "VRT", "ASML.AS", "ASM.AS", "BESI.AS", "VACN.SW"]
NOTE_TICKERS = ["NVDA", "MSFT", "META", "AVGO", "TSM", "ASML.AS", "VRT", "SU.PA", "SIE.DE", "ENR.DE", "ABBN.SW", "GEV",
                "CRWV", "NBIS", "MU", "ANET", "RR.L", "PRY.MI", "BESI.AS", "SAP.DE"]


def rd(name, **kw):
    p = os.path.join(T, name)
    return pd.read_csv(p, **kw) if os.path.exists(p) else pd.DataFrame()


def clean(v, nd):
    if isinstance(v, (float, np.floating)):
        return None if not np.isfinite(v) else round(float(v), nd)
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (pd.Timestamp, pd.Period)):
        return str(v)[:10]
    return v


def rec(df, cols=None, nd=4):
    if df is None or not len(df):
        return []
    d = df[[c for c in cols if c in df.columns]] if cols else df
    return [{k: clean(v, nd) for k, v in r.items()} for r in d.to_dict("records")]


def main():
    uni = load_universe()
    edges = load_edges()
    E = pd.read_parquet(os.path.join(PROC, "events.parquet"))
    D = {"as_of": "2026-10-22"}
    # ---------------- inventory ----------------
    tr_files = glob.glob(os.path.join(PROC, "transcripts", "*", "*.txt"))
    n_ir = sum(len(pd.read_csv(f)) for f in glob.glob(os.path.join(PROC, "ir", "*_manifest.csv")))
    kd = os.path.join(PROC, "keynotes", "keynote_docs.csv")
    ke = os.path.join(PROC, "keynotes", "keynote_events.csv")
    km = os.path.join(PROC, "keynotes", "keynote_mentions.csv")
    S = pd.read_parquet(os.path.join(PROC, "spill.parquet"), columns=["event_id"])
    D["inventory"] = {
        "companies": int(len(uni)), "tradeable": int((uni.tradeable == "1").sum()), "signal_only": int((uni.tradeable != "1").sum()),
        "us": int((uni.region == "US").sum()), "eu": int((uni.region == "EU").sum()), "asia": int((uni.region == "ASIA").sum()),
        "events": int(len(E)), "event_companies": int(E.ticker.nunique()), "events_ai": int((E.react_date >= "2023-01-01").sum()),
        "events_edgar": int((E.source == "edgar_8k").sum()), "events_ir": int((E.source == "ir").sum()), "events_yahoo": int((E.source == "yahoo").sum()),
        "transcripts": len(tr_files), "transcript_companies": len({os.path.basename(os.path.dirname(f)) for f in tr_files}),
        "edgar_docs": len(glob.glob(os.path.join(PROC, "edgar_text", "*", "*.txt"))), "ir_docs": int(n_ir),
        "ir_companies": len(glob.glob(os.path.join(PROC, "ir", "*_kpis.csv"))),
        "keynote_docs": len(pd.read_csv(kd)) if os.path.exists(kd) else 0, "keynote_events": len(pd.read_csv(ke)) if os.path.exists(ke) else 0,
        "keynote_mentions": len(pd.read_csv(km)) if os.path.exists(km) else 0,
        "spill_rows": int(len(S)), "price_start": "2014-06-02", "price_end": "2026-10-22",
        "edges": int(len(edges)), "tsmc_months": len(pd.read_csv(os.path.join(PROC, "tsmc_monthly.csv"))),
    }
    # ---------------- universe / network ----------------
    D["universe"] = rec(uni[["ticker", "name", "region", "country", "layer", "cake_layer", "sublayer", "berlin_slide", "tradeable", "notes"]])
    D["edges"] = rec(edges[["src", "dst", "rel", "evidence", "confidence", "note"]])
    pc = os.path.join(CONFIG, "private_companies.csv")
    D["private"] = rec(pd.read_csv(pc).fillna("")) if os.path.exists(pc) else []
    # ---------------- sympathy ----------------
    for era in ["ai", "pre"]:
        D[f"heat_{era}"] = rec(rd(f"spill_contemp_layers_{era}.csv"))
    P = rd("pair_map.csv")
    if len(P):
        strong = P[(P.n_all >= 20)].sort_values("corr_lo_all", ascending=False).head(25)
        D["top_pairs"] = rec(strong[["A", "B", "rel", "n_all", "beta_all", "corr_all", "corr_lo_all", "beta_pre", "beta_ai", "n_ai"]])
        cross = P[(P.n_all >= 20) & (P.layerA != P.layerB)].sort_values("corr_lo_all", ascending=False).head(15)
        D["top_cross_layer_pairs"] = rec(cross[["A", "B", "layerA", "layerB", "rel", "n_all", "beta_all", "corr_all", "corr_lo_all", "beta_ai"]])
    D["h1"] = rec(rd("h1_oos.csv"))
    D["contemp_rel_ai"] = rec(rd("spill_contemp_rel_ai.csv"))
    D["contemp_rel_pre"] = rec(rd("spill_contemp_rel_pre.csv"))
    D["region_drift"] = rec(rd("region_drift.csv"))
    D["drift_rel_ai"] = rec(rd("spill_drift_rel_ai.csv"))
    D["drift_rel_pre"] = rec(rd("spill_drift_rel_pre.csv"))
    D["intraday"] = rec(rd("intraday_continuation.csv"))
    # ---------------- fundamentals ----------------
    Q = rd("quarterly_capex_revenue.csv")
    if len(Q):
        Q = Q.rename(columns={Q.columns[0]: "cq"})
        Y = rd("quarterly_capex_revenue_yoy.csv")
        Y = Y.rename(columns={Y.columns[0]: "cq"})
        cap = pd.DataFrame({"cq": Q.cq, "capex_bn": Q.hyper_capex / 1e9, "yoy": Y.hyper_capex})
        D["capex_q"] = rec(cap[cap.capex_bn.notna()])
    D["leadlag"] = rec(rd("capex_leadlag.csv"))
    D["leadlag_peaks"] = rec(rd("capex_leadlag_peaks_diff.csv"))
    D["nowcast"] = rec(rd("capex_nowcast.csv"))
    tm = os.path.join(PROC, "tsmc_monthly.csv")
    D["tsmc"] = rec(pd.read_csv(tm)[["month", "revenue_ntd_bn", "yoy_pct", "mom_pct", "release_date"]].tail(36))
    D["h5"] = rec(rd("h5_tsmc_monthly.csv"))
    D["capex_accel"] = rec(rd("capex_accel_layer_drift.csv"))
    # orders
    op = os.path.join(PROC, "orders_panel.parquet")
    if os.path.exists(op):
        O = pd.read_parquet(op)
        O["cq"] = O.cq.astype(str)
        D["orders_series"] = rec(O[O.ticker.isin(SMALL_MULT_ORDERS) & (O.cq >= "2021Q1")][["ticker", "cq", "orders_yoy", "btb"]])
    D["orders_own_lead"] = rec(rd("orders_own_lead.csv"))
    D["orders_chain_lead"] = rec(rd("orders_chain_lead.csv"))
    D["orders_price"] = rec(rd("orders_price_tests.csv"))
    eu = []
    for f in sorted(glob.glob(os.path.join(PROC, "ir", "*_kpis.csv"))):
        k = pd.read_csv(f)
        tk = os.path.basename(f).replace("_kpis.csv", "")
        k = k[k.fiscal_period.astype(str).str.contains(r"Q[1-4]$|H[12]$", regex=True)].copy()
        k["ticker"] = tk
        k = k.sort_values("release_date").tail(1)
        eu.append(k[[c for c in ["ticker", "fiscal_period", "release_date", "revenue_yoy_pct", "orders_yoy_pct", "book_to_bill", "ai_dc_notes"] if c in k.columns]])
    D["eu_latest"] = rec(pd.concat(eu, ignore_index=True)) if eu else []
    notes = {}
    for f in glob.glob(os.path.join(PROC, "ir", "*_notes.md")) + glob.glob(os.path.join(PROC, "us_notes", "*_notes.md")):
        tk = os.path.basename(f).replace("_notes.md", "")
        if tk in NOTE_TICKERS:
            txt = open(f, encoding="utf-8", errors="ignore").read()
            bullets = [l.strip() for l in txt.splitlines() if l.strip().startswith(("-", "*")) and any(ch.isdigit() for ch in l[:16])]
            cur = [l.strip() for l in txt.splitlines() if l.lower().startswith("current state")]
            notes[tk] = {"bullets": bullets[-8:], "current": cur[0] if cur else ""}
    D["notes"] = notes
    tf = os.path.join(PROC, "transcript_features.parquet")
    if os.path.exists(tf):
        F = pd.read_parquet(tf)
        F = F[F.pub_date >= "2018-01-01"].copy()
        dt = pd.to_datetime(F.pub_date)
        F["half"] = dt.dt.year.astype(str) + "H" + ((dt.dt.month > 6) + 1).astype(str)
        g = F.groupby("half")[["ai_per10k", "dc_per10k", "constraint_per10k", "digestion_per10k", "orders_per10k", "tone"]].mean()
        g["n"] = F.groupby("half").size()
        D["text_trends"] = rec(g.reset_index())
    cg = os.path.join(PROC, "us_notes", "hyperscaler_capex_guidance.csv")
    if os.path.exists(cg):
        G = pd.read_csv(cg)
        D["capex_guidance"] = rec(G[G[["low_bn", "high_bn", "point_bn"]].notna().any(axis=1)])
    sigs = [pd.read_csv(f) for f in glob.glob(os.path.join(PROC, "us_notes", "demand_signals_*.csv"))]
    if sigs:
        SG = pd.concat(sigs, ignore_index=True)
        SG["layer"] = SG.ticker.map(dict(zip(uni.ticker, uni.layer)))
        SG["q"] = pd.to_datetime(SG.call_date, errors="coerce").dt.to_period("Q").astype(str)
        SG["direction"] = pd.to_numeric(SG.direction, errors="coerce")
        SG = SG.dropna(subset=["direction", "layer"])
        D["signal_index"] = rec(SG.groupby(["q", "layer"]).direction.agg(["sum", "count"]).reset_index())
        D["signal_rows"] = int(len(SG))
    cc = os.path.join(PROC, "customer_concentration.csv")
    if os.path.exists(cc):
        C = pd.read_csv(cc)
        D["concentration"] = rec(C[C.pct.notna()].sort_values(["ticker", "filingDate"]).groupby("ticker").tail(1)[["ticker", "filingDate", "pct", "named", "sentence"]])
    # ---------------- backtests ----------------
    D["backtest_events"] = rec(rd("backtest_events.csv"))
    D["network_perf"] = rec(rd("network_model_perf.csv"))
    D["custmom_perf"] = rec(rd("customer_momentum_perf.csv"))
    D["cascade"] = rec(rd("cascade_regressions.csv"))
    D["keynote_effect"] = rec(rd("keynote_effect.csv"))
    cm = os.path.join(PROC, "customer_momentum_pnl.parquet")
    if os.path.exists(cm):
        pnl = pd.read_parquet(cm)
        keep = {"H20|signal | net-long | vs index (original)": "net_long_vs_index",
                "H20|signal | dollar-neutral | vs AI basket": "neutral_vs_ai",
                "H20|baseline: long all signalled names | vs index": "baseline_vs_index"}
        pnl = pnl[[c for c in keep if c in pnl.columns]].rename(columns=keep)
        pnl = pnl[pnl.index >= "2016-01-01"].fillna(0)
        eq = ((1 + pnl).cumprod() - 1) * 100
        wk = eq.resample("W-FRI").last()
        wk.index = wk.index.strftime("%Y-%m-%d")
        D["custmom_equity"] = rec(wk.reset_index().rename(columns={"index": "date"}), nd=2)
    # ---------------- now ----------------
    sn = rd("season_now.csv")
    if len(sn):
        sn["ar_pct"] = sn.ar * 100
        D["season_now"] = rec(sn[["ticker", "name", "react_date", "ar_pct", "av", "surprise_pct", "source"]])
    D["playbook"] = rec(rd("playbook.csv"))
    D["live_signals"] = rec(rd("live_signals.csv"))
    if os.path.exists(ke):
        D["keynote_events"] = rec(pd.read_csv(ke)[["event_slug", "event_name", "keynote_date", "n_docs"]])
    if os.path.exists(km):
        M = pd.read_csv(km)
        D["keynote_top_mentions"] = rec(M[M.ticker.notna()].groupby("ticker").size().sort_values(ascending=False).head(20).rename("mentions").reset_index())
    out = os.path.join(REPORTS, "report_data.json")
    with open(out, "w") as f:
        json.dump(D, f, default=str, separators=(",", ":"), allow_nan=False)
    print("wrote", out, os.path.getsize(out) // 1024, "KB; keys:", len(D))


if __name__ == "__main__":
    main()
