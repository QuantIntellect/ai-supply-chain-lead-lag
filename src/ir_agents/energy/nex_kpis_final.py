"""Nexans KPI panel FY2022Q1 -> FY2026Q3. Values transcribed from the results press releases
(data/processed/ir_text/NEX.PA/<period>_press_release.txt); data-center sentences auto-extracted.
revenue = sales at STANDARD metal prices (Nexans' headline measure, stated in every release);
current-price sales (IFRS revenue) in extra_json.current_sales where stated."""
import sys, re, os
sys.path.insert(0, "/Users/sinamirzaei/Documents/aimapping/src/ir_agents/energy"); import irlib

T = "NEX.PA"
man = {r["fiscal_period"]: r for r in irlib.read_csv(f"data/processed/ir/{T}_manifest.csv") if r["doc_type"] == "press_release"}
BL = "PWR-Transmission (until 2024: Generation & Transmission) adjusted backlog at period end"
G = lambda e_lo, e_hi, f_lo, f_hi, fy: [
    {"metric": f"FY{fy} adjusted EBITDA", "low": e_lo, "high": e_hi, "unit": "EUR m"},
    {"metric": f"FY{fy} (normalized) free cash flow", "low": f_lo, "high": f_hi, "unit": "EUR m"}]
# period: (doc_period, period_end, revenue_std, rev_yoy, organic, extra, backlog_m, guidance_text, guidance_other)
D = {
 "FY2022Q1": ("FY2022Q1", "2022-03-31", 1623, None, 6.1, {"basis": "3M", "organic_ex_metallurgy_pct": 16.3}, 2400,
              "2022 guidance confirmed: EBITDA EUR 500-540m; normalized FCF EUR 150-200m", G(500, 540, 150, 200, 2022)),
 "FY2022H1": ("FY2022H1", "2022-06-30", 3401, None, 5.1, {"basis": "6M", "current_sales": 4342, "ebitda": 308, "margin_pct": 9.1}, 2200,
              "FY2022 guidance upgraded: EBITDA EUR 560-590m (from 500-540m); normalized FCF EUR 200-250m (from 150-200m)", G(560, 590, 200, 250, 2022)),
 "FY2022_9M": ("FY2022Q3", "2022-09-30", 5044, None, 6.7, {"basis": "9M", "q3_organic_growth_pct": 10.3, "electrification_organic_9m_pct": 16.2}, 2400,
              "FY2022 guidance upgraded: EBITDA EUR 580-600m (from 560-590m); normalized FCF EUR 225-275m (from 200-250m)", G(580, 600, 225, 275, 2022)),
 "FY2022": ("FY2022", "2022-12-31", 6745, None, 6.3, {"basis": "12M", "current_sales": 8369, "ebitda": 599, "margin_pct": 8.9, "electrification_organic_pct": 12.9}, 3500,
              "FY2023 guidance: EBITDA EUR 570-630m; normalized FCF EUR 150-250m", G(570, 630, 150, 250, 2023)),
 "FY2023Q1": ("FY2023Q1", "2023-03-31", 1674, None, 2.2, {"basis": "3M", "organic_ex_other_pct": 6.5}, 3200,
              "2023 guidance confirmed (set 2023-02-15: EBITDA EUR 570-630m; normalized FCF EUR 150-250m)", []),
 "FY2023H1": ("FY2023H1", "2023-06-30", 3322, None, -0.6, {"basis": "6M", "current_sales": 4009, "ebitda": 354, "margin_pct": 10.7,
              "backlog_note": "excludes EUR 1.4bn EuroAsia Interconnector just awarded"}, 5200,
              "FY2023 guidance upgraded: EBITDA EUR 610-650m (from 570-630m); normalized FCF EUR 220-300m (from 150-250m)", G(610, 650, 220, 300, 2023)),
 "FY2023_9M": ("FY2023Q3", "2023-09-30", 4921, None, -0.2, {"basis": "9M", "current_sales": 5904, "organic_ex_other_pct": 3.4, "q3_organic_growth_pct": 0.8,
              "gt_q3_organic_pct": 17.8}, 5200,
              "FY2023 guidance confirmed: EBITDA EUR 610-650m; normalized FCF EUR 220-300m", G(610, 650, 220, 300, 2023)),
 "FY2023": ("FY2023", "2023-12-31", 6512, None, -0.9, {"basis": "12M", "current_sales": 7790, "adj_ebitda": 665, "margin_pct": 10.2}, 6100,
              "FY2024 guidance: adj. EBITDA EUR 670-730m; normalized FCF EUR 200-300m", G(670, 730, 200, 300, 2024)),
 "FY2024Q1": ("FY2024Q1", "2024-03-31", 1692, None, 2.8, {"basis": "3M", "electrification_organic_pct": 6.7, "organic_ex_other_pct": 4.7}, 6700,
              "FY2024 guidance confirmed: adj. EBITDA EUR 670-730m; normalized FCF EUR 200-300m", G(670, 730, 200, 300, 2024)),
 "FY2024H1": ("FY2024H1", "2024-06-30", 3546, None, 6.1, {"basis": "6M", "current_sales": 4224, "adj_ebitda": 412, "margin_pct": 11.6,
              "q2_organic_growth_pct": 9.4, "electrification_organic_pct": 14.1}, 6700,
              "FY2024 guidance upgraded: adj. EBITDA EUR 750-800m (from 670-730m); normalized FCF EUR 275-375m (from 200-300m)", G(750, 800, 275, 375, 2024)),
 "FY2024_9M": ("FY2024Q3", "2024-09-30", 5226, None, 4.0, {"basis": "9M", "organic_ex_other_pct": 6.9, "electrification_q3_organic_pct": 7.9}, 6200,
              "FY2024 guidance (as updated July 2024) confirmed: adj. EBITDA EUR 750-800m; normalized FCF EUR 275-375m", G(750, 800, 275, 375, 2024)),
 "FY2024": ("FY2024", "2024-12-31", 7078, 8.7, 5.1, {"basis": "12M", "current_sales": 8546, "adj_ebitda": 804, "margin_pct": 11.4,
              "q4_organic_growth_pct": 8.3, "electrification_organic_pct": 13.0}, 7400,
              "FY2025 guidance: adj. EBITDA EUR 770-850m; FCF EUR 225-325m", G(770, 850, 225, 325, 2025)),
 "FY2025Q1": ("FY2025Q1", "2025-03-31", 1815.4, None, 4.1, {"basis": "3M", "electrification_organic_pct": 6.8}, 8100,
              "FY2025 guidance confirmed: adj. EBITDA EUR 770-850m; FCF EUR 225-325m (excluding future scope changes)", G(770, 850, 225, 325, 2025)),
 "FY2025H1": ("FY2025H1", "2025-06-30", 3765, None, 4.9, {"basis": "6M", "current_sales": 4696, "adj_ebitda": 441, "margin_pct": 11.7,
              "q2_organic_growth_pct": 5.7, "electrification_organic_pct": 7.8, "electrification_margin_pct": 13.7}, 7800,
              "FY2025 guidance upgraded: adj. EBITDA EUR 810-860m; FCF EUR 275-375m", G(810, 860, 275, 375, 2025)),
 "FY2025_9M": ("FY2025Q3", "2025-09-30", 5331, None, 5.8, {"basis": "9M", "q3_organic_growth_pct": 7.7, "electrification_organic_9m_pct": 9.4,
              "electrification_q3_organic_pct": 12.6}, 7900,
              "FY2025 guidance (as upgraded July 2025) confirmed: adj. EBITDA EUR 810-860m; FCF EUR 275-375m", G(810, 860, 275, 375, 2025)),
 "FY2025": ("FY2025", "2025-12-31", 6098, 10.1, 8.3, {"basis": "12M", "scope": "continuing operations (Industry & Solutions = AmerCable, Lynxeo, Autoelectric reclassified as discontinued; 2024 restated to 5,537)",
              "current_sales": 7810, "adj_ebitda": 728, "margin_pct": 11.9, "backlog_note": "includes EUR 1.2bn Great Sea Interconnector",
              "fy2025_guidance_rebased_2025_12_22": "adj. EBITDA EUR 710-760m; FCF EUR 275-375m (continuing ops)"}, 7700,
              "FY2026 guidance: adj. EBITDA EUR 730-810m; FCF EUR 210-310m", G(730, 810, 210, 310, 2026)),
 "FY2026Q1": ("FY2026Q1", "2026-03-31", 1496.8, 1.3, 0.1, {"basis": "3M", "electrification_organic_pct": 4.9,
              "segments": {"PWR-Transmission": {"organic_growth_pct": 8.8}, "PWR-Grid": {"organic_growth_pct": 5.7}, "PWR-Connect": {"organic_growth_pct": 2.5}},
              "backlog_note": "includes EUR 1.2bn Great Sea Interconnector (under rescheduling)"}, 7900,
              "FY2026 guidance confirmed: adj. EBITDA EUR 730-810m; FCF EUR 210-310m; H1 2026 expected softer than H2", G(730, 810, 210, 310, 2026)),
 "FY2026H1": ("FY2026H1", "2026-06-30", 3248.6, 5.0, 1.5, {"basis": "6M", "current_sales": 4736.0, "adj_ebitda": 387.7, "margin_pct": 11.9,
              "electrification_organic_pct": 4.5, "electrification_margin_pct": 13.2, "backlog_note": "includes EUR 1.2bn Great Sea Interconnector"}, 7700,
              "FY2026 guidance upgraded: adj. EBITDA EUR 770-840m (from 730-810m); FCF EUR 235-325m (from 210-310m)", G(770, 840, 235, 325, 2026)),
 "FY2026_9M": ("FY2026Q3", "2026-09-30", 4946.7, 10.1, 3.9, {"basis": "9M", "q3_organic_growth_pct": 9.0}, 7800,
              "FY2026 guidance (as upgraded July 2026) confirmed: adj. EBITDA EUR 770-840m; FCF EUR 235-325m; excludes Great Sea Interconnector execution in 2026", G(770, 840, 235, 325, 2026)),
}


