# Quant Forge

A full-stack algorithmic trading research platform with event-driven backtesting, parameter optimization, and a live interactive dashboard.

## Live Demo

- Dashboard: [https://quant-forge.vercel.app](https://quant-forge.vercel.app)
- API: [https://quant-forge-production.up.railway.app](https://quant-forge-production.up.railway.app)

## What is this?

Quant Forge lets you:
1. **Test trading strategies** against 5+ years of historical stock data
2. **Optimize parameters** automatically to find the best-performing settings
3. **Compare against benchmarks** (S&P 500) with institutional-grade metrics
4. **Visualize results** interactively with equity curves, trade logs, and performance metrics

Pick a stock ticker, choose a strategy, set a date range, hit Run, and get live results with detailed performance analysis.

## Tech Stack

| Layer | Technology | Hosting |
|-------|-----------|---------|
| Backtesting Engine | Python, pandas, numpy | Railway |
| API | Flask | Railway |
| Dashboard | React, Recharts, Tailwind CSS | Vercel |
| Data | yfinance | Fetched on demand |

## How It Works

### 1. Data Layer
- Fetches OHLCV (Open, High, Low, Close, Volume) data from yfinance
- Handles stock splits, missing values, and forward-fills trading gaps
- SPY downloaded alongside each backtest as the benchmark

### 2. Signal Generation
Five trading strategies, each outputting +1 (buy), -1 (sell), or 0 (flat) per day:

**Momentum** — Buy when N-day price return is positive, sell when negative.
- Formula: `signal = +1 if pct_change(N) > 0 else -1`
- Works in: strong trending markets
- Fails in: choppy, mean-reverting markets
- Default: window = 20 days

**Mean Reversion** — Buy when price is statistically oversold, sell when overbought, exit when price returns near the mean.
- Formula: `z = (price - SMA) / STD`. Buy if z < −threshold, sell if z > threshold, flat if |z| < 0.5
- Works in: rangebound, oscillating markets
- Fails in: strong trends
- Default: window = 20 days, threshold = 2σ

**RSI (Relative Strength Index)** — Overbought/oversold momentum indicator.
- Formula: `RSI = 100 - (100 / (1 + avg_gain / avg_loss))`
- Signal: buy when RSI < 30 (oversold), sell when RSI > 70 (overbought)
- Default: window = 14 days

**MACD (Moving Average Convergence Divergence)** — Trades crossovers between the MACD line and its signal line.
- Signal: buy when MACD crosses above signal line, sell when it crosses below (crossover only, not level)
- Default: fast = 12, slow = 26, signal = 9

**Bollinger Bands** — Statistically-driven breakout strategy.
- Signal: buy when price crosses below lower band, sell when price crosses above upper band
- Bands: `SMA ± (k × STD)`
- Default: window = 20 days, k = 2

### 3. Backtesting Engine
- **Event-driven loop** — Iterates day by day, generating signals and executing trades sequentially
- **No lookahead bias** — Signal from day T is only acted on at day T+1's price
- **Transaction costs** — 0.1% per trade on trade value (both buy and sell)
- **Whole shares only** — Fractional shares not used; leftover cash stays in portfolio
- **Benchmark comparison** — Every result compared against SPY buy-and-hold over the same period

### 4. Metrics Layer
All metrics calculated after the backtest completes:

- **Sharpe Ratio** — Annualised risk-adjusted return: `√252 × mean(excess_returns) / std(excess_returns)`. Risk-free rate set to 0%.
- **Max Drawdown** — Worst peak-to-trough portfolio decline
- **CAGR** — Compound Annual Growth Rate: `(final / initial) ^ (1 / years) - 1`
- **Win Rate** — % of completed buy→sell round trips that were profitable
- **Profit Factor** — Gross profit / gross loss across all trades
- **Alpha** — Strategy CAGR minus benchmark CAGR

## Metrics Reference

### Sharpe Ratio
Risk-adjusted return. `√252 × mean(daily excess returns) / std(daily excess returns)`.
- > 1.0 — excellent
- 0.5–1.0 — good
- < 0.5 — poor risk/reward

**Limitation:** Assumes normally distributed returns and penalises upside volatility equally to downside.

### Max Drawdown
Worst peak-to-trough decline. Lower magnitude is better.

### CAGR
Annualised return. Compare against S&P 500 historical average (~10%).

### Win Rate
% of completed round-trip trades that were profitable. Not sufficient alone — a 40% win rate with large winners can still be profitable (see profit factor).

### Profit Factor
Gross profit divided by gross loss. Above 1.5 is generally considered good; above 2.0 is excellent.

### Alpha
Strategy CAGR minus benchmark CAGR. Positive alpha means the strategy outperformed buy-and-hold SPY.

## Known Limitations

- **Risk-free rate set to 0%** — Sharpe ratio uses 0% risk-free rate. Current US Treasury rate (~4.5%) would meaningfully reduce reported Sharpe scores.
- **Daily OHLCV data only** — Uses end-of-day close prices. Real strategies use tick or minute data with bid/ask spreads, which would increase effective transaction costs.
- **Long-only execution** — Mean reversion and Bollinger Bands generate -1 signals but the engine exits rather than going short. True short selling would require margin and borrowing costs.
- **Single asset, no position sizing** — Each backtest runs on one ticker with full capital allocation. No diversification or Kelly criterion sizing.
- **Survivorship bias** — Only tests tickers you choose. A rigorous backtest would include all historical constituents including delisted stocks.
- **No market impact model** — Flat 0.1% transaction cost does not capture real slippage for large orders or illiquid stocks.
- **Parameter optimisation overfitting** — Grid search finds best in-sample parameters. Out-of-sample walk-forward validation not yet implemented.

*This is a research and learning platform. Past backtest performance does not predict future returns. Not financial advice.*