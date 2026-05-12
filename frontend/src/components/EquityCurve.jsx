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
  if (!data.chart_data || data.chart_data.length === 0) {
    return null
  }

  // Prepare chart data
  const chartData = data.chart_data.map((row) => ({
    date: row.Date,
    strategy: row.portfolio_value,
    spy: row.SPY_Portfolio_Value ?? row.SPY_Close,
    close: row.Close,
    signal: row.signal
  }))

  // Format for better readability
  const formatValue = (value) => {
    if (value >= 1000) {
      return `$${(value / 1000).toFixed(1)}k`
    }
    return `$${value.toFixed(0)}`
  }

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
            interval={Math.floor(chartData.length / 10)}
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
            dot={false}
            strokeWidth={2}
            name="Strategy"
            isAnimationActive={false}
          />
          <Line
            type="monotone"
            dataKey="spy"
            stroke="#10b981"
            dot={false}
            strokeWidth={2}
            name="S&P 500 (SPY)"
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
      <p className="text-xs text-gray-600 mt-4 text-center">
        Blue: Your strategy | Green: S&P 500 benchmark
      </p>
    </div>
  )
}
