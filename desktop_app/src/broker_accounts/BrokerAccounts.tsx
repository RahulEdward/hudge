'use client'
import { useState, useEffect } from 'react'
import { Plug, PlugZap, Shield, AlertTriangle, CheckCircle, XCircle, Loader2 } from 'lucide-react'

interface Broker {
  name: string
  id: string
  status: 'connected' | 'disconnected' | 'connecting'
  icon: string
}

export default function BrokerAccounts() {
  const [brokers, setBrokers] = useState<Broker[]>([
    { name: 'Angel One', id: 'angelone', status: 'disconnected', icon: '🔶' },
    { name: 'Zerodha', id: 'zerodha', status: 'disconnected', icon: '🟢' },
    { name: 'Dhan', id: 'dhan', status: 'disconnected', icon: '🔵' },
    { name: 'Fyers', id: 'fyers', status: 'disconnected', icon: '🟣' },
  ])
  const [selectedBroker, setSelectedBroker] = useState<string | null>(null)
  const [credentials, setCredentials] = useState<Record<string, string>>({})
  const [connecting, setConnecting] = useState(false)

  useEffect(() => {
    fetchBrokerStatus()
  }, [])

  const fetchBrokerStatus = async () => {
    try {
      const res = await fetch(`${process.env.BACKEND_URL}/api/v1/broker/status`)
      if (res.ok) {
        const data = await res.json()
        if (data.brokers) {
          setBrokers(prev => prev.map(b => ({
            ...b,
            status: data.brokers[b.id]?.connected ? 'connected' : 'disconnected'
          })))
        }
      }
    } catch {}
  }

  const handleConnect = async (brokerId: string) => {
    setConnecting(true)
    try {
      const res = await fetch(`${process.env.BACKEND_URL}/api/v1/broker/connect`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ broker: brokerId, credentials }),
      })
      if (res.ok) {
        setBrokers(prev => prev.map(b =>
          b.id === brokerId ? { ...b, status: 'connected' } : b
        ))
        setSelectedBroker(null)
      }
    } catch {}
    setConnecting(false)
  }

  const handleDisconnect = async (brokerId: string) => {
    try {
      await fetch(`${process.env.BACKEND_URL}/api/v1/broker/disconnect`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ broker: brokerId }),
      })
      setBrokers(prev => prev.map(b =>
        b.id === brokerId ? { ...b, status: 'disconnected' } : b
      ))
    } catch {}
  }

  const credentialFields: Record<string, string[]> = {
    angelone: ['API Key', 'Client ID', 'Password', 'TOTP Secret'],
    zerodha: ['API Key', 'API Secret', 'Request Token'],
    dhan: ['Client ID', 'Access Token'],
    fyers: ['Client ID', 'Access Token'],
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Broker Accounts</h1>
        <p className="text-muted text-sm">Connect and manage your trading accounts</p>
      </div>

      {/* Connection Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {brokers.map(broker => (
          <div key={broker.id}
            className={`card cursor-pointer transition-all hover:border-accent/50 ${
              selectedBroker === broker.id ? 'border-accent' : ''
            }`}
            onClick={() => setSelectedBroker(selectedBroker === broker.id ? null : broker.id)}>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <span className="text-2xl">{broker.icon}</span>
                <span className="font-semibold">{broker.name}</span>
              </div>
              {broker.status === 'connected' ? (
                <CheckCircle size={20} className="profit" />
              ) : (
                <XCircle size={20} className="text-muted" />
              )}
            </div>
            <div className={`text-sm ${broker.status === 'connected' ? 'profit' : 'text-muted'}`}>
              {broker.status === 'connected' ? '● Connected' : '○ Disconnected'}
            </div>
            {broker.status === 'connected' && (
              <button
                onClick={(e) => { e.stopPropagation(); handleDisconnect(broker.id) }}
                className="mt-3 w-full px-3 py-1.5 text-sm rounded-lg bg-loss/10 text-loss hover:bg-loss/20 transition-colors">
                Disconnect
              </button>
            )}
          </div>
        ))}
      </div>

      {/* Credential Entry */}
      {selectedBroker && brokers.find(b => b.id === selectedBroker)?.status !== 'connected' && (
        <div className="card">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Shield size={20} className="accent" />
            Connect {brokers.find(b => b.id === selectedBroker)?.name}
          </h2>
          <div className="flex items-center gap-2 mb-4 p-3 rounded-lg bg-accent/5 border border-accent/20">
            <AlertTriangle size={16} className="accent" />
            <span className="text-sm text-muted">Credentials are encrypted at rest using Fernet encryption</span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {(credentialFields[selectedBroker] || []).map(field => (
              <div key={field}>
                <label className="text-sm text-muted mb-1 block">{field}</label>
                <input
                  type={field.toLowerCase().includes('secret') || field.toLowerCase().includes('password') || field.toLowerCase().includes('token') ? 'password' : 'text'}
                  placeholder={field}
                  onChange={e => setCredentials(prev => ({ ...prev, [field.toLowerCase().replace(/ /g, '_')]: e.target.value }))}
                  className="w-full px-3 py-2 rounded-lg bg-background border border-border focus:border-accent focus:outline-none text-sm"
                />
              </div>
            ))}
          </div>
          <button
            onClick={() => handleConnect(selectedBroker)}
            disabled={connecting}
            className="mt-4 flex items-center gap-2 px-6 py-2.5 rounded-lg bg-accent text-white hover:bg-accent/80 transition-colors disabled:opacity-50">
            {connecting ? <Loader2 size={16} className="animate-spin" /> : <PlugZap size={16} />}
            {connecting ? 'Connecting...' : 'Connect'}
          </button>
        </div>
      )}

      {/* Connection Info */}
      <div className="card">
        <h2 className="text-lg font-semibold mb-3">Trading Mode</h2>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-profit/10 border border-profit/30">
            <div className="w-2 h-2 rounded-full bg-profit animate-pulse" />
            <span className="text-sm profit">Paper Trading Active</span>
          </div>
          <span className="text-sm text-muted">Switch to live trading after connecting a broker</span>
        </div>
      </div>
    </div>
  )
}
