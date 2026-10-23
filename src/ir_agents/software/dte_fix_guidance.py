"""Harmonisation fix for DTE.DE_kpis.csv: Q4-row FCF guidance had picked up prior-year actuals;
rebuild guidance_text as a concise statement from the numeric guidance fields."""
import os, sys, json, re
import pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
import fetch_util as fu

P = os.path.join(fu.PROC_IR, "DTE.DE_kpis.csv")
# FY group guidance verified sentence-by-sentence in each media information
# (data/processed/ir_text/DTE.DE/<period>_press_release*.txt): (ebitda_qual, ebitda_bn, fcf_qual, fcf_bn, flag)
G = {
 "2022Q1": ("more than", 36.6, "more than", 10.0, "raised"), "2022Q2": ("around", 37.0, "more than", 10.0, "raised"),
 "2022Q3": ("more than", 37.0, "", None, "raised"), "2022Q4": ("around", 40.8, "over", 16.0, "new"),
 "2023Q1": ("around", 40.9, "more than", 16.0, "raised"), "2023Q2": ("around", 41.0, "more than", 16.0, "raised"),
 "2023Q3": ("around", 41.1, "more than", 16.1, "raised"), "2023Q4": ("around", 42.9, "around", 18.9, "new"),
 "2024Q1": ("around", 42.9, "around", 18.9, "confirmed"), "2024Q2": ("around", 42.9, "around", 19.0, "raised (FCF)"),
 "2024Q3": ("around", 43.0, "around", 19.0, "raised (EBITDA)"), "2024Q4": ("around", 44.9, "around", 19.9, "new"),
 "2025Q1": ("around", 45.0, "around", 20.0, "raised"), "2025Q2": ("more than", 45.0, "over", 20.0, "raised"),
 "2025Q3": ("around", 45.3, "around", 20.1, "raised"), "2025Q4": ("around", 47.4, "around", 19.8, "new"),
 "2026Q1": ("around", 47.5, "more than", 19.8, "raised"), "2026Q2": ("around", 47.5, "around", 20.0, "raised (FCF)"),
}
k = pd.read_csv(P, dtype=str).fillna("")
for i, r in k.iterrows():
    ex = json.loads(r.extra_json) if r.extra_json else {}
    if r.fiscal_period not in G:
        continue
    eq, eb, fq, fb, flag = G[r.fiscal_period]
    for key in [x for x in ex if x.startswith("guidance_")]:
        ex.pop(key)
    ex.update({"guidance_adj_ebitda_al_eur_bn": eb, "guidance_adj_ebitda_al_qualifier": eq})
    if fb is not None:
        ex.update({"guidance_fcf_al_eur_bn": fb, "guidance_fcf_al_qualifier": fq})
    ex["guidance_note"] = "FY group guidance (EUR bn), verified against media information text"
    y = int(r.fiscal_period[:4]) + (1 if r.fiscal_period.endswith("Q4") else 0)
    parts = ["adj. EBITDA AL %s EUR %.1fbn" % (eq, eb)]
    if fb is not None:
        parts.append("FCF AL %s EUR %.1fbn" % (fq, fb))
    k.at[i, "guidance_text"] = "FY%d group guidance: %s [%s]" % (y, "; ".join(parts), flag)
    k.at[i, "extra_json"] = json.dumps(ex, ensure_ascii=False)
k.to_csv(P, index=False)
print(k[["fiscal_period", "guidance_text"]].to_string())
