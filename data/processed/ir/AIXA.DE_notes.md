# AIXA.DE (Aixtron SE): IR collection notes

Built 2026-10-23. Scripts: `src/ir_agents/semicap/aixa_listing.py`, `aixa_news.py`, `aixa_events.py`, `aixa_docs.py`, `aixa_kpi_parse.py`, `aixa_kpis.py` (they use the shared `irlib.py` conventions).

## Demand narrative, 2023–2026 (dated bullets)

- **2023-02-28 (FY22 results, 07:30 BMO).** Year-end equipment backlog was EUR 351.8m (+64% yoy). FY23 guidance: order intake EUR 600–680m, revenue EUR 580–640m, driven by GaN/SiC power electronics.
- **2023-07-27 (Q2 23, 07:30).** FY23 guidance raised: orders EUR 620–700m, revenue EUR 600–660m. Q2 orders were EUR 177.8m (+17% yoy) and backlog EUR 412.5m. SiC/GaN power was "by far" the largest share of orders, as customers built high-volume SiC/GaN fabs.
- **2023-10-26 (Q3 23, 07:30).** First order cooling: Q3 orders fell to EUR 118.5m (-17% yoy). Revenue was EUR 165.0m (+86%), with SiC+GaN at 82% of equipment revenue. Guidance confirmed.
- **2024-02-29 (FY23, 07:30).** Q4 orders were EUR 204.5m (+28% yoy) and Q4 deliveries a record, with revenue of EUR 214.2m. FY24 guidance was revenue EUR 630–720m, with no order-intake guidance given.
- **2024-04-25 (Q1 24, 07:30).** Orders fell to EUR 120.3m (-14% yoy). Micro LED was 37% of equipment orders. New SiC customers included a top-5 SiC maker, a major order from China, and Japanese customers.
- **2024-07-04 (ad hoc, 23:15 AMC; profit warning).** Preliminary Q2 orders were about EUR 176m, but FY24 revenue guidance was cut to EUR 620–660m (from 630–720m) and EBIT margin to 22–25%. Confirmed with the Q2 results on 2024-07-25.
- **2024-10-31 (Q3 24, 07:30).** A customer pushed out a major project delivery from Q3 to Q4. Management flagged "moderate demand expected for 2025". Q3 orders were EUR 143.5m.
- **2025-02-27 (FY24, 07:30).** FY25 guidance of revenue EUR 530–600m was down from FY24's EUR 633.2m. Q4 orders fell 23% yoy and backlog fell 18% to EUR 289.3m. SiC/GaN dropped to 55% of system revenue (2023: 74%). The release cites AI as a driver of optical datacom and of GaN/SiC power electronics.
- **2025-07-31 (Q2 25, 07:30).** Orders were EUR 118.5m (-33% yoy), tied with Q3-23 as the lowest quarter in the 2022–26 panel. Optoelectronics momentum came from datacom lasers for AI data centres, with the G10-AsP described as the laser "tool of record". A large G10-SiC volume order from China was booked and shipped in H1.
- **2025-10-17 (ad hoc, 14:38 INTRADAY; profit warning).** FY25 revenue guidance was cut to EUR 530–565m because of volume shifts and USD weakness, with margin guidance also cut.
- **2025-10-30 (Q3 25, 07:30).** The CEO said the demand upturn "has not yet materialized in Q3/2025". The AI data-centre build-out is the driver of optoelectronics tool demand. The datacom-laser pick-up seen in Q2 was confirmed in Q3 and is expected to continue into 2026. GaN power utilisation is rising on data-centre demand.
- **2026-02-26 (FY25, 07:48).** FY26 guidance was about EUR 520m ±30m. Q4 orders were EUR 169.6m (+8% yoy), the first yoy order growth since Q1 25. Optoelectronics was 23% of FY25 equipment revenue (FY24: 12%). SiC/GaN demand was subdued in Western markets, with China stabilising it.
- **2026-04-14 (ad hoc, 21:00 AMC; positive prelim).** Preliminary Q1 orders were about EUR 171m (+30% yoy) and FY26 revenue guidance was raised to about EUR 560m ±30m. The Q1 release on 2026-04-30 was titled "Inflection point driven by rising optoelectronics demand". A EUR 450m convertible bond followed on 2026-04-15, and in May Lumentum placed multiple G10-AsP orders for AI optical networks.
- **2026-07-30 (Q2 26, 07:30).** Orders were EUR 214.5m (+81% yoy; H1 +54%) and backlog EUR 456.9m (+61%). Major laser-system shipments start in Q3 26 and run "well beyond" 2026. A plant in Malaysia is planned.
- **2026-10-15 (ad hoc, 18:00 AMC; positive prelim).** Preliminary Q3 26: orders about EUR 275m (vs EUR 124.0m), revenue about EUR 184m, gross margin about 48%, EBIT about EUR 57m (about 31%), "significantly" above market expectations. FY26 guidance unchanged; the full Q3 statement is due 2026-10-29.

## Conventions used

- **Fiscal year and timezone.** The fiscal year is the calendar year. Timezone is `Europe/Berlin`, judged against Xetra hours 09:00–17:30: before 09:00 is BMO, 17:30 or later is AMC, anything else is INTRADAY.
- **Event types.**
  - Aixtron reports quarterly, so the July release (H1 report) is typed `Q2` and the Feb/Mar release (annual report with Q4) is typed `Q4`.
  - Ad-hoc guidance cuts are `profit_warning`: 2015-10-13, 2024-07-04 and 2025-10-17. The last two also carried preliminary quarterly figures.
  - Positive preliminary figures are `prelim`: 2026-04-14 (with a guidance raise) and 2026-10-15.
  - The guidance raise without figures (2021-06-09) and the San'an order-volume reduction (2015-12-09) are `trading_update`.
  - No Capital Markets Day was found in 2015–2026: none appears in the news archive, the financial-calendar archive (2020+) or a web search.
