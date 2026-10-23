"""Build data/processed/ir/AIXA.DE_kpis.csv. Numbers parsed from the 'Key financials' table of each results press release
(aixa_kpi_parse.parse); guidance/commentary transcribed from the same releases (see grep snippets in session)."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import irlib
import pandas as pd
from aixa_kpi_parse import parse

T = "AIXA.DE"
TXT = irlib.text_dir(T)
PE = {1: "03-31", 2: "06-30", 3: "09-30", 4: "12-31"}
# period: (guidance_text, fy_low, fy_high, fy_basis, extra guidance fields)
G = {
 "2022Q1": ("FY2022: order intake EUR 520-580m; revenues EUR 450-500m; gross margin ~41%; EBIT margin ~21-23%", 450, 500, "FY2022", {"fy_orders_low": 520, "fy_orders_high": 580, "fy_gm_pct": "~41", "fy_ebit_margin_pct": "21-23"}),
 "2022Q2": ("FY2022 confirmed: order intake EUR 520-580m; revenues EUR 450-500m; gross margin ~41%; EBIT margin ~21-23%", 450, 500, "FY2022", {"fy_orders_low": 520, "fy_orders_high": 580}),
 "2022Q3": ("FY2022 raised: order intake EUR 540-600m (prev. 520-580m); revenues unchanged EUR 450-500m; gross margin ~42% (prev. ~41%); EBIT margin ~22-24% (prev. 21-23%); exceptionally high Q4 shipments expected", 450, 500, "FY2022", {"fy_orders_low": 540, "fy_orders_high": 600, "fy_gm_pct": "~42", "fy_ebit_margin_pct": "22-24"}),
 "2022Q4": ("FY2023: order intake EUR 600-680m; revenues EUR 580-640m; gross margin ~45%; EBIT margin ~25-27% (budget FX 1.15 USD/EUR)", 580, 640, "FY2023", {"fy_orders_low": 600, "fy_orders_high": 680, "fy_gm_pct": "~45", "fy_ebit_margin_pct": "25-27"}),
 "2023Q1": ("FY2023 confirmed: order intake EUR 600-680m; revenues EUR 580-640m; gross margin ~45%; EBIT margin ~25-27%", 580, 640, "FY2023", {"fy_orders_low": 600, "fy_orders_high": 680}),
 "2023Q2": ("FY2023 raised: order intake EUR 620-700m (prev. 600-680m); revenues EUR 600-660m (prev. 580-640m); gross margin ~45%; EBIT margin ~25-27%", 600, 660, "FY2023", {"fy_orders_low": 620, "fy_orders_high": 700, "fy_gm_pct": "~45", "fy_ebit_margin_pct": "25-27"}),
 "2023Q3": ("FY2023 confirmed: order intake EUR 620-700m; revenues EUR 600-660m; gross margin ~45%; EBIT margin ~25-27%", 600, 660, "FY2023", {"fy_orders_low": 620, "fy_orders_high": 700}),
 "2023Q4": ("FY2024: revenues EUR 630-720m; gross margin ~43-45%; EBIT margin ~24-26% (FX 1.15 USD/EUR); Q1/2024 revenues EUR 100-120m; no order-intake guidance", 630, 720, "FY2024", {"nq_rev_low": 100, "nq_rev_high": 120, "fy_gm_pct": "43-45", "fy_ebit_margin_pct": "24-26"}),
 "2024Q1": ("FY2024 confirmed: revenues EUR 630-720m; gross margin ~43-45%; EBIT margin ~24-26%; Q2/2024 revenues EUR 120-140m", 630, 720, "FY2024", {"nq_rev_low": 120, "nq_rev_high": 140}),
 "2024Q2": ("FY2024 cut (ad hoc 2024-07-04, confirmed 2024-07-25): revenues EUR 620-660m (prev. 630-720m); gross margin ~43-45% (unch.); EBIT margin ~22-25% (prev. 24-26%); Q3/2024 revenues EUR 150-180m", 620, 660, "FY2024", {"nq_rev_low": 150, "nq_rev_high": 180, "fy_ebit_margin_pct": "22-25"}),
 "2024Q3": ("FY2024 confirmed: revenues EUR 620-660m; gross margin ~43-45%; EBIT margin ~22-25%; Q4/2024 revenues ~EUR 215-255m", 620, 660, "FY2024", {"nq_rev_low": 215, "nq_rev_high": 255}),
 "2024Q4": ("FY2025: revenues EUR 530-600m; gross margin ~41-42%; EBIT margin ~18-22% (FX 1.10 USD/EUR); Q1/2025 revenues EUR 90-110m", 530, 600, "FY2025", {"nq_rev_low": 90, "nq_rev_high": 110, "fy_gm_pct": "41-42", "fy_ebit_margin_pct": "18-22"}),
 "2025Q1": ("FY2025 confirmed: revenues EUR 530-600m; gross margin ~41-42%; EBIT margin ~18-22%; Q2/2025 revenues ~EUR 120-140m", 530, 600, "FY2025", {"nq_rev_low": 120, "nq_rev_high": 140}),
 "2025Q2": ("FY2025 confirmed: revenues EUR 530-600m; gross margin ~41-42%; EBIT margin ~18-22%; Q3/2025 revenues EUR 110-140m", 530, 600, "FY2025", {"nq_rev_low": 110, "nq_rev_high": 140}),
 "2025Q3": ("FY2025 cut (ad hoc 2025-10-17): revenues EUR 530-565m (prev. 530-600m); gross margin ~40-41% (prev. 41-42%); EBIT margin ~17-19% (prev. 18-22%); FX 1.15 USD/EUR; no explicit Q4 range found", 530, 565, "FY2025", {"fy_gm_pct": "40-41", "fy_ebit_margin_pct": "17-19"}),
 "2025Q4": ("FY2026: revenues ~EUR 520m +/-30m; gross margin ~41-42%; EBIT margin ~16-19% (FX 1.20 USD/EUR); Q1/2026 revenues ~EUR 65m +/-10m", 490, 550, "FY2026", {"nq_rev_low": 55, "nq_rev_high": 75, "fy_gm_pct": "41-42", "fy_ebit_margin_pct": "16-19"}),
 "2026Q1": ("FY2026 raised (ad hoc 2026-04-14): revenues ~EUR 560m +/-30m (prev. 520m +/-30m); gross margin ~42% (prev. 41-42%); EBIT margin 17-20% (prev. 16-19%); Q2/2026 revenues EUR 110m +/-10m", 530, 590, "FY2026", {"nq_rev_low": 100, "nq_rev_high": 120, "fy_gm_pct": "~42", "fy_ebit_margin_pct": "17-20"}),
 "2026Q2": ("Raised FY2026 guidance confirmed (revenues ~EUR 560m +/-30m); Q3/2026 revenues EUR 180m +/-20m", 530, 590, "FY2026", {"nq_rev_low": 160, "nq_rev_high": 200}),
 "2026Q3": ("Preliminary (ad hoc 2026-10-15): FY2026 guidance unchanged (revenues ~EUR 560m +/-30m); Q3 revenue ~EUR 184m within Q3 guide EUR 180m +/-20m; full Q3 statement scheduled 2026-10-29", 530, 590, "FY2026", {}),
}
N = {
 "2022Q1": "GaN power main revenue driver, then datacom lasers, Micro LED and LED; strongest order demand GaN then SiC power; high demand for optical datacom lasers and Micro LED.",
 "2022Q2": "Highest order intake since 2011; first volume order for Micro LED; strongest demand Micro LED tools then SiC/GaN power; strong optical datacom contribution.",
 "2022Q3": "New G10-SiC already largest order driver; unabated GaN/SiC power, laser (optical data transmission, 3D sensing) and Micro LED demand.",
 "2022Q4": "FY22 revenue mix: GaN/SiC power 42%, optoelectronics 28%, LED incl. Micro LED 27%; G10-AsP (opto/Micro LED) introduced.",
 "2023Q1": "GaN/SiC power growth accelerating; several large customers chose AIXTRON for GaN/SiC high-volume fabs.",
 "2023Q2": "SiC/GaN power by far largest share of orders; customers building HVM SiC/GaN capacity; FY23 guidance raised.",
 "2023Q3": "SiC+GaN systems 82% of Q3 equipment revenue; G10 family (SiC, GaN, AsP) complete.",
 "2023Q4": "Record Q4 deliveries; GaN/SiC power dominant; optoelectronics 12% of FY23 revenue.",
 "2024Q1": "Micro LED 37% of equipment orders; new top-5 SiC customer, a major order from China and several Japanese customers; datacom-laser demand stable.",
 "2024Q2": "SiC 57% / GaN 29% of equipment orders (follow-up orders from existing customers); FY24 revenue guidance cut on 2024-07-04 (weaker market).",
 "2024Q3": "Delivery of a major project pushed from Q3 to Q4 at customer request; moderate 2025 demand expected; long-term drivers: power electronics for IT/AI, SiC for e-mobility, Micro LED.",
 "2024Q4": "FY24: SiC/GaN 55% of system revenue (2023: 74%), LED incl. Micro LED 28%, opto 12%; AI cited as driver for GaN/SiC power and for optical datacom (positive opto momentum expected).",
 "2025Q1": "GaN/SiC power demand primarily from Asian customers; first 300mm GaN wafer processed in new Innovation Center.",
 "2025Q2": "Opto momentum from datacom lasers for AI data centers; G10-AsP 'tool of record' in lasers; large G10-SiC volume order from China received and shipped in H1/25; SiC/GaN not yet at turning point.",
 "2025Q3": "AI data-center build-out drives opto tool demand; datacom-laser pick-up confirmed, expected to continue into 2026; GaN power utilisation rising on data-center demand; FY25 guidance cut (volume shifts, FX).",
 "2025Q4": "FY25 equipment revenue: SiC/GaN 57%, opto 23%, LED/Micro LED 15%; opto recovery on AI laser/photonics demand; SiC/GaN subdued in West, China (Asia) stabilising.",
 "2026Q1": "Orders +30% yoy on very strong optoelectronics demand (inflection); FY26 guidance raised; major system shipments from Q2/26.",
 "2026Q2": "Orders +81% yoy (H1 +54%) on very strong opto/laser demand (e.g. multiple G10-AsP orders from Lumentum for AI optical networks, 2026-05-19); major laser shipments from Q3/26 continuing beyond 2026; Malaysia plant; EUR 450m convertible (Apr-26).",
 "2026Q3": "Preliminary: order intake ~EUR 275m (Q3/25: 124.0m), GM ~48%, EBIT ~EUR 57m (~31% margin), well above market expectations.",
}
DEF = {"orders_def": "order intake incl. spares & service (EUR m)", "backlog_def": "equipment order backlog only (excl. spares & service), period end",
       "fiscal_year": "calendar"}


def main():
    ev = pd.read_csv(os.path.join(irlib.PROC_IR, f"{T}_events.csv"), dtype=str).fillna("")
    rel = ev[ev.event_type.isin(["Q1", "Q2", "Q3", "Q4"])].set_index("fiscal_period").event_date.to_dict()
    rows = []
    for p in sorted(G):
        y, q = int(p[:4]), int(p[5])
        g = G[p]
        ex = dict(DEF)
        ex.update({"guidance_rev_basis": g[3]}); ex.update(g[4])
        r = {"ticker": T, "fiscal_period": p, "period_end": f"{y}-{PE[q]}", "currency": "EUR", "unit": "million",
             "guidance_text": g[0], "guidance_rev_low": g[1], "guidance_rev_high": g[2], "ai_dc_notes": N[p]}
        pr = os.path.join(TXT, f"{p}_press_release.txt")
        if os.path.exists(pr):
            v = parse(pr, q)
            r.update({"release_date": rel.get(p, ""), "revenue": v.get("revenue"), "orders": v.get("orders"),
                      "backlog": v.get("backlog"), "gross_margin_pct": v.get("gm"), "source_doc": pr})
            for k in ["revenue", "orders"]:
                if v.get(k) and v.get(k + "_py"):
                    r[k + "_yoy_pct"] = round((v[k] / v[k + "_py"] - 1) * 100, 1)
            ex.update({"revenue_py": v.get("revenue_py"), "orders_py": v.get("orders_py"), "backlog_py": v.get("backlog_py"),
                       "gross_profit": v.get("gross_profit"), "gross_margin_stated_rounded": True})
            if v.get("gross_profit") and v.get("revenue"):
                ex["gross_margin_calc_pct"] = round(v["gross_profit"] / v["revenue"] * 100, 1)
            if v.get("orders") and v.get("revenue"):
                ex["book_to_bill_calc"] = round(v["orders"] / v["revenue"], 2)
        elif p == "2026Q3":  # only the preliminary ad hoc so far (final statement due 2026-10-29)
            r.update({"release_date": "2026-10-15", "revenue": 184, "orders": 275, "gross_margin_pct": 48,
                      "revenue_yoy_pct": round((184 / 119.6 - 1) * 100, 1), "orders_yoy_pct": round((275 / 124.0 - 1) * 100, 1),
                      "source_doc": os.path.join(TXT, "2026Q3_adhoc_press_release.txt")})
            ex.update({"preliminary": True, "approximate_values": True, "gross_profit": 87, "ebit": 57,
                       "revenue_py": 119.6, "orders_py": 124.0})
        r["extra_json"] = ex
        rows.append(r)
    df = irlib.write_kpis(T, rows)
    print(df[["fiscal_period", "release_date", "revenue", "revenue_yoy_pct", "orders", "orders_yoy_pct", "backlog",
              "gross_margin_pct", "guidance_rev_low", "guidance_rev_high"]].to_string())


if __name__ == "__main__":
    main()
