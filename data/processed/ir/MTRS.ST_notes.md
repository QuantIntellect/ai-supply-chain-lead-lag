# Munters Group (MTRS.ST) - IR notes

Munters reports quarterly (interim reports Q1-Q3, year-end report = Q4) in SEK million.
Data-center exposure sits in business area **Data Center Technologies (DCT)** (separate business area
from 1 July 2022; before that "Data Centers" was inside AirTech). DCT order intake is very lumpy
(single US colocation / hyperscaler orders of SEK 0.6-2.1 bn), so quarterly DCT orders swing by
hundreds of percent; backlog is the better level indicator.

## Demand narrative 2023-2026 (dated)

- **2023-04-21 (Q1 2023)**: group orders 2,544 MSEK, -44% organic, "as no larger orders were received in the quarter"; DCT orders only 293 MSEK against the MUSD 115 order in Q1 2022, while net sales grew +38% organic on backlog conversion (SyCool Split ramp-up in the US).
- **2023-06-30 21:00 / 2023-10-27 17:30**: large US colocation orders resume: MUSD 88 (chilled-water air handlers), then MUSD 137 (about BSEK 1.5) for SyCool Split, for delivery in 2025. Q3 2023 orders were still -64% organic (DCT 404 MSEK, -88% y/y) against the record Q3 2022.
- **2024-02-01 (Q4 2023)**: orders 5,651 MSEK (+82% organic), DCT orders 3,184 MSEK; group backlog 11,333 MSEK. Figures were pre-released on 2024-01-22 00:45 because of a ransomware attack at a hosting provider.
- **2024-05-21 (CMD)**: mid-term growth target raised from 10% organic to >14% currency-adjusted net sales growth (adj. EBITA margin target still >14%).
- **2024-07-17 (Q2 2024)**: DCT orders flat (-2% organic), driven by "colocators ... hosting hyperscalers"; record adj. EBITA margin 17.8%. The Geoclima chiller acquisition was announced the same morning (07:00), which completed the DCT cooling portfolio (chillers).
- **2024-10-22 / 2024-11-07**: Q3 2024 DCT orders 898 MSEK (+122%), but AirTech had a weak battery outlook. A MSEK 375 LCX CDU (liquid-cooling) order followed from a new US colocation customer.
- **2025-02-05 (Q4 2024)**: group orders -23% (-29% organic) and DCT orders 1,787 MSEK (-44%) against the very large Q4 2023. Outlook: battery weakness expected to persist through 2025.
- **2025-04-29 (Q1 2025)**: DCT orders 1,108 MSEK (+223%), driven by chillers and CDUs, with "a solid level of orders from both colocators and hyperscalers" in the Americas.
- **2025-10-24 (Q3 2025)**: orders 4,159 MSEK (+57%, +56% organic); DCT 2,164 MSEK (+141%); DCT book-to-bill 1.4. AirTech cost programme of MSEK 250-300.
- **2025-11-12 to 2025-12-31**: a run of record AI and data-center orders. About MUSD 215 of CRAHs from a US **hyperscaler**; MUSD 82 of chillers for a US colocation provider "centered around high performance computing for AI"; MSEK 840 of chillers; and about BSEK 2.1 (CRAHs, CDUs, chillers) from a US colocation company. Deliveries run from Q4 2026 to Q1 2028.
- **2026-01-29 (Q4 2025)**: record orders 11,604 MSEK (+191%, +210% organic); DCT orders 9,215 MSEK (+416%); backlog 17,282 MSEK. However, the adj. EBITA margin fell to 10.0% (DCT tariffs, AirTech underutilisation). 2026 outlook: "historically high turnover", weighted to H2, with the margin expected to improve in H2 2026.
- **2026-04-24 08:00 / 2026-04-28 (Q1 2026)**: a BSEK 2.0 order for a "modular AI cooling solution" (high-capacity CDUs and over-the-rack CRAHs) for an AI-factory build-out at a US colocation provider, delivering early 2027 to Q1 2028. In Q1, orders were +49% organic, DCT +107%, and backlog was 18,991 MSEK.
- **2026-07-17 (Q2 2026)**: orders 8,699 MSEK (+144% organic), DCT 4,853 MSEK (+246%), and backlog a record 24,542 MSEK (DCT external backlog 19,185 MSEK). DCT sales nevertheless fell because the chiller ramp-up and component shortages limited throughput, and the adj. EBITA margin was 11.0% ("Exceptional demand - external headwinds currently affecting profitability").
- **2026-09 to 2026-10**: the expanded Daleville (Virginia) data-center cooling campus was completed (2026-09-11). The CEO transition was accelerated, with DCT head Stefan Aspman becoming CEO (2026-09-14). The Q3 2026 report is scheduled for 2026-10-23 07:30 CEST and the CMD for 2026-11-11.

## Material data-center order announcements (MAR inside information; not in events.csv)

These are not earnings events, so they are excluded from `MTRS.ST_events.csv` (its event_type set has no order category). Times are Europe/Stockholm, from the MFN feed.

