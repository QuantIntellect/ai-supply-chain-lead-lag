"""VACN.SW KPI table (CHF million), one row per results publication 2022Q1..2026Q3.
Values transcribed from the KPI tables / headline bullets of VAT media releases (texts in data/processed/ir_text/VACN.SW).
Rows: Q1/Q3 trading updates, Q2/Q4 preliminary releases (when published), H1 and FY results.
H1/FY rows hold half-year / full-year totals; stand-alone Q2/Q4 figures from those releases are in extra_json.
book_to_bill: as stated; where not stated it is computed as orders/revenue and flagged in extra_json."""
import os
import sys
import json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import write_kpis

T = "VACN.SW"
TXT = "data/processed/ir_text/VACN.SW/"
PE = {"Q1": "-03-31", "Q2": "-06-30", "H1": "-06-30", "Q3": "-09-30", "Q4": "-12-31", "FY": "-12-31"}
DEF = "orders = order intake; revenue = net sales; backlog = order backlog at period end; all CHF m, reported FX"

# fp, release_date, doc, revenue, rev_yoy, orders, ord_yoy, b2b, b2b_computed, backlog, gm, guid_text, lo, hi, ai, extra
R = [
    ("2022Q1", "2022-04-14", "2022Q1_press_release", 263.0, 36.8, 294.2, 22.3, 1.1, False, 487.0, None,
     "Q2 2022 net sales CHF 260-280m (constant FX); FY2022 sales, EBITDA, net income substantially higher, EBITDA margin higher",
     260, 280,
     "Strong semi demand; capacity additions for logic/foundry and memory amid chip shortage; risk that COVID clusters in China hit Q2 shipments",
     {}),
    ("2022Q2", "2022-07-13", "2022Q2_prelim_release", 286, 28, 354, 40, 1.24, False, 559, None,
     "Preliminary; H2 2022 sales expected above H1 2022 (no numeric guidance)", None, None,
     "Record semi investment in leading and legacy platforms; Display orders weaker",
     {"preliminary": True, "h1_orders": 648, "h1_sales": 549, "h1_ebitda_margin_pct_approx": 35}),
    ("2022H1", "2022-08-04", "2022H1_press_release", 549.0, 31.8, 648.5, 31.2, 1.18, True, 559.4, 65,
     "Q3 2022 net sales CHF 290-310m (constant FX); FY2022 substantially higher sales, EBITDA, EBITDA margin, net income, FCF",
     290, 310,
     "Continued high capex in semis (leading and legacy nodes); record Semiconductor and Global Service sales",
     {"ebitda": 192.1, "ebitda_margin_pct": 35.0, "net_income": 147.6, "fcf": 78.6, "q2_orders": 354.3,
      "q2_orders_yoy_pct": 39.7, "q2_sales": 285.9, "q2_sales_yoy_pct": 27.6, "q2_book_to_bill": 1.24}),
    ("2022Q3", "2022-10-13", "2022Q3_press_release", 305.5, 33.2, 312.2, 4.5, 1.02, False, 563.0, None,
     "Q4 2022 net sales CHF 285-315m (constant FX, excl. impact of US China rules of 7 Oct 2022); FY2022 net sales CHF 1.14-1.17bn; FY EBITDA margin ~35%",
     285, 315,
     "Leading-edge logic demand high; memory capex peaked in H1 2022, softer ahead; US export rules on China (7 Oct 2022) unclear; moderation expected 2023",
     {"fy_sales_guidance_low": 1140, "fy_sales_guidance_high": 1170}),
    ("2022Q4", "2023-01-12", "2022Q4_prelim_release", 290, 14, 249, -43, 0.86, False, 518, None,
     "Preliminary; softening market and US-China restrictions expected to continue into 2023 (no numeric guidance)", None, None,
     "Global moderation of semi capex; US restrictions slowed deliveries of equipment to China by major OEM customers",
     {"preliminary": True, "fy_orders": 1210, "fy_sales": 1144, "fy_fcf_approx": 225}),
    ("2022FY", "2023-03-02", "2022FY_press_release", 1145.5, 27.1, 1209.9, -1.5, 1.06, True, 517.7, 64,
     "Q1 2023 sales CHF 210-230m (constant FX); 2023 lower sales, EBITDA, EBITDA margin, net income, FCF; capex CHF 80-85m",
     210, 230,
     "Leading-edge logic for data processing healthy; China export restrictions dampened demand; AI cited among long-term drivers; cyclical slowdown 2023, return to growth 2024",
     {"ebitda": 400.4, "ebitda_margin_pct": 35.0, "net_income": 306.8, "fcf": 228.2, "q4_orders": 249.2,
      "q4_orders_yoy_pct": -42.7, "q4_sales": 291.0, "q4_sales_yoy_pct": 13.9, "q4_book_to_bill": 0.86}),
    ("2023Q1", "2023-04-13", "2023Q1_press_release", 232.7, -11.5, 136.4, -53.6, 0.6, False, 416.4, None,
     "Q2 2023 net sales CHF 200-230m (constant FX); 2023 lower sales, EBITDA, margin, net income, FCF", 200, 230,
     "Cyclical semi downturn, inventory correction; escalating China trade restrictions; leading-edge logic for data processing healthy",
     {}),
    ("2023Q2", "2023-07-13", "2023Q2_prelim_release", 221, -23, 155, -56, 0.7, False, 340, None,
     "Preliminary; no numeric guidance", None, None,
     "Weak consumer-exposed memory demand (smartphones, PCs); persisting China trade restrictions",
     {"preliminary": True, "h1_orders": 292, "h1_sales": 454}),
    ("2023H1", "2023-07-27", "2023H1_press_release", 453.8, -17.3, 291.7, -55.0, 0.64, True, 339.7, 62,
     "Q3 2023 sales CHF 190-220m; FY2023 lower sales/EBITDA/NI/FCF; EBITDA margin slightly below 32-37% target band",
     190, 220,
     "Market might have bottomed (Q2 orders +14% QoQ); China restrictions hit domestic high-end and non-domestic fab investment",
     {"ebitda": 132.4, "ebitda_margin_pct": 29.2, "net_income": 84.2, "fcf": 36.9, "q2_orders": 155.2,
      "q2_orders_yoy_pct": -56.2, "q2_sales": 221.0, "q2_sales_yoy_pct": -22.7, "q2_book_to_bill": 0.7}),
    ("2023Q3", "2023-10-12", "2023Q3_press_release", 209.8, -31.3, 163.7, -47.6, 0.78, False, 282.1, None,
     "Q4 2023 sales CHF 200-230m (constant FX); H2 EBITDA margin above H1 but slightly below 32-37% range", 200, 230,
     "Market bottom reached; lagging-edge investment in China healthy but concern about expanded restrictions; preparing for leading-edge transitions in 2024",
     {}),
    ("2023Q4", "2024-01-11", "2023Q4_prelim_release", 221, -24, 237, -5, 1.1, False, 292, None,
     "Preliminary; no numeric guidance", None, None,
     "Stabilizing semi demand; significant project wins in Advanced Industrials",
     {"preliminary": True, "fy_orders": 692, "fy_sales": 885}),
    ("2023FY", "2024-03-05", "2023FY_press_release", 885.3, -22.7, 691.9, -42.8, 0.78, True, 291.6, 62,
     "Q1 2024 sales CHF 185-205m (constant FX); 2024 higher sales, EBITDA, margin, NI, FCF; capex CHF 70-80m", 185, 205,
     "2023: NAND capex down ~1/3, DRAM -16%, logic ~flat; China invested heavily in lagging edge; AI a long-term driver; 2024 renewed growth expected",
     {"ebitda": 270.9, "ebitda_margin_pct": 30.6, "net_income": 190.3, "fcf": 188.8, "q4_orders": 236.5,
      "q4_orders_yoy_pct": -5.1, "q4_sales": 221.8, "q4_sales_yoy_pct": -23.8, "q4_book_to_bill": 1.1}),
    ("2024Q1", "2024-04-11", "2024Q1_press_release", 198.5, -14.7, 235.8, 72.8, 1.2, False, 323.9, None,
     "Q2 2024 sales CHF 235-255m; market development for 2024 and into 2025 confirmed", 235, 255,
     "Orders +73% YoY on recovering semi capex and strong demand from Chinese customers (subsidies/regionalization); memory recovery and leading-edge inflection",
     {}),
    ("2024H1", "2024-07-18", "2024H1_press_release", 449.6, -0.9, 506.7, 73.7, 1.13, True, 345.6, 66.4,
     "Q3 2024 sales CHF 235-255m incl. lower output from ERP ramp-up; FY2024 higher sales, EBITDA, margin, NI, FCF", 235, 255,
     "Semi equipment orders driven by AI-related demand, mostly DRAM and logic; China strong (regionalization); consumer electronics weak",
     {"ebitda": 135.3, "ebitda_margin_pct": 30.1, "net_income": 94.0, "fcf": 26.3, "q2_orders": 270.9,
      "q2_orders_yoy_pct": 74.5, "q2_sales": 251.1, "q2_sales_yoy_pct": 13.6, "q2_book_to_bill": 1.1}),
    ("2024Q3", "2024-10-17", "2024Q3_press_release", 209.4, -0.2, 259.1, 58.3, 1.2, False, 388.7, None,
     "Q4 2024 sales CHF 270-300m (constant FX) incl. recovery of Q3 ERP shortfall; FY2024 higher sales, EBITDA, margin, NI; FCF ~2023 level",
     270, 300,
     "Leading-edge build-out for HBM and high-end logic; memory growth led by DRAM, NAND later in 2025; ERP issue cut Q3 sales by ~CHF 22m (pre-warned 8 Oct 2024)",
     {"pre_announcement": "2024-10-08: Q3 sales below low end of CHF 235-255m guidance (ERP), CHF 20-25m shift to Q4"}),
    ("2024Q4", "2025-01-09", "2024Q4_prelim_release", 283, 28, 268, 13, 0.95, False, 370, None,
     "Preliminary; no numeric guidance", None, None,
     "Recovery in semiconductor markets continues; Q4 includes CHF 22m sales carried over from Q3 (ERP)",
     {"preliminary": True, "fy_orders": 1034, "fy_sales": 942, "book_to_bill_adj_for_carryover": 1.03}),
    ("2024FY", "2025-03-04", "2024FY_press_release", 942.2, 6.4, 1033.3, 49.3, 1.10, True, 370.3, 66,
     "Q1 2025 sales CHF 275-295m; 2025 higher orders, sales, EBITDA, margin, NI, FCF", 275, 295,
     "2025 growth from 2nm, GAA and ALD transitions; Chinese OEM demand to stay high; AI computing not yet driving broad data-center upgrades; DRAM/NAND capacity underutilized",
     {"ebitda": 293.7, "ebitda_margin_pct": 31.2, "net_income": 211.8, "fcf": 183.2, "q4_orders": 267.5,
      "q4_orders_yoy_pct": 13.1, "q4_sales": 283.2, "q4_sales_yoy_pct": 27.7, "q4_book_to_bill": 0.94,
      "q4_book_to_bill_adj": 1.02}),
    ("2025Q1", "2025-04-17", "2025Q1_press_release", 275.1, 38.6, 241.7, 2.5, 0.88, True, 339.1, None,
     "Q2 2025 sales CHF 260-290m; 2025 higher orders, sales, EBITDA, margin, NI, FCF; capex CHF 90-100m; tariff impact non-material",
     260, 290,
     "Hyperscaler 2025 capex >USD 300bn supportive for AI; orders volatile on geopolitics/tariffs; Chinese OEM demand high (self-sufficiency)",
     {}),
    ("2025H1", "2025-07-23", "2025H1_press_release", 558.0, 24.1, 489.4, -3.4, 0.88, True, 293.8, 65,
     "Q3 2025 sales CHF 255-285m; 2025 higher orders, sales, EBITDA, margin, NI, FCF", 255, 285,
     "Hyperscaler AI-infrastructure commitments; uncertainty on timing of 2nm/GAA high-volume manufacturing; Chinese orders strong",
     {"ebitda": 165.0, "ebitda_margin_pct": 29.6, "net_income": 105.6, "fcf": 50.7, "q2_orders": 247.7,
      "q2_orders_yoy_pct": -8.6, "q2_sales": 282.9, "q2_sales_yoy_pct": 12.7, "q2_book_to_bill": 0.9,
      "q2_orders_yoy_pct_cfx": -1.1}),
    ("2025Q3", "2025-10-16", "2025Q3_press_release", 257.9, 23.2, 238.1, -8.1, 0.92, False, 258.8, None,
     "Q4 2025 sales CHF 225-245m; 2025 higher sales, EBITDA, NI, FCF; capex CHF 70-80m", 225, 245,
     "Good demand for HBM and GAA masked by weak mature nodes and memory upgrades that do not need VAT; leading-node utilization >90%; capex acceleration expected H2 2026; China cycle seen sustained",
     {}),
    ("2025Q4", "2026-01-15", "2025Q4_prelim_release", 257, -9, 305, 14, 1.2, False, 304, None,
     "Preliminary; 2026 outlook deferred to FY release", None, None,
     "Q4 orders on technology transitions fueled by AI demand; China strong; HBM/DRAM capacity seen full for 2026; incl. CHF 30-35m pre-orders ahead of 1 Jan 2026 price increase",
     {"preliminary": True, "fy_orders": 1033, "fy_sales": 1073, "book_to_bill_adj_for_preorders": 1.1}),
    ("2025FY", "2026-03-03", "2025FY_press_release", 1073.5, 13.9, 1033.0, 0.0, 0.96, True, 304.3, 64,
     "Q1 2026 sales CHF 240-260m, book-to-bill substantially above 1; 2026 higher orders, sales, EBITDA, margin, NI, FCF; WFE ~USD 130bn",
     240, 260,
     "Order pick-up late 2025 as markets invest for AI-driven demand; leading-edge build-out; direct China business growing; 'readiness for AI-led semiconductor ramp'",
     {"ebitda": 321.6, "ebitda_margin_pct": 30.0, "net_income": 214.3, "fcf": 230.4, "q4_orders": 305.5,
      "q4_orders_yoy_pct": 14.2, "q4_sales": 257.7, "q4_sales_yoy_pct": -9.0, "q4_book_to_bill": 1.2,
      "orders_yoy_pct_cfx": 5.5}),
    ("2026Q1", "2026-04-16", "2026Q1_press_release", 220.9, -19.7, 356.3, 47.4, 1.6, False, 431.3, None,
     "Q2 2026 sales CHF 265-295m, book-to-bill above 1; 2026 outlook confirmed", 265, 295,
     "Hyperscaler 2026 capex est. >USD 750bn; unprecedented demand for leading-edge logic and memory tools (Semis orders +65% YoY); Middle East conflict delayed revenue recognition",
     {"pre_announcement": "2026-03-31: Q1 sales ~CHF 215m vs guidance CHF 240-260m; B2B ~1.6x (Middle East conflict supply-chain disruption)"}),
    ("2026H1", "2026-07-22", "2026H1_press_release", 511.9, -8.3, 856.4, 75.0, 1.67, True, 647.9, 66.6,
     "Q3 2026 sales CHF 355-385m (excl. Atonarp); 2026 higher orders, sales, EBITDA, margin, NI, FCF; quarterly output >CHF 450m run-rate by YE; 2027 guidance under review",
     355, 385,
     "Record Q2 orders CHF 500m driven by high-performance logic and DRAM for AI data centers; Chinese OEM demand edging higher; 2026 WFE ~USD 145bn (+23%)",
     {"ebitda": 148.2, "ebitda_margin_pct": 29.0, "net_income": 98.8, "fcf": 41.8, "q2_orders": 500.0,
      "q2_orders_yoy_pct": 101.9, "q2_sales": 291.0, "q2_sales_yoy_pct": 2.9, "q2_book_to_bill": 1.7}),
    ("2026Q3", "2026-10-15", "2026Q3_press_release", 376.4, 45.9, 696.6, 192.6, 1.9, False, 979.5, None,
     "Q4 2026 sales CHF 420-450m, book-to-bill above 1; 2027 sales significantly above top end of previous CHF 1.5-1.7bn guidance",
     420, 450,
     "Record orders (x3 YoY) on exceptional hyperscaler data-center capex and onset of GAA high-volume production; ordering windows up to 9+ months vs 3 at end-2025; no double bookings anticipated; China strong",
     {"orders_9m": 1553.0, "sales_9m": 888.3}),
]


