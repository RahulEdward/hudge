'use client'
import { useEffect, useState } from 'react'
import { RefreshCw } from 'lucide-react'

const API = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'

const LEVEL_COLOR: Record<string, string> = {
  INFO: 'text-blue-400',
  WARNING: 'text-yellow-400',
  ERROR: 'text-rose-400',
  DEBUG: 'text-slate-500',
}

export default function LogsView() {
  const [alerts, setAlerts] = useState<any[]>([])
  const [filter, setFilter] = useState<string>('all')

  const load = async () => {
    try {
      const res = await fetch(`${API}/api/v1/alerts/?limit=100`).then(r => r.json())
      if (res.success) setAlerts(res.alerts)
    } catch {}
  }

  useEffect(() => {
    load()
    const id = setInterval(load, 10000)
    return () => clearInterval(id)
  }, [])

  const filtered = filter === 'all' ? alerts : alerts.filter(a => a.priority === filter)

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-slate-100">Logs & Alerts</h1>
        <div className="flex gap-2">
          {['all', 'high', 'normal', 'low'].map(f => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-1 rounded-lg text-xs capitalize transition-colors ${
                filter === f ? 'bg-indigo-600 text-white' : 'bg-[#12121a] text-slate-400 hover:text-slate-100'
              }`}
            >
              {f}
            </button>
          ))}
          <button onClick={load} className="p-1.5 rounded-lg bg-[#12121a] text-slate-400 hover:text-slate-100">
            <RefreshCw size={14} />
          </button>
        </div>
      </div>

      <div className="card space-y-2 max-h-[calc(100vh-200px)] overflow-y-auto">
        {filtered.length === 0 ? (
          <p className="text-xs text-slate-500 py-8 text-center">No logs found</p>
        ) : (
          filtered.map((alert, i) => (
            <div key={i} className="flex items-start gap-3 py-2 border-b border-[#1e1e2e]/50 last:border-0">
              <div className={`text-[10px] px-1.5 py-0.5 rounded font-mono flex-shrink-0 ${
                alert.priority === 'high' ? 'bg-rose-900/40 text-rose-400' :
                alert.priority === 'critical' ? 'bg-rose-900 text-rose-300' :
                'bg-[#1e1e2e] text-slate-500'
              }`}>
                {alert.alert_type?.toUpperCase() || 'SYS'}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-xs font-medium text-slate-300">{alert.title}</p>
                <p className="text-xs text-slate-500 truncate">{alert.message}</p>
              </div>
              <span className="text-[10px] text-slate-600 flex-shrink-0">
                {new Date(alert.created_at).toLocaleTimeString()}
              </span>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
