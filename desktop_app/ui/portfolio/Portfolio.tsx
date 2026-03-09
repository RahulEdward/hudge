'use client'
import { useEffect, useState } from 'react'

const API = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'

export default function Portfolio() {
  const [summary, setSummary] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      try {
        const res = await fetch(`${API}/api/v1/portfolio/summary`).then(r => r.json())
        if (res.success) setSummary(res.summary)
      } catch {}
      setLoading(false)
    }
    load()
  }, [])

  const fmt = (n: number) => n?.toLocaleString('en-IN', { maximumFractionDigits: 2 }) || '0'

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-xl font-bold text-slate-100">Portfolio</h1>

      {loading ? (
        <div className="text-center text-slate-500 py-12">Loading portfolio...</div>
      ) : (
        <>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { label: 'Portfolio Value', value: `₹${fmt(summary?.total_value)}` },
              { label: 'Available Cash', value: `₹${fmt(summary?.available_cash)}` },
              { label: 'Total P&L', value: `₹${fmt(summary?.total_pnl)}`, color: summary?.total_pnl >= 0 ? 'text-emerald-400' : 'text-rose-400' },
              { label: 'Open Positions', value: summary?.position_count || 0 },
            ].map(({ label, value, color }) => (
              <div key={label} className="card">
                <p className="text-xs text-slate-500 mb-1">{label}</p>
                <p className={`text-2xl font-bold ${color || 'text-slate-100'}`}>{value}</p>
              </div>
            ))}
          </div>

          {summary?.positions?.length > 0 && (
            <div className="card">
              <h2 className="text-sm font-semibold text-slate-300 mb-4">Holdings</h2>
              <table className="w-full text-xs text-slate-400">
                <thead>
                  <tr className="border-b border-[#1e1e2e]">
                    <th className="text-left py-2">Symbol</th>
                    <th className="text-right py-2">Quantity</th>
                    <th className="text-right py-2">Avg Price</th>
                    <th className="text-right py-2">Current</th>
                    <th className="text-right py-2">P&L</th>
                  </tr>
                </thead>
                <tbody>
                  {summary.positions.map((p: any, i: number) => (
                    <tr key={i} className="border-b border-[#1e1e2e]/50">
                      <td className="py-2 font-medium text-slate-300">{p.symbol}</td>
                      <td className="text-right">{p.quantity}</td>
                      <td className="text-right">₹{p.average_price?.toFixed(2)}</td>
                      <td className="text-right">₹{p.average_price?.toFixed(2)}</td>
                      <td className={`text-right ${(p.pnl || 0) >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                        ₹{(p.pnl || 0).toFixed(2)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </div>
  )
}
