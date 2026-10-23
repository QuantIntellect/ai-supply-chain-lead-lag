# Infineon (IFX.DE) — IR notes

## Demand narrative 2023–2026 (from Infineon's quarterly releases)
- **2023-02-02, Q1 FY23:** a very profitable quarter, and the FY2023 outlook is raised.
- **2023-03-28 18:31 CEST, ad hoc (prelim, AMC):** Infineon "expects stronger results for second fiscal quarter and full 2023 fiscal year".
- **2023-05-04, Q2 FY23:** revenue EUR 4,119m and gross margin 46.6%. The outlook is raised again. This is the peak of the cycle.
- **2023-11-15, FY23:** record revenue and earnings, and further growth expected.
- **2024-05-07, Q2 FY24:** revenue EUR 3,632m. Prolonged weak demand in major target markets leads to a lower FY24 forecast.
- **2024-11-12, Q4 FY24:** "hardly any growth momentum in our end markets except from AI". Strong demand from AI servers and data centers lifts the quarter.
- **2025-02-04, Q1 FY25:** revenue EUR 3,424m (the trough), slightly better than expected, and the outlook is raised.
- **2025-11-12, Q4 FY25:** AI data centers are named a structural growth market.
- **2026-02-04, Q1 FY26:** revenue EUR 3,662m. Capex is raised to about EUR 2.7bn (from 2.2bn) "to further accelerate the expansion of manufacturing capacity for power supplies for AI data centers".
- **2026-05-06, Q2 FY26:** revenue EUR 3,812m. "AI boom strengthens further"; the full-year guidance is raised.
- **2026-08-05, Q3 FY26:** record revenue of EUR 4,172m, with segment result margin 19.1%. The Q4 FY26 outlook is about EUR 4.7bn (+13% q-o-q) and the FY26 outlook about EUR 16.3bn. AI data-center power supplies are "our most important growth driver."

## Methods and conventions
- **Fiscal year** ends 30 September: FY2026Q3 is Apr–Jun 2026, and the Q4 row is the combined Q4 and full-year release. Home market is Xetra (Europe/Berlin, cut-offs 09:00 / 17:35).
- **Event dates:**
  - FY2021Q4–FY2026Q3 come from the IR press-list JSON (`insightsarticlenewsl.pagelisting.json`, type "Quarterly Report").
  - 2015-01 to 2021-08 come from Yahoo earnings dates. These match the IR list on all 20 overlapping dates.
- **Event times:**
  - Quarterly releases from FY2024Q2 to FY2026Q3 (8 rows) are BMO. Each release's own text announces a same-day press/analyst conference at 08:00 CET/CEST, before the 09:00 Xetra open, so the release came out earlier; the exact time is not stated and is left blank.
  - All other quarterly rows are UNKNOWN. FY2021Q4 and FY2023Q1–Q3 announce a 09:30 call, which does not prove a release before 09:00. The 2015–2021 rows have no document.
  - Ad-hoc times come from Infineon's own ad-hoc PDF file names (for example `…-28-march-2023-18-31-uhr…`).
- **Ad-hoc classification:**
  - **Search-confirmed:** the ad-hoc PDF text is not machine-readable, so labels were checked by web search and press coverage. 2019-03-27 14:36 is the FY19 outlook cut (revenue about EUR 8.0bn ±2%, segment result margin 16% from 17.5%; shares -8.6%). 2020-03-26 13:30 is the withdrawal of the FY20 outlook (COVID-19). 2020-05-04 20:59 is the coronavirus impact on the FY20 outlook.
  - **Excluded as not results-related:** 2018-06-08 (topic not verified), 2019-06-03, 2019-06-17 and 2020-05-26 (Cypress deal and capital increases), 2019-09-25 (hybrid bond), 2021-11-25 (CEO succession), 2022-11-14 15:36 (topic not verified), 2023-03-02 (GaN Systems), 2024 (Qimonda) and 2025-04-07 (Marvell automotive Ethernet).
- **CMD:** 2021-10-05 (press release "ahead of its Capital Markets Day"). No other CMDs were found.
- **Not yet published:** Q4 FY26 results are expected around 2026-11-10 (Yahoo).
- **Docs:** for FY2021Q4–FY2026Q3 there are 20 press-release web pages plus 13 press-release PDFs and 1 presentation. PDFs could not be located for FY2022Q1–Q3, FY2023Q4, FY2024Q1 and FY2025Q2–Q4. No transcripts were found.
- **KPIs:**
  - Revenue, gross margin and next-quarter guidance (point estimate, low = high) are filled for 13 quarters; the FY outlook is in `extra_json`.
  - Gross margin is the first "gross margin x%" in the PDF and may be the adjusted rather than the reported figure.
  - Backlog and book-to-bill were not found in the releases (they appear only in investor presentations, which were not parsed). Revenue YoY is blank.
