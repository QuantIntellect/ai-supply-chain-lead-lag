# ASML Holding (ASML.AS) — IR collection notes

Collected 2026-10-23. Scripts: `src/ir_agents/semicap/asml_*.py` (shared helpers in `irlib.py`). Raw files: `data/raw/ir/ASML.AS/`.

## Conventions
- Dates are the local Amsterdam publication date. Times are HH:MM in Europe/Amsterdam. Timing is set against the Euronext Amsterdam session (09:00–17:30): before 09:00 = BMO, from 17:30 = AMC, otherwise INTRADAY.
- Each Q4 release also carries the full-year results; it is coded `event_type=Q4`, `fiscal_period=YYYYQ4`.
- Periods: the calendar starts with the Q4 2014 release on 2015-01-21 and runs to the Q3 2026 release on 2026-10-14.
- KPI money columns are in EUR million.
  - `revenue` is total net sales.
  - `orders` is quarterly net (system) bookings.
  - `backlog` is the period-end backlog, either from the press-release key-figures table (systems backlog through 2017Q4, and 2025Q4) or from an explicit text statement. "Around" and exact values are used; "over" values go only into `extra_json`.
  - `guidance_rev_low/high` is the next-quarter total net sales range. Full-year ranges are in `extra_json` (`fy_guidance_*`).
- `book_to_bill` is left blank because ASML never states it. `extra_json.derived_btb_bookings_over_system_sales` is net bookings divided by (total net sales minus Installed Base Management sales), and is a derived figure.
- YoY % is computed from the stated quarterly values in this table.
- `period_end` is the calendar quarter end. ASML's fiscal quarters end on a Sunday close to it, so this date is approximate.

## Release-time basis (important for event studies)
- **Regular results: 07:00 Amsterdam time (BMO).** Three independent sources:
  1. ASML's own pre-announcement text, "available ... at 07:00 CET" or "distributed via GlobeNewswire at 07:00 CET/CEST". This covers 17 releases: Q4 2015 (6-K exhibit, "7.00 am CET (1.00 am EST)"), 2019Q3, 2021Q1, 2021Q2, 2021Q4, 2022Q2, 2022Q4, 2023Q1, 2023Q2, 2023Q4, 2024Q4, 2025Q1–Q4, 2026Q1 and 2026Q2. Most are archived quarter pages on the Wayback Machine, and the URL is in `source_url`.
  2. GlobeNewswire wire-copy timestamps from the StockTitan JSON-LD `datePublished`, converted from UTC. These show exactly 07:00 local for every regular release from 2020Q3 to 2026Q3 (24 quarters), except 2024Q3.
  3. Wayback captures at 07:06 CEST (2022-04-20) and 07:25 CEST (2025-04-16) already show the results.
- ASML writes "CET" all year round, but it means local time.
- The pre-2020Q3 quarters not covered by (1) use the 07:00 convention: 2014Q4–2015Q3, 2016–2018, 2019Q1/Q2/Q4, 2020Q1/Q2 and 2020Q4. No regular release contradicts it. The per-row basis is in `data/raw/ir/ASML.AS/_time_basis.json`.
- **Pre-2016 HH:MM is inferred.** The earliest documented 07:00 is the January 2016 notice for Q4 2015. A 2006 ASML release used 08:00 CET. Either way these releases are BMO.
- **Exception: 2024Q3.** The results were published by accident on **Tue 2024-10-15** during Euronext trading, instead of the scheduled Wed 2024-10-16 07:00.
  - ASML's statement says "technical error ... erroneously published earlier today on part of our website".
  - NL Times reports that trading volume surged "minutes before 4:30 p.m.".
  - The GlobeNewswire release went out at 17:10 CEST and the statement at 18:16 CEST.
  - The row is coded INTRADAY with the time left blank, because the exact minute of the leak (about 16:25) is not documented. Use the 2024-10-15 close-to-close return.
- **CMDs.**
  - 2021-09-29 and 2024-11-14: the release was on the wire at 07:00, so BMO. The programmes ran 13:00–18:00 and 13:00–17:30 the same day.
  - 2022: the release (new 2025/2030 scenarios and a €12bn buyback) became public on **Thu 2022-11-10**, during trading. It was on EDGAR by 16:20 CET (6-K header ACCEPTANCE-DATETIME 10:20:28 ET), and the GlobeNewswire copy went out at 17:24 CET. The row is INTRADAY with the time left blank, because the exact publication minute is not documented.
    - The meeting and webcast were on Fri 2022-11-11, 13:30–16:30 CET. This is a scheduled session, not a publication, so it has no row of its own.
    - The asml.com page reads "Press release - November 10, 2022 ... At the Investor Day meeting on November 11", while the 6-K exhibit reads "November 10, 2022—At the Investor Day meeting today". The presentations in the 2022-11-14 6-K are dated November 11.
  - 2016-10-31 (New York) and 2018-11-08: time unknown.
