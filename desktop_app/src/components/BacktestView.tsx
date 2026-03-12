'use client'
import { BarChart2, TrendingUp, TrendingDown, Target } from 'lucide-react'

interface BacktestResult {
  metrics?: {
    total_return?: number
    sharpe_ratio?: number
    max_drawdown?: number
    win_rate?: number
    total_trades?: number
    profit_factor?: number
  }
  equity_curve?: { timestamp: string; equity: number }[]
}

interface BacktestViewProps {
  result?: BacktestResult
  className?: string
}

export default function BacktestView({ result, className = '' }: BacktestViewProps) {
  if (!result) {
    return (
      <div className={`card ${className}`}>
        <div className="flex flex-col items-center justify-center py-12 text-muted">
          <BarChart2 size={48} className="mb-4 opacity-30" />
          <p>No backtest results</p>
          <p className="text-sm">Run a backtest to see results here</p>
        </div>
      </div>
    )
  }

  const m = result.metrics || {}
  const isPositive = (m.total_return || 0) >= 0

  const metrics = [
    { label: 'Total Return', value: `${(m.total_return || 0).toFixed(2)}%`, positive: isPositive },
    { label: 'Sharpe Ratio', value: (m.sharpe_ratio || 0).toFixed(2), positive: (m.sharpe_ratio || 0) > 1 },
    { label: 'Max Drawdown', value: `${(m.max_drawdown || 0).toFixed(2)}%`, positive: false },
    { label: 'Win Rate', value: `${(m.win_rate || 0).toFixed(1)}%`, positive: (m.win_rate || 0) > 50 },
    { label: 'Total Trades', value: String(m.total_trades || 0), positive: true },
    { label: 'Profit Factor', value: (m.profit_factor || 0).toFixed(2), positive: (m.profit_factor || 0) > 1 },
  ]

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        {metrics.map(({ label, value, positive }) => (
          <div key={label} className="card text-center">
            <div className="text-xs text-muted mb-1">{label}</div>
            <div className={`text-lg font-bold ${positive ? 'profit' : 'loss'}`}>{value}</div>
          </div>
        ))}
      </div>

      {/* Equity Curve */}
      {result.equity_curve && result.equity_curve.length > 0 && (
        <div className="card">
          <div className="text-sm text-muted mb-3 flex items-center gap-2">
            <TrendingUp size={14} />
            Equity Curve
          </div>
          <div className="h-48 flex items-end gap-px">
            {result.equity_curve.map((point, i) => {
              const min = Math.min(...result.equity_curve!.map(p => p.equity))
              const max = Math.max(...result.equity_curve!.map(p => p.equity))
              const range = max - min || 1
              const height = ((point.equity - min) / range) * 100
              const isUp = i > 0 ? point.equity >= result.equity_curve![i - 1].equity : true

              return (
                <div key={i} className="flex-1 flex items-end">
                  <div style={{ height: `${height}%`, width: '100%', backgroundColor: isUp ? '#10b981' : '#f43f5e', minHeight: '2px', borderRadius: '1px 1px 0 0' }} />
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}
