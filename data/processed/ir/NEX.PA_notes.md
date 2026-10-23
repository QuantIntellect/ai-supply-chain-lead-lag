# Nexans (NEX.PA) - IR notes

Coverage: 55 events 2015-02-13 to 2026-10-22 (every Q1 / H1 / Q3 / FY release since FY2014 results, 4 CMD / strategy days, 1 preliminary release, 1 guidance suspension, 1 guidance re-basing). Documents: results press releases 2015-2026, results presentations 2022-2026, 2021 and 2024 CMD materials (70 files). KPI panel FY2022Q1 to FY2026 9M (19 rows).

## Demand narrative 2023-2026 (from the results releases)

- **2023-02-15 (FY2022):** A record year. The Generation & Transmission adjusted backlog reached EUR 3.5bn (+51% y/y), driven by the Celtic Interconnector. Electrification organic growth was +12.9%. FY2023 guidance: EBITDA EUR 570-630m.
- **2023-07-26 (H1 2023):** Guidance raised to EBITDA EUR 610-650m. Record G&T backlog of EUR 5.2bn, which excludes the EUR 1.4bn EuroAsia Interconnector just awarded. Nexans invested in a new cable-laying vessel "to address backlog growth".
- **2023-10-25 (9M 2023):** G&T grew +17.8% organically in Q3. Backlog was EUR 5.2bn, +115% y/y. A third cable-laying vessel was announced. The group overall was flat organically (-0.2% for 9M), dragged by Usages / Other.
- **2024-02-15 (FY2023):** Adjusted EBITDA hit a record EUR 665m and the G&T backlog was EUR 6.1bn. FY2024 guidance: adjusted EBITDA EUR 670-730m. The outlook names "datacenters, industrial and mobility markets" as expected to stay resilient.
- **2024-04-24 (Q1 2024):** Record G&T backlog of EUR 6.7bn. Electrification grew +6.7% organically. The release cites high demand in Middle East & Africa, "notably in datacenters".
- **2024-07-24 (H1 2024):** Electrification grew +14.1% organically and adjusted EBITDA reached EUR 412m (11.6% margin). FY2024 guidance raised to EUR 750-800m. The expanded Halden HV plant is now operational.
- **2024-11-13 (CMD, London):** "2028 ambition: Sparking Electrification". Nexans laid out its 2025-2028 roadmap as an electrification pure player, followed by the sale of AmerCable and Lynxeo.
- **2025-02-19 (FY2024):** Adjusted EBITDA hit a record EUR 804m and the PWR-Transmission backlog was EUR 7.4bn. FY2025 guidance: adjusted EBITDA EUR 770-850m.
- **2025-04-30 (Q1 2025):** Backlog reached a record EUR 8.1bn. Nexans won an RTE HVDC framework agreement worth more than EUR 1bn (offshore wind) and the Malta interconnector award. The release reports no material impact from US tariffs.
- **2025-07-30 (H1 2025):** FY2025 guidance raised to EUR 810-860m adjusted EBITDA. The Electrification margin was 13.7%.
- **2025-10-23 (9M 2025):** Electrification grew +12.6% organically in Q3 and the backlog was EUR 7.9bn (+27% y/y). Nexans agreed to acquire Electro Cables (Canada).
- **2025-12-22 (Autoelectric sale, 10:01 CET):** Nexans entered exclusive talks to sell Autoelectric to Motherson. FY2025 guidance was re-based to continuing operations: adjusted EBITDA EUR 710-760m, FCF EUR 275-375m.
- **2026-02-19 (FY2025):** Organic growth was +8.3% on continuing operations. The backlog was EUR 7.7bn, including EUR 1.2bn for the Great Sea Interconnector. FY2026 guidance: adjusted EBITDA EUR 730-810m, with H1 expected softer than H2.
- **2026-04-28 / 2026-07-29 (Q1, H1 2026):** Group organic growth slowed to +0.1% in Q1 (Electrification +4.9%), and PWR-Transmission growth is "normalizing". Nexans bought Republic Wire in the US and lists "capturing data centers future growth" as a pillar. In H1, FY2026 guidance was raised to EUR 770-840m.
- **2026-10-22 (9M 2026):** Q3 organic growth was +9.0%, with "exceptionally high momentum" in PWR-Grid and PWR-Connect, supported by utility frame agreements and "demand from data centers in North America". The backlog was EUR 7.8bn and guidance was confirmed.

Takeaway for the AI build-out: the transmission backlog ran from EUR 2.4bn to about EUR 8bn between 2022 and 2025, then plateaued at EUR 7.7-7.9bn (2025-2026). Data-center demand appears explicitly from 2024 onward, mostly in low/medium-voltage (PWR-Connect / PWR-Grid, North America and MEA). It is not a transmission driver.

## Timing methodology

- **Primary source:** GlobeNewswire's Nexans organization feed (crawled to `data/raw/ir/NEX.PA/globenewswire_list.csv`, 2013-2026). Its stamps are in US Eastern time and were converted to Europe/Paris with zoneinfo, so DST is handled.
- **Cross-check from Oct 2023:** the Euronext company-news feed (`euronext_press_list.csv`, stamps in CET/CEST). Where both sources cover an event they agree to the minute; the one exception is 2025-12-22 (10:01 vs 10:02), where the earliest stamp is used.
- **Results:** Nexans publishes before the open. Releases came out at 07:30 Paris time from 2015 to mid-2018 and at 07:00 since Nov 2018 (a few 07:04-07:33 outliers in 2019-2020; 06:55 for H1 2025).
- **Exceptions:**
  - 2016-01-26 08:30 (pre-release of net debt and impairments): BMO.
  - 2017-12-13 08:30 (strategic plan "Paced for Growth"): BMO.
  - 2020-03-24 18:40 (Covid-19 update suspending FY2020 guidance): AMC.
  - 2021-02-17 14:00 (Capital Markets Day release): intraday, same day as the 07:00 FY2020 results.
  - 2024-11-13 07:30 (CMD).
- **Event dates:** taken from the stamped releases, which match the release dates in the Nexans PDF file names.

## Gaps / caveats

- **Revenue definition:** `revenue` is sales at standard metal prices (Nexans' headline measure; copper at EUR 5,000/t). IFRS current-price sales are in `extra_json.current_sales` and are stated only in the H1/FY tables and 9M 2023.
- **Restatements:**
  - FY2025 figures are continuing operations (Industry & Solutions reclassified under IFRS 5; 2024 restated to EUR 5,537m).
  - "Generation & Transmission" was renamed PWR-Transmission in 2024/25; the backlog definition is unchanged.
  - Pre-2023 EBITDA is unadjusted. The FY2023 release restated 2022 adjusted EBITDA to EUR 616m.
- **Not captured:**
  - Order intake: Nexans does not report it.
  - Book-to-bill: not stated.
  - Segment-level sales and margins: not transcribed, except Electrification organic growth and the Q1 2026 segment growth rates. They are available in the extracted texts.
- **Q1/Q3 releases:** no EBITDA or margin (Nexans reports sales only).
- **Transcripts:** none published on the IR site.
- **Excluded from events:** the 2026-02-19 "virtual event" deep dive (same day as FY results) and the 2025-03-06 18:10 statement on Great Sea Interconnector rumours. These are not results, guidance or CMD events.
