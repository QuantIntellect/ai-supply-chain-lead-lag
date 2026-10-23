"""Finalize data/processed/ir/LR.PA_kpis.csv: parsed figures (lr_kpis.py -> kpi_rows.pkl) plus
guidance and datacenter notes transcribed from the release texts (each value checked by grep)."""
import os, sys
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import *
TK = "LR.PA"
import json
rows = json.load(open(os.path.join(RAW_IR, TK, "kpi_rows.json")))  # own intermediate (JSON, no pickle)

# fp: (text, sales_growth_exFX_low, high, organic_low, high, adj_margin_low, high)
G = {
    "2022Q1": ("FY2022 targets (Feb-22) confirmed: sales growth at constant FX +5% to +11% (organic +3% to +7%, scope +2% to +4%) [ranges as restated in H1-22 release]", 5, 11, 3, 7, None, None),
    "2022Q2": ("FY2022 raised: sales growth at constant FX +9% to +12% (organic +6% to +9%, scope ~+3%); adj. op. margin about 20% (19.9%-20.7% before acquisitions)", 9, 12, 6, 9, 19.9, 20.7),
    "2022Q3": ("FY2022 confirmed: sales growth at constant FX +9% to +12% (organic +6% to +9%, scope ~+3%); adj. op. margin about 20%", 9, 12, 6, 9, None, None),
    "2022Q4": ("FY2023 targets: sales growth at constant FX +2% to +6% incl. scope ~+3%; adj. op. margin before acquisitions ~20%", 2, 6, None, None, None, None),
    "2023Q1": ("FY2023 confirmed: sales growth at constant FX +2% to +6% incl. scope ~+3%; adj. op. margin before acquisitions ~20%", 2, 6, None, None, None, None),
    "2023Q2": ("FY2023 raised: sales growth at constant FX excl. Russia +5% to +8% (scope ~+2%); adj. op. margin before acquisitions ~20.5%", 5, 8, None, None, None, None),
    "2023Q3": ("FY2023 specified: sales growth ~+5% (organic +2.5% to +3.5%, scope ~+2%); adj. op. margin 20.5%-21.0% before acquisitions", 5, 5, 2.5, 3.5, 20.5, 21.0),
    "2023Q4": ("FY2024 targets: low single-digit sales growth (organic + acquisitions, excl. FX); adj. op. margin before acquisitions 20.0%-20.8%", None, None, None, None, 20.0, 20.8),
    "2024Q1": ("FY2024 confirmed: low single-digit sales growth; adj. op. margin before acquisitions 20.0%-20.8%", None, None, None, None, 20.0, 20.8),
    "2024Q2": ("FY2024 unchanged: low single-digit sales growth; adj. op. margin before acquisitions 20.0%-20.8%", None, None, None, None, 20.0, 20.8),
    "2024Q3": ("FY2024 specified: low single-digit sales growth; adj. op. margin after acquisitions 20.0%-20.4%", None, None, None, None, 20.0, 20.4),
    "2024Q4": ("FY2025 targets: sales growth +6% to +10% (organic + acquisitions, excl. FX); adj. op. margin after acquisitions stable vs 2024", 6, 10, None, None, None, None),
    "2025Q1": ("FY2025 confirmed: sales growth +6% to +10% excl. FX; adj. op. margin after acquisitions stable vs 2024", 6, 10, None, None, None, None),
    "2025Q2": ("FY2025 raised (pre-announced 17-Jul-25): sales growth +10% to +12% excl. FX (organic +5% to +7%, acquisitions ~+5%); adj. op. margin after acquisitions 20.5%-21.0%", 10, 12, 5, 7, 20.5, 21.0),
    "2025Q3": ("FY2025 confirmed: sales growth +10% to +12% excl. FX (organic +5% to +7%, acquisitions ~+5%); adj. op. margin 20.5%-21.0%", 10, 12, 5, 7, 20.5, 21.0),
    "2025Q4": ("FY2026 targets: sales growth excl. FX +10% to +15% (organic +4% to +7%, acquisitions +6% to +8%); adj. op. margin after acquisitions 20.5%-21.0%", 10, 15, 4, 7, 20.5, 21.0),
    "2026Q1": ("FY2026 confirmed: sales growth excl. FX +10% to +15% (organic +4% to +7%, acquisitions +6% to +8%); adj. op. margin 20.5%-21.0%", 10, 15, 4, 7, 20.5, 21.0),
    "2026Q2": ("FY2026 raised: sales growth excl. FX +16% to +19% (organic +8% to +10%, acquisitions ~+8%); adj. op. margin 20.5%-21.0% (unchanged)", 16, 19, 8, 10, 20.5, 21.0),
}
DC = {
    "2022Q2": "2 bolt-on datacenter acquisitions announced (Usystems: DC cooling/racks; Voltadis: DC services)",
    "2023Q2": "growth buoyed by faster-expanding segments incl. datacenters; Teknica (UPS for datacenters) acquired",
    "2023Q3": "ZPE Systems (datacenter) acquisition; growth driven by energy efficiency, datacenters, connected products",
    "2023Q4": "datacenters now ~15% of total sales; 2 of 5 2023 acquisitions in datacenters",
    "2024Q1": "organic -5.4% in contracting markets excluding datacenters; Netrack (DC racks, India) acquired",
    "2024Q2": "Q2 organic +1.5% stemmed notably from datacenters; 3 DC acquisitions in H1 (Netrack, Davenham, Vass)",
    "2024Q3": "growth driven by acquisitions and datacenters, notably sustained US datacenter growth; 4 of 7 YTD acquisitions in DC",
    "2024Q4": "datacenters ~20% of sales (proforma), organic growth close to +15% in 2024",
    "2025Q1": "accelerating organic growth in datacenters (20% of 2024 sales)",
    "2025Q2": "datacenters 24% of H1-25 sales; Q2 organic +10.1% largely fueled by datacenters; FY guide raised in 17-Jul pre-release",
    "2025Q3": "9M organic +8.2% driven by strong momentum in datacenters; 4 DC acquisitions YTD",
    "2025Q4": "datacenters EUR2.4bn = 26% of 2025 sales (vs EUR0.7bn in 2020); 2 new US/Brazil DC acquisitions",
    "2026Q1": "Q1 sales +18% ex-FX driven by datacenters and acquisitions",
    "2026Q2": "H1 record +17% ex-FX driven by datacenters/energy transition; FY26 guide raised; CMD (29-Sep-26): DC >EUR3bn sales in 2026, 32% of sales",
}
out = []
for r in rows:
    fp = r["fiscal_period"]
    e = dict(r["extra_json"])
    for k in ("guidance_sales_growth_exfx_pct", "guidance_organic_growth_pct", "guidance_adj_op_margin_pct", "dc_share_mentions_pct"):
        e.pop(k, None)
    if fp in G:
        txt, sl, sh, ol, oh, ml, mh = G[fp]
        r["guidance_text"] = txt
        r["guidance_rev_low"], r["guidance_rev_high"] = ("" if sl is None else sl), ("" if sh is None else sh)
        e["guidance_rev_unit"] = "FY sales growth % excl. FX (organic + acquisitions); not a revenue level"
        e["guidance_organic_growth_pct"] = [ol, oh] if ol is not None else None
        e["guidance_adj_op_margin_pct"] = [ml, mh] if ml is not None else None
    if fp.endswith(("Q2", "Q4")):
        e["adj_operating_margin_note"] = "H1/FY cumulative adjusted operating margin" if fp.endswith("Q2") else "FY adjusted operating margin"
    else:
        e["adj_operating_margin_note"] = "cumulative (3M/9M) adjusted operating margin"
    e["orders_note"] = "Legrand does not report order intake"
    if int(fp[:4]) < 2022:
        e["review_note"] = "auto-parsed figures only; guidance and DC notes not transcribed for pre-2022 quarters"
    r["ai_dc_notes"] = DC.get(fp, "")
    r["extra_json"] = e
    out.append(r)
print(write_kpis(TK, out), len(out))
