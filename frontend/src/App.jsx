import React, { useState } from 'react'
import axios from 'axios'
import StrategyForm from './components/StrategyForm'
import EquityCurve from './components/EquityCurve'
import MetricsCards from './components/MetricsCards'
import TradeLog from './components/TradeLog'

// Prefer explicit Vercel env var; fallback to deployed Railway API.
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://quant-forge-production.up.railway.app'

const parseApiResponse = (data) => {
  if (typeof data !== 'string') {
    return data
  }

  try {
    return JSON.parse(data)
  } catch {
    return data
  }
}

export default function App() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [results, setResults] = useState(null)
  const [backtest, setBacktest] = useState(false)
  const [optimizing, setOptimizing] = useState(false)

  const formatParams = (params = {}) => {
    const entries = Object.entries(params)
    if (!entries.length) {
      return 'default parameters'
    }
    return entries.map(([key, value]) => `${key}: ${value}`).join(' | ')
  }

  const handleBacktest = async (formData) => {
    setLoading(true)
    setError(null)
    setBacktest(true)
    setOptimizing(false)

    try {
      const response = await axios.post(`${API_BASE_URL}/backtest`, {
        ticker: formData.ticker,
        strategy: formData.strategy,
        params: formData.params,
        initial_cash: formData.initialCash,
        start_date: formData.startDate,
        end_date: formData.endDate,
        benchmark_ticker: 'SPY'
      }, { responseType: 'json' 
      })
      const parsed = parseApiResponse(response.data)
      setResults(parsed)
    } catch (err) {
      setError(err.response?.data?.error || 'Backtest failed. Make sure the API is running.')
      setResults(null)
    } finally {
      setLoading(false)
    }
  }

  const handleOptimize = async (formData) => {
    setLoading(true)
    setError(null)
    setBacktest(false)
    setOptimizing(true)

    try {
      const response = await axios.post(`${API_BASE_URL}/optimize`, {
        ticker: formData.ticker,
        strategy: formData.strategy,
        initial_cash: formData.initialCash,
        start_date: formData.startDate,
        end_date: formData.endDate,
        window_range: formData.windowRange || [10, 50],
        window_step: formData.windowStep || 5,
        threshold_range: formData.thresholdRange || [1, 3],
        threshold_step: formData.thresholdStep || 0.5,
        fast_range: formData.fastRange || [5, 20],
        fast_step: formData.fastStep || 3,
        slow_range: formData.slowRange || [20, 35],
        slow_step: formData.slowStep || 3,
        signal_range: formData.signalRange || [5, 15],
        signal_step: formData.signalStep || 2,
        top_n: formData.topN || 5
      })
      setResults(parseApiResponse(response.data))
    } catch (err) {
      setError(err.response?.data?.error || 'Optimization failed. Make sure the API is running.')
      setResults(null)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">📊 Quant Forge</h1>
              <p className="text-gray-600 text-sm mt-1">Algorithmic Trading Research Platform</p>
            </div>
            <div className="text-right">
              <p className="text-xs text-gray-500">API: {API_BASE_URL}</p>
              <p className="text-xs text-green-600 font-medium">● Live</p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left: Form */}
          <div className="lg:col-span-1">
            <StrategyForm
              onBacktest={handleBacktest}
              onOptimize={handleOptimize}
              loading={loading}
            />
          </div>

          {/* Right: Results */}
          <div className="lg:col-span-2">
            {error && (
              <div className="card bg-red-50 border border-red-200 text-red-700 mb-6">
                <h3 className="font-bold mb-2">❌ Error</h3>
                <p className="text-sm">{error}</p>
              </div>
            )}

            {loading && (
              <div className="card text-center py-12">
                <div className="animate-spin inline-block w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full"></div>
                <p className="mt-4 text-gray-600">
                  {optimizing ? 'Optimizing parameters...' : 'Running backtest...'}
                </p>
              </div>
            )}

            {results && !loading && (
              <>
                {backtest && results.chart_data && (
                  <>
                    <EquityCurve data={results} />
                    <MetricsCards result={results} />
                    {results.chart_data.length > 0 && (
                      <TradeLog trades={results.chart_data} />
                    )}
                  </>
                )}

                {optimizing && results.top_results && (
                  <div className="space-y-4">
                    <h2 className="text-2xl font-bold text-gray-900 mb-4">
                      Top Results ({results.count} tested)
                    </h2>
                    {results.top_results.map((result, idx) => (
                      <div key={idx} className="card border-2 border-blue-200">
                        <div className="flex justify-between items-start mb-4">
                          <div>
                            <h3 className="font-bold text-lg">
                              {idx + 1}. {formatParams(result.params_used)}
                            </h3>
                            <p className="text-sm text-gray-600">
                              {result.ticker} - {result.strategy}
                            </p>
                          </div>
                          <div className="text-right">
                            <div className="text-2xl font-bold text-green-600">
                              {(result.metrics.sharpe_ratio || 0).toFixed(2)}
                            </div>
                            <div className="text-xs text-gray-600">Sharpe</div>
                          </div>
                        </div>
                        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
                          <div>
                            <div className="text-gray-600">Return</div>
                            <div className="font-bold text-green-600">
                              {(result.total_return || 0).toFixed(1)}%
                            </div>
                          </div>
                          <div>
                            <div className="text-gray-600">Max DD</div>
                            <div className="font-bold text-red-600">
                              {((result.metrics.max_drawdown || 0) * 100).toFixed(2)}%
                            </div>
                          </div>
                          <div>
                            <div className="text-gray-600">Win Rate</div>
                            <div className="font-bold">
                              {((result.metrics.win_rate || 0) * 100).toFixed(2)}%
                            </div>
                          </div>
                          <div>
                            <div className="text-gray-600">Final Value</div>
                            <div className="font-bold">
                              ${result.final_value?.toFixed(0)}
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </>
            )}

            {!results && !loading && (
              <div className="card text-center py-12 text-gray-500">
                <p className="text-lg">👉 Select a strategy and click "Run Backtest" or "Optimize"</p>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 text-center text-sm text-gray-600">
          <p>Quant Forge • Built with Python, Flask, React • Deployed on Railway & Vercel</p>
        </div>
      </footer>
    </div>
  )

  
}
