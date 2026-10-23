# ENR.DE - Siemens Energy AG: IR notes

Coverage starts at the listing on 2020-09-28, when Siemens Energy was spun off from Siemens AG. The calendar does not include any Siemens AG dates from before the listing. The only pre-listing row is the spin-off Capital Markets Day (2020-09-01, Munich, virtual). The fiscal year ends 30 Sep, so FY2025Q1 = Oct-Dec 2024. All figures are in EUR m; the source documents state them in EUR m, or in EUR bn multiplied by 1000.

## Demand narrative, 2023-2026 (dated)

- **2023-01-19 (ad hoc, 19:56 CET):** Q1 FY23 orders came in at EUR 12,727m against a consensus of EUR 9,453m. Even so, Siemens Gamesa charges led the company to cut its FY23 profit-margin guidance to 1-3% (from 2-4%). The Q1 release on 2023-02-07 attributed the orders surge to a large Grid Technologies (GT) grid-connection order in Germany and "strong demand in the USA". GT orders were EUR 6.3bn.
- **2023-06-22 (ad hoc, 19:22 CEST):** Profit guidance withdrawn. Siemens Gamesa onshore quality costs were "likely to be in excess of 1 bn Euro". At Q3 (2023-08-07) the FY23 outlook became: profit margin before Special items (SI) of -10% to -8%, and a net loss of about EUR 4.5bn. Group orders still rose 51% nominal to EUR 14.9bn.
- **2023-10-26 (ad hoc, 10:41, intraday):** Responding to reports of guarantee talks with the German government, the company said FY23 results would be "fully in line with guidance". It added that the former Gas and Power businesses were on track for their FY25 mid-term targets.
- **2023-11-15 / 2023-11-21 (FY23 results and CMD Hamburg):** FY23 orders were EUR 50.4bn and the backlog EUR 112bn. FY24 guidance was 3-7% comparable revenue growth.
- **2024-01-23 to 2024-08-07 (FY24 Q1-Q3):**
  - 2024-01-23: Q1 pre-released above expectations; orders EUR 15.4bn, +23.9% comparable.
  - Q1 release: GT book-to-bill 3.96, GT backlog EUR 28bn.
  - 2024-05-08: FY24 revenue guidance raised to 10-12% comparable growth; GT backlog at a record EUR 30bn.
  - Q3: record Gas Services (GS) order intake, and record backlogs at both GS and GT.
- **2024-11-12 (19:37 ad hoc, then the FY24 release at 19:44 CET, the evening before the ER dateline):** FY24 orders EUR 50.2bn, backlog EUR 123bn. The FY28 margin target was raised to 10-12% (from 8% or above). FY25 guidance: 8-10% comparable growth, 3-5% margin.
- **2025-01-27 (ad hoc, 19:40):** Q1 FY25 pre-release. Free cash flow (FCF) pre tax was strong enough that the company expected to exceed its FY25 FCF guidance of up to EUR 1bn.
- **2025-04-16 (ad hoc, 19:25):** FY25 outlook raised to 13-15% comparable revenue growth (from 8-10%) and a 4-6% margin (from 3-5%). In Q2 (released 2025-05-08), GS booked its highest quarterly orders to date, EUR 7.0bn.
- **2025-11-13 (FY25 results, AMC; ad hoc 21:15):**
  - FY25 orders EUR 58.9bn (GS EUR 23.0bn, GT EUR 21.4bn), backlog EUR 138bn.
  - The FY26 outlook explicitly cites "the strong growth of data centers". Guidance: 11-13% comparable growth, 9-11% margin.
  - The FY28 margin target was raised to 14-16%.
  - Capital Market Day followed on 2025-11-20.
- **2026-02-11 (Q1 FY26):** Orders EUR 17.6bn, of which GS EUR 8.75bn. The release describes "robust demand ... with strong data center expansion".
- **2026-04-23 (ad hoc, 17:55, AMC):**
  - FY26 outlook raised to 14-16% comparable growth (from 11-13%) and a 10-12% margin (from 9-11%).
  - Net income about EUR 4bn; FCF pre tax about EUR 8bn (from EUR 4-5bn).
  - GT revenue-growth assumption raised to 25-27%.
  - Preliminary Q2 orders EUR 17,749m.
- **2026-05-12 (Q2 FY26):** GS orders EUR 8.9bn, "mainly driven by demand from the U.S. in connection with data centers".
- **2026-08-05 (Q3 FY26):**
  - Orders hit a record EUR 17.9bn, with book-to-bill 1.57 and backlog EUR 162bn.
  - GS set an order record of EUR 9,967m, +61.9% comparable: "Demand from the U.S., including large orders related to data centers, and orders from the Middle East and Asia for new power plants".
  - FY26 margin guided to the upper end of 10-12%.
- **2026-08-25 (ad hoc, 20:25):** Preparations started to separate Transformation of Industry into a standalone company. This is a corporate event and is not in the events file.

## Timing methodology

- **Ad hoc (Art. 17 MAR) clock times:**
  - Through 2024-08 they come from EQS News datelines, e.g. "22-Jun-2023 / 19:22 CET/CEST". The pages are saved as `data/raw/ir/ENR.DE/eqs_adhoc_*.html`. In the EQS listing feed the displayed time matched `data-current-time` UTC + 1h in winter.
  - From 2024-11 they come from pressetext (pta), Siemens Energy's newer distributor, e.g. "(pta030/12.11.2024/19:37 UTC+1)". Saved as `pta_*.html`.
  - Both feeds print Europe/Berlin wall-clock time, so no conversion was needed.
  - EQS coverage of ENR ends 2024-08-30 and pta coverage starts 2024-11-04. For the gap, the IR page's list "Ad Hoc Announcements 2024 (before November 12, 2024)" shows only 2024-01-23.
