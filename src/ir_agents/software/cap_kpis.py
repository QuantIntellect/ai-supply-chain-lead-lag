"""Write data/processed/ir/CAP.PA_kpis.csv. Values hand-transcribed from the Capgemini press releases
(data/processed/ir_text/CAP.PA/*_press_release.txt), verified with regex probes (cap_kpi_probe.py).
Blank = not stated in the release. Growth in %; amounts in EUR m. Q2/Q4 rows only carry figures the
H1/FY releases state explicitly (nothing derived)."""
import os, csv, json, sys
sys.path.insert(0, os.path.dirname(__file__))
import fetch_util as fu

T = "CAP.PA"
OUT = os.path.join(fu.PROC_IR, "%s_kpis.csv" % T)
SRC = "data/processed/ir_text/CAP.PA/%s_press_release.txt"
PE = {"Q1": "03-31", "Q2": "06-30", "Q3": "09-30", "Q4": "12-31", "H1": "06-30", "FY": "12-31"}

G22a = ("FY2022: cc growth +8% to +10%; op margin 12.9%-13.1%; organic FCF > EUR1.7bn", 8, 10)
G22b = ("FY2022 (raised Jul-22): cc growth +14% to +15% (was +8% to +10%); op margin 12.9%-13.1%; organic FCF > EUR1.7bn", 14, 15)
G23 = ("FY2023: cc growth +4% to +7%; op margin 13.0%-13.2%; organic FCF ~EUR1.8bn", 4, 7)
G24a = ("FY2024: cc growth 0% to +3%; op margin 13.3%-13.6%; organic FCF ~EUR1.9bn", 0, 3)
G24b = ("FY2024 (cut Jul-24): cc growth -1.5% to -0.5% (was 0% to +3%); op margin 13.3%-13.6%; organic FCF ~EUR1.9bn", -1.5, -0.5)
G24c = ("FY2024 (cut Oct-24): cc growth -2.4% to -2.0% (was -1.5% to -0.5%); op margin 13.3%-13.4% (was 13.3%-13.6%); organic FCF ~EUR1.9bn", -2.4, -2.0)
G25a = ("FY2025: cc growth -2.0% to +2.0%; op margin 13.3%-13.5%; organic FCF ~EUR1.9bn", -2.0, 2.0)
G25b = ("FY2025 (Jul-25, excl. WNS): cc growth -1.0% to +1.0% (was -2% to +2%); op margin 13.3%-13.5%; organic FCF ~EUR1.9bn", -1.0, 1.0)
G25c = ("FY2025 (raised Oct-25, incl. WNS ~2pts M&A): cc growth +2.0% to +2.5%; op margin 13.3%-13.4%; organic FCF ~EUR1.9bn", 2.0, 2.5)
G26a = ("FY2026: cc growth ~+6.5% to +8.5% (inorganic ~4.5-5pts); op margin 13.6%-13.8%; organic FCF ~EUR1.8-1.9bn", 6.5, 8.5)
G26b = ("FY2026 (raised Jul-26): cc growth ~+8.5% to +9.0% (inorganic ~5pts); op margin 13.6%-13.8%; organic FCF ~EUR1.8-1.9bn", 8.5, 9.0)

