'use client'
import { useEffect, useState } from 'react'
import { AlertTriangle, Plus } from 'lucide-react'

const API = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'

export default function LiveTrading() {
  const [positions, setPositions] = useState<any[]>([])
  const [order, setOrder] = useState({ symbol: 'NIFTY', side: 'BUY', quantity: '1', order_type: 'MARKET', price: '0', product_type: 'INTRADAY' })
  const [loading, setLoading] = useState(false)
  const [killActive, setKillActive] = useState(false)
  const [msg, setMsg] = useState('')

  useEffect(() => {
    const load = async () => {
      try {
        const res = await fetch(`${API}/api/v1/trades/positions`).then(r => r.json())
        if (res.success) setPositions(res.positions)
      } catch {}
    }
    load()
    const id = setInterval(load, 10000)
    return () => clearInterval(id)
  }, [])

  const placeOrder = async () => {
    setLoading(true)
    setMsg('')
    try {
      const res = await fetch(`${API}/api/v1/trades/order`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...order, quantity: parseInt(order.quantity), price: parseFloat(order.price) }),
      }).then(r => r.json())
      setMsg(res.success ? `Order ${res.order?.status || 'placed'}` : `Error: ${res.error}`)
    } catch (e) { setMsg('Connection error') }
    setLoading(false)
  }

  const activateKillSwitch = async () => {
    if (!confirm('Activate kill switch? All trading will be halted.')) return
    await fetch(`${API}/api/v1/trades/kill-switch`, { method: 'POST' })
    setKillActive(true)
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-slate-100">Live Trading</h1>
        <button
          onClick={activateKillSwitch}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm transition-colors ${
            killActive ? 'bg-rose-900 text-rose-300' : 'bg-rose-600/20 hover:bg-rose-600/40 text-rose-400'
          }`}
        >
          <AlertTriangle size={14} />
          {killActive ? 'Kill Switch ACTIVE' : 'Kill Switch'}
        </button>
      </div>

      {/* Order Panel */}
      <div className="card">
        <h2 className="text-sm font-semibold text-slate-300 mb-4">Place Order</h2>
        <div className="grid grid-cols-2 lg:grid-cols-3 gap-3">
          {[
            { key: 'symbol', label: 'Symbol' },
            { key: 'quantity', label: 'Quantity' },
            { key: 'price', label: 'Price (0 = Market)' },
          ].map(({ key, label }) => (
            <div key={key}>
              <label className="block text-xs text-slate-500 mb-1">{label}</label>
              <input
                value={(order as any)[key]}
                onChange={e => setOrder(o => ({ ...o, [key]: e.target.value }))}
                className="w-full bg-[#0a0a0f] border border-[#1e1e2e] rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-600"
              />
            </div>
          ))}
          <div>
            <label className="block text-xs text-slate-500 mb-1">Side</label>
            <select
              value={order.side}
              onChange={e => setOrder(o => ({ ...o, side: e.target.value }))}
              className="w-full bg-[#0a0a0f] border border-[#1e1e2e] rounded-lg px-3 py-2 text-sm text-slate-100"
            >
              <option>BUY</option>
              <option>SELL</option>
            </select>
          </div>
          <div>
            <label className="block text-xs text-slate-500 mb-1">Product</label>
            <select
              value={order.product_type}
              onChange={e => setOrder(o => ({ ...o, product_type: e.target.value }))}
              className="w-full bg-[#0a0a0f] border border-[#1e1e2e] rounded-lg px-3 py-2 text-sm text-slate-100"
            >
              <option value="INTRADAY">Intraday (MIS)</option>
              <option value="DELIVERY">Delivery (CNC)</option>
            </select>
          </div>
        </div>
        <div className="flex items-center gap-3 mt-4">
          <button
            onClick={placeOrder}
            disabled={loading || killActive}
            className="flex items-center gap-2 px-6 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 rounded-lg text-sm text-white"
          >
            <Plus size={14} />
            {loading ? 'Placing...' : 'Place Order'}
          </button>
          {msg && <p className={`text-xs ${msg.includes('Error') ? 'text-rose-400' : 'text-emerald-400'}`}>{msg}</p>}
        </div>
      </div>

      {/* Positions */}
      <div className="card">
        <h2 className="text-sm font-semibold text-slate-300 mb-4">Open Positions</h2>
        {positions.length === 0 ? (
          <p className="text-xs text-slate-500">No open positions</p>
        ) : (
          <table className="w-full text-xs text-slate-400">
            <thead>
              <tr className="border-b border-[#1e1e2e]">
                <th className="text-left py-2">Symbol</th>
                <th className="text-right py-2">Qty</th>
                <th className="text-right py-2">Avg Price</th>
                <th className="text-right py-2">P&L</th>
              </tr>
            </thead>
            <tbody>
              {positions.map((p: any, i: number) => (
                <tr key={i} className="border-b border-[#1e1e2e]/50">
                  <td className="py-2 font-medium text-slate-300">{p.symbol}</td>
                  <td className="text-right">{p.quantity}</td>
                  <td className="text-right">₹{p.average_price?.toFixed(2)}</td>
                  <td className={`text-right ${(p.pnl || 0) >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                    ₹{(p.pnl || 0).toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
