# Data sources

Every input, the script that fetches it, what it covers and its known gaps. Refresh order from an empty `data/` folder is at the bottom.

## Market data

| Source | Script | Output | Coverage / notes |
|---|---|---|---|
| Yahoo Finance via `yfinance` 1.7 | `fetch_prices.py` | `data/processed/prices/prices_long.parquet` (local only) | Daily OHLCV, raw and adjusted, 2014-06-02 → 2026-10-22, for all 96 tickers, 4 ADR lines (ASML, STM, NOK, SAP) and 21 benchmarks (SPY, QQQ, SMH, SOXX, sector ETFs, STOXX 600, DAX, CAC, FTSE, AEX, SMI, TAIEX, KOSPI, Nikkei, EURUSD, VIX). Opens are unreliable for some names (overnight return 0 on 5–15% of days for WULF, SOI.PA, OKLO, NKT.CO); the FTSE index has no usable opens. |
| Yahoo earnings dates | `fetch_earnings_dates.py` | `yahoo_earnings_dates.parquet` | Up to 100 past dates per ticker with EPS estimate, actual and surprise; time stamps are approximate. Almost empty for SU.PA, NEX.PA, SOI.PA, VACN.SW, CAP.PA, RR.L (filled by IR calendars). |

## SEC EDGAR (requires a declared User-Agent)

| Source | Script | Output | Notes |
|---|---|---|---|
| Submissions JSON | `fetch_edgar.py` | `edgar_filings.parquet`, `sec_cik_map.csv` | 20,958 filings (8-K, 10-Q, 10-K, 6-K, 20-F) for 65 SEC registrants incl. ADR filers (ASML, STM, NOK, SAP, TSM, ARM, NBIS, CLS, IREN). `acceptanceDateTime` is offset, do not use for timing. |
| Filing index pages | `edgar_index.py 8k` / `6k` | `edgar_earnings_index[_6k].parquet`, `edgar_exhibits[_6k].parquet` | Authoritative ET "Accepted" stamps for 2,350 earnings 8-Ks and 2,664 6-Ks; exhibit tables. |
| XBRL companyfacts | `fetch_xbrl.py` | `fundamentals_q.parquet` | Quarterly revenue, capex, finance-lease principal, gross profit, operating income, RPO, inventory, deferred revenue for US-GAAP filers; discrete quarters derived from YTD facts. IFRS 20-F filers have annual data only. |
| Documents | `fetch_edgar_docs.py` | `edgar_text/` (local only), `edgar_docs_index.csv` | 4,071 documents: 8-K EX-99 press releases (2,842), earnings-period 6-K exhibits (1,104), latest two 10-K / 20-F per company (129). |
| TSMC 6-K monthly revenue | `tsmc_monthly.py` | `tsmc_monthly.csv` | 153 months, 2013-12 → 2026-09, with MoM / YoY. |

## Earnings-call transcripts

| Source | Script | Output | Notes |
|---|---|---|---|
| Motley Fool | `fetch_fool.py` | `transcripts/<T>/*.txt` (local only), `fool_transcripts_index.csv` | 1,212 transcripts for 65 US-listed names (1,192 after de-duplication), mostly 2018–2026. Discovered through monthly sitemaps. Missing quarters include NVIDIA Feb 2024 and May–Aug 2025, Meta 2023, Micron 2021–23, Oracle Q1 FY26, Alphabet Q2 2026. The site returns HTTP 429 under load; `fool_gapfill.py` (URL guessing) found nothing and was stopped. File dates can differ from call dates; corrected with `us_notes/call_date_map_*.csv`. |
| Company-published transcripts | European IR collectors | `data/raw/ir/<T>/`, `ir_text/<T>/` (local only) | ASML (43), Dassault (47), Deutsche Telekom (18), NKT (19), Rolls-Royce (12), Aixtron (11), STMicro CEO scripts (19). |

## European investor relations (24 companies)

Collected by five agents (`src/ir_agents/*`), one folder per sector group. Each company has `data/processed/ir/<T>_events.csv` (release calendar with local times and BMO / AMC class), `<T>_kpis.csv` (quarterly KPIs), `<T>_manifest.csv` (downloaded documents) and `<T>_notes.md` (methods, gaps and a dated 2023–26 demand narrative). 2,154 documents in total.

