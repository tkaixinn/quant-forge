import React from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts'

export default function EquityCurve({ data }) {
  const rawChartData = Array.isArray(data.chart_data) ? data.chart_data : []

  const chartData = rawChartData
    .map((row) => ({
      date: row.Date ?? row.date,
      strategy: Number(row.portfolio_value ?? row.strategy ?? row.Portfolio_Value),
      spy: Number(row.SPY_Portfolio_Value ?? row.SPY_Close ?? row.spy),
      close: Number(row.Close ?? row.close),
      signal: row.signal
    }))
    .filter((row) => row.date && Number.isFinite(row.strategy))
    .sort((left, right) => String(left.date).localeCompare(String(right.date)))

  console.log('EquityCurve chartData length:', chartData.length)
  console.log('EquityCurve first row:', chartData[0])

  if (chartData.length === 0) {
    return (
      <div className="card mb-6">
        <h2 className="text-xl font-bold mb-2 text-gray-900">Equity Curve</h2>
        <p className="text-sm text-gray-600">
          No chartable backtest data was returned for this run.
        </p>
      </div>
    )
  }

  const strategyValues = chartData.map((row) => row.strategy).filter(Number.isFinite)
  const minStrategy = Math.min(...strategyValues)
  const maxStrategy = Math.max(...strategyValues)
  const isFlatStrategy = strategyValues.length > 0 && Math.abs(maxStrategy - minStrategy) < 1e-6
  const showDots = isFlatStrategy || chartData.length < 20

  const formatValue = (value) => {
    if (!Number.isFinite(value)) {
      return '$0'
    }
    if (value >= 1000) {
      return `$${(value / 1000).toFixed(1)}k`
    }
    return `$${value.toFixed(0)}`
  }

  const showSpy = chartData.some((row) => Number.isFinite(row.spy))

  return (
    <div className="card mb-6">
      <h2 className="text-xl font-bold mb-4 text-gray-900">Equity Curve</h2>
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={chartData} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis
            dataKey="date"
            stroke="#94a3b8"
            tick={{ fontSize: 12 }}
            interval={Math.max(1, Math.floor(chartData.length / 10))}
          />
          <YAxis
            stroke="#94a3b8"
            tick={{ fontSize: 12 }}
            tickFormatter={formatValue}
          />
          <Tooltip
            formatter={(value) => formatValue(value)}
            labelStyle={{ color: '#000' }}
            contentStyle={{ backgroundColor: '#fff', border: '1px solid #cbd5e1' }}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="strategy"
            stroke="#2563eb"
            dot={showDots ? { r: 2 } : false}
            activeDot={showDots ? { r: 4 } : false}
            strokeWidth={2}
            name="Strategy"
            isAnimationActive={false}
          />
          {showSpy && (
            <Line
              type="monotone"
              dataKey="spy"
              stroke="#10b981"
              dot={showDots ? { r: 2 } : false}
              activeDot={showDots ? { r: 4 } : false}
              strokeWidth={2}
              name="S&P 500 (SPY)"
              isAnimationActive={false}
            />
          )}
        </LineChart>
      </ResponsiveContainer>
      {isFlatStrategy && (
        <p className="text-xs text-amber-700 mt-3 text-center">
          This strategy stayed flat during the selected period, so the equity curve may look nearly horizontal.
        </p>
      )}
      <p className="text-xs text-gray-600 mt-4 text-center">
        Blue: Your strategy | Green: S&P 500 benchmark
      </p>
    </div>
  )
}