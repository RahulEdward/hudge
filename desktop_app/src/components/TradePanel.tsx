'use client'
import { useState } from 'react'
import { ShoppingCart, TrendingUp, TrendingDown, AlertCircle } from 'lucide-react'

interface TradePanelProps {
  className?: string
}

export default function TradePanel({ className = '' }: TradePanelProps) {
  const [side, setSide] = useState<'BUY' | 'SELL'>('BUY')
  const [symbol, setSymbol] = useState('NIFTY')
  const [orderType, setOrderType] = useState('MARKET')
  const [quantity, setQuantity] = useState(1)
  const [price, setPrice] = useState('')
  const [product, setProduct] = useState('INTRADAY')

  const handleSubmit = async () => {
    try {
      await fetch(`${process.env.BACKEND_URL}/api/v1/trading/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symbol, side, order_type: orderType, quantity, price: price ? parseFloat(price) : 0, product }),
      })
    } catch {}
  }

  return (
    <div className={`card ${className}`}>
      <h3 className="text-sm font-semibold mb-3 flex items-center gap-2">
        <ShoppingCart size={16} />
        Quick Order
      </h3>

      {/* Side Toggle */}
      <div className="flex gap-2 mb-3">
        <button onClick={() => setSide('BUY')}
          className={`flex-1 py-2 rounded-lg text-sm font-medium transition-all ${
            side === 'BUY' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-surface border border-border text-muted'
          }`}>
          <TrendingUp size={14} className="inline mr-1" /> BUY
        </button>
        <button onClick={() => setSide('SELL')}
          className={`flex-1 py-2 rounded-lg text-sm font-medium transition-all ${
            side === 'SELL' ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30' : 'bg-surface border border-border text-muted'
          }`}>
          <TrendingDown size={14} className="inline mr-1" /> SELL
        </button>
      </div>

      {/* Symbol */}
      <div className="mb-3">
        <label className="text-xs text-muted mb-1 block">Symbol</label>
        <input value={symbol} onChange={e => setSymbol(e.target.value)}
          className="w-full px-3 py-2 text-sm rounded-lg bg-background border border-border focus:border-accent focus:outline-none" />
      </div>

      {/* Order Type & Product */}
      <div className="grid grid-cols-2 gap-2 mb-3">
        <div>
          <label className="text-xs text-muted mb-1 block">Type</label>
          <select value={orderType} onChange={e => setOrderType(e.target.value)}
            className="w-full px-2 py-2 text-sm rounded-lg bg-background border border-border focus:border-accent focus:outline-none">
            <option value="MARKET">Market</option>
            <option value="LIMIT">Limit</option>
            <option value="SL">Stop Loss</option>
            <option value="SL-M">SL-Market</option>
          </select>
        </div>
        <div>
          <label className="text-xs text-muted mb-1 block">Product</label>
          <select value={product} onChange={e => setProduct(e.target.value)}
            className="w-full px-2 py-2 text-sm rounded-lg bg-background border border-border focus:border-accent focus:outline-none">
            <option value="INTRADAY">Intraday</option>
            <option value="DELIVERY">Delivery</option>
            <option value="MARGIN">Margin</option>
          </select>
        </div>
      </div>

      {/* Qty & Price */}
      <div className="grid grid-cols-2 gap-2 mb-4">
        <div>
          <label className="text-xs text-muted mb-1 block">Quantity</label>
          <input type="number" value={quantity} onChange={e => setQuantity(Number(e.target.value))}
            className="w-full px-3 py-2 text-sm rounded-lg bg-background border border-border focus:border-accent focus:outline-none" />
        </div>
        {orderType !== 'MARKET' && (
          <div>
            <label className="text-xs text-muted mb-1 block">Price</label>
            <input type="number" value={price} onChange={e => setPrice(e.target.value)}
              className="w-full px-3 py-2 text-sm rounded-lg bg-background border border-border focus:border-accent focus:outline-none" />
          </div>
        )}
      </div>

      {/* Submit */}
      <button onClick={handleSubmit}
        className={`w-full py-2.5 rounded-lg text-sm font-medium transition-all ${
          side === 'BUY' ? 'bg-emerald-600 hover:bg-emerald-500 text-white' : 'bg-rose-600 hover:bg-rose-500 text-white'
        }`}>
        {side} {symbol}
      </button>
    </div>
  )
}
