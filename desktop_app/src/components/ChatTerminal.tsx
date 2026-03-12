'use client'
import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Loader2, Sparkles } from 'lucide-react'

interface Message {
  role: 'user' | 'assistant'
  content: string
  agent?: string
  timestamp?: string
}

interface ChatTerminalProps {
  sessionId?: string
  className?: string
  compact?: boolean
}

export default function ChatTerminal({ sessionId = 'default', className = '', compact = false }: ChatTerminalProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages])

  const sendMessage = async () => {
    if (!input.trim() || loading) return
    const userMsg: Message = { role: 'user', content: input, timestamp: new Date().toLocaleTimeString() }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setLoading(true)

    try {
      const res = await fetch(`${process.env.BACKEND_URL}/api/v1/agents/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input, session_id: sessionId }),
      })
      if (res.ok) {
        const data = await res.json()
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: data.response || data.message || 'No response',
          agent: data.agent,
          timestamp: new Date().toLocaleTimeString(),
        }])
      }
    } catch {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Connection error. Is the backend running?', timestamp: new Date().toLocaleTimeString() }])
    }
    setLoading(false)
  }

  return (
    <div className={`flex flex-col ${compact ? 'h-64' : 'h-full'} ${className}`}>
      <div ref={scrollRef} className="flex-1 overflow-auto space-y-3 p-3">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-muted opacity-50">
            <Sparkles size={24} className="mb-2" />
            <span className="text-sm">Ask anything about markets, strategies, or trading</span>
          </div>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={`flex gap-2 ${msg.role === 'user' ? 'justify-end' : ''}`}>
            {msg.role === 'assistant' && (
              <div className="w-7 h-7 rounded-full bg-accent/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                <Bot size={14} className="accent" />
              </div>
            )}
            <div className={`max-w-[80%] rounded-lg px-3 py-2 text-sm ${
              msg.role === 'user' ? 'bg-accent/20 text-white' : 'bg-surface border border-border'
            }`}>
              <div className="whitespace-pre-wrap">{msg.content}</div>
              <div className="text-xs text-muted mt-1 flex items-center gap-2">
                {msg.timestamp}
                {msg.agent && <span className="text-accent">via {msg.agent}</span>}
              </div>
            </div>
            {msg.role === 'user' && (
              <div className="w-7 h-7 rounded-full bg-white/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                <User size={14} />
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="flex items-center gap-2 text-muted text-sm">
            <Loader2 size={14} className="animate-spin" />
            Thinking...
          </div>
        )}
      </div>
      <div className="flex gap-2 p-3 border-t border-border">
        <input value={input} onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && sendMessage()}
          placeholder="Type your message..."
          className="flex-1 px-3 py-2 rounded-lg bg-background border border-border focus:border-accent focus:outline-none text-sm" />
        <button onClick={sendMessage} disabled={loading || !input.trim()}
          className="px-3 py-2 rounded-lg bg-accent text-white hover:bg-accent/80 disabled:opacity-50 transition-colors">
          <Send size={16} />
        </button>
      </div>
    </div>
  )
}
