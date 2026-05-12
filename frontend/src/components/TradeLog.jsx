import React, { useState } from 'react'

export default function TradeLog({ trades }) {
  const [expanded, setExpanded] = useState(false)
  
  // Extract only executed trades, not every day the strategy stays bullish/bearish
  const tradeData = trades
    .filter(t => t.trade_action !== 0)
    .map((t, idx) => ({
      date: t.Date,
      close: t.Close,
      signal: t.trade_action > 0 ? 'BUY' : 'SELL',
      trigger_state: t.execution_signal > 0 ? 'LONG' : 'FLAT',
      position: t.position,
      portfolio_value: t.portfolio_value
    }))
    .slice(0, expanded ? undefined : 10)

  if (tradeData.length === 0) {
    return null
  }

  return (
    <div className="card">
      <div className="mb-4">
        <h2 className="text-xl font-bold mb-2 text-gray-900">
          Trade Log ({trades.filter(t => t.trade_action !== 0).length} executed trades)
        </h2>
        <p className="text-xs text-gray-500 bg-blue-50 px-3 py-2 rounded border border-blue-200">
          <strong>Strategy Type:</strong> Long-only. BUY = enter position, SELL = exit position (not short).
          Position shows shares held, Portfolio shows portfolio value after execution.
        </p>
      </div>
      
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b-2 border-gray-300 bg-gray-50">
              <th className="text-left px-4 py-2 font-bold text-gray-700">Date</th>
              <th className="text-right px-4 py-2 font-bold text-gray-700">Price</th>
              <th className="text-center px-4 py-2 font-bold text-gray-700">Signal</th>
              <th className="text-center px-4 py-2 font-bold text-gray-700">Position State</th>
              <th className="text-right px-4 py-2 font-bold text-gray-700">Shares Held</th>
              <th className="text-right px-4 py-2 font-bold text-gray-700">Portfolio Value</th>
            </tr>
          </thead>
          <tbody>
            {tradeData.map((trade, idx) => (
              <tr key={idx} className="border-b border-gray-200 hover:bg-gray-50">
                <td className="px-4 py-2 text-gray-700">{trade.date}</td>
                <td className="px-4 py-2 text-right font-mono text-gray-700">
                  ${trade.close?.toFixed(2)}
                </td>
                <td className="px-4 py-2 text-center">
                  <span
                    className={`inline-block px-3 py-1 rounded-full text-xs font-bold ${
                      trade.signal === 'BUY'
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                    }`}
                  >
                    {trade.signal}
                  </span>
                </td>
                <td className="px-4 py-2 text-center text-xs font-semibold text-gray-600">
                  {trade.trigger_state === 'LONG' ? (
                    <span className="inline-block px-3 py-1 rounded-full bg-green-50 text-green-700 font-semibold">
                      IN POSITION
                    </span>
                  ) : (
                    <span className="inline-block px-3 py-1 rounded-full bg-gray-50 text-gray-700 font-semibold">
                      NO POSITION
                    </span>
                  )}
                </td>
                <td className="px-4 py-2 text-right font-mono text-gray-700">
                  {trade.position > 0 ? '+' : ''}{trade.position}
                </td>
                <td className="px-4 py-2 text-right font-mono font-bold text-blue-600">
                  ${trade.portfolio_value?.toFixed(0)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {trades.filter(t => t.trade_action !== 0).length > 10 && (
        <button
          onClick={() => setExpanded(!expanded)}
          className="mt-4 text-sm text-blue-600 hover:text-blue-800 font-medium"
        >
          {expanded ? '▲ Show less' : '▼ Show all trades'}
        </button>
      )}
    </div>
  )
}