# fp, release, revenue, rev_yoy, orders, orders_yoy, b2b, guidance, ai_notes, extra, src_period
R = [
 ("2022Q1", "2022-04-28", 5167, 21.0, 5473, 26, 1.06, G22a, "", {"cc_growth_pct": 17.7, "headcount": 340700}, "2022Q1"),
 ("2022Q2", "2022-07-28", None, None, 6134, 19, 1.11, G22b, "", {"cc_growth_pct": 19.3, "organic_growth_pct": 18.1}, "2022H1"),
 ("2022H1", "2022-07-28", 10688, 22.7, 11607, 22, 1.09, G22b, "", {"cc_growth_pct": 18.5, "organic_growth_pct": 17.2, "operating_margin_pct": 12.2, "operating_margin_eur_m": 1301, "organic_fcf_eur_m": 193, "headcount": 352100}, "2022H1"),
 ("2022Q3", "2022-10-27", 5553, 22.0, 5427, 13, 0.98, G22b, "", {"cc_growth_pct": 15.7, "organic_growth_pct": 14.3, "cc_growth_9m_pct": 17.5, "revenue_9m_eur_m": 16241, "headcount": 358400}, "2022Q3"),
 ("2022Q4", "2023-02-21", None, None, 6685, 11.4, 1.16, G23, "", {"cc_growth_pct": 14.0, "organic_growth_pct": 12.8}, "2022FY"),
 ("2022FY", "2023-02-21", 21995, 21.1, 23719, 16.8, 1.08, G23, "", {"cc_growth_pct": 16.6, "organic_growth_pct": 15.3, "operating_margin_pct": 13.0, "operating_margin_eur_m": 2867, "organic_fcf_eur_m": 1852, "headcount": 359600, "dividend_eur": 3.25}, "2022FY"),
 ("2023Q1", "2023-05-04", 5729, 10.9, 5867, 6.5, 1.02, G23, "", {"cc_growth_pct": 10.7, "headcount": 357000}, "2023Q1"),
 ("2023Q2", "2023-07-28", None, None, 6101, 1, 1.07, G23, "", {"cc_growth_pct": 5.2, "organic_growth_pct": 4.7}, "2023H1"),
 ("2023H1", "2023-07-28", 11426, 6.9, 11968, 4, None, G23, "Jul-2023: announced EUR2bn investment over 3 years in AI (GenAI) incl. training", {"cc_growth_pct": 7.9, "operating_margin_pct": 12.4, "operating_margin_eur_m": 1413, "organic_fcf_eur_m": -53, "headcount": 349500}, "2023H1"),
 ("2023Q3", "2023-11-07", 5480, -1.3, 5275, 1, 0.96, G23, "Demand for generative AI accelerated in Q3: >100 GenAI projects signed, strong pipeline; Gen AI campus launched", {"cc_growth_pct": 2.3, "cc_growth_9m_pct": 6.0, "organic_growth_9m_pct": 5.5, "revenue_9m_eur_m": 16906, "headcount": 342700}, "2023Q3"),
 ("2023Q4", "2024-02-14", None, None, 6643, 1.7, 1.18, G24a, "", {"cc_growth_pct": -0.2}, "2023FY"),
 ("2023FY", "2024-02-14", 22522, 2.4, 23887, 2.6, 1.06, G24a, "GenAI 'top of mind for all large organizations'; partners incl. Microsoft, Google, AWS, Salesforce, Mistral AI", {"cc_growth_pct": 4.4, "operating_margin_pct": 13.3, "organic_fcf_eur_m": 1963, "headcount": 340400, "dividend_eur": 3.40}, "2023FY"),
 ("2024Q1", "2024-04-30", 5527, -3.5, 5655, -3.5, 1.02, G24a, "Launched GenAI platform for industry use cases; growth reflects client investment in Gen AI", {"cc_growth_pct": -3.3, "organic_growth_pct": -3.6, "headcount": 337200}, "2024Q1"),
 ("2024Q2", "2024-07-26", None, None, 6138, 0, 1.09, G24b, "", {"cc_growth_pct": -1.9, "organic_growth_pct": -2.3, "orders_yoy_note": "stable at constant currency"}, "2024H1"),
 ("2024H1", "2024-07-26", 11138, -2.5, 11793, -1.7, 1.06, G24b, "GenAI drives client discussions; engaging in larger programs to deploy use cases at scale; >120k employees trained on GenAI tools", {"cc_growth_pct": -2.6, "operating_margin_pct": 12.4, "operating_margin_eur_m": 1384, "organic_fcf_eur_m": 163}, "2024H1"),
 ("2024Q3", "2024-10-30", 5377, -1.9, 5222, -0.8, 0.97, G24c, "GenAI bookings ~EUR600m over last 9 months (~3.5% of Group bookings)", {"cc_growth_pct": -1.6, "cc_growth_9m_pct": -2.3, "revenue_9m_eur_m": 16515, "genai_bookings_9m_eur_m": 600, "genai_bookings_share_9m_pct": 3.5}, "2024Q3"),
 ("2024Q4", "2025-02-18", None, None, 6806, None, 1.22, G25a, "GenAI ~5% of Q4 bookings", {"cc_growth_pct": -1.1, "organic_growth_pct": -1.5, "genai_bookings_share_pct": 5}, "2024FY"),
 ("2024FY", "2025-02-18", 22096, -1.9, 23821, None, 1.08, G25a, "GenAI bookings close to 4% of FY2024 bookings (~5% in Q4); >EUR900m GenAI bookings in 2024 (per WNS deal release)", {"cc_growth_pct": -2.0, "operating_margin_pct": 13.3, "organic_fcf_eur_m": 1961, "headcount": 341100, "dividend_eur": 3.40, "genai_bookings_share_pct": 4, "genai_bookings_eur_m_gt": 900}, "2024FY"),
 ("2025Q1", "2025-04-29", 5553, 0.5, 5884, 2.8, 1.06, G25a, "Generative + agentic AI >6% of Q1 bookings", {"cc_growth_pct": -0.4, "headcount": 342700, "genai_bookings_share_pct_gt": 6}, "2025Q1"),
 ("2025Q2", "2025-07-30", None, None, 6109, 1.5, 1.10, G25b, "Generative + agentic AI >7% of Q2 bookings; WNS acquisition (agentic AI-powered Intelligent Operations) announced 2025-07-07", {"cc_growth_pct": 0.7, "genai_bookings_share_pct_gt": 7}, "2025H1"),
 ("2025H1", "2025-07-30", 11107, -0.3, 11993, 2.1, 1.08, G25b, "Strong pipeline in generative and agentic AI; EUR2bn share buyback", {"cc_growth_pct": 0.2, "operating_margin_pct": 12.4, "organic_fcf_eur_m": 60}, "2025H1"),
 ("2025Q3", "2025-10-28", 5393, 0.3, 5161, 1.5, 0.96, G25c, "Robust deal wins in generative and agentic AI; GenAI/agentic >8% of client bookings (Q3 presentation); WNS closed 2025-10-17", {"cc_growth_pct": 2.9, "cc_growth_9m_pct": 1.0, "revenue_9m_eur_m": 16500, "genai_bookings_share_pct_gt": 8}, "2025Q3"),
 ("2025Q4", "2026-02-13", None, None, 7202, None, 1.21, G26a, "Generative + agentic AI >10% of Q4 bookings", {"cc_growth_pct": 10.6, "genai_bookings_share_pct_gt": 10, "note": "Q4 includes WNS and Cloud4C (closed Q4 2025)"}, "2025FY"),
 ("2025FY", "2026-02-13", 22465, 1.7, 24356, 3.9, 1.08, G26a, "GenAI bookings >8% of FY2025 bookings (>10% in Q4)", {"cc_growth_pct": 3.4, "operating_margin_pct": 13.3, "organic_fcf_eur_m": 1949, "net_profit_group_share_eur_m": 1601, "headcount": 423400, "dividend_eur": 3.40, "genai_bookings_share_pct_gt": 8}, "2025FY"),
 ("2026Q1", "2026-04-30", 5943, 7.0, 6054, 6.2, 1.02, G26a, "Generative + agentic AI >11% of Q1 bookings; clients moving to agentic AI projects", {"cc_growth_pct": 11.0, "headcount": 421000, "genai_bookings_share_pct_gt": 11}, "2026Q1"),
 ("2026Q2", "2026-07-30", None, None, 6547, 9.2, 1.07, G26b, "", {"cc_growth_pct": 11.6, "orders_yoy_basis": "year-on-year (basis not stated)"}, "2026H1"),
 ("2026H1", "2026-07-30", 12082, 8.8, 12602, None, 1.04, G26b, "Agentic AI 'at the center of virtually every client conversation'; pipeline expanded substantially; first client investments in new agentic tech stack; no GenAI bookings share disclosed", {"cc_growth_pct": 11.3, "operating_margin_pct": 12.5, "operating_margin_eur_m": 1506, "organic_fcf_eur_m": 37, "headcount": 417600}, "2026H1"),
 ("2026Q3", "2026-10-30", None, None, None, None, None, None, "", {"status": "scheduled 2026-10-30 07:00 Paris; not yet published as of 2026-10-23"}, None),
]

