'use client'
import { LayoutDashboard, MessageSquare, TrendingUp, BarChart2, Zap, Briefcase, Settings, FileText, Activity } from 'lucide-react'

const navItems = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'chat', label: 'AI Chat', icon: MessageSquare },
  { id: 'strategies', label: 'Strategy Lab', icon: TrendingUp },
  { id: 'backtest', label: 'Backtest', icon: BarChart2 },
  { id: 'trading', label: 'Live Trading', icon: Zap },
  { id: 'portfolio', label: 'Portfolio', icon: Briefcase },
  { id: 'settings', label: 'Settings', icon: Settings },
  { id: 'logs', label: 'Logs', icon: FileText },
] as const

type Page = typeof navItems[number]['id']

interface SidebarProps {
  activePage: Page
  onNavigate: (page: Page) => void
}

export default function Sidebar({ activePage, onNavigate }: SidebarProps) {
  return (
    <aside className="w-16 lg:w-56 flex-shrink-0 bg-[#12121a] border-r border-[#1e1e2e] flex flex-col py-4">
      {/* Logo */}
      <div className="px-4 mb-8 flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center">
          <Activity size={16} className="text-white" />
        </div>
        <span className="hidden lg:block font-bold text-sm text-slate-100">Quant AI Lab</span>
      </div>

      {/* Nav */}
      <nav className="flex-1 space-y-1 px-2">
        {navItems.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => onNavigate(id)}
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all ${
              activePage === id
                ? 'bg-indigo-600/20 text-indigo-400 border border-indigo-600/30'
                : 'text-slate-400 hover:text-slate-100 hover:bg-white/5'
            }`}
          >
            <Icon size={18} className="flex-shrink-0" />
            <span className="hidden lg:block">{label}</span>
          </button>
        ))}
      </nav>

      {/* Footer */}
      <div className="px-4 py-2">
        <div className="hidden lg:flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          <span className="text-xs text-slate-500">Paper Trading</span>
        </div>
      </div>
    </aside>
  )
}
