'use client'
import { useState } from 'react'
import Sidebar from '../components/Sidebar'
import Dashboard from '../dashboard/Dashboard'
import AIChat from '../agents/AIChat'
import StrategyLab from '../strategy_results/StrategyLab'
import BacktestLab from '../backtest_lab/BacktestLab'
import LiveTrading from '../live_trading/LiveTrading'
import Portfolio from '../portfolio/Portfolio'
import Settings from '../settings/Settings'
import LogsView from '../logs_view/LogsView'

type Page = 'dashboard' | 'chat' | 'strategies' | 'backtest' | 'trading' | 'portfolio' | 'settings' | 'logs'

export default function Home() {
  const [activePage, setActivePage] = useState<Page>('dashboard')

  const pages: Record<Page, React.ReactNode> = {
    dashboard: <Dashboard />,
    chat: <AIChat />,
    strategies: <StrategyLab />,
    backtest: <BacktestLab />,
    trading: <LiveTrading />,
    portfolio: <Portfolio />,
    settings: <Settings />,
    logs: <LogsView />,
  }

  return (
    <div className="flex h-screen overflow-hidden bg-[#0a0a0f]">
      <Sidebar activePage={activePage} onNavigate={setActivePage} />
      <main className="flex-1 overflow-auto">
        {pages[activePage]}
      </main>
    </div>
  )
}