| Group | Companies | Timing quality | KPI highlights |
|---|---|---|---|
| Semicap | ASML, ASM International, BESI, Aixtron, VAT | ASML 07:00 BMO (48 results); ASM after close (~18:00); BESI, VAT, Aixtron BMO | Bookings / orders, book-to-bill, backlog. ASML stopped disclosing bookings after 2025 Q4. |
| Chips / network | Infineon, STMicro, Soitec, SUSS, Nokia | Nokia exact (08:00 Helsinki); STM BMO; Soitec after close; SUSS exact since mid-2020; Infineon mostly date-only before 2024 | Revenue, gross margin, guidance; Nokia AI & cloud orders only for 2026 Q3. |
| Electrical / DC | Schneider, Siemens, ABB, Legrand, Munters | Schneider ~07:30 Paris (AMF stamps); Siemens BMO except three evening Q1s; ABB BMO; Legrand, Munters exact | ABB orders since 2015; Siemens orders and book-to-bill by segment; Munters data-center orders; Schneider data-center commentary (no order intake disclosed). |
| Energy / cables | Siemens Energy, Rolls-Royce, Prysmian, Nexans, NKT | RR 07:00 RNS; Prysmian intraday until 9M 2023 then 07:00; Siemens Energy FY24 / FY25 released after the close | Siemens Energy orders, backlog, book-to-bill by segment; cable transmission backlogs; RR Power Systems data-center growth. |
| Software / telco | SAP, Deutsche Telekom, Dassault, Capgemini | SAP after the close since Q3 2023 (~22:05 CEST); others 07:00 BMO | SAP current cloud backlog; Capgemini bookings and GenAI share; T-Systems order entry. |

## NVIDIA keynotes and the Berlin slide

`src/keynotes/*` → `data/processed/keynotes/`: 32 keynotes 2023-01 → 2026-10 (CES, GTC, Computex / GTC Taipei, GTC Paris, GTC DC, GTC Berlin, SIGGRAPH, SC, Davos, AI Summits, partner events), 454 documents (live blogs and press kits; 2023 kits from Wayback snapshots), 3,610 company mentions across 414 companies (60 universe tickers). `keynote_time_et` carries a UTC offset; 11 keynotes have no exact start time. Hub pages can contain up to ~10 days of pre-keynote content. The YouTube video could not be downloaded (bot check), so the record is NVIDIA's text. `config/private_companies.csv` describes the 39 private companies on the Berlin slide (identities resolved: "AWbotics" = Wandelbots, the unreadable model logo = Ineffable Intelligence, Radiant = Brookfield's AI-cloud unit, Volta = Volta Infra, Firebird = Armenian AI-factory cloud, Cursive at medium confidence).

## LLM reading passes over the calls

Two agents read `data/processed/digests/<T>.md` (auto-extracted demand sentences per call, 2022+) for 65 US-listed companies and wrote `data/processed/us_notes/`: per-company dated notes, 2,511 demand statements with verbatim management quotes (`demand_signals_*.csv`), 1,038 stated relationships (`relations_*.csv`), and 85 hyperscaler capex guidance statements. Quotes were validated by script against the transcripts.

## Refresh order (from an empty data folder)

```bash
PY=".venv/bin/python -I"
$PY src/fetch_prices.py
$PY src/fetch_edgar.py
$PY src/edgar_index.py 8k && $PY src/edgar_index.py 6k
$PY src/fetch_earnings_dates.py
$PY src/fetch_xbrl.py
$PY src/tsmc_monthly.py
$PY src/fetch_fool.py          # slow; rate-limited
$PY src/fetch_edgar_docs.py
./run_all.sh                    # all analyses, report, generated docs
```

The European IR outputs, keynote outputs and US call notes are committed; their collectors are one-off scripts with absolute paths from the original machine. To refresh them, re-run the relevant collector (after fixing paths) or repeat the agent task described in `PROGRESS.md`.