- **Trading updates and statements.**
  - Berlin fire: first notice 2022-01-03 at 14:30 ("too early" to assess the impact on output) and impact update 2022-01-07 at 13:00. Both are INTRADAY, from wire copies, and both are in the CSV.
  - The export-control statements were not on the wire and are UNKNOWN. 2023-01-28 (Saturday) and 2024-01-01 (holiday) fall before the next open.
- **EDGAR caveat for the project lead.** In the raw data.sec.gov submissions JSON, and so in `data/processed/edgar_filings.parquet`, `acceptanceDateTime` is **not UTC**.
  - ASML 6-K 0001628280-25-045043: the filing header shows ACCEPTANCE-DATETIME 2025-10-15 06:01:05 ET, while the JSON/parquet shows 14:01:05Z. True UTC would be 10:01:05Z.
  - The same pattern holds for 0001628280-26-003701 (header 06:03:31 ET, JSON 16:03:31Z) and for Donnelley-filed 6-Ks.
  - The JSON value equals header ET + 8h under EDT and + 10h under EST.
  - The same holds for a US filer: NVDA 8-K 0001045810-26-000073 has header 2026-08-26 16:21:19 ET, but the parquet shows 2026-08-27T00:21:19Z.
  - Treating the field as UTC therefore turns pre-market US filings into intraday ones, and moves after-close filings onto the next calendar date. Use the `-index-headers.html` ACCEPTANCE-DATETIME (ET) instead.
  - ASML's results 6-Ks are filed when EDGAR opens (about 06:00 ET), hours after the 07:00 CET release, so they were not used as release times.

## Non-results events included
- **CMD (Investor Days):**
  - 2016-10-31: New York, "ASML Affirms 2020 Growth Opportunity".
  - 2018-11-08: Veldhoven.
  - 2021-09-29: virtual, long-term outlook raised.
  - 2022-11-10: new 2025/2030 scenarios and a €12bn buyback.
  - 2024-11-14: 2030 revenue of about €44–60bn and gross margin of about 56–60%.
  - The Q2 2026 deck schedules the next CMD for 2027-06-10. It is outside the window.
- **profit_warning:** 2020-03-30, "ASML updates the market on expected Q1 2020 results" (COVID-19). Q1 sales fell below guidance and revenue shifted to later quarters.
- **trading_update:**
  - 2018-12-03: delivery delays at the start of 2019 caused by a fire at a supplier.
  - 2022-01-03 and 2022-01-07: Berlin fire notice, then its impact assessment on output.
  - Export-control statements that address the financial outlook: 2023-01-28, 2023-03-08, 2023-06-30, 2023-10-17, 2024-01-01, 2024-09-06 and 2024-12-02 ("impact ... to fall within outlook for 2025"). On 2024-12-02 a second statement was published on the same day; it is not listed separately.
- **Not included:** AGM results, buyback reports, management changes (for example the CEO succession on 2023-11-30), and the 2026-01-28 "strengthening focus on engineering" statement, which was issued with the Q4 2025 results.

## Documents (`ASML.AS_manifest.csv`)
- **Press releases:** 48 quarterly releases from 2014Q4 to 2026Q3, taken from the EDGAR 6-K exhibits (HTML), plus 6 special releases.
- **IR presentations:** 45, from EDGAR 6-K exhibits (HTML with slide text). Missing for 2014Q4, 2015Q1 and 2020Q2.
- **Transcripts (43), all published by ASML itself:**
  - Investor-call transcripts or prepared remarks: 2018Q1–2019Q2, 2020Q1, 2020Q3, 2021Q2, 2022Q4, 2023Q4, 2024Q1–2025Q4 (except 2025Q1/Q2) and 2026Q1–Q2.
  - Video-interview transcripts for most quarters from 2018Q3 to 2026Q1.
  - They come from `ourbrand.asml.com` and the Sitecore edge host. The `/static-files/` links on the current asml.com results page return 404 after a locale redirect.
- **Text:** `data/processed/ir_text/ASML.AS/<period>_{press_release,presentation,transcript,video_transcript}.txt`.

