"""RR.L KPI panel (FY2022H1 -> FY2026H1 + trading updates with figures). Values transcribed from
the RNS results statements (Investegate body copies) and results presentations; a self-check
verifies that each transcribed figure string occurs in its cited source text."""
import sys; sys.path.insert(0, "/Users/sinamirzaei/Documents/aimapping/src/ir_agents/energy"); import irlib
import os, re, json
import rr_common as C

man = irlib.read_csv("data/processed/ir/RR.L_manifest.csv")


def doc(fp, dt, contains=""):
    hits = [m["local_path"] for m in man if m["fiscal_period"] == fp and m["doc_type"] == dt and contains in m["local_path"]]
    assert len(hits) == 1, (fp, dt, contains, hits)
    return hits[0]


def seg(rev=None, org=None, uop=None, margin=None, orders=None, oyoy=None, b2b=None, backlog=None, **kw):
    d = {"revenue": rev, "organic_growth_pct": org, "underlying_operating_profit": uop, "margin_pct": margin,
         "orders": orders, "orders_yoy_pct": oyoy, "book_to_bill": b2b, "backlog": backlog}
    d.update(kw)
    return {k: v for k, v in d.items() if v is not None}


MARGIN_DEF = "underlying operating margin (underlying operating profit / underlying revenue)"
REV_BASIS = "underlying revenue (at hedge-book achieved FX rates; RR's headline revenue measure)"
PSBL = "Power Systems order backlog per results presentation divisional slide"