| date | time | value | customer / product |
|---|---|---|---|
| 2022-03-30 | 08:00 | MUSD 115 | US colocation, SyCool Split |
| 2022-08-29 | 16:00 | MUSD 63 | US colocation, CRAHs |
| 2022-08-30 | 08:00 | MUSD 176 (largest ever at the time) | US colocation, SyCool Split |
| 2023-06-30 | 21:00 | MUSD 88 | US colocation, chilled-water air handlers |
| 2023-10-27 | 17:30 | MUSD 137 | US colocation, SyCool Split |
| 2023-12-28 | 10:25 | MUSD 65 | US colocation, CRAHs |
| 2024-11-07 | 09:00 | MSEK 375 | new US colocation customer, LCX CDU (liquid cooling) |
| 2025-11-12 | 08:35 | about MUSD 215 | US hyperscaler, CRAHs |
| 2025-12-02 | 09:00 | MUSD 82 | US colocation (HPC for AI), chillers |
| 2025-12-11 | 08:15 | MSEK 840 | new US colocation customer, chillers |
| 2025-12-31 | 18:15 | about BSEK 2.1 | US colocation, CRAHs, CDUs, chillers |
| 2026-04-24 | 08:00 | about BSEK 2.0 | US colocation, modular AI cooling (CDUs, CRAHs) |

Earlier ones: 2017-05-26 08:00 and 2017-11-06 07:00 data-center cooling orders. Other non-earnings MAR items are a CEO change (2018-12-18 17:38), the FoodTech Equipment divestment (2025-02-09 11:05), a review of a potential FoodTech divestment (2026-06-16 19:00) and the Geoclima acquisition (2024-07-17 07:00).

## Sources, method, conventions

- **Events**: the MFN news feed (https://www.mfn.se/all/a/munters-group, paginated with `?limit=48&offset=n`, 472 items from 2017-05-26 to 2026-10-09). Times are MFN publication stamps in Stockholm local time, and they match the MAR statements in the releases ("submitted for publication ... at 07.30 CEST"). Releases went out at 08:00 until the Q4 2020 report (2021-02-04) and at 07:30 from Q1 2021 onwards. All 46 events carry an HH:MM time.
- Profit warnings: 2017-12-13 23:02 (Data Center profitability) and 2019-10-23 18:00 (SEK 116m extra Dison data-center costs). Prelim: 2024-01-22 00:45. CMDs: 2019-05-09, 2020-05-28 and 2021-05-11 (Capital Markets Updates, 14:00 webcasts), 2022-12-08 (targets release at 07:30) and 2024-05-21 (08:00). A scan of all 155 non-routine English releases for MAR statements (`data/raw/ir/MTRS.ST/mfn_mar_scan.csv`) found no other earnings-type releases. Every Yahoo date for MTRS.ST matches an event within ±1 day.
- **Q3 2026 row (2026-10-23 07:30)** is *scheduled*: it comes from the 2026-10-09 invitation and had not been published when the data was collected. Re-check it after release. CMD 2026 (2026-11-11 14:00 CET) is outside the window and not included.
- **Munters listed on Nasdaq Stockholm in May 2017**, so there are no events for 2015 to mid-2017. That gap is real, not missing data.
- **Docs** (82 in the manifest): interim-report PDFs from 2017Q2 to 2026Q2 (Cision attachments); quarterly presentations from 2022Q1 to 2026Q2 (munters.com, which needed an Edge user-agent); MFN press-release pages for the 2022+ reports, prelim and CMD releases; and the two profit-warning PDFs. Munters does not publish call transcripts (webcast only). Text is in `data/processed/ir_text/MTRS.ST/`.
- **KPIs** (18 quarters, 2022Q1 to 2026Q2) are SEK million, as reported at release. They are not restated for the 2025 FoodTech Equipment divestment, so later reports show restated "continuing operations" history.
  - `orders` is group order intake and `revenue` is net sales. `*_yoy_pct` is the reported total change; where it is computed from reported levels, extra_json says so (`*_computed`).
  - `backlog` is the group order backlog from the report's quarterly overview. `book_to_bill` is filled only where it is stated in the text; the calculated value is `book_to_bill_calc` in extra_json.
  - `gross_margin_pct` is left blank (not extracted). The adj. EBITA margin is in extra_json.
  - extra_json also holds organic sales and order growth, and segment orders, sales, external backlog and margin for AirTech, DCT and FoodTech.
  - `guidance_text` holds the mid-term targets and, from the Q4 2025 report on, the "Business outlook 2026". Munters gives no numeric revenue guidance, so `guidance_rev_low` and `guidance_rev_high` are blank.
- **Gaps and caveats**:
  - The 2022Q3, 2022Q4 and 2023Q1 report PDFs have a fragmented text layer. For those quarters, group orders, sales and backlog come from the 2024Q2 report's quarterly overview, and segment orders from the prior-year columns of the 2023Q3, 2023Q4 and 2024Q1 reports. Both are flagged in extra_json.
  - 2022Q1 segment orders are derived as Jan-Jun minus Apr-Jun from the 2022Q2 report.
  - DCT Q4 2022 orders were only 30 MSEK, after a MSEK 465 cancellation.
