'use client'
import { useEffect, useState } from 'react'
import { TrendingUp, TrendingDown, Activity, DollarSign, Target, BarChart2 } from 'lucide-react'

const API = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'

interface PortfolioData {
  total_value: number
  total_pnl: number
  pnl_pct: number
  position_count: number
  available_cash: number
}

function StatCard({ label, value, change, icon: Icon, color }: any) {
  return (
    <div className="card">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs text-slate-500 mb-1">{label}</p>
          <p className="text-2xl font-bold text-slate-100">{value}</p>
          {change !== undefined && (
            <p className={`text-xs mt-1 ${change >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
              {change >= 0 ? '+' : ''}{change}%
            </p>
          )}
        </div>
        <div className={`p-2 rounded-lg ${color}`}>
          <Icon size={18} className="text-white" />
        </div>
      </div>
    </div>
  )
}

export default function Dashboard() {
  const [portfolio, setPortfolio] = useState<PortfolioData | null>(null)
  const [alerts, setAlerts] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      try {
        const [portRes, alertRes] = await Promise.all([
          fetch(`${API}/api/v1/portfolio/summary`).then(r => r.json()),
          fetch(`${API}/api/v1/alerts/?unread_only=true&limit=5`).then(r => r.json()),
        ])
        if (portRes.success) setPortfolio(portRes.summary)
        if (alertRes.success) setAlerts(alertRes.alerts || [])
      } catch (e) {
        console.error('Dashboard load error:', e)
      } finally {
        setLoading(false)
      }
    }
    load()
    const interval = setInterval(load, 30000)
    return () => clearInterval(interval)
  }, [])

  const fmt = (n: number) => n?.toLocaleString('en-IN', { maximumFractionDigits: 2 }) || '0'

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-slate-100">Dashboard</h1>
        <div className="flex items-center gap-2 text-xs text-slate-500">
          <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          Paper Trading Active
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Portfolio Value"
          value={`₹${fmt(portfolio?.total_value || 0)}`}
          icon={DollarSign}
          color="bg-indigo-600"
        />
        <StatCard
          label="Total P&L"
          value={`₹${fmt(portfolio?.total_pnl || 0)}`}
          change={portfolio?.pnl_pct}
          icon={portfolio?.total_pnl >= 0 ? TrendingUp : TrendingDown}
          color={portfolio?.total_pnl >= 0 ? 'bg-emerald-600' : 'bg-rose-600'}
        />
        <StatCard
          label="Open Positions"
          value={portfolio?.position_count || 0}
          icon={Activity}
          color="bg-violet-600"
        />
        <StatCard
          label="Available Cash"
          value={`₹${fmt(portfolio?.available_cash || 0)}`}
          icon={Target}
          color="bg-amber-600"
        />
      </div>

      {/* Alerts */}
      <div className="card">
        <h2 className="text-sm font-semibold text-slate-300 mb-4">Recent Alerts</h2>
        {alerts.length === 0 ? (
          <p className="text-xs text-slate-500">No alerts</p>
        ) : (
          <div className="space-y-2">
            {alerts.map((alert, i) => (
              <div key={i} className="flex items-start gap-3 py-2 border-b border-[#1e1e2e] last:border-0">
                <div className={`w-2 h-2 mt-1.5 rounded-full flex-shrink-0 ${
                  alert.priority === 'high' ? 'bg-rose-500' : 'bg-indigo-500'
                }`} />
                <div>
                  <p className="text-xs font-medium text-slate-300">{alert.title}</p>
                  <p className="text-xs text-slate-500">{alert.message}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {loading && (
        <div className="text-center text-slate-500 text-sm py-8">Loading dashboard...</div>
      )}
    </div>
  )
}
