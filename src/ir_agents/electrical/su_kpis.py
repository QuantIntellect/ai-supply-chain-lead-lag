"""Assemble data/processed/ir/SU.PA_kpis.csv (2022Q1-2026Q3).
Quarter revenue / organic / reported growth / business split were regex-extracted
from the release texts (su_segments.json, su_systems.json) and checked by hand;
margins, guidance and data-center notes transcribed from the releases.
Schneider does not disclose order intake or book-to-bill; backlog only at year-end."""
import os, sys, json
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import *

T = "SU.PA"
P = os.path.join(RAW_IR, T, "pages")
seg = json.load(open(os.path.join(P, "su_segments.json")))
sysd = json.load(open(os.path.join(P, "su_systems.json")))
ev = pd.read_csv(os.path.join(PROC_IR, f"{T}_events.csv"))
rel = {r.fiscal_period: r.event_date for r in ev.itertuples() if r.event_type in ("Q1", "H1", "Q3", "FY")}
QEND = {1: "03-31", 2: "06-30", 3: "09-30", 4: "12-31"}
# period: (revenue €m, organic %, reported %)
REV = {"2022Q1": (7566, 9.8, 15.9), "2022Q2": (8511, 10.3, 17.4), "2022Q3": (8779, 12.1, 21.6), "2022Q4": (9320, 16.0, 17.8),
       "2023Q1": (8493, 15.8, 12.3), "2023Q2": (9140, 14.8, 7.4), "2023Q3": (8789, 11.5, 0.1), "2023Q4": (9480, 9.1, 1.7),
       "2024Q1": (8606, 5.3, 1.3), "2024Q2": (9567, 7.1, 4.7), "2024Q3": (9311, 8.0, 5.9), "2024Q4": (10669, 12.5, 12.5),
       "2025Q1": (9325, 7.4, 8.4), "2025Q2": (10011, 8.3, 4.6), "2025Q3": (9721, 9.0, 4.4), "2025Q4": (11095, 10.7, 4.0),
       "2026Q1": (9767, 11.2, 4.7), "2026Q2": (11459, 16.5, 14.5), "2026Q3": (11460, 16.9, 17.9)}
SEG22 = {"2022Q1": (5673, 10.0, 1893, 9.2), "2022Q2": (6634, 11.6, 1877, 6.0), "2022Q3": (6808, 12.1, 1971, 12.0)}
# H1/FY margins (Q2 row = H1, Q4 row = FY)
MARG = {"2022Q2": (40.6, 17.3), "2022Q4": (40.6, 17.6), "2023Q2": (42.4, 18.0), "2023Q4": (41.8, 17.9),
        "2024Q2": (43.4, 18.6), "2024Q4": (42.6, 18.6), "2025Q2": (42.4, 18.2), "2025Q4": (42.1, 18.7), "2026Q2": (42.5, 19.3)}
