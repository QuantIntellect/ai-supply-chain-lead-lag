# VACN.SW — VAT Group AG: IR notes

Collected 2026-10-23. Scripts: `src/ir_agents/semicap/vacn_*.py` (news index, EQS index, download, events, extract, OCR, KPIs).

## Coverage and conventions

- **The series starts at the April 2016 IPO.** VAT listed on SIX on 2016-04-14. The first results event is H1 2016 (2016-08-25). There are no VAT results publications for 2015, so 2015 is not a gap.
- Timezone is Europe/Zurich. SIX continuous trading runs 09:00–17:30: before 09:00 = BMO, from 17:30 = AMC, otherwise INTRADAY.
- **Reporting rhythm.** VAT publishes full results only for H1 (July/Aug) and FY (March).
  - Q1 and Q3 are *trading updates* (orders, sales, backlog, book-to-bill, next-quarter sales guidance) → `event_type=trading_update`, `fiscal_period=YYYYQ1/Q3`.
  - The January "Q4 and FY preliminary results" release → `prelim`, `YYYYQ4`.
  - The July "Q2/HY preliminary" release (2017, 2020–2023 only) → `prelim`, `YYYYQ2`.
  - Ad hoc sales warnings → `profit_warning`: 2024-10-08 (ERP issue) and 2026-03-31 (Middle East conflict).
  - Short-time-work ad hoc releases (2018-10-10, 2018-12-19, 2019-03-29, 2019-06-28, 2023-06-15, 2023-09-20, 2023-11-30) are demand signals. They are tagged `trading_update`, with `fiscal_period` set to the quarter of publication.
  - Capital Markets Days: 2020-12-02, 2022-12-02 and 2025-05-20 → `CMD`.
- **Not included in events:** AGMs, management or board changes, block sales, refinancing, the Dec-2021 CHF 160m capex programme, and the Atonarp acquisition (2026-07-22, same morning as the H1 results).
- **Events:** 66 events from 2016-08-25 to 2026-10-15.
  - By type: 28 trading_update, 12 prelim, 11 H1, 10 FY, 3 CMD, 2 profit_warning.
- **KPIs** (`VACN.SW_kpis.csv`): 25 rows, one per results publication, 2022Q1 → 2026Q3.
  - Money columns are in CHF million at reported FX. Orders = order intake; revenue = net sales; backlog = order backlog at period end.
  - H1 and FY rows hold half-year / full-year totals. The stand-alone Q2 and Q4 figures (orders, sales, YoY, book-to-bill) are in `extra_json`, as are EBITDA, EBITDA margin, net income and FCF.
  - Q2 rows exist only for 2022 and 2023, which had a July prelim. For 2024–2026, Q2 is only in the H1 row's `extra_json`.
  - `book_to_bill` is the stated value. Where it was not stated (all H1/FY totals, and 2025Q1) it is orders ÷ revenue, flagged `book_to_bill_computed`.
  - Gross margin is disclosed only in H1 and FY releases, so it is blank for Q1, Q3 and prelim rows.
  - Guidance columns hold VAT's next-quarter net-sales range, mostly at constant FX. FY ranges and 2027 targets are in `guidance_text` / `extra_json`.
- **Documents:** 232 files in `data/raw/ir/VACN.SW/` (docs/ = PDFs, news_pages/ = HTML), listed in `VACN.SW_manifest.csv`.
  - By type: 129 press_release, 26 presentation, 11 interim_report, 5 annual_report (FY2021–FY2025), 61 other (invitations, AGM, governance).
  - 107 text files are in `data/processed/ir_text/VACN.SW/`, covering 2016H1 → 2026Q3 plus CMD2020/2022/2025.
- **No transcripts.** VAT publishes call replays only as mp3/mp4 audio and video, not transcripts. These were not downloaded.
- **Image-only PDFs.**
  - The 2023Q3, 2024Q1, 2024H1 and 2024Q3 press-release PDFs have no text layer. Their text comes from the identical HTML release on vatgroup.com/news.
  - The 2023FY and 2024H1 presentations and the 2024 investor deck were OCR'd with tesseract (`vacn_ocr.py`). Expect OCR noise.

## Time-source basis (how reliable is `event_time_local`)

