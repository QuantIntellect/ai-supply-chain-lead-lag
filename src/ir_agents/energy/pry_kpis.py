"""Build data/processed/ir/PRY.MI_kpis.csv (FY2022Q1 -> FY2026H1) from Prysmian results press releases.
Group figures transcribed from release headlines/financial-highlight tables (see source_doc); 2024+ segment
figures parsed from the releases' 'business overview' tables (pry_segtables.py -> segment_tables.json).
revenue_yoy_pct = nominal change computed from the current and prior-year revenue stated in the same table."""
import sys; sys.path.insert(0, "/Users/sinamirzaei/Documents/aimapping/src/ir_agents/energy"); import irlib
import json, os
T = "PRY.MI"
SEG = json.load(open(os.path.join(irlib.RAW_IR, T, "segment_tables.json")))
EV = {r["fiscal_period"]: r["event_date"] for r in irlib.read_csv(os.path.join(irlib.PROC_IR, f"{T}_events.csv"))}
DOC = lambda rel_period: f"data/raw/ir/PRY.MI/{rel_period}_press_release.pdf"
M22 = "Adj. EBITDA / sales; headline margin as stated (1Q22 and 1H22 headline margins are at 2021 metal prices)"
M23 = "Adj. EBITDA / sales at current metal prices"
M25 = "Adj. EBITDA / revenues at standard metal prices (Cu EUR5,500/t, Al EUR1,500/t, Pb EUR2,000/t), as reported from 2025"
BL_OLD = "Projects (submarine & HV) order book/backlog incl. only orders with Notice to Proceed, EUR m (pre-2024 segment structure)"
BL_NEW = "Transmission segment backlog, EUR m (approximate as stated)"
def G(metric, lo, hi, period, note=""):
    d = {"metric": metric, "low": lo, "high": hi, "unit": "EUR m", "period": period}
    if note: d["note"] = note
    return d
def segs_from_table(rel, total):
    for tb in SEG.get(rel, []):
        if tb.get("Total Group", {}).get("revenue") == total:
            out = {}
            for k, v in tb.items():
                if k == "Total Group": continue
                out[k] = {"revenue": v["revenue"], "organic_growth_pct": v["organic_growth_pct"], "adj_ebitda": v["adj_ebitda"],
                          "margin_pct": v["margin_pct"]}
                if "margin_current_metal_pct" in v:
                    out[k]["margin_current_metal_pct"] = v["margin_current_metal_pct"]
            return out, tb["Total Group"]
    return None, None
R = []
def row(fp, pe, rel, rev, prior, org, ebitda, margin, mdef, backlog=None, bdef=None, guid_text="", gother=None,
        dc="", extra=None, segs=None, q_org=None, ev_fp=None):
    ej = {"organic_growth_pct": org, "adj_ebitda": ebitda, "margin_pct": margin, "margin_def": mdef,
          "revenue_prior_year": prior, "revenue_yoy_basis": "nominal, computed from stated current vs prior-year revenue"}
    if q_org is not None: ej["q_organic_growth_pct"] = q_org
    if bdef: ej["backlog_def"] = bdef
    if gother: ej["guidance_other"] = gother
    if segs: ej["segments"] = segs
    if extra: ej.update(extra)
    ej = {k: v for k, v in ej.items() if v is not None}
    R.append({"fiscal_period": fp, "period_end": pe, "release_date": EV.get(ev_fp or rel), "currency": "EUR", "unit": "m",
              "revenue": rev, "revenue_yoy_pct": round((rev / prior - 1) * 100, 1) if rev and prior else None,
              "backlog": backlog, "guidance_text": guid_text, "ai_dc_notes": dc, "extra_json": ej, "source_doc": DOC(rel)})

