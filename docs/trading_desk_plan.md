# Turning the research into an automated desk

## Verdict

Do not automate the post-release supply-chain signals as they stand. After costs they earn roughly nothing:

| | Value (2019–2026, walk-forward) |
|---|---|
| Rank IC, 5-day horizon | 0.015 (t = 3.9) |
| Gross return / volatility / Sharpe | 6.0% / 12.3% / 0.49 |
| Net return / Sharpe (10–15 bp one way) | 0.3% / 0.03 |
| Max drawdown (net) | −28% |
| Turnover | 19.5% of book per day |
| Break-even cost | ≈ 12 bp one way |
| Net Sharpe by period | 0.42 (2019–22), −0.35 (2023–24), −0.21 (2025–26) |

Expect a flat-to-losing book with real drawdowns if this model is traded. What works (same-day co-movement, capex / orders ordering) belongs in risk management and slower forecasting.

## Plan

### 1. Use what works now (manual or semi-automated)

- Hedging around reports: size and hedge exposure with the same-day betas (`reports/tables/playbook.csv`, `pair_map.csv`). Tight pairs (Lam / Applied Materials ρ 0.90, Dell / HPE 0.86, STMicro / Infineon 0.85, ASML / ASM 0.81) are where this matters.
- Revenue watchlist: track the capex-driven nowcast (`capex_nowcast.csv`) for Vertiv, Fabrinet, Monolithic Power, Marvell, Arista, Ciena against reported results each quarter.

### 2. Test the two places an edge could exist (4–6 weeks, paid data)

1. **Cross-time-zone opening test.** A US company reports after the 16:00 New York close; its after-hours move is known before Asia and Europe open. Question: do Asian and European suppliers' opening auctions fully price it? Needs US extended-hours prices (16:00–20:00 ET) and European / Asian opening-auction prices. This is the most direct lead-lag trade; the daily-data diagnostic was positive but used prices not available at the foreign open. Spec in `docs/next_steps.md`.
2. **Nowcast vs consensus.** Does the capex-driven revenue nowcast (and the orders lead) predict revenue beats against analyst consensus, and the release-day reaction? Needs point-in-time consensus revenue estimates.

Pass bar, fixed before looking: out-of-sample (2025–26) net Sharpe > 0.5, hedged against the AI basket, realistic costs and capacity (≤ 5% of daily volume), stable sign in both halves of the sample. Anything below is dropped.

Optional third line: options. Same-day betas imply volatility for co-movers on a reporter's day; test whether co-movers' implied volatility under-prices it (needs options data).

### 3. Build the desk only if a test passes

| Component | Requirement |
|---|---|
| Event feed | SEC EDGAR real-time filings, RNS / EQS / AMF / regulatory feeds with time stamps; keep the release calendar (`events.parquet`) current |
| Parsing | Guidance, orders, backlog and capex numbers from releases within seconds (regex plus an LLM extractor with validation) |
| Signal engine | Same definitions as the research code (reaction session, entry after the reporter's session closes, AI-basket hedge) |
| Risk | Market- and AI-sector-neutral (SMH / SOXX or basket hedge), position caps as % of daily volume, blackout around each stock's own earnings, gross / net limits, drawdown stop |
| Execution | Broker API with US, European and Asian access (Interactive Brokers or similar); opening / closing auction orders for Europe and Asia |
| Monitoring | Live vs backtest P&L by signal, slippage vs model, kill switch |
| Compliance | Public information only; record the source and time stamp of every input |

### 4. Roll out slowly

Paper trade for about three months, then 5–10% of intended capital for three to six months. Scale only if live results match the backtest within its error band.

## Realistic expectations

- Most candidate signals fail validation, as most of these did.
- If one survives, a market-neutral book in this niche might reach a net Sharpe of 0.5–1.0, with limited capacity (European small caps such as Aixtron, SUSS and Soitec are thin) and decay as others trade the same news.
- Budget about 2–3 months of research before any live trading, plus data subscriptions (intraday / extended-hours prices, consensus estimates, possibly options).
