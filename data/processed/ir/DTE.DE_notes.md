# DTE.DE (Deutsche Telekom) — IR notes

## AI / data-center demand narrative (2023–2026)

- **2023-11-02 (13:15 CET, ad hoc):** Ahead of Q3 results, the board proposed raising the 2023 dividend to EUR 0.77 and buying back up to EUR 2bn of shares in 2024. The stated basis was 2023 business performance. This is a capital-return signal, not an AI item. (events: trading_update)
- **2024-08-08 (Q2 2024 call):** Analysts started asking about AI and the data-center/chip build-out. T-Systems was steady, with organic revenue growth slowing to 2.1%. AI was not yet a reported revenue line.
- **2024-10-10/11 (CMD 2024, Bonn):** Targets to 2027 were set: adj. EBITDA AL CAGR of 4–6% and about EUR 1bn of "data, AI & scale" savings outside the US. Expected gross financial impact from AI by 2027 is about EUR 0.8bn. The organisation plan named an "AI Factory" at T-Systems and an AI Competence Center. An ad hoc that evening (18:30 CEST) set a 2024 dividend of EUR 0.90 and a 2025 buyback of up to EUR 2bn.
- **2025-05-15 (Q1 2025 call):** Management described digital sovereignty and the German fiscal stimulus as tailwinds for T-Systems and the German B2B business.
- **2025-08-07 (Q2 2025):** DT said it had partnered with NVIDIA to build "Europe's first industrial AI factory", starting in Q1 2026. Interest in digital-sovereignty offerings was rising. T-Systems order entry was EUR 1,153m (+20.5% y/y, from the backup), and FY guidance was raised again.
- **2025-11-13 (Q3 2025):** DT and NVIDIA had launched the Industrial AI Cloud the week before (early Nov 2025). Combined investment is EUR 1bn, billed as "Europe's largest AI factory", going live in Q1 2026. T-Systems adj. EBITDA AL was EUR 127m (+22.8% organic), but order entry fell to EUR 689m (-20.7% y/y).
- **2026-02-26 (FY2025):** AI-related revenues were "ahead of plan". The 2026 aim is now EUR 200m, on track for the "EUR 700m+" committed at CMD 2024. 2026 EBITDA AL growth will be more modest because of investment in sovereign cloud and AI. 2026 guidance: adj. EBITDA AL about EUR 47.4bn, FCF AL about EUR 19.8bn.
- **2026-05-13 (Q1 2026 call):** The CEO said the Munich Industrial AI Cloud's Blackwell (B200) capacity was "sold out". RTX GPUs were about 40% utilised after three months. Sovereign cloud was named as a key growth area.
- **2026-08-06 (Q2 2026):** All 10,000 Blackwell B200 GPUs in Munich were sold out. Management cited growing demand for sovereign cloud, secure digitisation and AI infrastructure, with T-Systems "our lighthouse". T-Systems order entry was EUR 998m (-13.4% y/y), though a full-year rise is still expected. FCF AL guidance was raised to about EUR 20.0bn. An ad hoc that evening (18:30 CEST) added up to EUR 3bn to the 2026 buyback (AMC).
- **2026-10-05 (AI Investor Day, Bonn; agenda from 12:00):**
  - B2B AI-related revenue is expected at about EUR 250m in 2026, above the EUR 200m ambition. The longer-run ambition is EUR 800m.
  - Gross AI & automation impact is raised to about EUR 1.1bn by 2027, up from about EUR 0.8bn at CMD 2024. About EUR 2.5bn of gross savings is expected by 2030.
  - New AI value pools should add more than EUR 1bn of revenue by 2030.
  - The Industrial AI Cloud is live, with B200 sold out and an extension under way. DT is evaluating an EU AI Gigafactory bid as part of a consortium; partner maincubes targets 400 MW and secured EUR 2.5bn of funding in Jan 2026.
  - DT has invested more than EUR 300m in AI companies.
  - Forecast and mid-term targets were confirmed.

