import React, { useState, useEffect } from 'react'
import { API_BASE_URL } from '../lib/api'

const STRATEGIES = [
  {
    name: 'momentum',
    label: 'Momentum',
    description: 'Buy positive momentum, sell negative momentum'
  },
  {
    name: 'mean_reversion',
    label: 'Mean Reversion',
    description: 'Buy oversold (z < -threshold), sell overbought (z > threshold), flat near mean'
  },
  {
    name: 'rsi',
    label: 'RSI',
    description: 'Relative Strength Index signals'
  },
  {
    name: 'macd',
    label: 'MACD',
    description: 'Moving Average Convergence Divergence crossover'
  },
  {
    name: 'bollinger_bands',
    label: 'Bollinger Bands',
    description: 'Buy below lower band, sell above upper band'
  }
]

export default function StrategyForm({ onBacktest, onOptimize, loading }) {
  const [ticker, setTicker] = useState('MSFT')
  const [strategy, setStrategy] = useState('momentum')
  const [mode, setMode] = useState('backtest')

  // Shared param
  const [window, setWindow] = useState(20)

  // Mean reversion specific
  const [threshold, setThreshold] = useState(2)

  // Bollinger Bands specific — separate num_std so it's independent from threshold
  const [numStd, setNumStd] = useState(2)

  // RSI specific
  const [rsiOverbought, setRsiOverbought] = useState(70)
  const [rsiOversold, setRsiOversold] = useState(30)

  // MACD specific
  const [macdFast, setMacdFast] = useState(12)
  const [macdSlow, setMacdSlow] = useState(26)
  const [macdSignal, setMacdSignal] = useState(9)

  const [initialCash, setInitialCash] = useState(10000)

  const getDefaultEndDate = () => new Date().toISOString().split('T')[0]
  const getDefaultStartDate = () => {
    const d = new Date()
    d.setFullYear(d.getFullYear() - 5)
    return d.toISOString().split('T')[0]
  }

  const [startDate, setStartDate] = useState(getDefaultStartDate())
  const [endDate, setEndDate] = useState(getDefaultEndDate())
  const [availableStart, setAvailableStart] = useState(null)
  const [availableEnd, setAvailableEnd] = useState(null)

  const [windowMin, setWindowMin] = useState(10)
  const [windowMax, setWindowMax] = useState(50)
  const [windowStep, setWindowStep] = useState(5)

  const handleBacktest = () => {
    let params = {}

    if (strategy === 'momentum') {
      params = { window: parseInt(window) }
    } else if (strategy === 'mean_reversion') {
      params = { window: parseInt(window), threshold: parseFloat(threshold) }
    } else if (strategy === 'bollinger_bands') {
      params = { window: parseInt(window), num_std: parseFloat(numStd) }
    } else if (strategy === 'rsi') {
      params = {
        window: parseInt(window),
        overbought: parseInt(rsiOverbought),
        oversold: parseInt(rsiOversold)
      }
    } else if (strategy === 'macd') {
      params = {
        fast: parseInt(macdFast),
        slow: parseInt(macdSlow),
        signal_window: parseInt(macdSignal)  // fixed: was 'signal', must be 'signal_window'
      }
    }

    onBacktest({ ticker, strategy, params, initialCash: parseFloat(initialCash), startDate, endDate })
  }

  const handleOptimize = () => {
    onOptimize({
      ticker,
      strategy,
      windowRange: [parseInt(windowMin), parseInt(windowMax)],
      windowStep: parseInt(windowStep),
      thresholdRange: [1, 3],
      thresholdStep: 0.5,
      initialCash: parseFloat(initialCash),
      startDate,
      endDate,
      topN: 5
    })
  }

  useEffect(() => {
    let cancelled = false
    async function fetchRange() {
      try {
        const url = `${API_BASE_URL}/data_range?ticker=${encodeURIComponent(ticker)}`
        const res = await fetch(url)
        if (!res.ok) return
        const data = await res.json()
        if (cancelled) return
        setAvailableStart(data.earliest)
        setAvailableEnd(data.latest)
        const availStart = new Date(data.earliest)
        const availEnd = new Date(data.latest)
        if (new Date(startDate) < availStart) setStartDate(data.earliest)
        if (new Date(endDate) > availEnd) setEndDate(data.latest)
      } catch (err) {}
    }
    fetchRange()
    return () => { cancelled = true }
  }, [ticker])

  return (
    <div className="card sticky top-8">
      <h2 className="text-xl font-bold mb-4 text-gray-900">Configuration</h2>

      <div className="mb-4">
        <label className="label">Stock Ticker</label>
        <input
          type="text"
          value={ticker}
          onChange={(e) => setTicker(e.target.value.toUpperCase())}
          placeholder="MSFT, AAPL, GOOGL..."
          className="input"
          disabled={loading}
        />
        <p className="text-xs text-gray-500 mt-1">5+ years of historical data</p>
      </div>

      <div className="mb-4">
        <label className="label">Strategy</label>
        <select
          value={strategy}
          onChange={(e) => setStrategy(e.target.value)}
          className="input"
          disabled={loading}
        >
          {STRATEGIES.map((s) => (
            <option key={s.name} value={s.name}>{s.label}</option>
          ))}
        </select>
        <p className="text-xs text-gray-600 mt-2">
          {STRATEGIES.find(s => s.name === strategy)?.description}
        </p>
      </div>

      <div className="mb-4">
        <label className="label">Initial Capital ($)</label>
        <input
          type="number"
          value={initialCash}
          onChange={(e) => setInitialCash(e.target.value)}
          min="100"
          step="100"
          className="input"
          disabled={loading}
        />
      </div>

      <div className="mb-4">
        <label className="label">Date Range</label>
        <div className="flex gap-2 items-center min-w-0">
          <div className="flex-1 min-w-0">
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="input w-full"
              disabled={loading}
              min={availableStart || undefined}
              max={availableEnd || undefined}
            />
            <p className="text-xs text-gray-500 mt-1">From</p>
          </div>
          <div className="flex-1 min-w-0">
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="input w-full"
              disabled={loading}
              min={availableStart || undefined}
              max={availableEnd || undefined}
            />
            <p className="text-xs text-gray-500 mt-1">To</p>
          </div>
        </div>
      </div>

      <div className="mb-4">
        <label className="label">Mode</label>
        <div className="flex gap-2">
          <button
            onClick={() => setMode('backtest')}
            className={`flex-1 py-2 rounded-lg font-medium transition-colors ${
              mode === 'backtest' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
            disabled={loading}
          >
            Backtest
          </button>
          <button
            onClick={() => setMode('optimize')}
            className={`flex-1 py-2 rounded-lg font-medium transition-colors ${
              mode === 'optimize' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
            disabled={loading}
          >
            Optimize
          </button>
        </div>
      </div>

      {mode === 'backtest' && (
        <>
          {/* Window — shown for all strategies except MACD */}
          {strategy !== 'macd' && (
            <div className="mb-4">
              <label className="label">Window (days)</label>
              <input
                type="number"
                value={window}
                onChange={(e) => setWindow(e.target.value)}
                min="5" max="100"
                className="input"
                disabled={loading}
              />
            </div>
          )}

          {/* Mean reversion: threshold */}
          {strategy === 'mean_reversion' && (
            <div className="mb-4">
              <label className="label">Threshold (σ) — z-score trigger</label>
              <input
                type="number"
                value={threshold}
                onChange={(e) => setThreshold(e.target.value)}
                min="0.5" max="5" step="0.5"
                className="input"
                disabled={loading}
              />
              <p className="text-xs text-gray-500 mt-1">
                Buy when z &lt; −{threshold}, sell when z &gt; {threshold}
              </p>
            </div>
          )}

          {/* Bollinger Bands: num_std — separate from threshold */}
          {strategy === 'bollinger_bands' && (
            <div className="mb-4">
              <label className="label">Num Std Devs — band width</label>
              <input
                type="number"
                value={numStd}
                onChange={(e) => setNumStd(e.target.value)}
                min="0.5" max="5" step="0.5"
                className="input"
                disabled={loading}
              />
              <p className="text-xs text-gray-500 mt-1">
                Standard deviations from mean for upper/lower bands
              </p>
            </div>
          )}

          {/* RSI: overbought / oversold */}
          {strategy === 'rsi' && (
            <>
              <div className="mb-4">
                <label className="label">Oversold threshold (buy below)</label>
                <input
                  type="number"
                  value={rsiOversold}
                  onChange={(e) => setRsiOversold(e.target.value)}
                  min="10" max="45" step="5"
                  className="input"
                  disabled={loading}
                />
              </div>
              <div className="mb-4">
                <label className="label">Overbought threshold (sell above)</label>
                <input
                  type="number"
                  value={rsiOverbought}
                  onChange={(e) => setRsiOverbought(e.target.value)}
                  min="55" max="90" step="5"
                  className="input"
                  disabled={loading}
                />
              </div>
            </>
          )}

          {/* MACD: fast / slow / signal */}
          {strategy === 'macd' && (
            <>
              <div className="mb-4">
                <label className="label">Fast EMA period</label>
                <input
                  type="number"
                  value={macdFast}
                  onChange={(e) => setMacdFast(e.target.value)}
                  min="3" max="20"
                  className="input"
                  disabled={loading}
                />
              </div>
              <div className="mb-4">
                <label className="label">Slow EMA period</label>
                <input
                  type="number"
                  value={macdSlow}
                  onChange={(e) => setMacdSlow(e.target.value)}
                  min="10" max="50"
                  className="input"
                  disabled={loading}
                />
              </div>
              <div className="mb-4">
                <label className="label">Signal line period</label>
                <input
                  type="number"
                  value={macdSignal}
                  onChange={(e) => setMacdSignal(e.target.value)}
                  min="3" max="20"
                  className="input"
                  disabled={loading}
                />
              </div>
            </>
          )}

          <button
            onClick={handleBacktest}
            disabled={loading || !ticker}
            className="btn btn-primary w-full"
          >
            {loading ? 'Running...' : '▶ Run Backtest'}
          </button>
        </>
      )}

      {mode === 'optimize' && (
        <>
          <div className="mb-4">
            <label className="label">Window Range</label>
            <div className="flex gap-2 items-center">
              <input type="number" value={windowMin} onChange={(e) => setWindowMin(e.target.value)} className="input flex-1" disabled={loading} />
              <span className="text-gray-600">to</span>
              <input type="number" value={windowMax} onChange={(e) => setWindowMax(e.target.value)} className="input flex-1" disabled={loading} />
            </div>
          </div>
          <div className="mb-4">
            <label className="label">Window Step</label>
            <input type="number" value={windowStep} onChange={(e) => setWindowStep(e.target.value)} min="1" className="input" disabled={loading} />
          </div>
          <button
            onClick={handleOptimize}
            disabled={loading || !ticker}
            className="btn btn-primary w-full"
          >
            {loading ? 'Optimizing...' : '⚙️ Start Optimization'}
          </button>
        </>
      )}

      <div className="mt-6 pt-4 border-t border-gray-200">
        <p className="text-xs text-gray-500">
          💡 <strong>Tip:</strong> Transaction cost: 0.1% per trade. Benchmark: S&P 500.
        </p>
      </div>
    </div>
  )
}