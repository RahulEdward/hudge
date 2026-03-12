'use client'
import { useState } from 'react'
import { Play, BarChart2 } from 'lucide-react'

const API = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'

const METRICS = [
  { key: 'total_return_pct', label: 'Total Return', suffix: '%' },
  { key: 'win_rate', label: 'Win Rate', suffix: '%' },
  { key: 'sharpe_ratio', label: 'Sharpe Ratio', suffix: '' },
  { key: 'max_drawdown_pct', label: 'Max Drawdown', suffix: '%' },
  { key: 'profit_factor', label: 'Profit Factor', suffix: '' },
  { key: 'total_trades', label: 'Total Trades', suffix: '' },
]

export default function BacktestLab() {
  const [form, setForm] = useState({
    strategy_id: '',
    symbol: 'NIFTY',
    timeframe: '1D',
    start_date: '2023-01-01',
    end_date: '2024-12-31',
    initial_capital: 1000000,
  })
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const run = async () => {
    setLoading(true)
    setError('')
    setResult(null)
    try {
      const res = await fetch(`${API}/api/v1/backtest/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      }).then(r => r.json())
      if (res.success) setResult(res.result)
      else setError(res.error || 'Backtest failed')
    } catch (e) {
      setError('Connection error')
    }
    setLoading(false)
  }

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-xl font-bold text-slate-100">Backtest Lab</h1>

      {/* Form */}
      <div className="card grid grid-cols-2 lg:grid-cols-3 gap-4">
        {[
          { key: 'strategy_id', label: 'Strategy ID', placeholder: 'Leave blank for auto' },
          { key: 'symbol', label: 'Symbol', placeholder: 'NIFTY' },
          { key: 'timeframe', label: 'Timeframe', placeholder: '1D' },
          { key: 'start_date', label: 'Start Date', placeholder: '2023-01-01' },
          { key: 'end_date', label: 'End Date', placeholder: '2024-12-31' },
          { key: 'initial_capital', label: 'Capital (₹)', placeholder: '1000000' },
        ].map(({ key, label, placeholder }) => (
          <div key={key}>
            <label className="block text-xs text-slate-400 mb-1">{label}</label>
            <input
              value={(form as any)[key]}
              onChange={e => setForm(f => ({ ...f, [key]: e.target.value }))}
              placeholder={placeholder}
              className="w-full bg-[#0a0a0f] border border-[#1e1e2e] rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-600"
            />
          </div>
        ))}
        <div className="col-span-2 lg:col-span-3 flex justify-end">
          <button
            onClick={run}
            disabled={loading}
            className="flex items-center gap-2 px-6 py-2 bg-indigo-600 hover:bg-indigo-500 rounded-lg text-sm text-white disabled:opacity-50"
          >
            <Play size={14} />
            {loading ? 'Running...' : 'Run Backtest'}
          </button>
        </div>
      </div>

      {error && <div className="text-rose-400 text-sm card">{error}</div>}

      {/* Results */}
      {result && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
            {METRICS.map(({ key, label, suffix }) => (
              <div key={key} className="card">
                <p className="text-xs text-slate-500 mb-1">{label}</p>
                <p className={`text-xl font-bold ${
                  key === 'max_drawdown_pct' ? 'text-rose-400' :
                  key === 'total_return_pct' && result[key] >= 0 ? 'text-emerald-400' : 'text-slate-100'
                }`}>
                  {typeof result[key] === 'number' ? result[key].toFixed(2) : result[key]}{suffix}
                </p>
              </div>
            ))}
          </div>

          {result.trade_log?.length > 0 && (
            <div className="card">
              <h3 className="text-sm font-semibold text-slate-300 mb-3">Trade Log</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-xs text-slate-400">
                  <thead>
                    <tr className="border-b border-[#1e1e2e]">
                      <th className="text-left py-2">Date</th>
                      <th className="text-right py-2">Entry</th>
                      <th className="text-right py-2">Exit</th>
                      <th className="text-right py-2">P&L</th>
                      <th className="text-right py-2">Return</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.trade_log.slice(0, 20).map((t: any, i: number) => (
                      <tr key={i} className="border-b border-[#1e1e2e]/50">
                        <td className="py-1.5">{t.date}</td>
                        <td className="text-right">₹{t.entry_price}</td>
                        <td className="text-right">₹{t.exit_price}</td>
                        <td className={`text-right ${t.pnl >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                          ₹{t.pnl?.toFixed(2)}
                        </td>
                        <td className={`text-right ${t.return_pct >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                          {t.return_pct?.toFixed(2)}%
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