def dc_notes(doc_fp):
    t = re.sub(r"\s+", " ", open(os.path.join(irlib.TEXT_IR, T, f"{doc_fp}_press_release.txt"), encoding="utf-8").read())
    out = []
    for m in re.finditer(r"data[ -]?cent(?:er|re)s?", t, re.I):
        a = max(t.rfind(". ", 0, m.start()) + 2, m.start() - 220)
        b = t.find(". ", m.end())
        b = min(b if b > 0 else m.end() + 200, m.end() + 200)
        s = t[a:b + 1].strip()
        if s not in out:
            out.append(s)
        if len(out) >= 2:
            break
    return " | ".join(out)[:600]


rows = []
for fp, (dfp, pe, rev, yoy, org, ex, bl, gtxt, gother) in D.items():
    ex = dict(ex)
    ex["organic_growth_pct"] = org
    ex["revenue_def"] = "sales at standard metal prices (EUR m)"
    if "ebitda" in ex or "adj_ebitda" in ex:
        ex["margin_def"] = "(adjusted) EBITDA as % of sales at standard metal prices"
    ex["backlog_def"] = BL
    if gother:
        ex["guidance_other"] = gother
    rows.append({"fiscal_period": fp, "period_end": pe, "release_date": man[dfp]["pub_date"], "currency": "EUR", "unit": "m",
                 "revenue": rev, "revenue_yoy_pct": yoy, "backlog": bl, "guidance_text": gtxt,
                 "ai_dc_notes": dc_notes(dfp), "extra_json": ex, "source_doc": man[dfp]["local_path"]})
irlib.write_kpis(T, rows)
