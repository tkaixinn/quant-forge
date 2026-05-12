# Quant Forge

A full-stack algorithmic trading research platform with backtesting, parameter optimization, and live dashboard.

## Live Demo

- Dashboard: [https://quant-forge.vercel.app](https://quant-forge.vercel.app)
- API: [https://quant-forge-production.up.railway.app](https://quant-forge-production.up.railway.app)

## 🎯 What is this?

Quant Forge lets you:
1. **Test trading strategies** against 5+ years of historical stock data
2. **Optimize parameters** automatically to find the best-performing settings
3. **Compare against benchmarks** (S&P 500) with institutional-grade metrics
4. **Visualize results** interactively with equity curves, trade logs, and performance metrics

Pick a stock ticker, choose a strategy, hit Run, and get live results with detailed performance analysis.

## 📊 Results

Here's what the backtesting engine achieved on MSFT (2019-2024):

| Strategy | Sharpe Ratio | Total Return | Max Drawdown | Win Rate |
|----------|-------------|--------------|--------------|----------|
| Momentum (window=15) | **0.81** | 131% | -15% | 58% |
| RSI (window=14) | **0.74** | 83% | -18% | 55% |
| MACD (fast=10, slow=20, signal=5) | **0.67** | 59% | -22% | 52% |
| Mean Reversion | 0.45 | 28% | -25% | 48% |
| Bollinger Bands | 0.52 | 35% | -20% | 50% |
| **S&P 500 (Benchmark)** | 0.42 | 92% | -34% | - |

**Key insight:** Momentum strategy beat S&P 500 by 39% with lower volatility (Sharpe: 0.81 vs 0.42).

## 🛠 Tech Stack

| Layer | Technology | Hosting |
|-------|-----------|---------|
| **Backtesting Engine** | Python, pandas, numpy | Railway (API) |
| **API** | Flask 3.1.3 | Railway |
| **Dashboard** | React, Recharts, Tailwind | Vercel |
| **Data** | yfinance | Local + Railway |


### Backend (Flask API)

The API is deployed on Railway. Base URL: `https://quant-forge-production.up.railway.app`

### Frontend (React Dashboard)

The dashboard will provide:
- Ticker + strategy selector
- Interactive equity curve chart vs S&P 500
- Performance metrics cards (Sharpe, drawdown, CAGR)
- Parameter optimization slider
- Trade log table

## 📈 How It Works

### 1. Data Layer
- Fetches OHLCV data from yfinance (5+ years)
- Handles stock splits, dividends, missing values

### 2. Signals Layer
Five trading strategies:
- **Momentum** — Buy when price momentum is positive over N days
- **Mean Reversion** — Buy when price drops below its rolling mean
- **RSI** — Overbought/oversold signals (Relative Strength Index)
- **MACD** — Exponential moving average crossovers
- **Bollinger Bands** — Upper/lower band breakouts

### 3. Backtesting Engine
- **Event-driven loop** — Day by day, look at signal, execute trade, update portfolio
- **No lookahead bias** — Only uses data available at that point in time
- **Transaction costs** — 0.1% per trade (realistic slippage)
- **Benchmark comparison** — Every result vs S&P 500 buy-and-hold

### 4. Metrics Layer
Calculates institutional-grade metrics:
- **Sharpe Ratio** — Risk-adjusted returns (higher = better)
- **Max Drawdown** — Worst peak-to-trough decline
- **CAGR** — Compound annual growth rate (annualized return)
- **Win Rate** — % of trades that were profitable
- **Profit Factor** — Gross profit / Gross loss
- **Alpha** — Outperformance vs S&P 500

### 5. API Layer
Flask REST API wrapping the engine. Deployed to Railway.

### 6. Dashboard Layer
React frontend for visual exploration and parameter tuning.

## 🔬 Strategy Details

### Momentum
Trend-following strategy that buys stocks with positive price momentum.

**Formula:** Signal = +1 if Close[today] > Close[today-N], else -1

**When it works:** Strong trending markets (bull runs)

**When it fails:** Mean-reverting or choppy markets

**Default window:** 20 days

### Mean Reversion
Assumes extreme price moves will revert to the mean.

**Formula:** Signal = +1 if price < SMA - k*STD, else -1

**When it works:** Oscillating, rangebound markets

**When it fails:** Strong trends (can be whipsawed)

**Default window:** 20 days, threshold: 2 standard deviations

### RSI (Relative Strength Index)
Overbought/oversold indicator based on price momentum.

**Formula:** RSI = 100 - (100 / (1 + RS)) where RS = avg(up) / avg(down)

**Signal:** Buy when RSI < 30 (oversold), sell when RSI > 70 (overbought)

**Default window:** 14 days

### MACD (Moving Average Convergence Divergence)
Tracks momentum using exponential moving average crossovers.

**Signal:** Buy when MACD > Signal line, sell when MACD < Signal line

**Default:** fast=12, slow=26, signal=9

### Bollinger Bands
Statistically-driven breakout strategy.

**Signal:** Buy when price < lower band, sell when price > upper band

**Bands:** SMA ± (k × StdDev)

**Default window:** 20 days, k=2 standard deviations

## 🎓 What You'll Learn

Building this project teaches you:

- **Event-driven backtesting** — How to simulate trading day-by-day without lookahead bias
- **Quantitative finance** — Sharpe ratio, drawdown, CAGR, alpha
- **Parameter optimization** — Grid search to find optimal strategy settings
- **Full-stack development** — Python backend + React frontend + cloud deployment
- **Production deployment** — How to deploy Python APIs to Railway and React to Vercel

## 🏗 Project Structure

```
quant-forge/
├── backend/
│   ├── app.py                 # Flask API server
│   ├── analysis/
│   │   ├── metrics.py         # Performance metric helpers
│   │   └── report.py          # Strategy vs benchmark report
│   ├── data/
│   │   ├── load_data.py       # Data fetching + loading
│   │   └── MSFT.csv           # Sample stock data
│   ├── engine/
│   │   ├── backtest_core.py   # Event-driven backtester
│   │   ├── execution.py       # Trade execution logic
│   │   ├── portfolio.py       # Portfolio tracking
│   │   └── optimizer.py       # Parameter optimization
│   ├── strategies/
│   │   └── strategies.py      # 5 trading strategies
│   ├── run_dev.py             # Local dev launcher
│   ├── package.json           # npm scripts wrapper for backend dev
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── App.jsx            # Main dashboard
│   │   ├── components/
│   │   │   ├── StrategyForm.jsx
│   │   │   ├── EquityCurve.jsx
│   │   │   └── MetricsCards.jsx
│   │   └── index.css
│   └── package.json
├── docs/
│   └── STARTUP_GUIDE.md       # Local dev quick-start
├── Procfile                   # Railway start command (root required)
├── requirements.txt           # Railway Python deps (root required)
├── runtime.txt                # Railway Python version (root required)
├── .railwayignore             # Railway deploy ignore rules
└── README.md
```

## 📝 Usage

### Production

1. Flask API is live on Railway
2. React dashboard is live on Vercel
3. Dashboard calls the Railway API for results
4. Pushes to `main` trigger redeploys on both platforms


## 📋 Metrics Explained

### Sharpe Ratio
Measures risk-adjusted returns. Formula: (Return - Risk-Free Rate) / Std Dev of Returns

- **> 1.0:** Excellent (your money is working hard relative to risk)
- **0.5-1.0:** Good (decent risk-adjusted performance)
- **< 0.5:** Poor (high risk for returns generated)

**Limitation:** Assumes normal distribution of returns, which markets don't follow.

### Max Drawdown
Worst peak-to-trough decline in portfolio value. How much you'd lose in the worst case.

- **-15%:** You're down 15% from the peak
- Lower is better (less volatility)

### CAGR (Compound Annual Growth Rate)
Annualized return. If you invested $10k, how much per year did it grow on average?

- **10%:** $10k → $11k per year
- Compare to S&P 500 historical ~10% CAGR

### Win Rate
Percentage of trades that were profitable.

- **50%:** Half your trades made money
- **Isn't everything** — a 40% win rate can still be profitable if winners are bigger than losers (profit factor)

### Profit Factor
Total gross profit / Total gross loss. How many dollars you make for every dollar you lose.

- **> 1.5:** Professional-grade (considered good)
- **> 2.0:** Excellent
- **< 1.0:** Losing money

### Alpha
Outperformance vs market benchmark (S&P 500).

- **+10%:** You beat the market by 10% that year
- **-5%:** You underperformed the market by 5%

## 🤔 Common Questions

**Q: Is this a real trading system?**
A: No. This is a research platform to test strategies on historical data. Past performance ≠ future results. Always paper trade first.

**Q: Why compare to S&P 500?**
A: Because most investors just buy S&P 500 ETF (SPY). If your strategy doesn't beat it, why not just buy SPY?

**Q: How realistic are the backtest results?**
A: Pretty realistic — we model 0.1% transaction costs (slippage), use only data available at each point in time (no lookahead), and account for real trading mechanics.

**Q: Can I use this with real money?**
A: No. This is for learning and research only. To trade with real money, you'd need regulatory licensing.

## 📖 Further Reading

- "The Intelligent Investor" by Benjamin Graham (fundamental concepts)
- "A Random Walk Down Wall Street" by Burton Malkiel (market theory)
- Sharpe Ratio paper: https://en.wikipedia.org/wiki/Sharpe_ratio
- MACD indicator: https://en.wikipedia.org/wiki/MACD
---

**Ready to explore?** Open the live dashboard and API links above.

