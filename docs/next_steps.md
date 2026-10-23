# Research backlog

Ordered by expected value. Each item states the data it needs, the design and the pass bar. Log every new test in `PROGRESS.md` before looking at results.

## 1. Cross-time-zone opening reaction (highest priority)

- **Question:** after a US after-close release (NVDA, MSFT, GOOGL, AMZN, META, AVGO, MU, AMD, MRVL, ORCL, DELL…), do European and Asian edge partners and same-layer peers under-react at their opening auction and drift during their session?
- **Data:** US extended-hours trades or 1-minute bars (16:00–20:00 ET) for reporters; opening-auction and intraday prices for European (Xetra, Euronext, SIX, LSE) and Asian (TWSE, KRX, TSE) responders. Vendors: Interactive Brokers historical API, Databento, Polygon (US), exchange data for EU/Asia.
- **Design:** signal = reporter's move from the 16:00 close to 20:00 ET (known before Taipei opens at 21:00 ET and Europe at 03:00 ET). Responder outcome = auction-to-close and auction-to-next-close returns vs the regional AI basket. Use the existing event calendar (`events.parquet`), responder sets from `edges.csv` and same-layer membership, and the time-zone rules in `events.Calendar`. Fit 2015–2024, test 2025–26.
- **Pass bar:** hold-out net Sharpe > 0.5 after auction costs, positive in both halves, capacity ≤ 5% of opening-auction volume.

## 2. Nowcast vs consensus

- **Question:** do the capex-driven revenue nowcast (`capex_nowcast.csv`) and order leads (`orders_panel.parquet`) predict revenue surprises vs consensus, and do those predicted surprises move prices on release day?
- **Data:** point-in-time consensus revenue and guidance estimates (LSEG I/B/E/S, FactSet, Visible Alpha, or a cheaper API with history).
- **Design:** predicted Δ revenue growth minus consensus-implied Δ growth → sign of the revenue surprise and release-day AR. Quarterly, 2016–2026; walk-forward.
- **Pass bar:** surprise-sign hit rate > 60% out of sample, and a release-day long-short (AI-basket hedged) with net Sharpe > 0.5.

## 3. Options around reports

- **Question:** does co-movers' implied volatility on a reporter's release day under-price the same-day beta moves?
- **Data:** daily implied volatility / option prices for US names (OptionMetrics, ORATS, CBOE DataShop).
- **Design:** expected co-mover move = β × reporter implied move; compare with co-mover's implied event volatility; straddle P&L.

## 4. Data quality

- Fill transcript gaps (NVIDIA Feb 2024, May–Aug 2025; Meta 2023; Micron 2021–23; Oracle Q1 FY26; Alphabet Q2 2026) from a licensed transcript source.
- Verify the 27 "industry knowledge" links and single-mention call links against 10-K supplier / customer disclosures; drop or upgrade.
- Add Infineon 2015–2021 and SUSS pre-2020 exact release times (EQS archive); add Asian release times (TWSE MOPS, KRX DART).
- Replace Yahoo EPS surprises with a consensus source (also needed for item 2).
- Add point-in-time universe membership to reduce survivorship (e.g., include companies that were AI darlings and fell out).

## 5. Maintenance after each earnings season

1. `fetch_prices.py`, `fetch_edgar.py`, `edgar_index.py 8k`, `fetch_earnings_dates.py`, `fetch_xbrl.py`, `tsmc_monthly.py`; append new European releases to `data/processed/ir/<T>_events.csv` and `_kpis.csv`.
2. `fetch_fool.py` for new transcripts (slow), then `digests.py`; extend `us_notes` with a reading pass on the new calls.
3. `./run_all.sh`, review `reports/run_all.log`, update `docs/findings.md` if a conclusion changes, republish the report.
4. Score the nowcast against the reported quarter (Vertiv, Fabrinet, Monolithic Power for 2026 Q3; Marvell, Arista, Ciena for 2026 Q4).
