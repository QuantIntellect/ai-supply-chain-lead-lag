# Schneider Electric (SU.PA): demand narrative, 2023–2026

Schneider does not disclose order intake or book-to-bill. It discloses backlog only once a year, at year-end:

| Year-end | Backlog | Note |
|---|---|---|
| 2022 | €16.5bn | about 6 months of sales |
| 2023 | €19.2bn | |
| 2024 | €21.4bn | |
| 2025 | €25.4bn | up +18%; Energy Management €21bn, up +21% |

"Demand" below is the company's own wording. It reports demand growth for the Data Center & Networks (DC&N) end-market only qualitatively ("double-digit", "triple-digit"). On calls, the CFO has said the book-to-bill was above 1 in Q1-23, Q3-23, Q2-25 and Q3-25. All growth rates are organic unless stated otherwise. EM = Energy Management. NA = North America.

- **2023-02-16 (FY22 results):** Q4-22 revenue rose +16.0% to €9.3bn, with EM up +17.5%. DC&N had "another quarter of strong demand and double-digit sales growth". Backlog "remains high". FY23 target: revenue +9% to +11%.
- **2023-04-27 (Q1-23):** revenue rose +15.8% and backlog was at a record level at the end of Q1. Pure data centers grew strong double-digit across enterprise, hyperscale, colocation and edge. The FY23 target was raised to +10% to +13%.
- **2023-07-27 (H1-23):** Q2 revenue rose +14.8%. The company first linked AI to its numbers: "Electrification ... and Artificial Intelligence driving increased traction for Data Centers". Backlog kept growing. The target was raised again, to +11% to +13%, and the H1 adjusted EBITA margin reached a record 18.0%.
- **2023-10-26 / 2023-11-09 (Q3-23 and CMD):** Q3 revenue rose +11.5%, with NA EM up +17.7%. In data centers, "AI-related demand is becoming visible", and group backlog grew again. The CMD set a 2024–27 revenue CAGR target of +7% to +10%.
- **2024-02-15 (FY23):** the company entered 2024 with a "record level of backlog", mainly in systems. Discrete automation weakened, and the FY24 target was set at +6% to +8%.
- **2024-07-31 (H1-24):** Q2 revenue rose +7.1%, with EM up +9.8% and Industrial Automation down -3.5%. Pure data-center demand and sales grew strong double-digit, led by the Internet Giants. Systems reached 30% of revenue.
- **2024-10-17 / 2024-10-30:** Schneider announced the acquisition of Motivair (liquid cooling) to "strengthen its leading position in Data Centers". In Q3-24, revenue rose +8.0% (NA EM +18.3%), and DC&N demand and sales both grew strong double-digit.
- **2025-02-20 (FY24):** Q4-24 revenue rose +12.5%, with EM up +15.2% and NA EM up +25.3%. Systems grew +27% in Q4. FY25 target: +7% to +10%.
- **2025-04-28 (Q1-25, published after the close at 17:35):** revenue rose +7.4%. DC&N demand and sales grew strong double-digit, driven by colocation, prefab and cooling. On the call, analysts focused on softer data-center business in Western Europe and on tariffs.
- **2025-07-31 (H1-25):** Q2 revenue rose +8.3%. Data-center demand grew double-digit once one customer's order, moved into H2-25 as expected, is excluded. AI demand was broadening from the Internet Giants to colocation providers. Gross margin fell 90bp because of tariffs and raw-material costs.
- **2025-10-30 (Q3-25):** revenue rose +9.0% against a high Q3-24 base. The company won business from neo-clouds and smaller AI players. The FY25 target was reaffirmed but steered to the lower half of the range.
- **2025-12-11 (CMD):** 2026–30 targets: revenue CAGR of +7% to +10% and +250bp of cumulative adjusted EBITA margin expansion.
- **2026-02-26 (FY25):** Q4-25 revenue rose +10.7% to €11.1bn. Pure data-center demand grew **triple-digit year on year**, from both hyperscale and colocation customers. Year-end backlog was €25.4bn, up +18%. The part to be executed beyond one year rose to €8.0bn from €4.8bn. FY26 target: +7% to +10%.
- **2026-07-30 (H1-26):** Q2 revenue rose +16.5%, with EM up +17.7% and systems up +28%. DC&N demand grew triple-digit, with a record backlog. The FY26 target was raised to +10% to +13%.
- **2026-10-05 to 2026-10-20:**
  - 2026-10-05: Schneider announced the acquisition of PTC.
  - 2026-10-16: Q3-26 results came out about two weeks earlier than usual. Revenue rose +16.9% to €11.5bn (EM +18.8%). DC&N demand grew triple-digit for a second quarter, led by North America, with China and East Asia accelerating. The company said this gives "visibility into 2027 and 2028", and raised the FY26 target to +12% to +14%.
  - 2026-10-19/20: a c.€6.0bn capital increase.

## Sources, method, gaps

- **Release dates:** from Schneider's IR financial-results page, for 2013–2025, parsed from the Nuxt payload into `data/raw/ir/SU.PA/pages/results_table.json`. Dates for 2026 come from the AMF records. The date line on every release PDF was checked against these.
- **Release times:** from the AMF/DILA regulated-information API (`info-financiere.gouv.fr`, dataset `flux-amf-new-prod`, ISIN FR0000121972), which gives the deposit timestamp at dissemination. These were converted to local wall-clock time using each record's own offset field. Records from 2013–2016 carry a fixed +01:00 offset, so applying a plain timezone conversion would put summer releases one hour late.
  - Releases normally go out between 06:59 and 07:32 Paris time, which is BMO.
  - **Exception:** Q1-25 was published on 2025-04-28 at 17:35, which is AMC, and the call was held in the evening.
- **Gaps in timing:**
  - H1-18 and Q3-18 use 07:30 from the 2018 financial calendar ("press release at 7:30am local time").
  - FY16 (2017-02-16) and Q3-19 (2019-10-24) have no time. Both are classed BMO because the calls were in the morning: the FY16 transcript header shows 8:30 GMT, and the Q3-19 call opens with "good morning". The AMF filing for Q3-19 was deposited late, on 25 Oct.
- **CMD rows:** use the time of the investor-day press release. They include the 2017 Digital Day, the 2020 virtual ESG investor day and the 2024 India investor event.
- **Unscheduled update:** 2017-01-09 is a non-cash write-down of deferred tax assets, filed as inside information and coded as `trading_update`.
- **No profit warnings** were found from 2015 to 2026.
- **KPIs:**
  - Quarterly revenue, organic growth and reported growth come from the release text and appendix tables.
  - Revenue and organic growth by business and NA EM are in `extra_json`. The NA EM figure is not available for 2026 because the regions were redefined.
  - Margins are disclosed only for H1 and FY, so they sit on the Q2 and Q4 rows.
  - Backlog is disclosed only at year-end, so it is filled on the Q4 rows only.
  - `book_to_bill` is left blank. The CFO's remarks on book-to-bill are in `extra_json`.
  - `guidance_rev_low/high` give the FY **organic growth %** range, not an amount in euros.
- **Documents:**
  - For 2022Q1–2026Q3: releases, presentations and transcripts, plus the H1 and FY accounts. The H1-24 release was taken from the AMF archive because the IR page has no link to it.
  - For 2013–2021: releases only.
  - The Q3-18 and FY18 release links on the IR page return 404.
