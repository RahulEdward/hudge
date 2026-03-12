'use client'
import { useState, useEffect } from 'react'
import { Package, Download, Trash2, Search, CheckCircle, Loader2 } from 'lucide-react'

interface Plugin {
  name: string
  version: string
  description: string
  author: string
  category: string
  tags: string[]
  installed?: boolean
}

export default function PluginMarketplace() {
  const [plugins, setPlugins] = useState<Plugin[]>([])
  const [search, setSearch] = useState('')
  const [activeCategory, setActiveCategory] = useState('all')
  const [loading, setLoading] = useState<string | null>(null)

  useEffect(() => {
    fetchPlugins()
  }, [])

  const fetchPlugins = async () => {
    try {
      const res = await fetch(`${process.env.BACKEND_URL}/api/v1/plugins/marketplace`)
      if (res.ok) {
        const data = await res.json()
        setPlugins(data.plugins || [])
      }
    } catch {
      // Fallback sample data
      setPlugins([
        { name: 'options_chain_analyzer', version: '1.0.0', description: 'Analyze options chain data with Greeks calculation and strategy suggestions', author: 'Quant AI Lab', category: 'analysis', tags: ['options', 'greeks'] },
        { name: 'sentiment_scanner', version: '1.0.0', description: 'Scan news and social media for market sentiment using NLP', author: 'Quant AI Lab', category: 'data', tags: ['sentiment', 'nlp'] },
        { name: 'multi_timeframe_analysis', version: '1.0.0', description: 'Run analysis across multiple timeframes simultaneously', author: 'Quant AI Lab', category: 'analysis', tags: ['timeframe', 'analysis'] },
        { name: 'telegram_signals', version: '1.0.0', description: 'Publish trading signals to a Telegram channel automatically', author: 'Quant AI Lab', category: 'communication', tags: ['telegram', 'signals'] },
        { name: 'sector_rotation', version: '1.0.0', description: 'Track sector rotation and identify trending sectors', author: 'Quant AI Lab', category: 'strategy', tags: ['sector', 'momentum'] },
      ])
    }
  }

  const handleInstall = async (pluginName: string) => {
    setLoading(pluginName)
    try {
      await fetch(`${process.env.BACKEND_URL}/api/v1/plugins/install`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: pluginName }),
      })
    } catch {}
    await new Promise(r => setTimeout(r, 1000))
    setPlugins(prev => prev.map(p =>
      p.name === pluginName ? { ...p, installed: true } : p
    ))
    setLoading(null)
  }

  const handleUninstall = async (pluginName: string) => {
    setLoading(pluginName)
    try {
      await fetch(`${process.env.BACKEND_URL}/api/v1/plugins/uninstall`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: pluginName }),
      })
    } catch {}
    await new Promise(r => setTimeout(r, 500))
    setPlugins(prev => prev.map(p =>
      p.name === pluginName ? { ...p, installed: false } : p
    ))
    setLoading(null)
  }

  const categories = ['all', ...Array.from(new Set(plugins.map(p => p.category)))]
  const filtered = plugins.filter(p => {
    const matchSearch = !search || p.name.includes(search.toLowerCase()) || p.description.toLowerCase().includes(search.toLowerCase())
    const matchCategory = activeCategory === 'all' || p.category === activeCategory
    return matchSearch && matchCategory
  })

  const categoryIcons: Record<string, string> = {
    all: '📦', analysis: '📊', data: '📡', strategy: '🎯', communication: '💬',
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Package size={24} className="accent" />
          Plugin Marketplace
        </h1>
        <p className="text-muted text-sm">Extend your platform with additional capabilities</p>
      </div>

      {/* Search & Filters */}
      <div className="flex gap-4 items-center">
        <div className="relative flex-1 max-w-md">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted" />
          <input value={search} onChange={e => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 rounded-lg bg-surface border border-border focus:border-accent focus:outline-none text-sm"
            placeholder="Search plugins..." />
        </div>
        <div className="flex gap-2">
          {categories.map(cat => (
            <button key={cat} onClick={() => setActiveCategory(cat)}
              className={`flex items-center gap-1 px-3 py-1.5 text-sm rounded-lg border transition-colors ${
                activeCategory === cat ? 'bg-accent/20 border-accent text-accent' : 'bg-surface border-border text-muted hover:text-white'
              }`}>
              <span>{categoryIcons[cat] || '📦'}</span>
              {cat.charAt(0).toUpperCase() + cat.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Plugin Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map(plugin => (
          <div key={plugin.name} className="card hover:border-accent/30 transition-all">
            <div className="flex items-start justify-between mb-3">
              <div>
                <h3 className="font-semibold">{plugin.name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</h3>
                <span className="text-xs text-muted">v{plugin.version} • {plugin.author}</span>
              </div>
              {plugin.installed && <CheckCircle size={18} className="profit" />}
            </div>
            <p className="text-sm text-muted mb-3">{plugin.description}</p>
            <div className="flex items-center justify-between">
              <div className="flex gap-1">
                {plugin.tags.map(tag => (
                  <span key={tag} className="px-2 py-0.5 text-xs rounded-full bg-accent/10 text-accent">{tag}</span>
                ))}
              </div>
              {plugin.installed ? (
                <button onClick={() => handleUninstall(plugin.name)}
                  disabled={loading === plugin.name}
                  className="flex items-center gap-1 px-3 py-1.5 text-xs rounded-lg bg-loss/10 text-loss hover:bg-loss/20 transition-colors">
                  {loading === plugin.name ? <Loader2 size={12} className="animate-spin" /> : <Trash2 size={12} />}
                  Uninstall
                </button>
              ) : (
                <button onClick={() => handleInstall(plugin.name)}
                  disabled={loading === plugin.name}
                  className="flex items-center gap-1 px-3 py-1.5 text-xs rounded-lg bg-accent/10 text-accent hover:bg-accent/20 transition-colors">
                  {loading === plugin.name ? <Loader2 size={12} className="animate-spin" /> : <Download size={12} />}
                  Install
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {filtered.length === 0 && (
        <div className="text-center py-12 text-muted">
          <Package size={48} className="mx-auto mb-4 opacity-30" />
          <p>No plugins found</p>
        </div>
      )}
    </div>
  )
}
