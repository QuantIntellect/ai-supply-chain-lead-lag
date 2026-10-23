# SUSS MicroTec (SMHN.DE) — IR notes

## Demand narrative 2023–2026 (from SUSS releases, EQS)
- **2023-01-09 16:26 CET, prelim:** FY2022 sales and EBIT margin forecast to beat market expectations.
- **2023-02-02, CMD:** targets to 2025 confirmed.
- **2023-07-27 17:08 CEST, profit warning:** FY2023 forecast adjusted.
- **2023-08-03:** order entry in H2 "may benefit from the announced capacity expansions … in semiconductors for AI applications."
- **2023-10-25 17:19, profit warning:** FY2023 forecast adjusted on preliminary Q3 figures.
- **2023-11-09:** record bonder orders in Q3; shipment delays slow sales.
- **2024-03-27:** order momentum "driven by capacity expansions for the production of microchips used in Artificial Intelligence (AI) applications", with the bonder business (temporary bonding for HBM and AI) expected to lead growth.
- **2024-04-18 10:37 CEST, ad hoc:** Q1 2024 well above the prior year. Order intake EUR 98.3m, backlog EUR 456.9m and gross margin 39.1%.
- **2024-07-18 19:23, ad hoc:** FY2024 guidance raised.
- **2024-08-07:** Q2 orders were mostly temporary-bonding tools, plus a hybrid-bonding order.
- **2025-01-16 20:17, prelim:** FY2024 sales of about EUR 445m, beating the EUR 380–410m forecast.
- **2025-10-27 18:47 CET, profit warning:** Q3 2025 gross margin 33.1% against 38.1% consensus, and the FY2025 gross-margin guidance is cut to 35–37%.
- **2026-03-30:** FY2025 record sales, "mainly driven by AI chip modules".
- **2026-05-07:** Q1 2026 order intake reaches a record EUR 149.3m on demand from the AI chip-module value chain.
- **2026-08-06:** Q2 2026 order intake reaches a record EUR 260.7m, including about EUR 115m of coating tools for an OSAT supplying "a leading player in the AI chip module value chain". The order book is a record EUR 473.7m, of which about EUR 220m converts in 2027.

## Methods and conventions
- **Calendar year**, home market Xetra (Europe/Berlin, cut-offs 09:00 / 17:35).
- **Event types:** prelim = preliminary FY or quarter figures; FY = annual report; Q2 = half-year report.
- **Times:**
  - From June 2020 on, times come from the EQS stamp ("DD-Mon-YYYY / HH:MM CET/CEST" or "DD.MM.YYYY / HH:MM") on each suss.com release page.
  - Where that stamp is missing, the suss.com page timestamp is used; it matched the EQS stamp in the cases checked.
  - Regular reports from 2023 on are published at 07:30 (BMO). Ad-hocs are often intraday or after the close.
- **Gaps:**
  - 2015 to May 2020 rows come from Yahoo report dates with timing UNKNOWN, because the suss.com news archive starts in June 2020.
  - Missing for that period: the Q1–Q3 reports of 2017 and 2018, the FY2018 annual report (Mar 2019), Q3 2019, Q1 2020, and all ad-hocs before June 2020.
- **Not yet published:** Q3 2026 report (about 2026-11-05).
- **Docs:**
  - 14 interim reports and 4 annual reports (2022–2026, from suss.com/finanzberichte).
  - 30 release pages saved as HTML (`doc_type=press_release`).
  - 1 investor presentation (October 2026).
- **KPIs:**
  - Regex over the release text. Coverage is partial and the extraction should be reviewed.
  - Book-to-bill is derived as orders / sales only when both are found, and flagged in `extra_json`.
  - Several quarters (FY2024Q3–FY2025Q3) came back empty; their figures are in the interim-report PDFs, which were not parsed.