- **Events excluded on purpose (not results-type):**
  - M&A and governance ad-hocs: the CEO exit on 2017-01-20, the ALD/CVD sale on 2017-05-25, 2017-10-24 and 2017-11-16, board changes, the IRUJA JV, the Malaysia plant on 2026-03-25 and the convertible bond on 2026-04-15.
  - The 2016 Fujian Grand Chip takeover saga: 2016-05-23, 2016-10-24, 2016-11-18, 2016-12-03 and 2016-12-08.
  - The 2016-07-19 notice rescheduling the Q2/Q3 2016 releases. The Q2 release moved from 2016-07-26 to 2016-08-11 and Q3 to 2016-11-08, and the calendar uses the actual dates.
  - Annual general meetings.
- **Upcoming event, not in the CSV:** Q3/9M-2026 Quarterly Group Statement, scheduled for 2026-10-29 according to the IR financial calendar.

## Time-source basis (for the event study)

- **2017-01 → 2026-10: document timestamps.** 39 of 44 rows carry the exact EQS/DGAP distribution timestamp, which is printed on each aixtron.com news page ("30.10.2025 / 07:30 CET/CEST").
  - Every timestamped scheduled results release was at 07:25–07:48, so all are BMO.
  - The ad-hocs were released at 17:18 (2021-06-09, INTRADAY), 23:15, 14:38, 21:00 and 18:00.
- **Convention-based timing (time column blank, `timing` = BMO).**
  - Five scheduled releases have no timestamp on the page: 2018-10-30, 2019-02-26, 2019-04-30, 2019-07-25 and 2019-10-24.
  - The eight scheduled results releases of 2015–2016 (taken from archived aixtron.com pages via the Wayback Machine) also have no timestamp. They had a 15:00 CET call on the same day, and the datelines are the same day.
  - BMO is applied to both groups by the irlib rule: the convention holds on more than 30 timestamped releases across 2017–2026 with no exception. The 2015–2016 rows extrapolate it to before the verified window, so treat them as lower confidence.
- **2015–2016 completeness.** The current IR news archive starts in 2017-01. Dates for 2015–2016 come from partial Wayback captures of the old aixtron.com finance-news, ad-hoc and press archives, and the regular results releases are complete. Results-relevant ad-hocs from Jan–Apr 2015 could have been missed, because no capture of that listing page exists.
- **UNKNOWN timing:** the two 2015 ad-hocs, 2015-10-13 (guidance cut) and 2015-12-09 (San'an). No timestamp was found, so use a [0,+1] window for these.

## Documents (manifest: 69 entries)

- **Results press releases, 2022Q1–2026Q2:** 18 scheduled releases plus 4 ad-hoc/prelim releases (2024Q2, 2025Q3, 2026Q1, 2026Q3). They are HTML from aixtron.com, and the text is cut to the release body.
- **Results presentations:** 18 PDFs, covering every quarter from 2022Q1 to 2026Q2.
- **Reports:** quarterly statements and H1 reports (14) and annual reports for 2022–2025 (4).
- **Company-published call transcripts or prepared speeches:** 2022Q1, 2022Q3, 2025Q1, 2025Q2, 2025Q3, 2025Q4, 2026Q1 and 2026Q2, plus older ones for 2017Q3, 2020Q1 and 2020Q3.
  - Other quarters have only audio recordings (mp3/mp4, not downloaded) or nothing.
  - The 2016–2018 transcript links on the archive page return 404.
- **Text files** are in `data/processed/ir_text/AIXA.DE/<period>_<doctype>.txt`. Ad-hoc releases use the doctype `adhoc_press_release`, and annual reports use the period `YYYYFY`.
- **`pub_date`** for presentations, reports and transcripts is the results date for that period. The actual upload or call date can differ: the calls are held on results day at 10:00 or 15:00 CET.

## KPI notes and gaps

- **Source and definitions.** Figures come from the "Key financials at a glance" table in each results release, in EUR millions.
  - `orders` is total order intake including spares and service.
  - `backlog` is the equipment-only order backlog at period end.
  - `gross_margin_pct` is the rounded whole-percent figure the table states. The exact gross profit / revenue figure is in `extra_json.gross_margin_calc_pct`.
- **Book-to-bill.** Aixtron never states a book-to-bill ratio, so the column is blank. Orders / revenue is in `extra_json.book_to_bill_calc`.
- **YoY changes** are calculated from the current and prior-year figures stated in the same release. Prior-year values can differ slightly from the original release; for example, Q4-24 revenue appears as 226.9 in its own release and 226.7 in the FY25 release.
- **Guidance columns.**
  - `guidance_rev_low` and `guidance_rev_high` hold the full-year revenue guidance in force after that release. For Q4 rows this is next year's guidance (`extra_json.guidance_rev_basis`).
  - Next-quarter revenue guidance is in `extra_json.nq_rev_low/high`. Aixtron has given it since the FY23 release, except that no explicit Q4-25 range was found.
  - Order-intake guidance (`fy_orders_low/high`) exists only for FY2022 and FY2023.
  - "±" guidance is converted to a range, for example 560 ±30 becomes 530–590.
- **2026Q3** comes only from the 2026-10-15 preliminary ad hoc. The values are approximate (`extra_json.preliminary=true`) and backlog is blank. Replace them after the 2026-10-29 statement.
- **Not collected:** quarterly KPIs before 2022Q1 (events only); a regional or China split of orders (only qualitative mentions are in the notes); the separate HGB German-GAAP statements; sustainability reports.
