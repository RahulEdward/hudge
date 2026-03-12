'use client'
import { useState, useEffect, useRef } from 'react'
import { Terminal, Filter, Trash2, Download, AlertCircle, Info, AlertTriangle } from 'lucide-react'

interface LogEntry {
  timestamp: string
  level: 'INFO' | 'WARNING' | 'ERROR' | 'DEBUG'
  source: string
  message: string
}

interface LogsViewerProps {
  className?: string
  maxLines?: number
}

const LEVEL_STYLES: Record<string, string> = {
  INFO: 'text-blue-400',
  WARNING: 'text-amber-400',
  ERROR: 'text-rose-400',
  DEBUG: 'text-slate-500',
}

const LEVEL_ICONS: Record<string, any> = {
  INFO: Info,
  WARNING: AlertTriangle,
  ERROR: AlertCircle,
  DEBUG: Terminal,
}

export default function LogsViewer({ className = '', maxLines = 500 }: LogsViewerProps) {
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [filter, setFilter] = useState('')
  const [levelFilter, setLevelFilter] = useState<string | null>(null)
  const [autoScroll, setAutoScroll] = useState(true)
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Poll backend for logs
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`${process.env.BACKEND_URL}/api/v1/health`)
        if (res.ok) {
          const data = await res.json()
          setLogs(prev => {
            const newEntry: LogEntry = {
              timestamp: new Date().toISOString().slice(11, 23),
              level: 'INFO',
              source: 'system',
              message: `Health check: ${data.status || 'ok'} — Agents: ${data.agents_active || '0'} active`,
            }
            const updated = [...prev, newEntry]
            return updated.slice(-maxLines)
          })
        }
      } catch {}
    }, 10000)

    return () => clearInterval(interval)
  }, [maxLines])

  useEffect(() => {
    if (autoScroll && scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [logs, autoScroll])

  const filteredLogs = logs.filter(log => {
    if (levelFilter && log.level !== levelFilter) return false
    if (filter && !log.message.toLowerCase().includes(filter.toLowerCase()) && !log.source.toLowerCase().includes(filter.toLowerCase())) return false
    return true
  })

  return (
    <div className={`card flex flex-col ${className}`} style={{ height: '400px' }}>
      {/* Toolbar */}
      <div className="flex items-center gap-3 pb-3 border-b border-border">
        <div className="relative flex-1 max-w-xs">
          <Filter size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted" />
          <input value={filter} onChange={e => setFilter(e.target.value)}
            placeholder="Filter logs..."
            className="w-full pl-9 pr-3 py-1.5 text-sm rounded-lg bg-background border border-border focus:border-accent focus:outline-none" />
        </div>
        <div className="flex gap-1">
          {['INFO', 'WARNING', 'ERROR', 'DEBUG'].map(level => (
            <button key={level} onClick={() => setLevelFilter(levelFilter === level ? null : level)}
              className={`px-2 py-1 text-xs rounded transition-colors ${
                levelFilter === level ? `${LEVEL_STYLES[level]} bg-white/5` : 'text-muted hover:text-white'
              }`}>
              {level}
            </button>
          ))}
        </div>
        <div className="ml-auto flex gap-2">
          <button onClick={() => setAutoScroll(!autoScroll)}
            className={`text-xs px-2 py-1 rounded ${autoScroll ? 'text-accent' : 'text-muted'}`}>
            Auto-scroll {autoScroll ? 'ON' : 'OFF'}
          </button>
          <button onClick={() => setLogs([])} className="text-muted hover:text-white">
            <Trash2 size={14} />
          </button>
        </div>
      </div>

      {/* Log Output */}
      <div ref={scrollRef} className="flex-1 overflow-auto font-mono text-xs mt-2 space-y-0.5">
        {filteredLogs.length === 0 ? (
          <div className="text-center text-muted py-8">
            <Terminal size={24} className="mx-auto mb-2 opacity-30" />
            <p>No log entries</p>
          </div>
        ) : (
          filteredLogs.map((log, i) => {
            const Icon = LEVEL_ICONS[log.level] || Terminal
            return (
              <div key={i} className="flex items-start gap-2 py-0.5 hover:bg-white/5 px-2 rounded">
                <span className="text-muted flex-shrink-0">{log.timestamp}</span>
                <Icon size={12} className={`flex-shrink-0 mt-0.5 ${LEVEL_STYLES[log.level]}`} />
                <span className={`flex-shrink-0 ${LEVEL_STYLES[log.level]}`}>[{log.level}]</span>
                <span className="text-accent flex-shrink-0">{log.source}</span>
                <span className="text-slate-300">{log.message}</span>
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}