## Gaps
- **Missing call transcripts:** 2022Q1–Q3, 2023Q1–Q3, 2025Q1, 2025Q2 and 2026Q3. They are listed on asml.com, but the links are broken and no working copy was found.
- **Missing video transcripts:** 2019Q3, 2020Q4, 2021Q3, 2022Q1, 2022Q2, 2023Q1, 2023Q2, 2026Q2 and 2026Q3.
- **Orders:** blank for 2026Q1–Q3. ASML stopped reporting quarterly bookings after 2025 and now reports systems backlog once a year.
- **Backlog:** blank for 2018–2021Q1 and for most non-Q4 quarters after that. It was not stated as a number.
- **Next-quarter guidance:** 2020Q1 has none because ASML withdrew guidance.
- **China:** the China share of system sales is on the presentation slides (`*_presentation.txt`) but was not parsed into the KPI file.

## Demand narrative 2023–2026
- **2023-01-25 (Q4'22):** Q4 net bookings were €6.3bn and FY22 bookings a record €30.7bn. The year-end backlog was €40.4bn. ASML guided 2023 net sales growth of more than 25% and a Q1'23 range of €6.1–6.5bn, while flagging macro and export-control uncertainty.
- **2023-04-19 (Q1'23):** Bookings fell to €3.75bn, with a backlog of over €38.9bn. ASML described "mixed signals on demand" as some major customers adjusted the timing of their demand while others absorbed it, particularly in DUV.
- **2023-10-18 (Q3'23):** Bookings were €2.6bn, the low of the cycle. ASML called 2024 a "transition year" with revenue similar to 2023, because customers were uncertain about the shape of the recovery.
- **2024-01-24 (Q4'23):** Bookings were a record €9.2bn, of which €5.6bn EUV. The backlog was about €39bn. ASML kept its view of a flat 2024 and guided Q1'24 at €5.0–5.5bn.
- **2024-04-17 (Q1'24):** Sales were €5.3bn, down 21.6% YoY, and bookings €3.6bn. ASML kept its view of a 2024 weighted toward the second half.
- **2024-07-17 (Q2'24):** Bookings were €5.6bn. The CEO statement named AI the main driver: "strong developments in AI, driving most of the industry recovery and growth".
- **2024-10-15 (Q3'24, published early and intraday):** Bookings were €2.6bn, against a consensus of about €5.4bn according to press reports. ASML cut its 2025 view to €30–35bn, the lower half of its earlier range. It cited Logic fab push-outs caused by competitive foundry dynamics (affecting EUV timing), limited Memory capacity additions and a slower non-AI recovery.
- **2024-11-14 (Investor Day):** ASML confirmed its 2030 scenarios of about €44–60bn revenue and about 56–60% gross margin, with AI as the key growth driver.
- **2025-01-29 (Q4'24):** Bookings were €7.1bn, of which €3.0bn EUV. ASML called AI "the key driver for growth" and confirmed 2025 at €30–35bn. On the call it said bookings would be reported only through 2025.
- **2025-07-16 (Q2'25):** Bookings were €5.5bn. "AI customers' fundamentals remain strong", but because of macro and geopolitical uncertainty ASML "cannot confirm" growth in 2026. It guided FY25 at about +15%.
- **2025-10-15 (Q3'25):** Bookings were €5.4bn, of which €3.6bn EUV. ASML said AI momentum was extending to more customers in leading-edge Logic and advanced DRAM. It expected China sales to decline significantly in 2026 and said 2026 sales would not be below 2025.
- **2026-01-28 (Q4'25):** Bookings were a record €13.2bn, of which €7.4bn EUV, with Memory at 56%. The year-end backlog was €38.8bn. ASML guided 2026 at €34–39bn as customers grew more confident that AI demand would last. These are the last quarterly bookings reported.
- **2026-04-15 / 2026-07-15:** ASML raised its 2026 guidance to €36–40bn, and then to €43–45bn with a gross margin of 54–56%. It cited AI-related infrastructure investment in advanced Logic and Memory. The 2026 range was said to accommodate the outcomes of ongoing export-control discussions.
- **2026-10-14 (Q3'26):** Sales were €11.7bn, up 55% YoY, with a gross margin of 57.5%. ASML narrowed FY26 to €44–45bn and guided Q4'26 at €14.2–15.2bn. "Customers continue to increase their short- and medium-term equipment demand forecasts", driven by the size and duration of AI investment.
