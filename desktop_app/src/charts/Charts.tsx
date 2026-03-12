'use client'
import { useState, useEffect } from 'react'
import { BarChart2, TrendingUp, TrendingDown, RefreshCw } from 'lucide-react'

interface ChartData {
  timestamp: string
  open: number
  high: number
  low: number
  close: number
  volume: number
}

export default function Charts() {
  const [symbol, setSymbol] = useState('NIFTY')
  const [timeframe, setTimeframe] = useState('1D')
  const [data, setData] = useState<ChartData[]>([])
  const [loading, setLoading] = useState(false)
  const [quote, setQuote] = useState<any>(null)

  const symbols = ['NIFTY', 'BANKNIFTY', 'FINNIFTY', 'RELIANCE', 'TCS', 'INFY', 'HDFCBANK']
  const timeframes = ['1m', '5m', '15m', '1h', '1D']

  useEffect(() => {
    fetchQuote()
    fetchData()
  }, [symbol, timeframe])

  const fetchQuote = async () => {
    try {
      const res = await fetch(`${process.env.BACKEND_URL}/api/v1/market/quote/${symbol}`)
      if (res.ok) setQuote(await res.json())
    } catch {}
  }

  const fetchData = async () => {
    setLoading(true)
    try {
      const res = await fetch(`${process.env.BACKEND_URL}/api/v1/market/ohlc/${symbol}?timeframe=${timeframe}`)
      if (res.ok) {
        const result = await res.json()
        setData(result.data || [])
      }
    } catch {}
    setLoading(false)
  }

  const change = quote ? (quote.ltp - (quote.close || quote.ltp)) : 0
  const changePct = quote?.close ? ((change / quote.close) * 100) : 0
  const isPositive = change >= 0

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Charts</h1>
          <p className="text-muted text-sm">Market data visualization with technical indicators</p>
        </div>
        <button onClick={() => { fetchQuote(); fetchData() }}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-surface border border-border hover:border-accent transition-colors">
          <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
          Refresh
        </button>
      </div>

      {/* Symbol & Timeframe Selectors */}
      <div className="flex gap-4 items-center">
        <div className="flex gap-2">
          {symbols.map(s => (
            <button key={s} onClick={() => setSymbol(s)}
              className={`px-3 py-1.5 text-sm rounded-lg border transition-colors ${
                symbol === s ? 'bg-accent/20 border-accent text-accent' : 'bg-surface border-border hover:border-accent/50'
              }`}>
              {s}
            </button>
          ))}
        </div>
        <div className="h-6 w-px bg-border" />
        <div className="flex gap-1">
          {timeframes.map(tf => (
            <button key={tf} onClick={() => setTimeframe(tf)}
              className={`px-3 py-1.5 text-xs rounded-lg transition-colors ${
                timeframe === tf ? 'bg-accent text-white' : 'bg-surface text-muted hover:text-white'
              }`}>
              {tf}
            </button>
          ))}
        </div>
      </div>

      {/* Price Header */}
      <div className="card flex items-center gap-8">
        <div>
          <div className="text-sm text-muted">{symbol}</div>
          <div className="text-3xl font-bold">₹{quote?.ltp?.toLocaleString() || '—'}</div>
        </div>
        <div className={`flex items-center gap-1 text-lg ${isPositive ? 'profit' : 'loss'}`}>
          {isPositive ? <TrendingUp size={20} /> : <TrendingDown size={20} />}
          <span>{isPositive ? '+' : ''}{change.toFixed(2)}</span>
          <span className="text-sm">({isPositive ? '+' : ''}{changePct.toFixed(2)}%)</span>
        </div>
        {quote && (
          <div className="ml-auto flex gap-6 text-sm">
            <div><span className="text-muted">Open</span> <span className="ml-2">₹{quote.open?.toLocaleString() || '—'}</span></div>
            <div><span className="text-muted">High</span> <span className="ml-2 profit">₹{quote.high?.toLocaleString() || '—'}</span></div>
            <div><span className="text-muted">Low</span> <span className="ml-2 loss">₹{quote.low?.toLocaleString() || '—'}</span></div>
            <div><span className="text-muted">Volume</span> <span className="ml-2">{quote.volume?.toLocaleString() || '—'}</span></div>
          </div>
        )}
      </div>

      {/* Chart Area */}
      <div className="card" style={{ minHeight: '450px' }}>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2 text-sm text-muted">
            <BarChart2 size={16} />
            Candlestick Chart — {symbol} ({timeframe})
          </div>
        </div>
        {loading ? (
          <div className="flex items-center justify-center h-96">
            <RefreshCw size={24} className="animate-spin text-accent" />
          </div>
        ) : data.length > 0 ? (
          <div className="h-96 flex items-end gap-px">
            {data.slice(-80).map((candle, i) => {
              const isGreen = candle.close >= candle.open
              const range = Math.max(...data.slice(-80).map(d => d.high)) - Math.min(...data.slice(-80).map(d => d.low))
              const minPrice = Math.min(...data.slice(-80).map(d => d.low))
              const bodyTop = Math.max(candle.open, candle.close)
              const bodyBottom = Math.min(candle.open, candle.close)
              const bodyHeight = Math.max(((bodyTop - bodyBottom) / range) * 100, 1)
              const bodyY = ((bodyBottom - minPrice) / range) * 100
              const wickTop = ((candle.high - bodyTop) / range) * 100
              const wickBottom = ((bodyBottom - candle.low) / range) * 100

              return (
                <div key={i} className="flex-1 flex flex-col items-center justify-end relative" style={{ height: '100%' }}>
                  <div className="w-px" style={{
                    height: `${wickTop}%`,
                    backgroundColor: isGreen ? '#10b981' : '#f43f5e',
                  }} />
                  <div style={{
                    width: '60%',
                    minWidth: '3px',
                    height: `${bodyHeight}%`,
                    backgroundColor: isGreen ? '#10b981' : '#f43f5e',
                    borderRadius: '1px',
                  }} />
                  <div className="w-px" style={{
                    height: `${wickBottom}%`,
                    backgroundColor: isGreen ? '#10b981' : '#f43f5e',
                  }} />
                  <div style={{ height: `${bodyY}%` }} />
                </div>
              )
            })}
          </div>
        ) : (
          <div className="flex items-center justify-center h-96 text-muted">
            <div className="text-center">
              <BarChart2 size={48} className="mx-auto mb-4 opacity-30" />
              <p>No chart data available</p>
              <p className="text-sm">Connect a broker to load market data</p>
            </div>
          </div>
        )}
      </div>

      {/* Volume Chart */}
      {data.length > 0 && (
        <div className="card">
          <div className="text-sm text-muted mb-3">Volume</div>
          <div className="h-24 flex items-end gap-px">
            {data.slice(-80).map((candle, i) => {
              const maxVol = Math.max(...data.slice(-80).map(d => d.volume || 1))
              const height = ((candle.volume || 0) / maxVol) * 100
              const isGreen = candle.close >= candle.open
              return (
                <div key={i} className="flex-1" style={{
                  height: `${height}%`,
                  backgroundColor: isGreen ? 'rgba(16,185,129,0.4)' : 'rgba(244,63,94,0.4)',
                  borderRadius: '1px 1px 0 0',
                }} />
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}