def fmt(x):
    return "" if x is None else x

def main():
    with open(OUT, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ticker", "fiscal_period", "period_end", "release_date", "currency", "unit", "revenue", "revenue_yoy_pct",
                    "orders", "orders_yoy_pct", "book_to_bill", "backlog", "gross_margin_pct", "guidance_text",
                    "guidance_rev_low", "guidance_rev_high", "ai_dc_notes", "extra_json", "source_doc"])
        for fp, rel, rev, yoy, orders, oyoy, b2b, g, ai, ex, src in R:
            yr, per = fp[:4], fp[4:]
            ex = dict(ex)
            if orders is not None and oyoy is not None and "orders_yoy_basis" not in ex:
                ex["orders_yoy_basis"] = "constant currency"
            if g:
                ex["guidance_cc_growth_low"], ex["guidance_cc_growth_high"] = g[1], g[2]
            if "genai_bookings_share_pct_gt" in ex and "genai_bookings_share_pct" not in ex:
                ex["genai_bookings_share_pct"] = ex["genai_bookings_share_pct_gt"]
                ex["genai_bookings_share_qualifier"] = "more than"
            srcp = (SRC % src) if src else ""
            if fp == "2025Q3":
                srcp += ";data/processed/ir_text/CAP.PA/2025Q3_presentation.txt"
            w.writerow([T, fp, "%s-%s" % (yr, PE[per]), rel, "EUR", "EUR m", fmt(rev), fmt(yoy), fmt(orders), fmt(oyoy),
                        fmt(b2b), "", "", g[0] if g else "", "", "", ai, json.dumps(ex, ensure_ascii=False), srcp])
    print("wrote", OUT, len(R))

if __name__ == "__main__":
    main()
