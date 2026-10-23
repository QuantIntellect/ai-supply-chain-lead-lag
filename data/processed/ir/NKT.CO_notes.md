# NKT (NKT.CO) - IR notes

Coverage: 64 events 2015-02-27 to 2026-09-29:
- every Q1, Q2/H1, Q3 and annual report since the FY2014 annual report
- 6 CMD / strategy events (2015-09-23, 2017-09-19, 2022-09-22, 2024-12-02, 2025-11-19, 2026-09-29)
- 4 preliminary-figure releases with outlook raises
- 5 standalone outlook updates
- 1 guidance withdrawal (NKT Photonics, 2020-05-05)

Documents: interim/annual reports, webcast presentations, call transcripts and the quarterly-figures workbooks for 2022-2026, plus CMD decks for 2015, 2017, 2022, 2024 and 2026 and the 2022 CMD transcript (78 files).

KPI panel: discrete quarters FY2022Q1 to FY2026Q2, plus full years FY2022-FY2025 (22 rows).

## Demand narrative 2023-2026

- **2023-04-26 (18:32, prelim Q1) / 2023-05-10 (Q1):** Q1 organic growth was +34% with record operational EBITDA of EUR 56.9m. The high-voltage backlog jumped to EUR 7.0bn (from EUR 4.7bn at end-2022) on offshore-wind awards in the Netherlands and the UK. FY2023 revenue outlook raised to EUR 1.8-1.9bn (from 1.75-1.85bn).
- **2023-05-24:** NKT invested in more high-voltage capacity and upgraded its medium-term financial ambitions.
- **2023-08-15 (13:06) / 2023-08-16 (Q2):** Operational EBITDA outlook raised to EUR 215-245m (from 200-230m). The HV backlog reached EUR 7.6bn, from offshore wind in the UK and Poland plus an interconnector.
- **2023-10-30 (22:05, prelim Q3) / 2023-11-08 (Q3):** Outlook raised again. Q3 organic growth was +44% and the HV backlog hit a record EUR 11.0bn, driven by five firm projects under a 50Hertz framework agreement plus two capacity-reservation agreements.
- **2024-02-21 (FY2023):** Organic growth +36%; HV backlog EUR 10.8bn at year-end.
- **2024-04 to 2024-06:** NKT announced investments in medium-voltage capacity and acquired SolidAl "to address growing grid demand".
- **2024-07-11 (11:55, prelim Q2):** FY2024 revenue outlook raised to EUR 2.33-2.43bn (from 2.21-2.36bn excluding SolidAl). The Q2 report followed on 2024-08-16 with +29% organic growth.
- **2024-12-02 (07:37):** Updated medium-term financial ambitions, with an investor webcast.
- **2025-02-21 (FY2024):** Organic growth +26% and record operational EBITDA of EUR 344m. The HV backlog was EUR 10.6bn. The annual report cites rising electricity demand from "data centres", EV charging and heat pumps.
- **2025-08-14 (17:21 outlook update, 17:23 Q2 report):** FY2025 outlook raised to revenue EUR 2.65-2.75bn (from 2.37-2.52bn) and operational EBITDA EUR 360-390m (from 330-380m). The upgrade was driven by Solutions and Service & Accessories.
- **2025-09-15 to 2026-03-04:** NKT was named preferred bidder for a Scotland-England HV interconnector. It then signed final contracts for two HVDC projects in Scotland (2026-01-19) and a record order for Eastern Green Link 3 (2026-03-04).
- **2025-11-19 (Q3 + strategy):** A new strategy with 2030 medium-term ambitions and new business lines (Transmission / Grid Solutions & Accessories / Distribution). Q3 organic growth was +11%.
- **2026-02-25 (FY2025):** Organic growth +6% with a Q4 of -8%. Operational EBITDA was a record EUR 390m and the backlog EUR 10.2bn. The report links power demand growth to "data centres and the use of artificial intelligence (AI)".
- **2026-05-13 (Q1 2026):** "Record-high order intake" took the Transmission backlog to EUR 13.5bn. The report cites "the build-out of data centres, leading to grid enhancements". Organic growth was -4% (Transmission project ramp-down).
- **2026-08-13 (17:44 outlook update, 17:47 H1 report):** Operational EBITDA outlook raised to EUR 400-430m (from 360-410m); revenue outlook narrowed to EUR 2.65-2.75bn. The backlog was EUR 13.0bn. The 2026-09-29 Investor Day confirmed the 2030 ambitions and set capital-allocation priorities.