ROWS = [
  dict(fp="FY2022H1", pe="2022-06-30", rd="2022-08-04", rev=5308,
       g="2022 guidance (set 24 Feb 2022) unchanged: low-to-mid-single-digit underlying revenue growth; underlying operating margin broadly unchanged on 2021 (3.8%); modestly positive free cash flow.",
       dc="Power Systems: record order intake, demand strongest for power generation 'with orders including mission critical backup power for data centres for very large customers worldwide'. Rolls-Royce SMR design going through the UK Generic Design Assessment (GDA).",
       ej={"organic_growth_pct": 4, "revenue_prior": 5227, "statutory_revenue": 5600, "underlying_operating_profit": 125,
           "margin_pct": 2.4, "free_cash_flow": -68, "free_cash_flow_def": "free cash flow from continuing operations (group FCF incl. discontinued: -77)",
           "segments": {"Power Systems": seg(1371, None, 119, 8.7, 2100, 53, 1.5, 3700, revenue_growth_pct_stated=20, backlog_label="order book"),
                        "Civil Aerospace": seg(2339, None, -79, -3.4, revenue_growth_pct_stated=8),
                        "Defence": seg(1609, None, 189, 11.7, 1400, None, 0.9, 6500, backlog_label="order book")}},
       checks=["5,308", "5,227", "(68)", "2.4%", "£2.1bn was 53%", "1.5x", "8.7%", "2,339", "1,609", "£1.4bn with a book-to-bill ratio of 0.9x", "£6.5bn"],
       deck_checks=["£3.7bn"]),
  dict(fp="FY2022", pe="2022-12-31", rd="2023-02-23", rev=12691,
       g="2023 guidance: underlying operating profit £0.8-£1.0bn; free cash flow £0.6-£0.8bn.",
       go=[("underlying_operating_profit", 800, 1000, "GBP m", 2023), ("free_cash_flow", 600, 800, "GBP m", 2023)],
       dc="Power Systems order intake +29% to a record £4.3bn, with strong demand notably in Power Generation 'including mission critical backup power'; 76% order cover for 2023. New Markets R&D (£108m) included design development to ready the SMR to progress through the UK GDA.",
       ej={"organic_growth_pct": 14, "revenue_prior": 10947, "statutory_revenue": 13520, "underlying_operating_profit": 652,
           "margin_pct": 5.1, "free_cash_flow": 505, "free_cash_flow_def": "free cash flow (continuing operations)",
           "segments": {"Power Systems": seg(3347, 23, 281, 8.4, 4300, 29, 1.3, 4000),
                        "Civil Aerospace": seg(5686, 25, 143, 2.5),
                        "Defence": seg(3660, 2, 432, 11.8, 5400, None, 1.5, 8500)}},
       checks=["12,691", "10,947", "505", "5.1%", "£4.3bn, 29% higher", "3,347 23%", "8.4%", "5,686 25%", "3,660 2%", "£8.5bn", "£5.4bn"],
       deck_checks=["£4.3bn Up 29% 1.3x book to bill £4.0bn"]),
  dict(fp="FY2023Q2", pe="2023-06-30", rd="2023-07-26", rev=None, tu=True,
       g="Trading update (pre-H1): full-year 2023 guidance raised to underlying operating profit £1.2-£1.4bn (consensus £934m) and free cash flow £0.9-£1.0bn (consensus £732m); H1 underlying operating profit expected £660-£680m and FCF £340-£360m.",
       go=[("underlying_operating_profit", 1200, 1400, "GBP m", 2023), ("free_cash_flow", 900, 1000, "GBP m", 2023),
           ("h1_underlying_operating_profit_prelim", 660, 680, "GBP m", 2023), ("h1_free_cash_flow_prelim", 340, 360, "GBP m", 2023)],
       dc="",
       ej={"guidance_change": "raised"},
       checks=["£660m-£680m", "£340m-£360m", "£1.2bn-£1.4bn", "£0.9bn-£1.0bn"]),
  dict(fp="FY2023H1", pe="2023-06-30", rd="2023-08-03", rev=6950,
       g="2023 guidance (raised 26 July 2023): underlying operating profit £1.2-£1.4bn; free cash flow £0.9-£1.0bn.",
       go=[("underlying_operating_profit", 1200, 1400, "GBP m", 2023), ("free_cash_flow", 900, 1000, "GBP m", 2023)],
       dc="Power Systems order intake £1.9bn (-14%), book-to-bill 1.1x, record order cover; OE revenue +33% driven by stationary PowerGen equipment. Rolls-Royce SMR entered stage 2 of the UK GDA.",
       ej={"organic_growth_pct": 28, "revenue_prior": 5308, "statutory_revenue": 7523, "underlying_operating_profit": 673,
           "margin_pct": 9.7, "free_cash_flow": 356,
           "segments": {"Power Systems": seg(1774, 24, 125, 7.0, 1900, -14, 1.1, 3900),
                        "Civil Aerospace": seg(3257, 38, 405, 12.4),
                        "Defence": seg(1913, 15, 261, 13.6, 2700, 87, 1.4, 8900)}},
       checks=["6,950", "5,308", "356", "9.7%", "£1.9bn, 14% lower", "Book to bill was 1.1x", "1,774 24%", "7.0%", "3,257 38%", "1,913 15%"],
       deck_checks=["£1.9bn Down 14% 1.1x book to bill £3.9bn", "£2.7bn Up 87% 1.4x book to bill £8.9bn"]),
  dict(fp="FY2023", pe="2023-12-31", rd="2024-02-22", rev=15409,
       g="2024 guidance: underlying operating profit £1.7-£2.0bn; free cash flow £1.7-£1.9bn. Mid-term targets (CMD 28 Nov 2023, 2027 timeframe): underlying operating profit £2.5-£2.8bn, margin 13-15%, FCF £2.8-£3.1bn, return on capital 16-18%.",
       go=[("underlying_operating_profit", 1700, 2000, "GBP m", 2024), ("free_cash_flow", 1700, 1900, "GBP m", 2024),
           ("midterm_underlying_operating_profit", 2500, 2800, "GBP m", 2027), ("midterm_operating_margin", 13, 15, "%", 2027),
           ("midterm_free_cash_flow", 2800, 3100, "GBP m", 2027), ("midterm_return_on_capital", 16, 18, "%", 2027)],
       dc="Power Systems revenue +16% with 34% growth in power generation 'driven by data centre growth, where we have a leading position'; power generation profitability tripled. Rolls-Royce SMR progressing through stage two of the UK GDA.",
       ej={"organic_growth_pct": 21, "revenue_prior": 12691, "statutory_revenue": 16486, "underlying_operating_profit": 1590,
           "margin_pct": 10.3, "free_cash_flow": 1285,
           "segments": {"Power Systems": seg(3968, 16, 413, 10.4, 4300, None, 1.1, 4100, orders_yoy_text="flat year on year", power_generation_revenue_growth_pct=34),
                        "Civil Aerospace": seg(7348, 29, 850, 11.6),
                        "Defence": seg(4077, 12, 562, 13.8, 5200, None, 1.3, 9200)}},
       checks=["15,409", "12,691", "1,285", "10.3%", "Order intake in Power Systems was £4.3bn, flat", "book-to-bill ratio of 1.1x", "3,968 16%", "34% growth in the power generation", "7,348 29%", "4,077 12%", "£1.7bn-£2.0bn", "£1.7bn-£1.9bn", "£2.5bn-£2.8bn"],
       deck_checks=["£4.3bn ORDER INTAKE Book-to-bill ratio 1.1x £4.1bn ORDER BACKLOG", "£5.2bn ORDER INTAKE Book-to-bill ratio 1.3x £9.2bn"]),
  dict(fp="FY2024H1", pe="2024-06-30", rd="2024-08-01", rev=8182,
       g="2024 guidance raised: underlying operating profit £2.1-£2.3bn (previous £1.7-£2.0bn); free cash flow £2.1-£2.2bn (previous £1.7-£1.9bn). Mid-term targets (2027) reiterated.",
       go=[("underlying_operating_profit", 2100, 2300, "GBP m", 2024), ("free_cash_flow", 2100, 2200, "GBP m", 2024),
           ("midterm_underlying_operating_profit", 2500, 2800, "GBP m", 2027), ("midterm_free_cash_flow", 2800, 3100, "GBP m", 2027)],
       dc="Power Systems capturing 'strong demand for data centres' in Power Generation (PG revenue +15%), orders +26% with book-to-bill 1.3x. Rolls-Royce SMR completed step 2 of the UK GDA and moved to step 3 on 30 Jul 2024; shortlisted by Vattenfall (Sweden).",
       ej={"organic_growth_pct": 19, "revenue_prior": 6950, "statutory_revenue": 8861, "underlying_operating_profit": 1149,
           "margin_pct": 14.0, "free_cash_flow": 1158, "guidance_change": "raised",
           "segments": {"Power Systems": seg(1837, 6, 189, 10.3, 2400, 26, 1.3, 4600, power_generation_revenue_growth_pct=15),
                        "Civil Aerospace": seg(4119, 27, 740, 18.0),
                        "Defence": seg(2219, 18, 345, 15.5, 1700, None, 0.8, 8500)}},
       checks=["8,182", "6,950", "1,158", "14.0%", "£2.4bn, 26% up", "book-to-bill ratio of 1.3x", "1,837 6%", "10.3%", "4,119 27%", "2,219 18%", "£2.1bn-£2.3bn", "£2.1bn-£2.2bn", "15%"],
       deck_checks=["£2.4bn ORDER INTAKE Book-to-bill ratio 1.3x £4.6bn ORDER BACKLOG", "£1.7bn ORDER INTAKE Book-to-bill ratio 0.8x £8.5bn"]),
  dict(fp="FY2024", pe="2024-12-31", rd="2025-02-27", rev=17848,
       g="2025 guidance: underlying operating profit £2.7-£2.9bn; free cash flow £2.7-£2.9bn. Upgraded mid-term targets (2028): underlying operating profit £3.6-£3.9bn, margin 15-17%, FCF £4.2-£4.5bn, return on capital 18-21%.",
       go=[("underlying_operating_profit", 2700, 2900, "GBP m", 2025), ("free_cash_flow", 2700, 2900, "GBP m", 2025),
           ("midterm_underlying_operating_profit", 3600, 3900, "GBP m", 2028), ("midterm_operating_margin", 15, 17, "%", 2028),
           ("midterm_free_cash_flow", 4200, 4500, "GBP m", 2028), ("midterm_return_on_capital", 18, 21, "%", 2028)],
       dc="Power Systems: data centre orders +42% yoy; power generation revenue +25% and data centre revenue +46%. Rolls-Royce SMR named preferred supplier by the Czech Government/ČEZ (late 2024); shortlisted in UK (one of four) and Sweden (one of two, Vattenfall).",
       ej={"organic_growth_pct": 17, "revenue_prior": 15409, "statutory_revenue": 18909, "statutory_revenue_yoy_pct": 15,
           "underlying_operating_profit": 2464, "margin_pct": 13.8, "free_cash_flow": 2425,
           "segments": {"Power Systems": seg(4271, 11, 560, 13.1, 5100, 19, 1.2, 4800, data_centre_orders_yoy_pct=42,
                                              power_generation_revenue_growth_pct=25, data_centre_revenue_growth_pct=46),
                        "Civil Aerospace": seg(9040, 24, 1505, 16.6),
                        "Defence": seg(4522, 13, 644, 14.2, 13300, None, 2.9, 17400)}},
       checks=["17,848", "15,409", "2,425", "13.8%", "£5.1bn, up 19%", "book-to-bill ratio of 1.2x", "data centre orders up 42%", "by 46% for data centres", "4,271 11%", "9,040 24%", "4,522 13%", "£2.7bn-2.9bn", "£3.6bn-£3.9bn"],
       deck_checks=["£5.1bn ORDER INTAKE Book-to-bill ratio 1.2x £4.8bn ORDER BACKLOG", "£13.3bn ORDER INTAKE Book-to-bill ratio 2.9x £17.4bn"]),
  dict(fp="FY2025Q1", pe="2025-03-31", rd="2025-05-01", rev=None, tu=True,
       g="AGM trading update: 2025 guidance of underlying operating profit £2.7-£2.9bn and free cash flow £2.7-£2.9bn reiterated despite tariff and supply-chain uncertainty.",
       go=[("underlying_operating_profit", 2700, 2900, "GBP m", 2025), ("free_cash_flow", 2700, 2900, "GBP m", 2025)],
       dc="Power Systems revenue growth led by power generation, 'driven by continued demand for back-up power generators for data centres'; order intake up with book-to-bill 1.5x; next-generation engine (EIS 2028) in prototype testing. ČEZ made a strategic investment in Rolls-Royce SMR in March; final tender submitted to Great British Nuclear in April (decision expected June); only company in Step 3 of the UK GDA.",
       ej={"guidance_change": "reiterated", "segments": {"Power Systems": seg(b2b=1.5)}},
       checks=["book-to-bill ratio of 1.5x", "back-up power generators for data centres", "made a strategic investment into the business in March"]),
  dict(fp="FY2025H1", pe="2025-06-30", rd="2025-07-31", rev=9057,
       g="2025 guidance raised: underlying operating profit £3.1-£3.2bn; free cash flow £3.0-£3.1bn. Mid-term targets (2028) reiterated: underlying operating profit £3.6-£3.9bn, FCF £4.2-£4.5bn.",
       go=[("underlying_operating_profit", 3100, 3200, "GBP m", 2025), ("free_cash_flow", 3000, 3100, "GBP m", 2025),
           ("midterm_underlying_operating_profit", 3600, 3900, "GBP m", 2028), ("midterm_free_cash_flow", 4200, 4500, "GBP m", 2028)],
       dc="Power Systems order intake +32% (book-to-bill 1.4x) with power generation orders +68%, including an 85% yoy increase in data centre orders; data centre revenue +45%. Rolls-Royce SMR selected as sole provider of the UK's first SMR programme.",
       ej={"organic_growth_pct": 13, "revenue_prior": 8182, "statutory_revenue": 9490, "statutory_revenue_yoy_pct": 7,
           "underlying_operating_profit": 1733, "margin_pct": 19.1, "free_cash_flow": 1582, "guidance_change": "raised",
           "segments": {"Power Systems": seg(2042, 20, 313, 15.3, 2900, 32, 1.4, 5600, power_generation_orders_yoy_pct=68,
                                              data_centre_orders_yoy_pct=85, power_generation_revenue_growth_pct=26,
                                              data_centre_revenue_growth_pct=45),
                        "Civil Aerospace": seg(4786, 17, 1193, 24.9),
                        "Defence": seg(2223, 1, 342, 15.4, 4000, None, 1.8, 18800)}},
       checks=["9,057", "8,182", "1,582", "19.1%", "£2.9bn with a book-to-bill ratio of 1.4x", "32% increase", "rose by 68%", "85% year on year increase in data centre orders", "data centre revenue growth of 45%", "2,042 20%", "4,786 17%", "2,223 1%", "£3.1bn-£3.2bn", "£3.0bn-£3.1bn"],
       deck_checks=["£2.9bn ORDER INTAKE Book-to-bill ratio 1.4x £5.6bn ORDER BACKLOG", "£4.0bn ORDER INTAKE Book-to-bill ratio 1.8x £18.8bn"]),
  dict(fp="FY2025", pe="2025-12-31", rd="2026-02-26", rev=20059,
       g="2026 guidance: underlying operating profit £4.0-£4.2bn; free cash flow £3.6-£3.8bn. Upgraded mid-term targets (2028): underlying operating profit £4.9-£5.2bn, margin 18-20%, FCF £5.0-£5.3bn, return on capital 23-26%.",
       go=[("underlying_operating_profit", 4000, 4200, "GBP m", 2026), ("free_cash_flow", 3600, 3800, "GBP m", 2026),
           ("midterm_underlying_operating_profit", 4900, 5200, "GBP m", 2028), ("midterm_operating_margin", 18, 20, "%", 2028),
           ("midterm_free_cash_flow", 5000, 5300, "GBP m", 2028), ("midterm_return_on_capital", 23, 26, "%", 2028)],
       dc="Power Systems order intake £6.1bn (+21%, book-to-bill 1.2x) with power generation orders +31%; power generation revenue +30% including data centre revenue +35%; capacity expansion in Germany and US (Aiken, Mankato) 'driven by data centres'; new fast-start gas generator for data-centre prime power; next-gen Series 4000 (2028) targets data centres. Rolls-Royce SMR in final stage of Vattenfall's Swedish competition; ČEZ strategic investment.",
       ej={"organic_growth_pct": 14, "revenue_prior": 17848, "statutory_revenue": 21207, "statutory_revenue_yoy_pct": 12,
           "underlying_operating_profit": 3462, "margin_pct": 17.3, "free_cash_flow": 3270,
           "segments": {"Power Systems": seg(4892, 19, 852, 17.4, 6100, 21, 1.2, 6100, power_generation_orders_yoy_pct=31,
                                              power_generation_revenue_growth_pct=30, data_centre_revenue_growth_pct=35),
                        "Civil Aerospace": seg(10382, 15, 2130, 20.5),
                        "Defence": seg(4772, 8, 689, 14.4, 5500, None, 1.1, 17400)}},
       checks=["20,059", "17,848", "3,270", "17.3%", "£ 6.1 bn, a 21 % increase", "book-to-bill ratio of 1.2 x", "order intake rose by 31 %", "data centre revenue growth of 35 %", "4,892 19%", "10,382 15%", "4,772 8%", "£4.0bn-£4.2bn", "£3.6bn-£3.8bn", "£4.9bn-£5.2bn", "£ 17.4 bn"],
       deck_checks=["£6.1bn ORDER INTAKE Book-to-bill ratio 1.2x £6.1bn ORDER BACKLOG"]),
  dict(fp="FY2026Q1", pe="2026-03-31", rd="2026-04-30", rev=None, tu=True,
       g="AGM trading update: 2026 guidance of underlying operating profit £4.0-£4.2bn and free cash flow £3.6-£3.8bn reiterated.",
       go=[("underlying_operating_profit", 4000, 4200, "GBP m", 2026), ("free_cash_flow", 3600, 3800, "GBP m", 2026)],
       dc="Power Systems strong start 'driven by power generation, led by data centres': power generation order intake across gas and diesel engines ~50% higher yoy in Q1; March a record month for orders; Power Systems order backlog £7.3bn at 31 March.",
       ej={"guidance_change": "reiterated", "backlog_def": "Power Systems order backlog at 31 March 2026 as stated in the AGM trading update; no group total stated",
           "segments": {"Power Systems": seg(backlog=7300, power_generation_orders_yoy_pct_approx=50)}},
       checks=["£7.3bn", "around 50% higher"]),
  dict(fp="FY2026H1", pe="2026-06-30", rd="2026-07-30", rev=11279,
       g="2026 guidance raised: underlying operating profit £4.7-£4.9bn; free cash flow £3.8-£4.0bn (previous £4.0-£4.2bn / £3.6-£3.8bn).",
       go=[("underlying_operating_profit", 4700, 4900, "GBP m", 2026), ("free_cash_flow", 3800, 4000, "GBP m", 2026)],
       dc="Power Systems order intake £4.6bn (>50% increase, book-to-bill 1.8x); power generation orders +55% 'reflecting strong demand for backup and prime power solutions for data centres', supported by framework agreements with data centre customers; power generation revenue +41%. Rolls-Royce SMR successful in every competitive European nuclear tender; selected by Videberg Kraft to supply three SMRs in Sweden.",
       ej={"organic_growth_pct": 26, "revenue_prior": 9057, "statutory_revenue": 11448, "statutory_revenue_yoy_pct": 21,
           "underlying_operating_profit": 2534, "margin_pct": 22.5, "free_cash_flow": 1964, "guidance_change": "raised",
           "segments": {"Power Systems": seg(2604, 28, 528, 20.3, 4600, None, 1.8, 8000, orders_yoy_text="more than a 50% increase",
                                              power_generation_orders_yoy_pct=55, power_generation_revenue_growth_pct=41),
                        "Civil Aerospace": seg(6186, 29, 1567, 25.3),
                        "Defence": seg(2484, 17, 522, 21.0, 2400, None, 1.0, 17500)}},
       checks=["11,279", "9,057", "1,964", "22.5%", "£ 4.6 bn, more than a 50 % increase", "book-to-bill ratio of 1.8 x", "rose by 55%", "growth was 41 %", "2,604 28%", "6,186 29%", "2,484 17%", "£4.7bn-£4.9bn", "£3.8bn-£4.0bn", "£17.5bn"],
       deck_checks=["£4.6bn ORDER INTAKE Book-to-bill ratio 1.8x £8.0bn ORDER BACKLOG"]),
]