- **Regular results releases:** Neither feed carries Siemens Energy's earnings releases, with one exception (FY24, below). Instead, every earnings release (ER) states a same-day press conference call before the 09:00 Xetra open: "starting at 8:30 a.m. CE(S)T today". Exceptions are 7:15 a.m. (Q1 FY23), 8 a.m. (Q1 FY21) and 9 a.m. (FY20, with the analyst call at 11 a.m.). The ERs also state the analyst-call times, at 10:00-11:30. On that basis these 22 releases are marked BMO with a blank clock time; source_url points to the ER PDF. The FY20 BMO depends on a 09:00 press conference, which is borderline.
- **FY24:** The release was published 2024-11-12 at 19:44 CET as a pta "business news" item with the ER attached, seven minutes after the 19:37 ad hoc. The ER itself is dated Nov 13, and the press call ran at 8:00 on Nov 13. The event date is therefore 2024-11-12, AMC. Yahoo's 2024-11-13 is the reaction day, not the release day.
- **FY25:** The 2025-11-13 ad hoc (21:15 CET) says the full Q4 release would be published "today", and the ER dates its press call "8:30 a.m. CET on 14 November". The event is therefore 2025-11-13, AMC, with the exact time unknown.
- **Event dates:** Taken from the IR accordion titles and cross-checked against ER datelines. All 24 match, except that the FY24 ER dateline (Nov 13) differs from its actual publication (Nov 12, above). Yahoo dates are wrong for FY21 (Yahoo Nov 11; the ER says 2021-11-10) and Q2 FY24 (Yahoo May 7; the ER says 2024-05-08).
- **CMD times:** These are the first agenda slot: 2020-09-01 12:00, 2022-05-24 09:00, 2023-11-21 13:00. No agenda was found for 2025-11-20, so its time is UNKNOWN. The 2022-05-24 CMD is labelled INTRADAY only because 09:00 counts as the open in classify_timing; the CMD started at the open, not mid-session. The 2020-09-01 CMD predates the listing.
- **Event-type choices:**
  - profit_warning: ad hocs that cut or withdrew group guidance (2021-07-14, 2022-01-20, 2022-04-19, 2023-01-19, 2023-06-22).
  - trading_update: ad hocs that raised guidance or targets (2024-11-12, 2025-04-16, 2025-11-13, 2026-04-23), plus 2023-10-26, which confirmed FY23 was in line with guidance.
  - prelim: preliminary figures with guidance unchanged (2021-01-24, 2024-01-23, 2025-01-27; the last also signalled FCF above guidance).
  - The 2024-11-12 and 2025-11-13 evenings each have two rows, the ad hoc and the FY release, with the same reaction day.
- **Ad hocs excluded as non-results or non-guidance:**
  - 2022-05-18: comment on media reports
  - 2022-05-21: Siemens Gamesa tender offer
  - 2022-09-06: two items on mandatory convertible notes
  - 2023-03-15: two items on the capital increase
  - 2025-07-30: dividend restriction lifted (12:45)
  - 2026-08-25: Transformation of Industry separation (20:25)
- **Other exclusions:** The Hydrogen Day (2021-03-19) and the pre-close IR calls (transcripts for 2026-06-29 and 2026-09-30 are in the manifest) are not events.

## KPI notes

- **Source and coverage:** Rows are parsed from each ER's "Key figures" and "Overview of Segment figures" tables (script `enr_kpis.py`). There are discrete quarters FY2022Q1-FY2026Q3, H1 and 9M year-to-date rows from the Q2/Q3 ERs, and FY2022-FY2025 full-year rows from the Q4 ERs.
- **Growth rates:** revenue_yoy_pct and orders_yoy_pct are nominal ("Actual"). Comparable growth is in `organic_growth_pct` and `orders_organic_growth_pct`.
- **Backlog:** Group backlog is stated in EUR bn, rounded, in the key-figures table. Segment backlog and book-to-bill (quarterly rows only, FY2023Q1 onward) come from the ER segment commentary, e.g. "Book-to-bill ratio was 2.65 and order backlog increased to €73bn". The commentary does not state them every quarter, so some are blank.
- **Margin basis:**
  - FY2023 onward: margin_pct = Profit margin before Special items.
  - FY2022 rows: the originally reported Adjusted EBITA margin before special items.
  - FY2022 segments use the restated "Comparable key figures FY2022" (published 2023-02-07: GS/GT/TI/Siemens Gamesa structure, Profit before SI). The originally reported Gas and Power / Siemens Gamesa figures are kept in `segments_as_reported`.
- **Guidance:** guidance_rev_low/high are the group comparable revenue growth ranges, with the basis stated in extra_json. Q1-Q3 releases guide the current fiscal year; Q4 releases guide the next one (`guidance_fy`). Q3 FY25 reaffirmed the Q2 outlook only by reference, so its numeric fields are blank.

## Gaps

- No exact clock time for the 22 regular results releases (BMO is inferred, see above) or for the FY25 release (AMC). The CMD 2025 time is unknown.
- No earnings-call transcripts are published; only recordings exist. Only the two pre-close call transcripts that are online were downloaded.
- Not downloaded: annual reports, shareholder letters and the Excel data books.
- Documents for FY2020-FY2021 were downloaded but not parsed into KPIs.
- Segment backlog is missing where the ER commentary does not state it (e.g. GS in Q3 FY25 to Q1 FY26). Data-center order values are not disclosed numerically. AI and data-center comments only appear from FY25 Q4 onward; Q3 FY26 also credits GT transformer growth to "data center projects".
- ai_dc_notes come from automatically selected sentences, with a fallback to a grid-related sentence. Some rows, mostly FY2022 and Q2 FY2023, have none.
