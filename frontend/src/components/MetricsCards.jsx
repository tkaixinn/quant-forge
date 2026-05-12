import React from 'react'

export default function MetricsCards({ result }) {
  const metrics = result.metrics || {}
  const benchmarkMetrics = result.benchmark_metrics || {}

  const toNumber = (value) => {
    const n = Number(value)
    return Number.isNaN(n) ? 0 : n
  }

  const toDisplay = (value, digits = 2) => {
    const n = Number(value)
    if (n === Number.POSITIVE_INFINITY) {
      return '∞'
    }
    if (n === Number.NEGATIVE_INFINITY) {
      return '-∞'
    }
    if (!Number.isFinite(n)) {
      return '0.00'
    }
    return n.toFixed(digits)
  }

  const cards = [
    {
      label: 'Sharpe Ratio',
      valueNum: toNumber(metrics.sharpe_ratio),
      benchmarkNum: toNumber(benchmarkMetrics.sharpe_ratio),
      value: toDisplay(metrics.sharpe_ratio, 2),
      benchmark: toDisplay(benchmarkMetrics.sharpe_ratio, 2),
      comparator: 'greater',
      color: 'blue'
    },
    {
      label: 'Total Return',
      valueNum: toNumber(result.total_return),
      benchmarkNum: toNumber(benchmarkMetrics.total_return),
      value: `${toNumber(result.total_return).toFixed(1)}%`,
      benchmark: `${toNumber(benchmarkMetrics.total_return).toFixed(1)}%`,
      comparator: 'greater',
      color: toNumber(result.total_return) > toNumber(benchmarkMetrics.total_return) ? 'green' : 'red'
    },
    {
      label: 'Max Drawdown',
      valueNum: toNumber(metrics.max_drawdown),
      benchmarkNum: toNumber(benchmarkMetrics.max_drawdown),
      value: `${((metrics.max_drawdown || 0) * 100).toFixed(1)}%`,
      benchmark: `${((benchmarkMetrics.max_drawdown || 0) * 100).toFixed(1)}%`,
      comparator: 'greater',
      color: 'amber',
    },
    {
      label: 'CAGR',
      valueNum: toNumber(metrics.cagr),
      benchmarkNum: toNumber(benchmarkMetrics.cagr),
      value: `${((metrics.cagr || 0) * 100).toFixed(1)}%`,
      benchmark: `${((benchmarkMetrics.cagr || 0) * 100).toFixed(1)}%`,
      comparator: 'greater',
      color: 'blue'
    },
    {
      label: 'Win Rate',
      valueNum: toNumber(metrics.win_rate),
      benchmarkNum: null,
      value: `${((metrics.win_rate || 0) * 100).toFixed(0)}%`,
      benchmark: '-',
      color: 'purple'
    },
    {
      label: 'Profit Factor',
      valueNum: toNumber(metrics.profit_factor),
      benchmarkNum: null,
      value: toDisplay(metrics.profit_factor, 2),
      benchmark: '-',
      color: 'green'
    }
  ]

  return (
    <div className="mb-6">
      <h2 className="text-xl font-bold mb-4 text-gray-900">Performance Metrics</h2>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
        {cards.map((card, idx) => {
          const hasBenchmark = card.benchmark !== '-' && card.benchmarkNum !== null
          const isBetter =
            card.comparator === 'greater'
              ? card.valueNum > card.benchmarkNum
              : card.valueNum < card.benchmarkNum
          
          return (
            <div key={idx} className="metric-card border-l-4 border-blue-500">
              <div className="flex justify-between items-start">
                <div>
                  <p className="metric-label">{card.label}</p>
                  <p className={`metric-value text-${card.color}-600`}>{card.value}</p>
                </div>
                {hasBenchmark && (
                  <div className="text-right">
                    <p className="text-xs text-gray-500">SPY</p>
                    <p className="text-sm font-bold text-gray-700">{card.benchmark}</p>
                    {isBetter ? (
                      <p className="text-xs text-green-600 font-bold">✓ Better</p>
                    ) : (
                      <p className="text-xs text-red-600 font-bold">✗ Worse</p>
                    )}
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </div>

      <div className="card bg-blue-50 border border-blue-200">
        <h3 className="font-bold text-blue-900 mb-2">Summary</h3>
        <p className="text-sm text-blue-800">
          {result.ticker} - {result.strategy.replace('_', ' ').toUpperCase()}
        </p>
        <p className="text-sm text-blue-800 mt-1">
          Portfolio Value: <strong>${result.final_value?.toFixed(0)}</strong>
        </p>
        <p className="text-sm text-blue-700 mt-2">
          Alpha vs Market: <strong>{(result.alpha_vs_market * 100).toFixed(1)}%</strong>
        </p>
      </div>
    </div>
  )
}