def text_of(local_path):
    for f in os.listdir(os.path.join(irlib.TEXT_IR, C.TICKER)):
        p = os.path.join(irlib.TEXT_IR, C.TICKER, f)
        with open(p, encoding="utf-8") as fh:
            if fh.readline().strip() == f"[source: {local_path}]":
                return re.sub(r"\s+", " ", fh.read())
    raise FileNotFoundError(local_path)


def main():
    out, problems = [], []
    for r in ROWS:
        fp = r["fp"]
        src = doc(fp, "trading_update" if r.get("tu") else "press_release", "rns_")
        t = text_of(src)
        for c in r.get("checks", []):
            if re.sub(r"\s+", " ", c) not in t:
                problems.append((fp, "PR", c))
        ej = dict(r["ej"])
        if r.get("deck_checks"):
            deck = doc(fp, "presentation", "_presentation.pdf")
            td = text_of(deck)
            for c in r["deck_checks"]:
                if c not in td:
                    problems.append((fp, "deck", c))
            ej["segment_orders_backlog_source"] = deck
            ej["backlog_def"] = "segment order backlog (firm orders, no right to cancel) as shown on results presentation divisional slides; no group total stated"
        if r.get("rev") is not None:
            ej["revenue_basis"] = REV_BASIS
            ej["margin_def"] = MARGIN_DEF
            ej["organic_growth_def"] = "RR 'organic change': constant translational currency, excl. M&A"
        if r.get("go"):
            ej["guidance_other"] = [{"metric": m, "low": lo, "high": hi, "unit": u, "fiscal_year": y} for m, lo, hi, u, y in r["go"]]
        out.append({"fiscal_period": fp, "period_end": r["pe"], "release_date": r["rd"], "currency": "GBP", "unit": "m",
                    "revenue": r.get("rev"), "revenue_yoy_pct": None, "orders": None, "orders_yoy_pct": None,
                    "book_to_bill": None, "backlog": None, "gross_margin_pct": None, "guidance_text": r["g"],
                    "guidance_rev_low": None, "guidance_rev_high": None, "ai_dc_notes": r["dc"], "extra_json": ej,
                    "source_doc": src})
    print("CHECK PROBLEMS:", problems)
    irlib.write_kpis(C.TICKER, out)


if __name__ == "__main__":
    main()
