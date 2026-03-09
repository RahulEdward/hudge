'use client'
import { useState, useEffect } from 'react'
import { Save, LogIn, LogOut, CheckCircle, XCircle, Loader2 } from 'lucide-react'

const API = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'

interface OAuthStatus {
  openai: { connected: boolean; expires_at: string | null }
  anthropic: { connected: boolean; expires_at: string | null }
}

export default function Settings() {
  const [saved, setSaved] = useState(false)
  const [oauthStatus, setOauthStatus] = useState<OAuthStatus | null>(null)
  const [oauthLoading, setOauthLoading] = useState<string | null>(null)

  useEffect(() => {
    fetchOAuthStatus()
  }, [])

  const fetchOAuthStatus = async () => {
    try {
      const res = await fetch(`${API}/api/v1/llm/oauth/status`)
      const data = await res.json()
      setOauthStatus(data)
    } catch {
      // backend may not be running
    }
  }

  const handleOAuthLogin = async (provider: string) => {
    setOauthLoading(provider)
    try {
      const res = await fetch(`${API}/api/v1/llm/oauth/login/${provider}`, { method: 'POST' })
      const data = await res.json()
      if (data.auth_url) {
        // Open browser for OAuth authorization
        if (typeof window !== 'undefined' && (window as any).electronAPI?.openExternal) {
          (window as any).electronAPI.openExternal(data.auth_url)
        } else {
          window.open(data.auth_url, '_blank')
        }
        // Poll for completion
        let attempts = 0
        const poll = setInterval(async () => {
          attempts++
          await fetchOAuthStatus()
          const statusRes = await fetch(`${API}/api/v1/llm/oauth/status`)
          const status = await statusRes.json()
          if (status[provider]?.connected || attempts > 30) {
            clearInterval(poll)
            setOauthLoading(null)
            setOauthStatus(status)
          }
        }, 2000)
      }
    } catch {
      setOauthLoading(null)
    }
  }

  const handleOAuthLogout = async (provider: string) => {
    setOauthLoading(provider)
    try {
      await fetch(`${API}/api/v1/llm/oauth/logout/${provider}`, { method: 'POST' })
      await fetchOAuthStatus()
    } finally {
      setOauthLoading(null)
    }
  }

  const save = () => {
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  const ProviderRow = ({ provider, label }: { provider: string; label: string }) => {
    const status = oauthStatus?.[provider as keyof OAuthStatus]
    const loading = oauthLoading === provider
    return (
      <div className="flex items-center justify-between py-2">
        <div className="flex items-center gap-2">
          {status?.connected ? (
            <CheckCircle size={14} className="text-emerald-400" />
          ) : (
            <XCircle size={14} className="text-slate-600" />
          )}
          <span className="text-sm text-slate-300">{label}</span>
          {status?.connected && status.expires_at && (
            <span className="text-xs text-slate-500">
              (expires {new Date(status.expires_at).toLocaleDateString()})
            </span>
          )}
        </div>
        {loading ? (
          <Loader2 size={16} className="text-indigo-400 animate-spin" />
        ) : status?.connected ? (
          <button
            onClick={() => handleOAuthLogout(provider)}
            className="flex items-center gap-1 px-3 py-1 text-xs bg-rose-900/40 hover:bg-rose-900/70 text-rose-300 border border-rose-800/40 rounded-lg"
          >
            <LogOut size={12} /> Disconnect
          </button>
        ) : (
          <button
            onClick={() => handleOAuthLogin(provider)}
            className="flex items-center gap-1 px-3 py-1 text-xs bg-indigo-900/40 hover:bg-indigo-900/70 text-indigo-300 border border-indigo-800/40 rounded-lg"
          >
            <LogIn size={12} /> Connect
          </button>
        )}
      </div>
    )
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
          <label className="block text-xs text-slate-500 mb-1">API Key (optional if using OAuth)</label>
          <input type="password" placeholder="sk-..." className="w-full bg-[#0a0a0f] border border-[#1e1e2e] rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-600" />
        </div>
        <div>
          <label className="block text-xs text-slate-500 mb-1">Ollama URL</label>
          <input defaultValue="http://localhost:11434" className="w-full bg-[#0a0a0f] border border-[#1e1e2e] rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-600" />
        </div>
      </div>

      {/* OAuth Login */}
      <div className="card space-y-3">
        <div>
          <h2 className="text-sm font-semibold text-slate-300">OAuth Login</h2>
          <p className="text-xs text-slate-500 mt-0.5">Connect via OAuth 2.0 — no API key needed. Token is encrypted and stored locally.</p>
        </div>
        <div className="divide-y divide-[#1e1e2e]">
          <ProviderRow provider="anthropic" label="Anthropic Claude" />
          <ProviderRow provider="openai" label="OpenAI GPT-4" />
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
