# ABB (ABBN.SW) — demand narrative and data notes

Figures are USD, as first reported in each quarterly release. "comp" means comparable growth (ABB's organic measure). EL is the Electrification business area. From Q4 2025 the figures cover continuing operations only: Robotics is now discontinued, and the business areas are Electrification, Motion and Automation. Prior-year comparisons in those releases are restated on the same basis.

## Demand narrative 2023–2026

- **2023-04-25 (Q1'23):** Orders were $9.45bn (+9% comp), with book-to-bill at 1.20 and a record backlog of $21.6bn. EL orders grew only +5% comp. The release does not yet mention data centers.
- **2023-07-20 (Q2'23):** Group orders rose +2% comp and EL +3%. This is the first explicit data-center callout in the panel: demand was "particularly strong in segments like data centers and oil & gas".
- **2024-02-01 (Q4'23):** Orders were flat comp and book-to-bill was 0.93, which the release calls the seasonal Q4 pattern. EL orders rose +2% comp. Automation was hampered by "normalizing order patterns" and robotics weakness.
- **2024-04-18 (Q1'24):** Group orders fell −4% comp, a decline the release puts down to the timing of large orders. EL orders rose +8% comp, and "utilities and datacenters" grew particularly strongly in all regions.
- **2024-10-17 (Q3'24):** Data centers, utilities and infrastructure "stood out as strong". EL orders rose +10% comp and the EL Operational EBITA margin reached 24.1%.
- **2025-01-30 (Q4'24):** EL orders rose +16% comp, led by "particularly high demand in the data centers and utilities segments". ABB reported orders for its medium-voltage UPS (HiPerGuard) for data centers.
- **2025-04-17 (Q1'25):** This was a wobble. Data-center sentiment was "very strong", but quarterly DC orders "declined slightly due to slower activity noted for a specific customer within the hyperscale field". EL orders rose only +2% comp. ABB announced a plan to spin off Robotics.
- **2025-07-17 (Q2'25):** Data-center orders were up double-digit YoY. Group orders rose +14% comp to $9.8bn, with book-to-bill at 1.10.
- **2025-10-16 (Q3'25):** Data-center orders rose at a double-digit rate. EL orders rose +10% comp and EL backlog was $8.75bn. ABB announced $210m of North American EL capacity and R&D investment, citing "the surging power needs of AI in data centers".
- **2025-11-18 (CMD):** ABB moved to three business areas. It raised its Group Operational EBITA margin target to 18–22% (from 16–19%) and set a 22–26% target for EL. It confirmed the 5–7% through-cycle comparable growth target. Robotics was sold to SoftBank, announced on 2025-10-08.
- **2026-01-29 (Q4'25):** Orders rose +32% comp to $10.3bn and EL +33% comp. Data centers posted "very strong double-digit growth", and the release mentions the NVIDIA 800 VDC collaboration and the Applied Digital partnership. This was the first numeric guidance: FY26 comparable revenue +6–9%, and Q1'26 +7–10%.
- **2026-04-22 (Q1'26):** Orders rose +24% comp to $11.3bn, with book-to-bill at 1.29. EL orders "surged" +44% comp, and the release describes a "buoyant data center market". FY26 guidance was raised to high-single to low-double-digit comparable revenue growth.
- **2026-07-16 (Q2'26):** Orders rose +28% comp to $12.0bn and EL orders +58% comp. "Data center order growth was exceptional". FY26 guidance moved up again, to low-double-digit to low-teens. The Rotork acquisition was announced the same morning.
- **2026-10-20 (Q3'26):** Orders were a record $12.06bn (+40% comp) and EL +70% comp. Data-center orders showed a "triple-digit increase". Backlog was $32.3bn (+37% comp), and EL backlog $16.0bn (+85% comp). FY26 guidance is comparable revenue growth in the "low teens". ABB also announced an electrification JV with Mitsubishi Electric and launched its Infinitus DC (direct-current) portfolio for AI data centers.

**Read-through:** ABB's EL order growth went from low single digits in 2023 to a +44/+58/+70% comp sequence in 2026. Over the same period backlog grew faster than revenue. That is consistent with a large and accelerating AI/data-center electrification order wave starting in late 2025, with the brief hyperscaler pause in Q1 2025 as the one exception.

## Sources and method

- **Event timestamps:** Taken from the MFN.se feed for ABB (`mfn.se/all/a/abb`). This feed redistributes ABB's Cision items (to 2023) and EQS items (2023 onward) with second-level timestamps in Europe/Stockholm time, which is the same zone as Zurich. For each event the earliest version (English or Swedish) is used. Q4 2020 is not on MFN; its time comes from the ABB newsroom `DatePublished` field (05:45:34Z, i.e. 06:45 CET).
- **Timing:** All 56 events have an HH:MM time and all are BMO, typically 06:45–06:57. The exceptions are the Q2'26 release at 07:05 (published after the Rotork announcement at 07:00) and CMD releases at 07:16–07:20.
- **Cross-check:** All 48 Yahoo dates for ABBN.SW from 2015 to 2026-10 match an event within ±1 day, and every quarterly event matches a Yahoo date.
- **Events beyond quarterly results:**
  - CMDs: 2015-09-09, 2016-10-04, 2020-11-19 and 2025-11-18.
  - trading_update: 2020-03-30 (COVID-19 update) and 2021-04-15 (positive Q1 pre-release).
  - profit_warning: 2017-02-22 (Korean-subsidiary embezzlement, about a $100m pre-tax charge against already-reported unaudited 2016 results) and 2017-12-20 (EPC exit, with Q4'17 hit by about $150m of Operational EBITA plus $75m of charges).
  - Excluded as non-results corporate events: the 2018-12-17 Power Grids/Hitachi strategy announcement, the 2025-10-08 Robotics sale and the 2026-07-16 Rotork deal.
- **Documents:** Taken from `global.abb/group/en/investors/quarterly-results`.
  - Press releases for 2015Q1–2026Q3.
  - Financial-information PDFs and results presentations for 2022Q1–2026Q3.
  - The CMD 2025 release page.
  - ABB does not publish call transcripts on its IR site, so none were collected.
- **KPI extraction:** KPIs are regex-extracted from the "Key Figures" table in the financial information (orders, backlog, revenues, gross margin, Operational EBITA margin). Business-area orders, revenues and backlog come from the business-area tables. Guidance and data-center sentences come from the release text.
- **Book-to-bill:** The stated value is used when it is within ±0.03 of orders/revenues. Otherwise the computed ratio is used. `extra_json.book_to_bill_source` records which.

## Gaps

- The EL Operational EBITA margin is blank for 2023Q1–Q4 because the release tables in those quarters are images.
- guidance_rev_low/high is numeric only for the FY26 guidance given in Q4'25. All other ABB guidance is qualitative and is kept in guidance_text.
- The 2022 releases contain no data-center commentary, so ai_dc_notes is empty for those quarters.
- KPI coverage for 2015Q1–2021Q4 comes from a lighter pass over the release key-figures table only. It gives orders, revenues, their USD and comparable growth (like-for-like in 2015), Operational EBITA margin where parseable, and computed book-to-bill. Backlog, gross margin, guidance and business-area data are blank for those quarters.
