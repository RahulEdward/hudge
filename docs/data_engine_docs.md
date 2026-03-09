# QUANT AI LAB — Data Engine Documentation

## Overview

The Data Engine handles all market data operations: live streaming, historical data loading, tick storage, OHLC generation, and intelligent caching.

---

## Components

### 1. Market Stream (`market_stream.py`)

Real-time market data streaming from broker WebSocket feeds.

**Data Flow:**
```
Broker WebSocket → Normalize → Internal Event Bus → Redis Cache → UI/Agents
```

**Tick Data Format (Normalized):**
```json
{
  "symbol": "NIFTY",
  "ltp": 22250.50,
  "open": 22200.00,
  "high": 22280.00,
  "low": 22150.00,
  "close": 22250.50,
  "volume": 125000,
  "oi": 1250000,
  "bid": 22250.00,
  "ask": 22251.00,
  "timestamp": "2025-01-15T10:30:00+05:30"
}
```

**Supported Feeds:**
| Broker | Technology | Symbols |
|--------|-----------|---------|
| Angel One | SmartAPI WebSocket | NSE, BSE, MCX |
| Zerodha | KiteTicker WebSocket | NSE, BSE, MCX, CDS |
| Dhan | DhanHQ WebSocket | NSE, BSE |
| Fyers | Fyers DataSocket | NSE, BSE, MCX |

**Features:**
- Auto-reconnect on disconnect (exponential backoff)
- Multi-symbol subscription (up to 50 symbols)
- Heartbeat monitoring
- Data gap detection and filling

---

### 2. Historical Loader (`historical_loader.py`)

Downloads historical OHLCV data from broker APIs.

**Supported Timeframes:**

| Timeframe | Code | Max Lookback |
|-----------|------|-------------- |
| 1 minute | `1m` | 30 days |
| 5 minutes | `5m` | 90 days |
| 15 minutes | `15m` | 180 days |
| 1 hour | `1h` | 1 year |
| 1 day | `1D` | 10 years |

**OHLCV Format:**
```json
{
  "timestamp": "2025-01-15T10:30:00",
  "open": 22200.00,
  "high": 22280.00,
  "low": 22150.00,
  "close": 22250.50,
  "volume": 125000
}
```

**Features:**
- Automatic pagination for large date ranges
- Data validation (gaps, outliers, corporate action adjustment)
- Caches to SQLite for instant re-access
- Parallel download for multiple symbols

---

### 3. Tick Storage (`tick_storage.py`)

Stores raw tick data for replay and analysis.

**Storage:**
- SQLite with time-partitioned tables
- Compressed storage (run-length encoding for price)
- Rolling window (configurable retention: 7/30/90 days)
- Indexing by symbol + timestamp

**Tick-to-OHLCV Aggregation:**
```
Raw ticks → Group by time interval → Compute Open/High/Low/Close/Volume
```

Supports custom intervals: 1s, 5s, 10s, 30s, 1m, 2m, 3m, 5m, 10m, 15m, 30m, 1h, 2h, 4h, 1D

---

### 4. Data Cache (`data_cache.py`)

Redis-backed caching layer to reduce broker API calls.

**Cache Strategy:**

| Data Type | TTL | Key Format |
|-----------|-----|------------|
| Live quote | 1 second | `quote:{symbol}` |
| OHLCV (intraday) | 5 minutes | `ohlcv:{symbol}:{tf}:{date}` |
| OHLCV (daily) | 1 hour | `ohlcv:{symbol}:1D` |
| Indicators | 5 minutes | `ind:{symbol}:{tf}:{name}` |
| Historical (full) | 24 hours | `hist:{symbol}:{tf}:{range}` |

**Fallback:**
- If Redis unavailable, falls back to in-memory LRU cache
- Cache miss → fetch from broker API → store in cache

---

## Technical Indicators

Computed by the Data Engine and consumed by agents:

| Category | Indicators |
|----------|------------|
| Trend | EMA (9, 21, 50, 200), SMA, DEMA, TEMA, ADX, Supertrend |
| Momentum | RSI (14), MACD (12,26,9), Stochastic, Williams %R, CCI, ROC |
| Volatility | Bollinger Bands (20,2), ATR (14), Keltner Channels, Donchian |
| Volume | OBV, VWAP, Volume SMA Ratio, MFI, Accumulation/Distribution |
| Support/Resistance | Pivot Points, Fibonacci Retracement, Volume Profile |

**Computation:**
- Uses `pandas-ta` and `ta` libraries
- Computed on-demand and cached
- Supports custom indicator creation via plugin system

---

## Indian Market Specific

### Trading Hours
- Pre-market: 09:00 - 09:15 IST
- Market: 09:15 - 15:30 IST
- Post-market: 15:40 - 16:00 IST

### Supported Instruments

| Type | Examples |
|------|---------|
| Index Futures | NIFTY FUT, BANKNIFTY FUT, FINNIFTY FUT |
| Index Options | NIFTY CE/PE, BANKNIFTY CE/PE |
| Equities | Reliance, TCS, HDFC Bank, Infosys, etc. |
| Equity F&O | Stock Futures and Options |

### Symbol Normalization
Each broker uses different symbol formats. The Data Engine normalizes:
```
Angel One:   "NIFTY25JAN22200CE"  →  "NIFTY-22200-CE-25JAN"
Zerodha:     "NIFTY2510922200CE"  →  "NIFTY-22200-CE-25JAN"
Dhan:        "NIFTY-Jan2025-22200-CE" → "NIFTY-22200-CE-25JAN"
Internal:    "NIFTY-22200-CE-25JAN" (normalized format)
```
