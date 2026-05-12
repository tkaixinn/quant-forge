import React, { useState, useEffect } from 'react'

const STRATEGIES = [
  {
    name: 'momentum',
    label: 'Momentum',
    description: 'Buy positive momentum, sell negative momentum'
  },
  {
    name: 'mean_reversion',
    label: 'Mean Reversion',
    description: 'Buy oversold, sell overbought'
  },
  {
    name: 'rsi',
    label: 'RSI',
    description: 'Relative Strength Index signals'
  },
  {
    name: 'macd',
    label: 'MACD',
    description: 'Moving Average Convergence Divergence'
  },
  {
    name: 'bollinger_bands',
    label: 'Bollinger Bands',
    description: 'Upper/lower band breakouts'
  }
]

export default function StrategyForm({ onBacktest, onOptimize, loading }) {
  const [ticker, setTicker] = useState('MSFT')
  const [strategy, setStrategy] = useState('momentum')
  const [mode, setMode] = useState('backtest') // 'backtest' or 'optimize'
  
  // Backtest params
  const [window, setWindow] = useState(20)
  const [threshold, setThreshold] = useState(2)
  const [initialCash, setInitialCash] = useState(10000)
  
  // Date range (default to 5 years back)
  const getDefaultEndDate = () => {
    const today = new Date()
    return today.toISOString().split('T')[0]
  }
  
  const getDefaultStartDate = () => {
    const fiveYearsAgo = new Date()
    fiveYearsAgo.setFullYear(fiveYearsAgo.getFullYear() - 5)
    return fiveYearsAgo.toISOString().split('T')[0]
  }
  
  const [startDate, setStartDate] = useState(getDefaultStartDate())
  const [endDate, setEndDate] = useState(getDefaultEndDate())
  const [availableStart, setAvailableStart] = useState(null)
  const [availableEnd, setAvailableEnd] = useState(null)
  
  // Optimize ranges
  const [windowMin, setWindowMin] = useState(10)
  const [windowMax, setWindowMax] = useState(50)
  const [windowStep, setWindowStep] = useState(5)

  const handleBacktest = () => {
    const params = {}
    if (strategy === 'momentum' || strategy === 'rsi' || strategy === 'bollinger_bands') {
      params.window = parseInt(window)
    } else if (strategy === 'mean_reversion') {
      params.window = parseInt(window)
      params.threshold = parseFloat(threshold)
    } else if (strategy === 'macd') {
      params.fast = 12
      params.slow = 26
      params.signal = 9
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

  // Fetch available date range for ticker and clamp defaults
  useEffect(() => {
    let cancelled = false
    async function fetchRange() {
      try {
        const url = `${import.meta.env.VITE_API_URL || 'http://localhost:5002'}/data_range?ticker=${encodeURIComponent(ticker)}`
        const res = await fetch(url)
        if (!res.ok) return
        const data = await res.json()
        if (cancelled) return
        setAvailableStart(data.earliest)
        setAvailableEnd(data.latest)

        // Clamp current selected dates to available range
        const availStart = new Date(data.earliest)
        const availEnd = new Date(data.latest)
        const curStart = new Date(startDate)
        const curEnd = new Date(endDate)

        if (curStart < availStart) setStartDate(data.earliest)
        if (curEnd > availEnd) setEndDate(data.latest)
      } catch (err) {
        // ignore network errors for now
      }
    }
    fetchRange()
    return () => { cancelled = true }
  }, [ticker])

  return (
    <div className="card sticky top-8">
      <h2 className="text-xl font-bold mb-4 text-gray-900">Configuration</h2>

      {/* Ticker Input */}
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

      {/* Strategy Selector */}
      <div className="mb-4">
        <label className="label">Strategy</label>
        <select
          value={strategy}
          onChange={(e) => setStrategy(e.target.value)}
          className="input"
          disabled={loading}
        >
          {STRATEGIES.map((s) => (
            <option key={s.name} value={s.name}>
              {s.label}
            </option>
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
        <p className="text-xs text-gray-500 mt-1">Dollar amounts scale with this value.</p>
      </div>

      {/* Date Range Picker */}
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
        <p className="text-xs text-gray-500 mt-2">
          Note: Historical data will be downloaded for this period.
        </p>
      </div>

      {/* Mode Toggle */}
      <div className="mb-4">
        <label className="label">Mode</label>
        <div className="flex gap-2">
          <button
            onClick={() => setMode('backtest')}
            className={`flex-1 py-2 rounded-lg font-medium transition-colors ${
              mode === 'backtest'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
            disabled={loading}
          >
            Backtest
          </button>
          <button
            onClick={() => setMode('optimize')}
            className={`flex-1 py-2 rounded-lg font-medium transition-colors ${
              mode === 'optimize'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
            disabled={loading}
          >
            Optimize
          </button>
        </div>
      </div>

      {/* Backtest Params */}
      {mode === 'backtest' && (
        <>
          {(strategy === 'momentum' || strategy === 'rsi' || strategy === 'bollinger_bands') && (
            <div className="mb-4">
              <label className="label">Window (days)</label>
              <input
                type="number"
                value={window}
                onChange={(e) => setWindow(e.target.value)}
                min="5"
                max="100"
                className="input"
                disabled={loading}
              />
            </div>
          )}
          
          {strategy === 'mean_reversion' && (
            <>
              <div className="mb-4">
                <label className="label">Window (days)</label>
                <input
                  type="number"
                  value={window}
                  onChange={(e) => setWindow(e.target.value)}
                  min="5"
                  max="100"
                  className="input"
                  disabled={loading}
                />
              </div>
              <div className="mb-4">
                <label className="label">Threshold (σ)</label>
                <input
                  type="number"
                  value={threshold}
                  onChange={(e) => setThreshold(e.target.value)}
                  min="0.5"
                  max="5"
                  step="0.5"
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

      {/* Optimize Params */}
      {mode === 'optimize' && (
        <>
          <div className="mb-4">
            <label className="label">Window Range</label>
            <div className="flex gap-2 items-center">
              <input
                type="number"
                value={windowMin}
                onChange={(e) => setWindowMin(e.target.value)}
                className="input flex-1"
                disabled={loading}
              />
              <span className="text-gray-600">to</span>
              <input
                type="number"
                value={windowMax}
                onChange={(e) => setWindowMax(e.target.value)}
                className="input flex-1"
                disabled={loading}
              />
            </div>
          </div>

          <div className="mb-4">
            <label className="label">Window Step</label>
            <input
              type="number"
              value={windowStep}
              onChange={(e) => setWindowStep(e.target.value)}
              min="1"
              className="input"
              disabled={loading}
            />
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
