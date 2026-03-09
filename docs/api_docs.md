# QUANT AI LAB — API Documentation

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

All endpoints (except `/health` and `/auth/*`) require a JWT Bearer token.

```
Authorization: Bearer <token>
```

---

## Endpoints

### Health & System

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | System health check |
| GET | `/system/status` | System status with agent states |
| GET | `/system/logs` | Fetch recent system logs |

### Authentication (Google OAuth)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/google` | Exchange Google `id_token` for app JWT (called after Google OAuth) |
| POST | `/auth/refresh` | Refresh app JWT token using refresh token |
| POST | `/auth/logout` | Revoke session and clear tokens |
| GET | `/auth/me` | Get current logged-in user profile |
| POST | `/auth/llm/oauth` | OAuth login for LLM providers (OpenAI/Anthropic) |

**Google Login Request:**
```json
{
  "id_token": "eyJhbGciOiJSUzI1NiIs..."  // Google id_token from OAuth flow
}
```

**Google Login Response:**
```json
{
  "access_token": "app_jwt_token...",
  "refresh_token": "app_refresh_token...",
  "expires_in": 3600,
  "user": {
    "id": "usr_001",
    "email": "user@gmail.com",
    "name": "John Doe",
    "picture": "https://lh3.googleusercontent.com/..."
  }
}
```

### Agent Communication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/agents/chat` | Send message to AI agent |
| GET | `/agents/status` | Get all agent statuses |
| POST | `/agents/task` | Submit task to orchestrator |
| GET | `/agents/history` | Get conversation history |

**Chat Request Body:**
```json
{
  "message": "Analyze NIFTY for today",
  "agent": "market_analysis",
  "context": {}
}
```

**Chat Response:**
```json
{
  "response": "Market Analysis for NIFTY...",
  "agent": "market_analysis",
  "data": {
    "trend": "bullish",
    "regime": "trending",
    "volatility": "moderate",
    "support": [22100, 22000],
    "resistance": [22400, 22500]
  },
  "suggestions": ["Run backtest on breakout strategy"]
}
```

### Market Data

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/market/quote/{symbol}` | Live quote for symbol |
| GET | `/market/ohlc/{symbol}` | OHLC data with timeframe param |
| GET | `/market/indicators/{symbol}` | Technical indicators |
| GET | `/market/history/{symbol}` | Historical data |
| POST | `/market/stream/subscribe` | Subscribe to live stream |

### Trading

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/trades/order` | Place new order |
| PUT | `/trades/order/{id}` | Modify existing order |
| DELETE | `/trades/order/{id}` | Cancel order |
| GET | `/trades/orders` | List all orders |
| GET | `/trades/positions` | Current positions |
| GET | `/trades/holdings` | Holdings |
| GET | `/trades/funds` | Available funds |

**Order Request Body:**
```json
{
  "symbol": "NIFTY24MARFUT",
  "side": "BUY",
  "order_type": "LIMIT",
  "quantity": 50,
  "price": 22200.00,
  "stop_loss": 22100.00,
  "take_profit": 22400.00,
  "broker": "angel_one",
  "mode": "paper"
}
```

### Backtesting

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/backtest/run` | Run a backtest |
| GET | `/backtest/results/{id}` | Get backtest results |
| GET | `/backtest/history` | List past backtests |

**Backtest Request:**
```json
{
  "strategy": "breakout_pullback",
  "symbol": "NIFTY",
  "start_date": "2024-01-01",
  "end_date": "2025-12-31",
  "initial_capital": 1000000,
  "risk_per_trade": 0.01
}
```

**Backtest Response:**
```json
{
  "id": "bt_001",
  "metrics": {
    "win_rate": 63.2,
    "sharpe_ratio": 1.85,
    "max_drawdown": 8.3,
    "profit_factor": 1.72,
    "expectancy": 1250.0,
    "total_trades": 156,
    "net_profit": 195000
  },
  "equity_curve": [],
  "trades": []
}
```

### Portfolio

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/portfolio/summary` | Portfolio summary |
| GET | `/portfolio/performance` | Performance metrics |
| GET | `/portfolio/allocation` | Asset allocation |
| GET | `/portfolio/history` | Portfolio history |

### Strategy

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/strategy/list` | List discovered strategies |
| GET | `/strategy/{id}` | Strategy details |
| POST | `/strategy/approve/{id}` | Approve strategy for live trading |
| POST | `/strategy/reject/{id}` | Reject strategy |

### ML Lab

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/ml/train` | Train ML model |
| GET | `/ml/models` | List trained models |
| POST | `/ml/predict` | Run prediction |
| GET | `/ml/features` | Available features |

### Broker Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/broker/connect` | Connect to broker |
| POST | `/broker/disconnect` | Disconnect broker |
| GET | `/broker/status` | Broker connection status |
| POST | `/broker/credentials` | Save broker credentials (encrypted) |

### Plugins

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/plugins/list` | List available plugins |
| POST | `/plugins/install` | Install plugin |
| POST | `/plugins/uninstall` | Uninstall plugin |
| GET | `/plugins/marketplace` | Browse marketplace |

---

## WebSocket Endpoints

### `/ws/market`
Real-time market data streaming.

```json
// Subscribe
{"action": "subscribe", "symbols": ["NIFTY", "BANKNIFTY"]}

// Data Event
{"type": "tick", "symbol": "NIFTY", "ltp": 22250.50, "volume": 125000, "timestamp": "..."}
```

### `/ws/agent`
Real-time agent communication with streaming responses.

```json
// Send message
{"action": "chat", "message": "Analyze NIFTY", "agent": "market_analysis"}

// Streaming response
{"type": "chunk", "content": "Analyzing NIFTY...", "agent": "market_analysis"}
{"type": "complete", "data": {...}}
```

### `/ws/trades`
Real-time trade updates and alerts.

```json
{"type": "order_update", "order_id": "...", "status": "EXECUTED", "details": {...}}
{"type": "alert", "message": "Stop-loss hit on NIFTY position", "severity": "warning"}
```

---

## Error Responses

```json
{
  "error": true,
  "code": "BROKER_NOT_CONNECTED",
  "message": "Please connect to a broker before placing orders",
  "details": {}
}
```

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `AUTH_REQUIRED` | 401 | Authentication required |
| `AUTH_INVALID` | 401 | Invalid credentials |
| `BROKER_NOT_CONNECTED` | 400 | No broker connection |
| `ORDER_FAILED` | 400 | Order placement failed |
| `AGENT_ERROR` | 500 | Agent processing error |
| `RATE_LIMITED` | 429 | Too many requests |
