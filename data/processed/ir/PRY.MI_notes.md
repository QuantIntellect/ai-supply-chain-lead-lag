# PRY.MI (Prysmian S.p.A.): IR notes

Sources: prysmian.com Results Centre (results press releases and presentations), the prysmian.com newsroom, and the regulated-information storages. Prysmian has used eMarket Storage (Spafid Connect, now Teleborsa) since about 2015. Earlier filings (2014 to Feb 2015) are on 1Info (Computershare). All figures are in EUR m unless stated otherwise. Every number below is taken from the release named.

## Demand narrative 2023-2026 (dated)

- **2023-03-09 (FY22).** Projects order book reached €8.4bn. Energy sales grew +12.3%, "fuelled by renewables, power distribution and data centres". FY23 guidance was adj. EBITDA €1,375-1,525m and FCF €450-550m.
- **2023-07-27 (1H23).** Prysmian took €5.4bn of new Projects orders year to date. The order book was a record €9.1bn, not counting EGL1 and EGL2. FY23 guidance rose to adj. EBITDA €1,575-1,675m and FCF €550-650m. Telecom volumes slowed (-5.2% organic).
- **2023-10-05 (first-ever CMD, Naples, "Connect, to lead").** The company reshaped into four segments: Transmission, Power Grid, Electrification and Digital Solutions. 2027 targets were EBITDA of €2bn (±€100m), FCF of €900m-1bn and capex of €2.7bn over 2023-27.
- **2023-11-09 (9M23).** Projects backlog was about €10bn, plus about €10bn of orders with solid commitment (about €20bn in total). New orders of €13bn were awarded year to date. Telecom slowed, mainly in the US.
- **2024-02-29 (FY23).** Transmission backlog hit a record €18bn. FY24 outlook: adj. EBITDA €1,575-1,675m and FCF €675-775m.
- **2024-04-15.** Prysmian agreed to buy Encore Wire for $290/share (eMarket stamp 05:57, before the market opened). The deal closed on 2024-07-02. On 2024-08-01 the 1H24 release raised FY24 guidance to adj. EBITDA €1,900-1,950m. Power Grid margin was 13.2%, helped by grid enhancement in North America and EMEA.
- **2025-02-27 (FY24).** Transmission backlog was about €17bn. Transmission grew +33.7% organic in Q4. FY25 outlook: adj. EBITDA €2,250-2,350m.
- **2025-03-25/26.** Prysmian announced the Channell acquisition for Digital Solutions and held its CMD in New York. The 2028 targets were adj. EBITDA €2.95-3.15bn, FCF €1.5-1.7bn and more than 55% of revenues from solutions.
- **2025-07-31 and 2025-10-30.** FY25 guidance was raised twice: first to €2,300-2,375m, then to €2,375-2,425m (FCF €1,025-1,125m). Transmission organic growth was +22.8% in Q2 and +39.0% in Q3. Backlog was about €16bn, plus about €3bn of awards (EGL4, Tunita) not yet booked. The CEO tied I&C to data-center demand.
- **2026-02-26 (FY25).** This was the record year: adj. EBITDA €2,398m and FCF €1,171m. Transmission backlog was about €17bn including EGL4, plus about €2bn not yet booked. I&C growth was "driven by data center expansion in North America". FY26 outlook: adj. EBITDA €2,625-2,775m.
- **2026-04-30 (Q1'26).** I&C North America grew +10% organic, "driven by data centers". Digital Solutions grew +9.0% organic because "fiber demand for data centers" is surging. FY26 guidance was confirmed.
- **2026-07-30 (Q2'26/1H).** This was the best quarter yet: adj. EBITDA €730m and +9.4% organic growth. FY26 guidance rose to adj. EBITDA €2,800-2,900m and FCF €1,650-1,750m. The "transformative Molex deal" takes Prysmian into the inside-data-center space. Digital Solutions margin was 23.8%. The CEO cites the "AI-driven economy". A new CMD is planned within 1H27.
- **2026-08-03.** Prysmian agreed to buy Atkore (eMarket stamp 07:01). The deal closed on 2026-10-19 (eMarket stamp 14:40). Q3'26 results are scheduled for 2026-10-29. That date is in the future, so it is excluded from the events file.

## Timing methodology

- **Main source for the 52 events.** The time is the "Data/Ora Inizio Diffusione" stamp on the SDIR cover sheet of the regulatory PDF in eMarket Storage (emarketstorage.it). These were parsed by `pry_sdir_covers.py` into `data/raw/ir/PRY.MI/sdir_covers.csv`.
  - Only Prysmian filings (number prefix `0902-`) are used.
  - When the Italian and English versions were filed separately, the earlier stamp is used. That is usually the Italian one, about 1 minute earlier.
  - Stamps are in Italian local time. For 2024+ they match the newsroom datelines within a minute.
- **How the filings were found.**
  - The public eMarket listing only goes back to 30 Oct 2023.
  - Older filings, migrated into the storage in 2022-2023, were found by web search (`site:emarketstorage.it`).
  - Two filings were located by probing sequential storage IDs (`pry_probe_sdir.py`): the 2018-06-20 combined-guidance release (20:17) and the FY2019 release on 2020-03-05 (17:45).
- **2015-2016 filings.** The cover's "Inizio Diffusione presunta" is about 15 minutes after receipt (for example, receipt 15:47, dissemination 16:02). I used the dissemination time; classes are the same under either stamp.
- **FY2014 (2015-02-25).** The stamp is 1Info's `dataDiffusione` at 17:23 (`pry_1info.py`). That is 7 minutes before the 17:30 close, so it is INTRADAY. Its source_url points to the 1Info portal; the record comes from `POST https://www.1info.it/PORTALE1INFO/API/Comunicati` with `SearchFilter[emittente]=902`, saved in `data/raw/ir/PRY.MI/1info_index.json`.
- **Closing-auction edge case.** Q1 2019 (2019-05-13) went out at 17:33:09. That is inside Borsa Italiana's closing auction (17:30-17:35). It is classed AMC under the 17:30 rule, but the news may be partly in that day's closing price. No other event falls between 17:30 and 17:36.
- **What I deliberately did not use.**
  - Newsroom clock times before 2024. Their gap to the SDIR ranges from a couple of minutes to over two hours, with no consistent offset; for example, 9M23 shows 11:43 on the newsroom against SDIR 13:59, and some entries show "12:00 AM" or "4:41 AM".
  - Yahoo timestamps. Yahoo dates are often 1-5 days off the SDIR dates, for example 2020-03-06 against the actual 2020-03-05.
- **How the timing pattern changed.**

  | Period | Release time | Conference call |
  |---|---|---|
  | 2015 to 1Q20 | about 15:00-17:45 | 18:00 |
  | 1H20 to 9M23 | about 13:00-15:05 | 16:00 |
  | FY23 onwards | about 06:40-07:15 | 10:00 |

- **Event classification.**
  - The 2018-06-20 "Information document - combined guidance 2018" (Prysmian plus General Cable) is a `trading_update`.
  - The 2018-06-22 guidance cut (combined adj. EBITDA €860-920m, due to Western Link) is a `profit_warning`.
  - The 2019-04-17 re-approved FY2018 results (an extra €70m Western Link provision; FY19 guidance confirmed) is a `profit_warning` for FY2018.
  - Mid-year releases are coded H1. Their SDIR titles are "Results at/as of 30 June", even though the 2025-26 headlines say "Q2 & 1H".

## Gaps

- **Events not included.** Western Link operational updates (2018-09-12, 2018-10-16, 2019-02-20, 2019-02-27, 2019-04-08 at SDIR 18:11, 2019-11-23, 2020-01-12, 2020-01-16) carry no guidance change. Neither does the 2020-03-30 Covid dividend cut. None of these are in the events file. The 2016-2017 Western Link costs appeared inside the results releases, and I found no separate guidance announcement for them.
- **Transcripts.** None found on the Results Centre or linked from the releases; only webcast links. The manifest has press releases and presentations only.
- **KPIs.**
  - There is no revenue guidance, so `guidance_rev_*` is blank. EBITDA and FCF guidance are in `guidance_other`.
  - Segment detail is partial for 2022-2023 (old Projects/Energy/Telecom: headline organic growth and margins only). It is complete for 2024+, parsed from the release tables.
  - Discrete-quarter rows exist only where a release has a quarterly table: 3Q24, 4Q24, 2Q25, 3Q25, 4Q25 and 2Q26. Quarterly organic growth for the other periods is in `q_organic_growth_pct` where stated.
  - Backlog is not stated as a number for 9M24 ("substantially stable vs June").
- **Margin definitions change over time.** 1Q22/1H22 headline margins are at 2021 metal prices. 2023-24 margins are at current metal prices. From 2025 they are at standard metal prices. Check `margin_def` before comparing periods.
- **revenue_yoy_pct.** This is the nominal change, computed from the current and prior-year figures stated in each release.
