"""Orders pace: do order intake / book-to-bill / backlog lead revenue and prices along the chain?

Panel (quarterly, calendar quarter of period end):
  EU order reporters (IR KPIs): ABB, Siemens, Siemens Energy, ASML, ASM, BESI, VAT, Aixtron, Munters, Capgemini, DT (T-Systems)
  US: Vertiv orders growth (press releases), RPO YoY from XBRL as backlog proxy (GEV, PWR, ETN, HUBB, LRCX, KLAC, ...)
Tests (all on changes, d = quarter-on-quarter change of the YoY growth rate, to remove the common trend):
  A. own lead:     corr(d orders_yoy[t], d rev_yoy[t+k])                      pooled over companies
  B. chain lead:   composite d orders (semicap / electrification) -> d revenue of US groups at t+k
  C. prices:       reporter's orders acceleration -> (i) own release AR, (ii) peers' same-day AR beyond reporter AR,
                   (iii) peers' CAR[+1,+20] vs AI basket (drift), (iv) next same-season US release AR of the group
Outputs: data/processed/orders_panel.parquet, reports/tables/orders_*.csv
"""
import os
import re
import sys
import glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd
import statsmodels.api as sm
from common import PROC, REPORTS, load_universe

OUT = os.path.join(REPORTS, "tables")
GROUPS = {
    "semicap": {"orders": ["ASML.AS", "ASM.AS", "BESI.AS", "VACN.SW", "AIXA.DE"], "rev": ["AMAT", "LRCX", "KLAC", "TER"],
                "responders": ["AMAT", "LRCX", "KLAC", "TER", "ASML.AS", "ASM.AS", "BESI.AS", "VACN.SW", "AIXA.DE", "SMHN.DE"]},
    "electrification": {"orders": ["ABBN.SW", "SIE.DE", "ENR.DE", "MTRS.ST", "VRT"], "rev": ["VRT", "ETN", "HUBB", "NVT", "MOD", "PWR", "GEV"],
                        "responders": ["VRT", "ETN", "HUBB", "NVT", "MOD", "PWR", "GEV", "SU.PA", "LR.PA", "ABBN.SW", "SIE.DE", "ENR.DE",
                                       "PRY.MI", "NEX.PA", "NKT.CO", "MTRS.ST"]},
}


def eu_orders():
    rows = []
    for f in glob.glob(os.path.join(PROC, "ir", "*_kpis.csv")):
        tk = os.path.basename(f).replace("_kpis.csv", "")
        k = pd.read_csv(f)
        k = k[k.fiscal_period.astype(str).str.contains(r"Q[1-4]$", regex=True)]
        k = k[k.orders.notna() | k.orders_yoy_pct.notna()].copy()
        if k.empty:
            continue
        k["period_end"] = pd.to_datetime(k.period_end, errors="coerce")
        k["release_date"] = pd.to_datetime(k.release_date, errors="coerce")
        k = k.dropna(subset=["period_end"]).sort_values(["period_end", "release_date"]).drop_duplicates("period_end", keep="last")
        k["cq"] = k.period_end.dt.to_period("Q")
        k = k.set_index("cq")
        lvl = pd.to_numeric(k.orders, errors="coerce")
        yoy_calc = (lvl / lvl.shift(4) - 1) * 100
        # shift(4) is only valid if the index is contiguous quarters
        contiguous = (k.index.to_series().diff(4) == 4 * k.index.freq) if len(k) > 4 else pd.Series(False, index=k.index)
        yoy_calc = yoy_calc.where(contiguous.fillna(False).values)
        yoy = pd.to_numeric(k.orders_yoy_pct, errors="coerce").fillna(yoy_calc)
        rev = pd.to_numeric(k.revenue_yoy_pct, errors="coerce")
        for cq, r in k.iterrows():
            rows.append({"ticker": tk, "cq": cq, "release_date": r.release_date, "orders_yoy": yoy.get(cq),
                         "btb": pd.to_numeric(r.book_to_bill, errors="coerce"), "rev_yoy_ir": rev.get(cq), "src": "ir"})
    return pd.DataFrame(rows)