**Read-through for the AI supply chain:** DT is a small but fast-growing AI-factory operator. GPU capacity is sold out, and AI revenue is in the hundreds of millions of euros against roughly EUR 120bn of group revenue. The monetisation story is mostly about sovereignty (T-Systems, sovereign cloud) and AI-driven cost savings, not a large data-center capex cycle.

## Calendar / timing conventions

- **Scheduled results:** 47 quarterly releases, from FY2014 (2015-02-26) to Q2 2026 (2026-08-06). Dates come from telekom.com year pages and newsroom pages (`<meta name=date>`) and match the Yahoo date list exactly.
- **event_type:** Q4 rows are also the FY release, and Q2 rows are also H1.
- **Release times:**
  - DT's own pages document publication at **07:00 CET/CEST**, with a press conference at 10:00 and an analyst call at 13:00–14:00.
  - **Verified 07:00 for:** 2022Q3, 2022Q4, 2023Q1 and 2023Q2 (archived IR and calendar pages, via Wayback), and 2025Q2 and 2025Q3 (current IR page).
  - **All other scheduled rows** have a blank `event_time_local` with `timing=BMO`. BMO there is **inferred** from this documented standard practice; it is not a per-event time stamp.
  - **Q3 2026** is scheduled for 2026-11-05 (07:00 expected). It falls outside the window and is not included.
- **Ad hoc / CMD rows:**
  - **Ad hocs (`trading_update`):** these are capital-return ad hocs, all timed from DT's ad hoc pages: 2023-11-02 13:15 INTRADAY, 2024-10-10 18:30 AMC and 2026-08-06 18:30 AMC.
  - **CMDs:**
    - 2015-02-26/27: no time found (UNKNOWN); same day as the FY2014 release.
    - 2018-05-24: 14:00, the first session.
    - 2021-05-20: media release at 07:00.
    - 2024-10-10: 13:00, the first session.
    - 2026-10-05 AI Investor Day: 12:00, the first session.
- **Ad hocs not included in the events file:** the 2015–2026 ad hocs about TMUS/Sprint (2017-11-04, 2018-04-29, 2020-02-21) and the AGM postponement (2020-03-16). These are M&A and governance items with no fitting event_type.
- **Other:** FY2024 results were pre-announced in the calendar for 2025-02-19 but were published on 2025-02-26.

## KPI file conventions

- **revenue:** group net revenue for the quarter, IFRS, EUR m. `revenue_yoy_pct` is the reported change; organic growth, where stated, is in `extra_json.net_revenue_organic_yoy_pct`.
- **orders:** T-Systems (Systems Solutions segment) order entry in EUR m, adjusted for special factors, from the IR backup PDF. `book_to_bill` and `backlog` are blank because DT does not state them.
- **extra_json fields:**
  - Group: adj. EBITDA AL, FCF AL, service revenue and adj. net profit.
  - T-Systems: total revenue, adj. EBITDA AL and order entry.
  - Guidance: FY adj. EBITDA AL and FCF AL in EUR bn, with qualifier, regex-parsed from the release text.
- **Revenue guidance:** DT gives no numeric revenue guidance, so `guidance_rev_low` and `guidance_rev_high` are blank.
- **ai_dc_notes:** sentences pulled automatically from the release and transcript.

## Gaps

- **Release times:** exact times for most pre-2022 releases are not verified; they are BMO by documented practice.
- **2015 CMD:** no time found.
- **T-Systems order entry:** missing for 2023Q4 (backup layout did not parse) and 2025Q4 (no backup PDF on the year page).
- **T-Systems revenue/EBITDA for 2026Q1:** dropped because the backup layout changed in 2026.
- **Organic growth:** missing for several 2022–2023 quarters because of phrasing differences.
- **Language:** some 2024–2026 interim reports and presentations exist only in German ("Zwischenbericht", "Präsentation"). English versions were used where available.
- **Not downloaded:** annual reports (large).
- **Q3 2026:** not yet reported as of 2026-10-23.

Sources: telekom.com IR financial-results year pages and downloads page, newsroom media information, ad hoc disclosure pages, CMD and AI Investor Day pages; Wayback snapshots of telekom.com IR and financial-calendar detail pages.