# guidance stated in the release: (text, org rev growth low, high)
G = {
 "2022Q1": ("FY22 target confirmed: adj. EBITA +9% to +13% org; revenue +7% to +9% org; adj. EBITA margin +30 to +60bps org", 7, 9),
 "2022Q2": ("FY22 target upgraded: adj. EBITA +11% to +15% org (prev +9-13%); revenue +9% to +11% org (prev +7-9%); margin +30 to +60bps org", 9, 11),
 "2022Q3": ("FY22 target confirmed: adj. EBITA +11% to +15% org; revenue +9% to +11% org; margin +30 to +60bps org (~17.7%)", 9, 11),
 "2022Q4": ("FY23 target: adj. EBITA +12% to +16% org; revenue +9% to +11% org; margin +50 to +80bps org", 9, 11),
 "2023Q1": ("FY23 target upgraded: adj. EBITA +16% to +21% org; revenue +10% to +13% org; margin +100 to +130bps org", 10, 13),
 "2023Q2": ("FY23 target upgraded: adj. EBITA +18% to +23% org; revenue +11% to +13% org; margin +120 to +150bps org", 11, 13),
 "2023Q3": ("FY23 target reaffirmed: adj. EBITA +18% to +23% org; revenue +11% to +13% org; margin ~17.7-18.0%", 11, 13),
 "2023Q4": ("FY24 target: adj. EBITA +8% to +12% org; revenue +6% to +8% org; margin +40 to +60bps org. CMD Nov-2023: 2024-27 org revenue CAGR +7% to +10%", 6, 8),
 "2024Q1": ("FY24 target reaffirmed: adj. EBITA +8% to +12% org; revenue +6% to +8% org; margin ~18.0-18.2%", 6, 8),
 "2024Q2": ("FY24 target upgraded: adj. EBITA +9% to +13% org; revenue +6% to +8% org (unchanged); margin +60 to +80bps org", 6, 8),
 "2024Q3": ("FY24 target reaffirmed: adj. EBITA +9% to +13% org; revenue +6% to +8% org; margin ~18.1-18.3%", 6, 8),
 "2024Q4": ("FY25 target: adj. EBITA +10% to +15% org; revenue +7% to +10% org; margin +50 to +80bps org", 7, 10),
 "2025Q1": ("FY25 target reaffirmed: adj. EBITA +10% to +15% org; revenue +7% to +10% org; margin ~18.7-19.0%", 7, 10),
 "2025Q2": ("FY25 target reaffirmed incl. tariffs: adj. EBITA +10% to +15% org; revenue +7% to +10% org; margin +50 to +80bps org", 7, 10),
 "2025Q3": ("FY25 target reaffirmed, towards lower half of ranges: adj. EBITA +10% to +15% org; revenue +7% to +10% org", 7, 10),
 "2025Q4": ("FY26 target: adj. EBITA +10% to +15% org; revenue +7% to +10% org; margin +50 to +80bps org. CMD Dec-2025: 2026-30 org revenue CAGR +7% to +10%, +250bps margin cumulative", 7, 10),
 "2026Q1": ("FY26 target reaffirmed: adj. EBITA +10% to +15% org; revenue +7% to +10% org; margin ~19.1-19.4%", 7, 10),
 "2026Q2": ("FY26 target upgraded: adj. EBITA +14% to +19% org; revenue +10% to +13% org; margin +70 to +100bps org", 10, 13),
 "2026Q3": ("FY26 target upgraded: adj. EBITA +18% to +21% org; revenue +12% to +14% org; margin +100 to +120bps org (~19.7-19.9%)", 12, 14),
}
DC = {
 "2022Q1": "Data Center & Networks demand 'very strong'; sales to benefit from high backlog exiting 2021",
 "2022Q2": "DC&N end-market 'continues to remain very strong'; exposure across MV, LV, Secure Power, Cooling, BMS, software",
 "2022Q3": "DC&N continues to experience strong demand; DC growth supported by backlog execution",
 "2022Q4": "DC&N: another quarter of strong demand and double-digit sales growth; backlog 'remains high'",
 "2023Q1": "DC&N sales up double-digit, led by strong double-digit pure-DC growth (enterprise, hyperscale, colo, edge); record backlog end-Q1",
 "2023Q2": "Electrification and AI 'driving increased traction for Data Centers'; backlog still growing",
 "2023Q3": "AI-related DC demand 'becoming visible'; Group backlog grew further in Q3",
 "2023Q4": "DC demand very strong from internet giants and colos, sales helped by AI; record backlog entering 2024 (systems)",
 "2024Q1": "Very strong DC demand; Internet Giants (AI a contributing factor) plus enterprise/prefab traction",
 "2024Q2": "Pure DC demand and sales up strong double-digit, driven by Internet Giants",
 "2024Q3": "DC&N demand and sales both up strong double-digit; Motivair liquid-cooling acquisition announced; systems backlog gives visibility",
 "2024Q4": "DC&N demand and sales up double-digit; pure DC strongest",
 "2025Q1": "DC&N demand and sales up strong double-digit; colos, prefab and cooling (NA-led); Motivair closed",
 "2025Q2": "DC sales and demand up double-digit excl. one customer's order rephasing into H2-25; AI demand broadening from Internet Giants to colos",
 "2025Q3": "Sustained high DC demand vs high Q3-24 base; winning neo-cloud and smaller AI players",
 "2025Q4": "Pure DC demand up triple-digit YoY in Q4 (hyperscale and colo), strongest in North America",
 "2026Q1": "DC&N demand up double-digit despite high base (one very large order in Q1-25); strong liquid-cooling growth",
 "2026Q2": "DC&N demand up triple-digit in Q2 (AI and cloud; hyperscale, colo, sovereign, all four regions); record backlog",
 "2026Q3": "DC&N demand up triple-digit again in Q3, led by North America with China & East Asia accelerating; backlog gives visibility into 2027-28",
}
# year-end backlog (disclosed once a year with FY results; EUR million) and
# management book-to-bill remarks from the call transcripts (qualitative only)
BACKLOG = {"2022Q4": (16500, "record EUR16.5bn, ~6 months of sales (FY22 call)"),
           "2023Q4": (19200, "EUR19.2bn, >6 months of sales (FY23 presentation)"),
           "2024Q4": (21400, "EUR21.4bn, +~12% vs 2023 (FY24 presentation/call)"),
           "2025Q4": (25400, "EUR25.4bn, +18% YoY; EM EUR21bn +21%, IA EUR4bn +8%; >1y portion EUR8.0bn vs EUR4.8bn (FY25 presentation)")}