def us_orders():
    rows = []
    K = pd.read_csv(os.path.join(PROC, "press_release_kpis.csv"))
    v = K[K.ticker == "VRT"].copy()
    v["oy"] = v.organic_orders_pct.fillna(v.orders_growth_pct)
    E = pd.read_parquet(os.path.join(PROC, "events.parquet"))
    for r in v.itertuples():
        d = pd.Timestamp(r.date)
        cq = (d - pd.Timedelta(days=45)).to_period("Q")  # release ~3-6 weeks after quarter end
        rows.append({"ticker": "VRT", "cq": cq, "release_date": d, "orders_yoy": r.oy, "btb": r.book_to_bill, "src": "press_release"})
    return pd.DataFrame(rows)


def xbrl_panel():
    F = pd.read_parquet(os.path.join(PROC, "fundamentals_q.parquet"))
    rev = F[F.concept == "revenue"].copy()
    rev["cq"] = (rev.period_start + (rev.period_end - rev.period_start) / 2).dt.to_period("Q")
    R = rev.pivot_table(index="cq", columns="ticker", values="value", aggfunc="last")
    rpo = F[F.concept == "rpo"].copy()
    rpo["cq"] = rpo.period_end.dt.to_period("Q")
    B = rpo.pivot_table(index="cq", columns="ticker", values="value", aggfunc="last")
    full = pd.period_range("2014Q1", "2026Q3", freq="Q")
    R, B = R.reindex(full), B.reindex(full)
    return (R / R.shift(4) - 1) * 100, (B / B.shift(4) - 1) * 100


def corr_lead(x, y, ks=range(-1, 5), min_n=10):
    out = {}
    for k in ks:
        d = pd.concat([x, y.shift(-k)], axis=1).dropna()
        out[k] = (d.iloc[:, 0].corr(d.iloc[:, 1]) if len(d) >= min_n else np.nan, len(d))
    return out