# ---------------- 2022 (old segments: Projects / Energy / Telecom)
row("FY2022Q1", "2022-03-31", "FY2022Q1", 3677, 2810, 11.4, 288, 8.7, M22, 4200, BL_OLD,
    "FY2022 adj. EBITDA guidance EUR1,010-1,080m; results expected at the upper end of the range",
    [G("adj_ebitda", 1010, 1080, "FY2022", "expected at upper end")], "",
    {"margin_current_metal_pct": 7.8, "net_profit": 126, "awarded_not_in_backlog": 5000,
     "projects_new_orders": 1400},
    {"Energy": {"organic_growth_pct": 12.1, "adj_ebitda": 189}, "Telecom": {"organic_growth_pct": 7.4},
     "Projects": {"orders": 1400, "backlog": 4200}})
row("FY2022H1", "2022-06-30", "FY2022H1", 7949, 6034, 12.5, 699, 9.4, M22, 4300, BL_OLD,
    "FY2022 adj. EBITDA target raised by 30% to EUR1.3-1.4bn",
    [G("adj_ebitda", 1300, 1400, "FY2022", "upgraded")], "",
    {"net_profit": 259, "fcf_ltm": 174, "projects_orders_ytd": 2400, "awarded_not_in_backlog": 5800},
    {"Energy": {"organic_growth_pct": 13.6}, "Telecom": {"organic_growth_pct": 6.6},
     "Projects": {"organic_growth_pct": 28.4, "orders": 2400, "backlog": 4300}}, q_org=13.5)
row("FY2022_9M", "2022-09-30", "FY2022Q3", 12089, 9294, 15.0, 1131, 9.4, M22, 6850, BL_OLD,
    "FY2022 targets revised upwards: adj. EBITDA EUR1,425-1,475m; FCF EUR450-500m",
    [G("adj_ebitda", 1425, 1475, "FY2022", "upgraded"), G("fcf", 450, 500, "FY2022", "upgraded")],
    "Energy segment results driven by demand for technologies needed to upgrade power grids, data centres and solar energy.",
    {"net_profit": 431, "fcf_ltm": 344, "net_debt": 2372, "projects_order_intake_ytd": 3200},
    {"Projects": {"revenue": 1438, "backlog": 6850, "orders": 3200}}, q_org=16.2)
row("FY2022", "2022-12-31", "FY2022", 16067, 12736, 14.4, 1488, 9.3, M23, 8400, BL_OLD,
    "FY2023 guidance: adj. EBITDA EUR1,375-1,525m; FCF EUR450-550m",
    [G("adj_ebitda", 1375, 1525, "FY2023"), G("fcf", 450, 550, "FY2023")],
    "Energy sales +12.3% fuelled by renewables, power distribution and data centres; Telecom +10.9% driven by optical cables.",
    {"net_profit": 504, "fcf": 559, "net_debt": 1417, "projects_order_intake": 3400},
    {"Projects": {"organic_growth_pct": 30.3, "backlog": 8400, "orders": 3400}, "Energy": {"organic_growth_pct": 12.3},
     "Telecom": {"organic_growth_pct": 10.9}})
# ---------------- 2023
row("FY2023Q1", "2023-03-31", "FY2023Q1", 3992, 3677, 9.0, 427, 10.7, M23, 8300, BL_OLD, "", None, "",
    {"net_profit": 182, "fcf_ltm": 581, "net_debt": 2074, "backlog_incl_biscay_gulf": 9100},
    {"Projects": {"organic_growth_pct": 29.5, "backlog": 8300}, "Energy": {"organic_growth_pct": 6.6},
     "Telecom": {"organic_growth_pct": 5.7}})
row("FY2023H1", "2023-06-30", "FY2023H1", 8003, 7949, 4.8, 878, 11.0, M23, 9100, BL_OLD + "; excl. EGL1/EGL2",
    "FY2023 guidance upgraded: adj. EBITDA EUR1,575-1,675m; FCF EUR550-650m; CMD on 5 Oct 2023",
    [G("adj_ebitda", 1575, 1675, "FY2023", "upgraded (+EUR175m)"), G("fcf", 550, 650, "FY2023", "upgraded (+EUR100m)")], "",
    {"net_profit": 405, "fcf_ltm": 567, "projects_orders_ytd": 5400},
    {"Projects": {"organic_growth_pct": 23.5, "margin_pct": 11.0, "orders": 5400, "backlog": 9100},
     "Energy": {"organic_growth_pct": 3.4}, "Telecom": {"organic_growth_pct": -5.2, "margin_pct": 14.8}})