Takeaway: the HV/Transmission backlog grew from EUR 2.75bn (Q1 2022) to EUR 11.0bn (Q3 2023) on offshore wind and interconnectors, plateaued at EUR 10-11.5bn through 2025, then stepped up to EUR 13.0-13.5bn in 2026 (UK HVDC links). Data centres and AI appear in the narrative as a driver of grid and distribution demand from FY2024 on. They are not cited as a direct source of HV orders.

## Timing methodology

- **Primary source:** the investors.nkt.com company-announcement listing (`data/raw/ir/NKT.CO/ir_announcements_list.csv`), which shows the local Copenhagen publication time.
- **Cross-check:** every results and ad-hoc stamp from 2015 to Aug 2025 was compared with GlobeNewswire (`globenewswire_list.csv`, ET stamps converted to Europe/Copenhagen). All agree within 2 minutes. The one flagged case (2017-08-17) is a matching artifact with the CMD invitation issued the same morning.
- **Usual practice:** interim and annual reports come out before the open (about 07:30, or 08:00 in 2015-2017).
- **Exceptions:**
  - Q3 2019: 2019-11-20 at 23:22.
  - Q2 2025: 2025-08-14 at 17:23.
  - H1 2026: 2026-08-13 at 17:47.
  - These three are AMC, and the call is the next morning.
- **Ad-hoc preliminary figures and outlook updates:** often AMC (18:09, 18:32, 22:05) or intraday (11:55, 12:19, 13:06).
- **CMD 2017-09-19:** time UNKNOWN. No same-day announcement exists; the date comes from the 2017-08-17 invitation.

## Gaps / caveats

- **Revenue definition:** `revenue` is revenue at standard metal prices (NKT's headline and guidance basis). Market-price revenue is in `extra_json.market_price_revenue`.
- **Data source:** quarterly figures come from NKT's own workbook (`FY2026H1_quarterly-figures-nkt-h1-2026.xlsx`), not re-keyed from the PDFs.
- **Scope of 2022-2023 figures:** operational EBITDA and organic growth are for the power-cable business excluding NKT Photonics (old segment sheet); `extra_json` flags the scope.
- **Margin:** `margin_pct` is computed as operational EBITDA divided by std revenue from the workbook values.
- **Backlog:**
  - It is the high-voltage (from 2025: Transmission) order backlog as stated in the report text.
  - 2022 values are at market metal prices (std-price values are lower, e.g. EUR 4.1bn vs 4.7bn at end-2022).
  - Q2 2022 is blank (the report gives no number).
- **Guidance:** every row carries the full-year outlook stated in that report. The revenue range (std metal prices, EUR m) is in `guidance_rev_low/high`, the operational EBITDA range in `extra_json.guidance_other`, and `extra_json.guidance_year` gives the year it applies to (Q4/FY rows carry next year's outlook). The EBITDA range is missing where the regex did not catch it (Q2/Q4 2022, Q1 2025, FY2025). Intra-quarter changes are in the ad-hoc announcements (`data/raw/ir/NKT.CO/ann_*.html`) and the events file.
- **Order intake:** not populated as a number (only a text snippet where found). Book-to-bill: not stated.
- **Not yet available:** FY2026Q3 is not released (due 2026-11-19).
