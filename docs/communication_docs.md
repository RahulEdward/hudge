# QUANT AI LAB — Communication Layer Documentation

## Overview

Users interact with the system via three channels: Desktop App, Telegram Bot, and WhatsApp Web. All channels route through a unified Command Parser and Message Queue.

## Architecture

```
User Input (Desktop / Telegram / WhatsApp / Voice)
    │
    ▼
Command Parser (NLP Intent Detection)
    │
    ▼
Message Queue (Redis Streams)
    │
    ▼
Agent Orchestrator → AI Agents → Response
    │
    ▼
Response Router → Deliver to originating channel
```

## Command Parser

### Intent Detection

The parser classifies user messages into intents:

| Intent | Example Messages |
|--------|------------------|
| `market_analysis` | "Analyze NIFTY", "How is BANKNIFTY looking?" |
| `backtest_request` | "Backtest last 2 years", "Run backtest on this strategy" |
| `trade_execution` | "Execute with 1% risk", "Buy NIFTY at market" |
| `portfolio_request` | "Show my portfolio", "What are my holdings?" |
| `strategy_request` | "Find a strategy for NIFTY", "Create a momentum strategy" |
| `risk_query` | "What's my current exposure?", "Set max risk to 2%" |
| `status_query` | "System status", "Show active trades" |
| `stop_command` | "Stop all trades", "Kill switch" |

### Entity Extraction
- **Symbol**: NIFTY, BANKNIFTY, FINNIFTY, stock names
- **Timeframe**: "last 2 years", "1 hour", "daily"
- **Risk**: "1% risk", "2% per trade"
- **Quantity**: "50 lots", "100 shares"

---

## Telegram Bot

### Setup
1. Create bot via @BotFather
2. Set bot token in `configs/system_config.yaml`
3. Start bot service from desktop app

### Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message and setup |
| `/analyze <symbol>` | Run market analysis |
| `/backtest <symbol> <period>` | Run backtest |
| `/trade <symbol> <action>` | Execute trade |
| `/portfolio` | Show portfolio summary |
| `/status` | System and agent status |
| `/stop` | Stop all active trades |
| `/report` | Generate performance report |

### Example Conversation

```
User: /analyze NIFTY
Bot:  📊 NIFTY Market Analysis
      ─────────────────────
      Trend: 🟢 Bullish
      Regime: Trending
      Volatility: Moderate
      Support: 22,100 | 22,000
      Resistance: 22,400 | 22,500
      
      💡 Suggested: Breakout pullback strategy
      Type /backtest NIFTY 2y to validate

User: /backtest NIFTY 2y
Bot:  📈 Backtest Results
      ─────────────────────
      Win Rate: 63.2%
      Sharpe: 1.85
      Max DD: 8.3%
      Profit Factor: 1.72
      Net Profit: ₹1,95,000
      
      ✅ Approve with /trade NIFTY execute 1%

User: /trade NIFTY execute 1%
Bot:  ⚡ Trade Executed
      Symbol: NIFTY
      Side: BUY
      Risk: 1%
      Mode: Paper
      Order ID: ORD_001
```

---

## WhatsApp Integration

### Technology
- **Library**: Baileys (preferred) or whatsapp-web.js
- **Auth**: QR code scanning (NO official Business API)
- **Runtime**: Node.js subprocess managed by Electron

### Connection Flow

```
1. User opens desktop app → Settings → WhatsApp
2. App generates QR code via Baileys
3. User scans QR from WhatsApp mobile
4. Session authenticates and persists
5. Messages stream bidirectionally
```

### Features
- QR authentication
- Session persistence (survives app restart)
- Auto-reconnect on disconnect
- Message listener (text + voice)
- Send/receive messages
- Media handling (images for charts)

### Voice Message Support

```
Voice Message (OGG/Opus)
    → FFmpeg conversion
    → Whisper STT (speech-to-text)
    → Text command
    → Command Parser
    → AI Agents
    → Text response to WhatsApp
```

### Example Flow

```
User: "Analyze NIFTY"
Bot:  "📊 Market regime: bullish
       Suggested strategy: breakout pullback"

User: "Backtest last 2 years"
Bot:  "📈 Win rate: 63%
       Profit factor: 1.7
       Max drawdown: 8%"

User: "Execute with 1% risk"
Bot:  "⚡ Trade executed. Order ID: ORD_001
       Mode: Paper Trading"
```

---

## Message Queue

### Redis Streams

```python
# Producer (Telegram/WhatsApp → Queue)
await redis.xadd("messages", {
    "source": "telegram",
    "user_id": "123",
    "content": "Analyze NIFTY",
    "timestamp": "2025-01-01T10:00:00"
})

# Consumer (Queue → Agent Orchestrator)
messages = await redis.xread({"messages": "$"}, block=5000)
```

### Purpose
- Buffer incoming messages during high load
- Enable parallel processing of multi-user requests
- Decouple communication channels from AI processing
- Provide audit trail of all interactions

---

## Notification System

### Alert Types

| Alert | Channels | Priority |
|-------|----------|----------|
| Trade Executed | Desktop, Telegram, WhatsApp | High |
| Stop-Loss Hit | Desktop, Telegram, WhatsApp | Critical |
| Target Hit | Desktop, Telegram, WhatsApp | High |
| Daily Performance | Telegram, WhatsApp | Medium |
| System Error | Desktop | Critical |
| Agent Activity | Desktop | Low |

### Alert Manager

```python
class AlertManager:
    async def send_alert(self, alert: Alert):
        for channel in alert.channels:
            if channel == "desktop":
                await self.desktop_notify(alert)
            elif channel == "telegram":
                await self.telegram_notify(alert)
            elif channel == "whatsapp":
                await self.whatsapp_notify(alert)
```
