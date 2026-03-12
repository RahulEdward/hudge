'use client'
import { useEffect, useState } from 'react'
import { CheckCircle, XCircle, RefreshCw, Cpu, Clock } from 'lucide-react'

const API = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'

const STATUS_COLORS: Record<string, string> = {
  discovered: 'text-blue-400 bg-blue-900/20',
  backtesting: 'text-yellow-400 bg-yellow-900/20',
  pending_approval: 'text-amber-400 bg-amber-900/20',
  approved: 'text-emerald-400 bg-emerald-900/20',
  rejected: 'text-rose-400 bg-rose-900/20',
  live: 'text-green-400 bg-green-900/20',
}

export default function StrategyLab() {
  const [strategies, setStrategies] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [discovering, setDiscovering] = useState(false)

  const load = async () => {
    try {
      const res = await fetch(`${API}/api/v1/strategies/`).then(r => r.json())
      if (res.success) setStrategies(res.strategies)
    } catch (e) {}
    setLoading(false)
  }

  useEffect(() => { load() }, [])

  const discover = async () => {
    setDiscovering(true)
    try {
      await fetch(`${API}/api/v1/agents/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: 'discover strategy for NIFTY', agent_id: 'strategy_discovery' }),
      })
      setTimeout(load, 2000)
    } catch (e) {}
    setDiscovering(false)
  }

  const approve = async (id: string) => {
    await fetch(`${API}/api/v1/strategies/${id}/approve`, { method: 'POST' })
    load()
  }

  const reject = async (id: string) => {
    await fetch(`${API}/api/v1/strategies/${id}/reject`, { method: 'POST' })
    load()
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-slate-100">Strategy Lab</h1>
        <button
          onClick={discover}
          disabled={discovering}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 rounded-lg text-sm text-white disabled:opacity-50 transition-colors"
        >
          <Cpu size={14} />
          {discovering ? 'Discovering...' : 'Discover New Strategy'}
        </button>
      </div>

      {loading ? (
        <div className="text-center text-slate-500 py-12">Loading strategies...</div>
      ) : strategies.length === 0 ? (
        <div className="card text-center py-12">
          <Cpu size={32} className="text-slate-600 mx-auto mb-3" />
          <p className="text-slate-400">No strategies discovered yet</p>
          <p className="text-xs text-slate-600 mt-1">Click "Discover New Strategy" to let AI find trading opportunities</p>
        </div>
      ) : (
        <div className="space-y-3">
          {strategies.map((s, i) => (
            <div key={i} className="card">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="font-semibold text-slate-100">{s.name || `Strategy ${s.strategy_id}`}</h3>
                    <span className={`text-xs px-2 py-0.5 rounded-full ${STATUS_COLORS[s.status] || 'text-slate-400 bg-slate-800'}`}>
                      {s.status}
                    </span>
                    {s.symbol && <span className="text-xs text-slate-500">{s.symbol}</span>}
                  </div>
                  {s.description && (
                    <p className="text-xs text-slate-400 mb-3">{s.description.slice(0, 200)}...</p>
                  )}
                  <div className="flex items-center gap-4 text-xs text-slate-500">
                    {s.timeframe && <span>Timeframe: {s.timeframe}</span>}
                    {s.indicators?.length > 0 && <span>Indicators: {s.indicators.join(', ')}</span>}
                  </div>
                </div>
                {s.status === 'pending_approval' && (
                  <div className="flex gap-2 ml-4">
                    <button
                      onClick={() => approve(s.strategy_id)}
                      className="flex items-center gap-1 px-3 py-1.5 bg-emerald-600/20 hover:bg-emerald-600/40 text-emerald-400 rounded-lg text-xs transition-colors"
                    >
                      <CheckCircle size={12} /> Approve
                    </button>
                    <button
                      onClick={() => reject(s.strategy_id)}
                      className="flex items-center gap-1 px-3 py-1.5 bg-rose-600/20 hover:bg-rose-600/40 text-rose-400 rounded-lg text-xs transition-colors"
                    >
                      <XCircle size={12} /> Reject
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