row("FY2023_9M", "2023-09-30", "FY2023Q3", 11825, 12089, 1.5, 1286, 10.9, M23, 10000,
    BL_OLD + "; ~EUR10bn backlog plus ~EUR10bn orders with solid commitment (~EUR20bn total)",
    "FY2023 guidance confirmed (adj. EBITDA EUR1,575-1,675m; FCF EUR550-650m)",
    [G("adj_ebitda", 1575, 1675, "FY2023", "confirmed"), G("fcf", 550, 650, "FY2023", "confirmed")], "",
    {"net_profit": 575, "fcf_ltm": 729, "projects_orders_ytd": 13000, "order_book_incl_solid_commitment": 20000},
    {"Projects": {"organic_growth_pct": 23.9, "margin_pct": 11.7, "backlog": 10000, "orders": 13000}})
row("FY2023", "2023-12-31", "FY2023", 15354, 16067, -1.1, 1628, 10.6, M23, 18000,
    BL_NEW + "; 'record backlog in Transmission of EUR18bn' (total order book ~EUR20bn incl. orders with solid commitment)",
    "FY2024 outlook: adj. EBITDA EUR1,575-1,675m; FCF EUR675-775m",
    [G("adj_ebitda", 1575, 1675, "FY2024"), G("fcf", 675, 775, "FY2024")],
    "Telecom growth drivers remain strong: massive data growth, FTTH, 5G coverage, datacentres and IoT.",
    {"net_profit": 529, "fcf": 724, "new_projects_2023": 13000})
# ---------------- 2024 (new segments)
s, _ = segs_from_table("FY2024Q1", 3687)
s["Transmission"]["backlog"] = 18000
row("FY2024Q1", "2024-03-31", "FY2024Q1", 3687, 3992, -5.6, 412, 11.2, M23, 18000, BL_NEW + " ('over EUR18bn')",
    "FY2024 results expected in the upper end of the guidance range (adj. EBITDA EUR1,575-1,675m)",
    [G("adj_ebitda", 1575, 1675, "FY2024", "upper end expected")],
    "Digital Solutions drivers unchanged: massive data growth, FTTH, 5G coverage and datacentres; Encore Wire acquisition (announced 15 Apr 2024) to grow North America.",
    {"net_profit": 185, "net_debt": 1693, "fcf_ltm": 827}, s)
s, _ = segs_from_table("FY2024H1", 7819)
s["Transmission"]["backlog"] = 18000
row("FY2024H1", "2024-06-30", "FY2024H1", 7819, 8003, -3.0, 869, 11.1, M23, 18000, BL_NEW,
    "FY2024 outlook upgraded (incl. Encore Wire from 1 Jul 2024): adj. EBITDA EUR1,900-1,950m; FCF EUR840-920m",
    [G("adj_ebitda", 1900, 1950, "FY2024", "upgraded"), G("fcf", 840, 920, "FY2024", "upgraded")],
    "Digital Solutions drivers unchanged: massive data growth, FTTH, 5G coverage and datacentres.",
    {"net_profit": 402, "net_debt": 1321, "fcf_ltm": 889}, s)
s, tg = segs_from_table("FY2024Q3", 4543)
row("FY2024Q3", "2024-09-30", "FY2024Q3", 4543, tg["revenue_prior"], 1.8, tg["adj_ebitda"], 11.9, M23, None,
    BL_NEW + "; 'substantially stable compared to June' (no figure stated)", "", None,
    "First quarter including Encore Wire; I&C Q3 margin 11.5% driven by its consolidation.", {}, s)
s, _ = segs_from_table("FY2024Q3", 12362)
row("FY2024_9M", "2024-09-30", "FY2024Q3", 12362, 11825, -1.4, 1409, 11.4, M23, None,
    BL_NEW + "; 'substantially stable compared to June' (no figure stated)",
    "FY2024 outlook (upgraded at 1H24) confirmed",
    [G("adj_ebitda", 1900, 1950, "FY2024", "confirmed"), G("fcf", 840, 920, "FY2024", "confirmed")],
    "Digital Solutions drivers unchanged: massive data growth, FTTH, 5G coverage and datacentres.",
    {"net_profit": 619, "fcf_ltm": 979}, s, q_org=1.8)