| Basis | Events | Period |
|---|---|---|
| EQS News company feed, which shows CET/CEST local time. Verified against the dpa-AFX copy "23.07.2025 / 06:30 CET/CEST". | 36 | 2021-07-15 → 2026-10-15 |
| dpa-AFX copy of the EQS ad hoc (the item is missing from EQS's English list) | 1 | 2026-01-15 06:30 |
| VAT invitation stating "VAT will publish … at 7am CET/CEST" (a scheduled, pre-announced time rather than an observed stamp, so one tier below EQS) | 7 | 2018-04-17, 2018-10-25, 2019-10-24, 2020-04-16, 2020-08-06, 2021-03-04, 2021-04-15 |
| Secondary: marktpuls.ch reprint timestamped 07:00 | 1 | 2020-03-03 |
| **Convention 07:00** (see below) | 17 | 2016-08-25 → 2021-01-14 |
| No time (UNKNOWN) | 4 | short-time-work releases 2018-10-10, 2018-12-19, 2019-03-29, 2019-06-28 |

- **Convention 07:00.** It applies only to *scheduled results* releases that have no direct stamp. Verification: every stated or stamped results release from 2018–2021 was at 07:00–07:04 local, across ≥3 years with no exception. The 2016–2017 events lie outside that window, so treat them as an extrapolation.
- **Publication times by period:**
  - 2021-07 → 2022-07: 07:00–07:04.
  - From 2022-08-04: 06:30. Exceptions: H1 2023 at 06:45, CEO change 2023-02-09 at 07:00, Atonarp at 06:00.
- **Every timed event is BMO.** No VAT results release was found intraday or after the close.
- Unscheduled ad hoc releases before 2021-05 have no reliable time.
- The EQS feed for VAT jumps from 2016-08 to 2021-05; VAT presumably used a different distributor in between.

## Same-day confounders (event-study flags)

- **2021-01-14:** The Q4-20 prelim came out the same day as an ad hoc CFO change.
- **2023-07-27:** The H1-23 results (06:45) were preceded at 06:30 by Urs Gantner's appointment as CEO.
- **2026-07-22:** The H1-26 results (06:30) were preceded at 06:00 by the Atonarp acquisition.
- **Excluded ad hoc the lead may want:** 2021-12-17, the CHF 160m capex / capacity programme (07:02 per EQS).
- In the manifest, `fiscal_period` is blank for CMD and investor-deck documents. Their text files are named `CMD2020_…`, `CMD2022_…`, `CMD2025_…` and `2024DECK_…`.
- Per-event time sources are in `data/raw/ir/VACN.SW/events_detail.json` (field `time_source`).

## Demand narrative 2023–2026 (orders in CHF m, YoY unless stated)

- **2023-01-12 (Q4-22 prelim):** Orders fell about 43% to ~249. VAT said the US export rules of Oct-2022 "slowed down deliveries of equipment to China by our major OEM customers". It expected softening to continue into 2023.
- **2023-04-13 (Q1-23):** Order trough at 136 (−54%), book-to-bill 0.6. Sales held up from backlog execution. Short-time work for ~650 Haag staff followed on 2023-06-15 and was extended on 2023-09-20.
- **2023-07-27 (H1-23):** Q2 orders were +14% QoQ, and VAT said the market "might have bottomed". It guided the EBITDA margin slightly below its 32–37% band.
- **2023-10-12 (Q3-23):** Orders rose QoQ for a second quarter (164), and VAT said the "market bottom reached". China lagging-edge investment stayed healthy, with a risk of wider restrictions.
- **2023-11-30 / 2024-01-11:** Short-time work ended on Advanced Industrials demand. Q4-23 orders were +44% QoQ (~237), book-to-bill 1.1. This was the recovery inflection.
- **2024-04-11 (Q1-24):** Orders +73% to 236. The drivers were the semi capex recovery and strong Chinese customers (subsidies and regionalization), plus memory recovery.
- **2024-07-18 (H1-24):** First explicit AI attribution: "semiconductor equipment orders increased driven by AI-related demand with most activity in DRAM-memory and logic". Q2 orders were +75% (271).
- **2024-10-08:** Profit warning. Q3 sales fell below the low end of the CHF 235–255m guidance because of ERP problems, with about CHF 22m of sales shifted to Q4. The cause was operational, not demand: Q3 orders were +58%, and VAT cited the HBM and high-end logic build-out.
- **2025-03-04 (FY-24):** 2025 was guided as a growth year (2nm, GAA, ALD). VAT cautioned that "AI computing … has not driven widespread upgrading of data centers" and that DRAM/NAND capacity was underutilized.
- **2025-05-20 (CMD):** VAT cut its 2027 sales target to CHF 1.5–1.7bn, from the CHF 1.8–2.2bn set at CMD 2022, citing the lower market and FX.
- **2025-10-16 (Q3-25):** Orders −8% (238), book-to-bill 0.92, backlog −33%. VAT said weak mature nodes and upgrade-only memory spending "masked the good demand for HBM and GAA". It now expected capex acceleration in H2 2026, which was effectively a push-out.
- **2026-01-15 (Q4-25 prelim):** Orders ~305 (+28% QoQ) on "technology transitions fueled by demand for AI applications". HBM/DRAM capacity was seen as full for 2026. The quarter includes CHF 30–35m of pre-orders placed ahead of the 1-Jan-2026 price increase.
- **2026-03-31:** Profit warning. Q1 sales were ~215 against the CHF 240–260m guidance because the Middle East conflict disrupted the supply chain. Book-to-bill was ~1.6. Q1 orders were then reported at 356 (+47%) on 2026-04-16.
- **2026-07-22 (H1-26):** Record Q2 orders of 500 (+102%), book-to-bill 1.7, driven by high-performance logic and DRAM for AI data centers. The 2027 guidance was put under review.
- **2026-10-15 (Q3-26):** Record orders of 697 (×3 YoY), backlog 980, book-to-bill 1.9. VAT said ordering windows had stretched to 9+ months from 3 at end-2025, and that "no double bookings" were anticipated. It now expects 2027 sales "significantly above" the CHF 1.5–1.7bn range, which amounts to a guidance raise.

## Gaps and caveats

- The 2016–2017 news archive on vatgroup.com is incomplete. The Q1-2017 (2017-05-17) and Q3-2017 (2017-10-17) trading updates were added from the financial-reports page. No January prelim was found for FY2017, FY2018 or FY2019, and no July prelim for 2018, 2019, 2024, 2025 or 2026. These appear never to have been published, but this could not be fully proven.
- The FY2025 release's KPI table shows the prior-period backlog as 258.8 (the Q3-25 figure). The text gives a year-end backlog of 304 (−18% vs 370.3 at YE2024); the backlog column uses 304.3.
- KPI rows were not built for 2016–2021, but the release texts for those years are extracted and ready.
- YoY % values are as stated by VAT, at reported FX. Constant-FX variants appear in `extra_json` only where noted.