def main():
    rows = []
    for (fp, rd, doc, rev, ryoy, orders, oyoy, b2b, b2bc, bl, gm, gt, lo, hi, ai, extra) in R:
        ex = {"definitions": DEF}
        if b2bc:
            ex["book_to_bill_computed"] = True
        ex.update(extra)
        rows.append({"ticker": T, "fiscal_period": fp, "period_end": fp[:4] + PE[fp[4:]], "release_date": rd,
                     "currency": "CHF", "unit": "million", "revenue": rev, "revenue_yoy_pct": ryoy, "orders": orders,
                     "orders_yoy_pct": oyoy, "book_to_bill": b2b, "backlog": bl, "gross_margin_pct": gm,
                     "guidance_text": gt, "guidance_rev_low": lo, "guidance_rev_high": hi, "ai_dc_notes": ai,
                     "extra_json": json.dumps(ex), "source_doc": TXT + doc + ".txt"})
    df = write_kpis(T, rows)
    # chronological order (irlib sorts lexically by fiscal_period)
    df = df.sort_values(["release_date", "fiscal_period"])
    df.to_csv(os.path.join("/Users/sinamirzaei/Documents/aimapping/data/processed/ir", f"{T}_kpis.csv"), index=False)
    print(len(df), "rows", df.fiscal_period.min(), df.fiscal_period.max())


if __name__ == "__main__":
    main()