s, tg = segs_from_table("FY2024", 4664)
row("FY2024Q4", "2024-12-31", "FY2024", 4664, tg["revenue_prior"], 6.9, tg["adj_ebitda"], tg["margin_pct"], M23, 17000, BL_NEW,
    "", None, "", {}, s)
s, _ = segs_from_table("FY2024", 17026)
s["Transmission"]["backlog"] = 17000
row("FY2024", "2024-12-31", "FY2024", 17026, 15354, 0.5, 1927, 11.3, M23, 17000, BL_NEW + " ('substantially stable at approximately EUR17bn')",
    "FY2025 outlook: adj. EBITDA EUR2,250-2,350m; FCF EUR950-1,050m",
    [G("adj_ebitda", 2250, 2350, "FY2025"), G("fcf", 950, 1050, "FY2025")],
    "Digital Solutions outlook positive: massive data growth, FTTH, 5G coverage and datacentres.",
    {"fcf": 1011}, s, q_org=6.9)
# ---------------- 2025
s, _ = segs_from_table("FY2025Q1", 4771)
s["Transmission"]["backlog"] = 17000
row("FY2025Q1", "2025-03-31", "FY2025Q1", 4771, 3687, 5.0, 527, 13.1, M25, 17000, BL_NEW,
    "FY2025 outlook confirmed (adj. EBITDA EUR2,250-2,350m; FCF EUR950-1,050m); Channell acquisition closing expected in Q2",
    [G("adj_ebitda", 2250, 2350, "FY2025", "confirmed"), G("fcf", 950, 1050, "FY2025", "confirmed")],
    "Digital Solutions organic growth +3.4% with margin 13.2%; Channell acquisition (announced 25 Mar 2025) to enhance Digital Solutions.",
    {"net_profit": 150, "net_debt": 4884, "fcf_ltm": 998}, s)
s, tg = segs_from_table("FY2025H1", 4883)
row("FY2025Q2", "2025-06-30", "FY2025H1", 4883, 4132, 3.2, 605, 14.5, M25, None, None, "", None,
    "Channell (consolidated from June 2025) lifted Digital Solutions Q2 margin to 16.8% and adj. EBITDA to EUR63m.",
    {"net_profit": 276}, s)
s, _ = segs_from_table("FY2025H1", 9654)
s["Transmission"]["backlog"] = 16000
row("FY2025H1", "2025-06-30", "FY2025H1", 9654, 7819, 4.0, 1132, 13.8, M25, 16000, BL_NEW,
    "FY2025 outlook upgraded: adj. EBITDA EUR2,300-2,375m; FCF EUR1,000-1,075m",
    [G("adj_ebitda", 2300, 2375, "FY2025", "upgraded"), G("fcf", 1000, 1075, "FY2025", "upgraded")],
    "Channell (closed June 2025) strengthens Digital Solutions profitability.",
    {"net_profit": 426, "net_debt": 4694, "fcf_ltm": 979}, s, q_org=3.2)
s, tg = segs_from_table("FY2025Q3", 5030)
row("FY2025Q3", "2025-09-30", "FY2025Q3", 5030, 4543, 9.2, 644, 14.8, M25, None, None, "", None,
    "I&C benefits from exposure to drivers such as data centers (Q3 North America organic +10%); Channell boosts Digital Solutions margin to 19.6%.",
    {"net_profit": 596}, s)
