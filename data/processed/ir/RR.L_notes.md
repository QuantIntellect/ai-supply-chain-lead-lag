# RR.L: Rolls-Royce Holdings plc (LSE, GBP, calendar fiscal year)

Outputs: `RR.L_events.csv` (60 events, 2015-02-13 to 2026-07-30), `RR.L_kpis.csv` (12 rows: FY2022H1 to FY2026H1, plus 3 trading-update rows), `RR.L_manifest.csv` (92 documents). Scripts are in `src/ir_agents/energy/`: `rr_investegate_index.py`, `rr_rns_download.py`, `rr_calendar.py`, `rr_docs.py` and `rr_kpis.py`, plus the helper `rr_common.py`.

## Demand and guidance timeline, 2023-2026 (as stated in releases)

- **2023-02-23 (FY2022 results):** Power Systems (PS) order intake rose 29% to a record £4.3bn, with demand led by power generation "including mission critical backup power". 2023 guidance was underlying operating profit (UOP) of £0.8-1.0bn and free cash flow (FCF) of £0.6-0.8bn.
- **2023-07-26 (unscheduled trading update, positive):** Expected H1 UOP was £660-680m against consensus of £328m. FY2023 guidance was raised to UOP £1.2-1.4bn and FCF £0.9-1.0bn.
- **2023-08-03 (HY2023):** PS orders fell 14% to £1.9bn (book-to-bill 1.1x) and the PS margin was 7.0%. Rolls-Royce SMR entered stage 2 of the UK Generic Design Assessment (GDA).
- **2023-11-28 (Capital Markets Day):** Mid-term targets for the 2027 timeframe were UOP £2.5-2.8bn, margin 13-15%, FCF £2.8-3.1bn and return on capital 16-18%. The PS margin target was 12-14% (8.4% in 2022). Power generation was named a focus end-market.
- **2024-02-22 (FY2023):** PS revenue grew 16%, with 34% growth in power generation "driven by data centre growth, where we have a leading position". 2024 guidance was UOP £1.7-2.0bn and FCF £1.7-1.9bn.
- **2024-05-23 (AGM trading update):** This is the first explicit AI link: the "strong position in the data centre market is providing growth opportunities as we see higher demand from artificial intelligence and cloud services providers".
- **2024-08-01 (HY2024):** Guidance was raised to UOP £2.1-2.3bn and FCF £2.1-2.2bn. PS orders rose 26% (book-to-bill 1.3x). The SMR moved to step 3 of the GDA on 30 Jul 2024 and was shortlisted by Vattenfall.
- **2025-02-27 (FY2024):** Data-centre orders rose 42% and data-centre revenue 46%. PS orders were £5.1bn (+19%) and the PS order backlog £4.8bn. Mid-term targets were upgraded to UOP £3.6-3.9bn and FCF £4.2-4.5bn by 2028. 2025 guidance was UOP £2.7-2.9bn and FCF £2.7-2.9bn. ČEZ and the Czech government named Rolls-Royce SMR preferred supplier in late 2024.
- **2025-05-01 (AGM trading update):** PS book-to-bill was 1.5x on demand for "back-up power generators for data centres". Guidance was held despite tariffs. ČEZ made a strategic investment in Rolls-Royce SMR in March.
- **2025-07-31 (HY2025):** Power generation orders rose 68%, including an 85% yoy rise in data-centre orders; data-centre revenue rose 45%. PS orders were £2.9bn (+32%, book-to-bill 1.4x). Guidance was raised to UOP £3.1-3.2bn and FCF £3.0-3.1bn. Rolls-Royce SMR was selected as sole provider for the UK's first SMR programme.
- **2025-11-13 (trading update):** The next-generation engine (entry into service 2028) "primarily targets the data centre backup power generation market". In October RR launched a fast-start gas generator, available from 2026, that will offer prime power for data centres. The FY2025 release adds that it is aimed at sites awaiting a grid connection.
- **2026-02-26 (FY2025):** PS orders were £6.1bn (+21%, book-to-bill 1.2x), with power generation orders +31% and data-centre revenue +35%. The PS backlog was £6.1bn. Capacity is being expanded in Germany and at Aiken and Mankato in the US, "driven by data centres". 2026 guidance was UOP £4.0-4.2bn and FCF £3.6-3.8bn. Mid-term targets were raised again to UOP £4.9-5.2bn, margin 18-20% and FCF £5.0-5.3bn by 2028.
- **2026-04-30 (AGM trading update):** Q1 power generation orders across gas and diesel were about 50% higher, March was a record month for orders, and the PS backlog was £7.3bn at 31 March.
- **2026-06-26 (Power Systems teach-in webinar):** The deck presents data-centre backup and prime power as the core power-generation market. It cites "~20% OE revenue growth per year to the mid-term driven by data centres".
- **2026-07-30 (HY2026):** PS orders were £4.6bn ("more than a 50% increase", book-to-bill 1.8x). Power generation orders rose 55% on "backup and prime power solutions for data centres", and framework agreements with data-centre customers are in place. The PS backlog was £8.0bn. FY2026 guidance was raised to UOP £4.7-4.9bn and FCF £3.8-4.0bn. Rolls-Royce SMR was selected by Videberg Kraft to supply three SMRs in Sweden.

## Timing methodology

