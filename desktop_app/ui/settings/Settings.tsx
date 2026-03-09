'use client'
import { useState } from 'react'
import { Save } from 'lucide-react'

export default function Settings() {
  const [saved, setSaved] = useState(false)

  const save = () => {
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  return (
    <div className="p-6 space-y-6 max-w-2xl">
      <h1 className="text-xl font-bold text-slate-100">Settings</h1>

      {/* LLM */}
      <div className="card space-y-4">
        <h2 className="text-sm font-semibold text-slate-300">AI / LLM Configuration</h2>
        <div>
          <label className="block text-xs text-slate-500 mb-1">LLM Provider</label>
          <select className="w-full bg-[#0a0a0f] border border-[#1e1e2e] rounded-lg px-3 py-2 text-sm text-slate-100">
            <option value="ollama">Ollama (Local — Free)</option>
            <option value="anthropic">Anthropic Claude</option>
            <option value="openai">OpenAI GPT-4</option>
          </select>
        </div>
        <div>
          <label className="block text-xs text-slate-500 mb-1">API Key (if applicable)</label>
          <input type="password" placeholder="sk-..." className="w-full bg-[#0a0a0f] border border-[#1e1e2e] rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-600" />
        </div>
        <div>
          <label className="block text-xs text-slate-500 mb-1">Ollama URL</label>
          <input defaultValue="http://localhost:11434" className="w-full bg-[#0a0a0f] border border-[#1e1e2e] rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-600" />
        </div>
      </div>

      {/* Risk */}
      <div className="card space-y-4">
        <h2 className="text-sm font-semibold text-slate-300">Risk Parameters</h2>
        {[
          { label: 'Max Risk per Trade (%)', defaultValue: '1.0' },
          { label: 'Max Daily Loss (%)', defaultValue: '3.0' },
          { label: 'Max Concurrent Positions', defaultValue: '5' },
          { label: 'Kill Switch Drawdown (%)', defaultValue: '10.0' },
        ].map(({ label, defaultValue }) => (
          <div key={label}>
            <label className="block text-xs text-slate-500 mb-1">{label}</label>
            <input defaultValue={defaultValue} className="w-full bg-[#0a0a0f] border border-[#1e1e2e] rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-600" />
          </div>
        ))}
      </div>

      {/* Broker */}
      <div className="card space-y-4">
        <h2 className="text-sm font-semibold text-slate-300">Broker Configuration</h2>
        <div>
          <label className="block text-xs text-slate-500 mb-1">Active Broker</label>
          <select className="w-full bg-[#0a0a0f] border border-[#1e1e2e] rounded-lg px-3 py-2 text-sm text-slate-100">
            <option value="paper">Paper Trading (Simulation)</option>
            <option value="angel_one">Angel One</option>
            <option value="zerodha">Zerodha</option>
            <option value="dhan">Dhan</option>
            <option value="fyers">Fyers</option>
          </select>
        </div>
        <div>
          <label className="block text-xs text-slate-500 mb-1">Paper Trading Capital (₹)</label>
          <input defaultValue="1000000" className="w-full bg-[#0a0a0f] border border-[#1e1e2e] rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-600" />
        </div>
      </div>

      {/* Telegram */}
      <div className="card space-y-4">
        <h2 className="text-sm font-semibold text-slate-300">Telegram Bot</h2>
        <div>
          <label className="block text-xs text-slate-500 mb-1">Bot Token</label>
          <input type="password" placeholder="123456:ABC..." className="w-full bg-[#0a0a0f] border border-[#1e1e2e] rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-600" />
        </div>
      </div>

      <button
        onClick={save}
        className="flex items-center gap-2 px-6 py-2 bg-indigo-600 hover:bg-indigo-500 rounded-lg text-sm text-white"
      >
        <Save size={14} />
        {saved ? 'Saved!' : 'Save Settings'}
      </button>
    </div>
  )
}