B2B = {"2023Q1": "CFO: book-to-bill above 1 in Q1 (incl. Industrial Automation); not formally reported",
       "2023Q3": "CFO: book-to-bill higher than 1 in Q3 (record backlog despite sales growth)",
       "2025Q2": "CFO: book-to-bill 'decently above one'; strong double-digit backlog growth despite one large customer's order rephasing",
       "2025Q3": "CFO: positive book-to-bill in Data Center and generally across businesses in Q3"}
rows = []
for per, (rev, org, rep) in REV.items():
    y, q = int(per[:4]), int(per[-1])
    s = seg.get(per, {})
    ex = {"organic_growth_pct": org}
    if per in SEG22:
        a = SEG22[per]
        s = dict(em_rev=a[0], em_org=a[1], ia_rev=a[2], ia_org=a[3], **{k: v for k, v in s.items() if k.startswith("na_")})
    for k_src, k_dst in [("em_rev", "energy_mgmt_rev_eur_m"), ("em_org", "energy_mgmt_org_pct"), ("ia_rev", "ind_automation_rev_eur_m"),
                         ("ia_org", "ind_automation_org_pct"), ("na_em_rev", "north_america_em_rev_eur_m"), ("na_em_org", "north_america_em_org_pct")]:
        if k_src in s:
            ex[k_dst] = s[k_src]
    sy = sysd.get(per)
    if sy:
        ex["systems_share_pct"] = sy["systems_share_pct"]
        ex["systems_share_basis"] = sy["share_basis"]
        if sy["systems_org"]:
            ex["systems_org_pct_quarter"] = float(sy["systems_org"].rstrip("%"))
    gm = ""
    if per in MARG:
        gm = MARG[per][0]
        ex["adj_ebita_margin_pct"] = MARG[per][1]
        ex["margin_basis"] = "H1" if q == 2 else "FY"
    if per in B2B:
        ex["book_to_bill_comment"] = B2B[per]
    bl = ""
    if per in BACKLOG:
        bl = BACKLOG[per][0]
        ex["backlog_note"] = "year-end backlog: " + BACKLOG[per][1]
    ex["guidance_rev_basis"] = "FY organic revenue growth %"
    ex["orders_note"] = "Schneider does not disclose order intake; backlog disclosed only at year-end; 'demand' growth comments are qualitative"
    src = os.path.join("data", "raw", "ir", T, f"{per}_release.pdf")
    rows.append({"fiscal_period": per, "period_end": f"{y}-{QEND[q]}", "release_date": rel.get(per, ""),
                 "currency": "EUR", "unit": "EUR million", "revenue": rev, "revenue_yoy_pct": rep,
                 "backlog": bl, "gross_margin_pct": gm, "guidance_text": G[per][0], "guidance_rev_low": G[per][1],
                 "guidance_rev_high": G[per][2], "ai_dc_notes": DC[per], "extra_json": ex, "source_doc": src})
p = write_kpis(T, rows)
print(p, len(rows))
