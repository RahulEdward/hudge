'use client'
import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Loader2 } from 'lucide-react'

const API = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'

interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

const AGENT_OPTIONS = [
  { id: 'orchestrator', label: 'Auto (Orchestrator)' },
  { id: 'market_analysis', label: 'Market Analysis' },
  { id: 'strategy_discovery', label: 'Strategy Discovery' },
  { id: 'risk_management', label: 'Risk Management' },
  { id: 'reporting', label: 'Reporting' },
]

export default function AIChat() {
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: 'Namaste! I am your AI trading assistant. Ask me to analyze markets, discover strategies, check your portfolio, or execute trades.', timestamp: new Date() }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [agent, setAgent] = useState('orchestrator')
  const [sessionId] = useState(() => `session_${Date.now()}`)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const send = async () => {
    if (!input.trim() || loading) return
    const userMsg = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: userMsg, timestamp: new Date() }])
    setLoading(true)

    try {
      const res = await fetch(`${API}/api/v1/agents/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg, session_id: sessionId, agent_id: agent }),
      })
      const data = await res.json()
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.response || data.error || 'No response',
        timestamp: new Date()
      }])
    } catch (e) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Connection error. Make sure the backend is running.',
        timestamp: new Date()
      }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-full p-6">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-xl font-bold text-slate-100">AI Chat Terminal</h1>
        <select
          value={agent}
          onChange={e => setAgent(e.target.value)}
          className="bg-[#12121a] border border-[#1e1e2e] rounded-lg text-sm text-slate-300 px-3 py-1.5"
        >
          {AGENT_OPTIONS.map(a => (
            <option key={a.id} value={a.id}>{a.label}</option>
          ))}
        </select>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 mb-4 card">
        {messages.map((msg, i) => (
          <div key={i} className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : ''}`}>
            {msg.role === 'assistant' && (
              <div className="w-8 h-8 rounded-lg bg-indigo-600/30 flex items-center justify-center flex-shrink-0">
                <Bot size={14} className="text-indigo-400" />
              </div>
            )}
            <div className={`max-w-[80%] rounded-xl px-4 py-3 ${
              msg.role === 'user'
                ? 'bg-indigo-600 text-white'
                : 'bg-[#1e1e2e] text-slate-300'
            }`}>
              <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
              <p className="text-[10px] mt-1 opacity-40">{msg.timestamp.toLocaleTimeString()}</p>
            </div>
            {msg.role === 'user' && (
              <div className="w-8 h-8 rounded-lg bg-slate-700 flex items-center justify-center flex-shrink-0">
                <User size={14} className="text-slate-300" />
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-lg bg-indigo-600/30 flex items-center justify-center">
              <Loader2 size={14} className="text-indigo-400 animate-spin" />
            </div>
            <div className="bg-[#1e1e2e] rounded-xl px-4 py-3">
              <div className="flex gap-1">
                {[0,1,2].map(i => (
                  <div key={i} className="w-2 h-2 bg-indigo-500 rounded-full animate-bounce"
                    style={{ animationDelay: `${i * 0.15}s` }} />
                ))}
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="flex gap-3">
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && !e.shiftKey && send()}
          placeholder="Ask about markets, strategies, portfolio..."
          className="flex-1 bg-[#12121a] border border-[#1e1e2e] rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-600"
        />
        <button
          onClick={send}
          disabled={loading || !input.trim()}
          className="px-4 py-3 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 rounded-xl transition-colors"
        >
          <Send size={16} className="text-white" />
        </button>
      </div>
    </div>
  )
}
