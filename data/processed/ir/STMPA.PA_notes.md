# STMicroelectronics (STMPA.PA / NYSE: STM) — IR notes

## Demand narrative 2023–2026 (from ST earnings releases; USD)
- **2023 (Q1–Q3):** a peak cycle. Net revenues are USD 4.25–4.43bn per quarter and gross margin 47.6–49.7%, driven by automotive and industrial demand.
- **2024-01-25, Q4 2023:** revenues USD 4.28bn and gross margin 45.5%. The Q1 2024 outlook midpoint drops sharply, to about USD 3.6bn (derived range 3.47–3.73bn). This marks the start of the industrial and automotive inventory correction.
- **2024-04-25, Q1 2024:** revenues USD 3.47bn (-18.4% y-o-y) and gross margin 41.7%.
- **2024-07-25 and 2024-10-31:** revenues of USD 3.23–3.32bn and gross margin of 37.7–40.1%. Full-year 2024 plans are cut at both releases.
- **2024-11-20, CMD (Paris):** new 2027–2030 ambition and a manufacturing-reshaping plan.
- **2025-01-30, Q4 2024:** the Q1 2025 outlook implies the trough, with a midpoint of about USD 2.51bn.
- **2025-04-24, Q1 2025:** revenues USD 2.52bn (-27.3% y-o-y) and gross margin 33.4%. This is the cycle bottom.
- **2025-07-24 and 2025-10-23:** recovery, with USD 2.77bn (Q2) and USD 3.19bn (Q3).
- **2026-04-23, Q1 2026:** revenues USD 3.10bn (+23.0% y-o-y). ST says it is "now strategically positioned to capture upside from new AI driven programs… enabling the evolving AI infrastructure", and refers to an expanded strategic agreement announced on 2026-02-09.
- **2026-07-23, Q2 2026:** revenues USD 3.49bn (+26.0% y-o-y) and gross margin 34.8%. Q3 outlook midpoint is USD 3.70bn at about 37.0% gross margin. Q4 revenue is expected to exceed USD 4bn, "mainly driven by our engaged customer programs in AI datacenters and LEO satellites."

## Methods and conventions
- **Events:**
  - The investors.st.com quarterly-results table (release dates from Q2 2012) is cross-checked against EDGAR full-text-search 6-K hits for "STMicroelectronics Reports … Financial Results". Of 47 quarterly dates since 2015, 44 match exactly; three 6-Ks were filed the day after the release (2015-10-29, 2018-10-24, 2020-01-23), and the IR-table date is used for those.
  - **Timing:** ST's "announces timing" releases state that results come out "before the opening of trading on the European Stock Exchanges". This was verified for 2016 (SEC 6-K and ST press items), for the 2020–2022 6-Ks, and for the 2026-10-05 notice. All quarterly rows are therefore BMO (Euronext Paris, Europe/Paris, cut-offs 09:00 / 17:35).
  - An exact time is filled only for Q2 2026: the JSON-LD datePublished of 2026-07-23T01:00:27-04:00, which is 07:00 CEST. Times for other quarters were not individually verified, so `event_time_local` is blank.
  - **CMDs:** 2018-05-15 (London), 2019-05-14 (London), 2022-05-12 and 2024-11-20. Their timing is UNKNOWN.
  - No standalone profit-warning releases were found. ST's guidance changes came inside the quarterly releases.
- **Not yet published:** Q3 2026 results are scheduled for 2026-10-29, BMO, with the call at 09:30 CET. That is after 2026-10-23, so it is not in the events file.
- **Docs:** for FY2021Q4–FY2026Q2 there are 19 earnings releases, 19 earnings presentations and 19 "CEO scripts" (`doc_type=transcript`; these are prepared remarks, not full Q&A transcripts).
- **KPIs:**
  - `revenue` and `gross_margin_pct` come from the "ST reported … net revenues of $X, gross margin of Y%" sentence.
  - `revenue_yoy_pct` is filled only where the release states it.
  - Guidance low and high are derived from the outlook midpoint ± the stated basis points, with `guidance_derived=true` in `extra_json`.
  - Book-to-bill is rarely disclosed, so the field is blank.
- **Caveat:** EDGAR `acceptanceDateTime` values in `data/processed/edgar_filings.parquet` disagree with the EDGAR index page. For example, the STM 6-K of 2022-04-27 shows "Accepted 2022-04-27 16:15:43" on the index but 00:15Z in the parquet. Do not use the parquet times.