s, _ = segs_from_table("FY2025Q3", 14684)
s["Transmission"]["backlog"] = 16000
row("FY2025_9M", "2025-09-30", "FY2025Q3", 14684, 12362, 5.7, 1776, 14.1, M25, 16000,
    BL_NEW + "; plus ~EUR3bn awarded orders (incl. EGL4, Tunita) not yet in backlog",
    "FY2025 outlook upgraded again: adj. EBITDA EUR2,375-2,425m (prev. 2,300-2,375); FCF EUR1,025-1,125m (prev. 1,000-1,075)",
    [G("adj_ebitda", 2375, 2425, "FY2025", "upgraded"), G("fcf", 1025, 1125, "FY2025", "upgraded")],
    "CEO: I&C solid margins and growing revenues reflect exposure to important drivers such as data centers.",
    {"net_profit": 1022, "net_debt": 4318, "fcf_ltm": 859, "awarded_not_in_backlog": 3000}, s, q_org=9.2)
s, tg = segs_from_table("FY2025", 4966)
row("FY2025Q4", "2025-12-31", "FY2025", 4966, 4664, 4.3, 622, 14.5, M25, 17000, BL_NEW, "", None,
    "I&C Q4 organic +0.6% (North America +5.6%) with strong growth from data centers; Digital Solutions Q4 adj. EBITDA EUR75m vs EUR40m incl. Channell.",
    {}, s)
s, _ = segs_from_table("FY2025", 19650)
s["Transmission"]["backlog"] = 17000
row("FY2025", "2025-12-31", "FY2025", 19650, 17026, 5.4, 2398, 14.2, M25, 17000,
    BL_NEW + "; incl. EGL4; plus ~EUR2bn orders not yet in backlog",
    "FY2026 outlook: adj. EBITDA EUR2,625-2,775m; FCF EUR1,300-1,400m",
    [G("adj_ebitda", 2625, 2775, "FY2026"), G("fcf", 1300, 1400, "FY2026")],
    "Electrification I&C growth and margins driven by data center expansion in North America; Digital Solutions adj. EBITDA nearly doubled in Q4 incl. Channell.",
    {"net_profit": 1270, "fcf": 1171, "awarded_not_in_backlog": 2000}, s, q_org=4.3)
# ---------------- 2026
s, _ = segs_from_table("FY2026Q1", 5218)
s["Transmission"]["backlog"] = 17000
row("FY2026Q1", "2026-03-31", "FY2026Q1", 5218, 4771, 5.0, 601, 14.2, M25, 17000,
    BL_NEW + "; plus ~EUR2bn awarded projects not yet in backlog",
    "FY2026 guidance confirmed (adj. EBITDA EUR2,625-2,775m; FCF EUR1,300-1,400m)",
    [G("adj_ebitda", 2625, 2775, "FY2026", "confirmed"), G("fcf", 1300, 1400, "FY2026", "confirmed")],
    "I&C organic +5.8% thanks to North America (+10%) driven by data centers; Digital Solutions organic +9.0% as fiber demand for data centers surges.",
    {"fcf_ltm": 1191, "awarded_not_in_backlog": 2000}, s)
s, tg = segs_from_table("FY2026H1", 6021)
row("FY2026Q2", "2026-06-30", "FY2026H1", 6021, 4883, 9.4, 730, 15.4, M25, 17000, BL_NEW, "", None,
    "I&C organic +9.1% driven by North American data center demand; Digital Solutions Q2 margin 23.8% (optical cables, Channell), organic +18.0%; 'transformative Molex deal' to enter inside-data-center space.",
    {}, s)
s, _ = segs_from_table("FY2026H1", 11239)
s["Transmission"]["backlog"] = 17000
row("FY2026H1", "2026-06-30", "FY2026H1", 11239, 9654, 7.2, 1331, 14.8, M25, 17000,
    BL_NEW + "; plus ~EUR2bn awarded projects not yet in backlog",
    "FY2026 guidance upgraded: adj. EBITDA EUR2,800-2,900m (prev. 2,625-2,775); FCF EUR1,650-1,750m (prev. 1,300-1,400); new CMD within 1H27",
    [G("adj_ebitda", 2800, 2900, "FY2026", "upgraded"), G("fcf", 1650, 1750, "FY2026", "upgraded")],
    "Prysmian positions itself as front-running cable player for data centers after the Molex deal and Digital Solutions capacity increase; CEO cites AI-driven energy and data infrastructure build-out.",
    {"awarded_not_in_backlog": 2000}, s, q_org=9.4)
irlib.write_kpis(T, R)