def main():
    O = pd.concat([eu_orders(), us_orders()], ignore_index=True)
    O = O.sort_values(["ticker", "cq"]).drop_duplicates(["ticker", "cq"], keep="first")
    O["d_orders"] = O.groupby("ticker").orders_yoy.diff()
    O.to_parquet(os.path.join(PROC, "orders_panel.parquet"), index=False)
    print("orders panel:", O.groupby("ticker").agg(q=("cq", "count"), first=("cq", "min"), last=("cq", "max")).to_string())
    rev_yoy, rpo_yoy = xbrl_panel()
    dR = rev_yoy.diff()

    # ---- A. own lead (orders -> own revenue), pooled; revenue from IR file (EU) or XBRL (US)
    rows = []
    for tk, g in O.groupby("ticker"):
        g = g.set_index("cq")
        ry = g.rev_yoy_ir if tk not in rev_yoy.columns else rev_yoy[tk]
        ry = ry.reindex(pd.period_range(g.index.min(), "2026Q3", freq="Q"))
        oy = g.orders_yoy.reindex(ry.index)
        for k in range(0, 5):
            d = pd.concat([oy.diff(), ry.diff().shift(-k)], axis=1).dropna()
            for a, b in d.values:
                rows.append({"ticker": tk, "k": k, "d_orders": a, "d_rev_next": b})
    A = pd.DataFrame(rows)
    resA = []
    for k, d in A.groupby("k"):
        dd = d.copy()
        dd["z_o"] = dd.groupby("ticker").d_orders.transform(lambda s: (s - s.mean()) / s.std())
        dd["z_r"] = dd.groupby("ticker").d_rev_next.transform(lambda s: (s - s.mean()) / s.std())
        dd = dd.dropna()
        m = sm.OLS(dd.z_r, sm.add_constant(dd.z_o)).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(dd.ticker)[0]})
        resA.append({"lead_q": k, "n": len(dd), "companies": dd.ticker.nunique(), "corr_pooled": dd.z_o.corr(dd.z_r), "t": m.tvalues["z_o"]})
    RA = pd.DataFrame(resA)
    RA.to_csv(os.path.join(OUT, "orders_own_lead.csv"), index=False)
    print("\nA. own orders acceleration -> own revenue acceleration k quarters later (within-company z-scores):")
    print(RA.round(3).to_string(index=False))

    # ---- B. chain lead: group composite d(orders YoY) -> d(revenue YoY) of US group (and RPO for context)
    resB = []
    for gname, G in GROUPS.items():
        comp = O[O.ticker.isin(G["orders"])].pivot_table(index="cq", columns="ticker", values="orders_yoy").reindex(dR.index)
        # z-score each company's YoY to avoid one name dominating, then average
        z = (comp - comp.mean()) / comp.std()
        cidx = z.mean(axis=1, skipna=True).where(z.notna().sum(axis=1) >= 2)
        dcomp = cidx.diff()
        us_rev = rev_yoy[[c for c in G["rev"] if c in rev_yoy.columns]]
        us_z = ((us_rev - us_rev.mean()) / us_rev.std()).mean(axis=1, skipna=True)
        for k, (c, n) in corr_lead(dcomp, us_z.diff(), ks=range(-1, 5), min_n=8).items():
            resB.append({"group": gname, "lead_q": k, "corr_diff": c, "n": n, "measure": "d orders-index vs d US revenue (z)"})
        for k, (c, n) in corr_lead(cidx, us_z, ks=range(-1, 5), min_n=8).items():
            resB.append({"group": gname, "lead_q": k, "corr_diff": c, "n": n, "measure": "levels (common-trend caveat)"})
        for k, (c, n) in corr_lead(dcomp[dcomp.index >= pd.Period("2021Q1")], us_z.diff(), ks=range(0, 4), min_n=6).items():
            resB.append({"group": gname, "lead_q": k, "corr_diff": c, "n": n, "measure": "d, 2021Q1+"})
    RB = pd.DataFrame(resB)
    RB.to_csv(os.path.join(OUT, "orders_chain_lead.csv"), index=False)
    print("\nB. group orders index -> US group revenue growth:")
    print(RB.pivot_table(index=["group", "measure"], columns="lead_q", values="corr_diff").round(2).to_string())

    # ---- C. prices
    E = pd.read_parquet(os.path.join(PROC, "events.parquet"))
    S = pd.read_parquet(os.path.join(PROC, "spill.parquet"))
    abi = pd.read_parquet(os.path.join(PROC, "panel", "abret_ind.parquet"))
    # match each orders release to its event (reaction day within 0..4 days after release_date)
    O2 = O.dropna(subset=["release_date", "d_orders"]).copy()
    ev_rows = []
    for r in O2.itertuples():
        e = E[(E.ticker == r.ticker) & (E.react_date >= r.release_date - pd.Timedelta(days=1)) & (E.react_date <= r.release_date + pd.Timedelta(days=4))]
        if len(e):
            ev_rows.append({"event_id": e.event_id.iloc[0], "ticker": r.ticker, "react_date": e.react_date.iloc[0], "arA": e.ar.iloc[0],
                            "d_orders": r.d_orders, "orders_yoy": r.orders_yoy, "cq": r.cq})
    OE = pd.DataFrame(ev_rows)
    print("\norders releases matched to events:", len(OE), "of", len(O2))
    resC = []
    # (i) own release-day AR
    for era, d in [("all", OE), ("2023+", OE[OE.react_date >= "2023-01-01"])]:
        d = d.dropna(subset=["arA", "d_orders"])
        m = sm.OLS(d.arA * 100, sm.add_constant(d.d_orders.clip(-100, 100))).fit(cov_type="HC1")
        resC.append({"test": "(i) own release AR ~ d orders YoY", "era": era, "n": len(d), "b": m.params.iloc[1], "t": m.tvalues.iloc[1]})
    # (ii)/(iii) peers in the same group
    grp_of = {t: g for g, G in GROUPS.items() for t in G["orders"]}
    SS = S.merge(OE[["event_id", "d_orders"]], on="event_id")
    SS["grp"] = SS.A.map(grp_of)
    SS = SS[SS.grp.notna()]
    SS = SS[[b in GROUPS[g]["responders"] for b, g in zip(SS.B, SS.grp)]]
    SS = SS[~SS.own_near]
    # drift vs AI basket from abret_ind
    cs = {t: (abi[t].dropna().index, np.concatenate([[0.0], np.cumsum(abi[t].dropna().values)])) for t in abi.columns if abi[t].notna().any()}
    def car_ind(b, e, k=20):
        if b not in cs:
            return np.nan
        idx, c = cs[b]
        j = idx.searchsorted(e)
        return c[j + 1 + k] - c[j + 1] if (j < len(idx) and j + k + 1 < len(c)) else np.nan
    SS["car20_ind"] = [car_ind(b, e) for b, e in zip(SS.B, SS.entry_date)]
    for era, d in [("all", SS), ("2023+", SS[SS.t0A >= "2023-01-01"])]:
        d = d.dropna(subset=["ar0", "arA", "d_orders"]).copy()
        d["do"] = d.d_orders.clip(-100, 100)
        for y, lab in [("ar0", "(ii) peer same-day AR ~ d orders + reporter AR"), ("car20_ind", "(iii) peer CAR[+1,+20] vs AI basket ~ d orders + reporter AR")]:
            dd = d.dropna(subset=[y])
            dd = dd[~dd.own_in_30] if y == "car20_ind" else dd
            X = sm.add_constant(pd.DataFrame({"do": dd["do"], "arA": dd.arA * 100}))
            m = sm.OLS(dd[y] * 100, X).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(dd.t0A)[0]})
            resC.append({"test": lab, "era": era, "n": len(dd), "b": m.params["do"], "t": m.tvalues["do"],
                         "b_arA": m.params["arA"], "t_arA": m.tvalues["arA"]})
    # (iv) late reporters: US group members' own release AR ~ latest same-season group orders acceleration (released before)
    late = []
    for gname, G in GROUPS.items():
        src = OE[OE.ticker.isin(G["orders"])]
        for r in E[E.ticker.isin(G["rev"])].itertuples():
            prior = src[(src.react_date < r.react_date) & (src.react_date >= r.react_date - pd.Timedelta(days=45)) & (src.ticker != r.ticker)]
            if len(prior):
                late.append({"group": gname, "B": r.ticker, "date": r.react_date, "ar_own": r.ar * 100, "prior_d_orders": prior.d_orders.clip(-100, 100).mean(),
                             "prior_arA": prior.arA.mean() * 100, "n_prior": len(prior)})
    L = pd.DataFrame(late)
    for era, d in [("all", L), ("2023+", L[L.date >= "2023-01-01"])]:
        d = d.dropna()
        if len(d) < 15:
            continue
        X = sm.add_constant(d[["prior_d_orders", "prior_arA"]])
        m = sm.OLS(d.ar_own, X).fit(cov_type="HC1")
        resC.append({"test": "(iv) US group member release AR ~ prior same-season orders accel (+ their AR)", "era": era, "n": len(d),
                     "b": m.params["prior_d_orders"], "t": m.tvalues["prior_d_orders"], "b_arA": m.params["prior_arA"], "t_arA": m.tvalues["prior_arA"]})
    RC = pd.DataFrame(resC)
    RC.to_csv(os.path.join(OUT, "orders_price_tests.csv"), index=False)
    pd.set_option("display.width", 220)
    print("\nC. orders acceleration and prices (b per +1pp change in orders YoY; AR in %):")
    print(RC.round(4).to_string(index=False))
    OE.to_csv(os.path.join(OUT, "orders_events.csv"), index=False)


if __name__ == "__main__":
    main()
