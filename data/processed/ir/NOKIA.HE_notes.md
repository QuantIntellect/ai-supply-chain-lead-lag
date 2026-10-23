# Nokia (NOKIA.HE / NYSE: NOK) — IR notes

## Demand narrative 2023–2026 (from Nokia's own releases)
- **2023-07-14 08:30 EEST, profit warning (ad hoc):** Nokia cuts its FY2023 outlook. The Q2 report (2023-07-20) gives the new range of EUR 23.2–24.6bn net sales; Q2 net sales were flat y-o-y at constant currency.
- **2023-10-19, Q3 2023:** net sales EUR 4,982m (-20% y-o-y reported). Nokia announces a cost-reduction and operating-model reset on the same morning.
- **2023-12-30 00:15 EET, profit warning:** Nokia says it will not reach its 2023 outlook because smartphone-licence renewals are delayed. This is a Saturday release, so the first trading day affected is 2024-01-02.
- **2024 (Q1–Q3):** reported net sales fall 8–20% y-o-y in every quarter (Q1 EUR 4,667m, Q2 4,466m, Q3 4,326m). This is the trough of the 5G mobile-capex cycle.
- **2025-01-30, Q4 2024:** a return to growth (EUR 5,983m, +10.5%). Network Infrastructure grows strongly, with all units contributing.
- **2025-07-22 19:00 EEST, profit warning:** Nokia lowers its 2025 operating-profit guidance (currency and tariffs) after the close. In the Q2 report management says "connectivity is becoming a critical differentiator in the AI supercycle."
- **2025-10-28 (Inside Information, not in the events file because it is not a results event):** NVIDIA makes a USD 1.0bn equity investment in Nokia as part of a strategic partnership.
- **2025-11-19 13:00 EET, CMD:** new strategy, operating model and long-term targets. From 2026 Nokia reports two segments, Network Infrastructure and Mobile Infrastructure (comparatives recast on 2026-01-29).
- **2026-01-29, Q4 2025:** order intake is strong in Optical and IP Networks, and book-to-bill stays above 1, "driven by demand from AI & Cloud customers."
- **2026-04-23, Q1 2026:** net sales to AI & Cloud customers +49% (now 8% of group sales), and EUR 1bn of AI & Cloud orders booked in the quarter.
- **2026-07-23, Q2 2026:** net sales to AI & Cloud customers +105%. Group net sales +9% at constant currency.
- **2026-10-22, Q3 2026:** net sales to AI & Cloud customers +123% and AI & Cloud order intake +118%, with EUR 1.5bn of new AI & Cloud orders. In Network Infrastructure, IP Networks grows 43% and Optical 18%. Nokia expects combined Optical + IP Networks growth of 25–30% in 2027.

## Methods and conventions
- **Events:** the Nasdaq Nordic company-announcement API (`api.news.eu.nasdaq.com`, timeZone=EET) gives every stock-exchange release with its exact publication time in Helsinki local time. Source URLs point to view.news.eu.nasdaq.com.
  - All 48 quarterly reports from 2015-01 to 2026-10 were released at 08:00 Helsinki time, which is BMO (Nasdaq Helsinki opens 10:00; cut-offs are 10:00 / 18:30 including the closing auction). 08:00 EET/EEST is 01:00–02:00 ET, also before the NYSE open.
  - Same-morning add-ons (strategy and restructuring releases on 2015-10-29, 2018-10-25 and 2023-10-19) are folded into the quarterly row.
  - M&A, CEO changes and patent deals are excluded. The excluded items include the Alcatel-Lucent offer, Infinera (2024-06-27), the NVIDIA investment (2025-10-28) and the patent settlements.
- **Fiscal year:** calendar year. Q4 rows are the combined Q4 and full-year release.
- **Docs:** 20 interim reports (FY2021Q4–FY2026Q3, the PDF attachments of the exchange releases) and 18 presentations (nokia.com slides). The slides for FY2022Q2 and FY2023Q1 were not found (HTTP 403). Nokia publishes no transcripts.
- **KPIs:** taken by regex from the reported-results table.
  - `revenue` is reported net sales in EUR m. `revenue_yoy_pct` is computed against the prior-year figure printed in the same report, which may be restated. Constant-currency growth and comparable margins are in `extra_json`.
  - `gross_margin_pct` is the reported gross margin.
  - `orders` is filled only for FY2026Q3: the EUR 1.5bn of AI & Cloud new orders quoted by the CEO, flagged in `extra_json`. Nokia does not report group order intake.
- **Gaps:** FY2023Q2 net sales were not parsed (blank). No numeric backlog is disclosed.