- **Source.** The calendar comes from the Investegate RNS archive for RR. (`https://www.investegate.co.uk/company/RR.?perPage=300&page=N`, 12 pages, 3,332 items back to 1999). The full index is saved as `data/raw/ir/RR.L/_investegate_index.csv`. Each event's `event_time_local` is the HH:MM that Investegate lists for that RNS. The `source_url` is the Investegate page for the announcement.
- **Time zone.** Investegate shows UK local time, not GMT. The discriminating check: the 6 May 2022 notice says the AGM update "will be published at 7am on 12 May", which falls in BST, and Investegate lists that release at 07:00 AM, not 06:00. In addition, the HY2026 page's JSON-LD `dateCreated` is 2026-07-30 07:01:23 for a release stamped 07:00 in the BST period. December notices ("07:00 GMT") agree but do not discriminate, because GMT equals UK local time in winter. No conversion was applied.
- **Cross-check.** The dateline in every downloaded announcement body matches its listing date.
- **Timing classes.** These follow irlib against the LSE session (08:00-16:30). Almost all releases are at 07:00 and so BMO; the 2015-07-30 HY release is at 07:01. The two INTRADAY events are:
  - 2018-10-26 13:16, an unscheduled Trent 7000 statement confirming FY guidance.
  - 2022-05-13 10:00, the Civil Aerospace Investor Day.
- **Two rows without an RNS time.**
  - 2022-05-13 Civil Aerospace Investor Day: the date and the 10:00 UK webcast start come from the 6 May 2022 RNS notice. The time is not an RNS stamp, and the mid-term Civil guidance itself was published in the 07:00 RNS on 2022-05-12.
  - 2026-06-26 Power Systems teach-in webinar: the date comes from the rolls-royce.com results page. No time is published, so it is UNKNOWN.
- **Classification rules.**
  - An annual "Final/Full Year Results" release is `FY`.
  - `trading_update` covers AGM statements, IMSs, pre-close statements, trading statements and updates, and the 2020-10-01 "Proposed Recapitalisation" (the rights-issue release, which contains a "Trading update" section). The fiscal period is the latest quarter covered.
  - `profit_warning` is used when group guidance was cut or withdrawn, with fiscal_period set to the year affected:
    - 2015-07-06: 2015 PBT/FCF guidance cut, unscheduled.
    - 2015-11-12: this was the scheduled Q3 IMS, classified as a warning because of the 2016 profit headwinds.
    - 2020-04-06: COVID, 2020 guidance withdrawn, unscheduled.
    - 2021-01-26: 2021 FCF outflow of about £2bn against the earlier target of positive H2-2021 cash flow, unscheduled.
  - The 2023-07-26 guidance raise is a `trading_update`.
  - `CMD` covers 2015-11-24 (CEO operations-review investor update), 2018-06-15 (Capital Markets Event), 2022-05-13, 2023-11-28 and 2026-06-26.
- **Excluded announcements.**
  - Trent 1000 and Trent 7000 technical updates that only reaffirm guidance: 2018-04-13, 2018-06-11, 2019-04-10 and 2019-09-20. The 2018-10-26 statement is included because its headline is "FY guidance confirmed".
  - Restructuring announcements: 2018-06-14, 2020-05-20 and 2023-10-17.
  - Notices, annual-report and AGM documents, AGM results and buyback releases.
  - The next scheduled event, the 12 Nov 2026 trading update (rolls-royce.com financial calendar), is in the future and was dropped.

## Documents and KPI notes

- **RNS announcements.** These were downloaded with `irlib.download`. For each one a body-only copy (`*_body.html`) was derived, keeping the announcement text and dropping the site chrome. It also removes Investegate's AI-generated "Summary by AI" block, which is not company text. The text files, the manifest `local_path` and the KPI `source_doc` all point at these body copies.
- **Presentations and transcripts.** These come from rolls-royce.com for FY2021 results through HY2026, plus the CMD 2023 deck, its Power Systems deck and transcript, the 2026 Power Systems teach-in deck, and the Dec-2021 trading-update transcript. Some URLs were found by web search; the HY2022 and HY2025 decks and the FY2023 transcript were guessed from naming patterns. All were verified as the right documents.
- **Revenue.** `revenue` is group underlying revenue, measured at the hedge-book achieved FX rate. RR states only the organic change (constant translational currency, excluding M&A), which goes in `extra_json.organic_growth_pct`. `revenue_yoy_pct` is left blank because a reported change in underlying revenue is never stated. `revenue_prior` (the stated comparative), `statutory_revenue` and, where stated, `statutory_revenue_yoy_pct` are in extra_json.
- **Margin.** The headline margin is the underlying operating margin.
- **Orders and backlog.** Group orders and group backlog are not reported, so those columns are blank. PS and Defence order intake, book-to-bill and order backlog are in `segments`. Segment backlogs come from the divisional slides in the results presentations (`segment_orders_backlog_source`). Every transcribed figure is string-checked against its source text in `rr_kpis.py`.

## Gaps

- **Trading-update KPI rows.** These exist only where the update states figures: FY2023Q2 (H1 preview and guidance raise), FY2025Q1 (PS book-to-bill) and FY2026Q1 (PS backlog). The other updates mostly reiterate guidance and give qualitative demand comments.
- **Missing or approximate values.**
  - PS order growth for HY2026 is stated only as "more than 50%" and FY2023 only as "flat", so both are kept as text.
  - HY2022 has no organic % for the segments, so segment growth is the stated "up X%".
  - FY2022H1 guidance was qualitative only.
  - Data-centre revenue and order growth are percentages only; RR does not disclose absolute data-centre revenue or orders.
- **Documents not collected.** Results PDFs duplicate the RNS text and were not downloaded. Investor presentations (roadshow decks) and Investegate pages before 2015 were also skipped. Transcripts for trading-update calls other than Dec 2021 were not searched for. Other investor events, such as the Civil Aerospace and Defence divisional CMD pages, were not explored beyond the CMD 2023 decks.
- **Wayback Machine.** It was unreachable, so older rolls-royce.com archive listings could not be used to confirm completeness. The calendar's completeness rests on the Investegate index (all RNS items, 1999-2026).
