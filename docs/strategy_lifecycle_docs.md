# QUANT AI LAB — Strategy Lifecycle & Workflow Documentation

## Overview

Every trading strategy in Quant AI Lab follows a fully autonomous AI-driven lifecycle — from market analysis through execution. There is **NO manual strategy builder**. All strategies are discovered, validated, and managed by AI agents.

---

## Strategy Lifecycle

```
┌──────────────┐
│ Market Data  │ ← Data Engine fetches live/historical data
└──────┬───────┘
       │
       ▼
┌──────────────────────┐
│ AI Market Analysis   │ ← Market Analysis Agent: trend, regime, volatility, levels
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Strategy Discovery   │ ← Strategy Discovery Agent: AI creates strategy rules
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Backtesting          │ ← Backtesting Agent: validate on historical data
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Risk Analysis        │ ← Risk Management Agent: position sizing, risk checks
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ User Approval        │ ← Desktop / Telegram / WhatsApp notification
│ ✅ Approve           │    User reviews metrics and approves or rejects
│ ❌ Reject            │
└──────┬───────────────┘
       │ (if approved)
       ▼
┌──────────────────────┐
│ Live Execution       │ ← Execution Agent: routes to broker/paper engine
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Monitoring           │ ← Monitoring Agent: track positions, trailing SL
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Reporting            │ ← Reporting Agent: daily/weekly performance reports
└──────────────────────┘
```

---

## Phase Details

### Phase 1: Market Data Collection
- Data Agent fetches current market data
- OHLCV candles loaded for required timeframes
- Real-time tick feed established
- Data cached in Redis for fast agent access

### Phase 2: Market Analysis
- Market Analysis Agent receives the data
- Computes technical indicators (EMA, RSI, MACD, BB, ATR, ADX)
- Detects current trend direction (bullish / bearish / sideways)
- Classifies market regime (trending / mean-reverting / volatile / quiet)
- Identifies key support/resistance zones
- Uses LLM for qualitative synthesispip

**Output Example:**
```json
{
  "symbol": "NIFTY",
  "trend": "bullish",
  "regime": "trending",
  "volatility": "moderate",
  "support": [22100, 22000, 21850],
  "resistance": [22400, 22500, 22650],
  "confidence": 0.78,
  "summary": "NIFTY is in a strong uptrend with moderate volatility..."
}
```

### Phase 3: Strategy Discovery
- Strategy Discovery Agent receives market analysis
- Uses LLM to reason about viable strategies for current conditions
- Generates indicator combinations (e.g., EMA crossover + RSI filter)
- Creates entry rules (e.g., "Buy when EMA9 > EMA21 AND RSI > 50")
- Creates exit rules (e.g., "Sell when RSI > 70 OR price < EMA21")
- Outputs complete strategy specification

**Output Example:**
```json
{
  "name": "Trend Following Breakout",
  "description": "Buys on EMA crossover with RSI momentum confirmation...",
  "entry_rules": [
    {"indicator": "EMA", "condition": "crossover", "params": {"fast": 9, "slow": 21}},
    {"indicator": "RSI", "condition": "above", "params": {"period": 14, "level": 50}}
  ],
  "exit_rules": [
    {"indicator": "RSI", "condition": "above", "params": {"period": 14, "level": 70}},
    {"type": "trailing_stop", "params": {"trail_pct": 1.5}}
  ],
  "timeframe": "1h",
  "instruments": ["NIFTY"]
}
```

### Phase 4: Backtesting
- Backtesting Agent receives strategy specification
- Loads historical data (default: 2 years)
- Runs VectorBT simulation with slippage and commission
- Computes performance metrics

**Validation Criteria:**
| Metric | Minimum Threshold |
|--------|-------------------|
| Win Rate | > 50% |
| Sharpe Ratio | > 1.0 |
| Max Drawdown | < 15% |
| Profit Factor | > 1.3 |
| Minimum Trades | > 30 |

Strategies below thresholds are auto-rejected. Above thresholds → sent for risk analysis.

### Phase 5: Risk Analysis
- Risk Management Agent evaluates the strategy
- Calculates optimal position size for configured risk %
- Validates against portfolio-level risk limits
- Checks correlation with existing active strategies
- Assigns risk score (1-10)

### Phase 6: User Approval
- Strategy card displayed in desktop UI (Strategy Lab)
- Notification sent to Telegram/WhatsApp:
  ```
  📊 New Strategy Discovered!
  Name: Trend Following Breakout
  Symbol: NIFTY | TF: 1h
  Win Rate: 63% | Sharpe: 1.85
  Max DD: 8% | PF: 1.72
  Risk Score: 4/10
  
  ✅ Reply APPROVE to deploy
  ❌ Reply REJECT to discard
  ```
- User must explicitly approve or reject
- Approval can be done from any channel

### Phase 7: Live Execution
- On approval, strategy status changes to `live`
- Execution Agent activates the strategy
- Entry signals from live data → order placement via broker gateway
- Mode: Paper (default) or Live (requires explicit setting)

### Phase 8: Monitoring
- Monitoring Agent watches all positions from the strategy
- Updates trailing stops in real-time
- Checks exit conditions every tick/bar
- Sends alerts on: entry filled, SL hit, TP hit

### Phase 9: Reporting
- Daily: P&L, number of trades, metrics update
- Weekly: Strategy performance summary
- On-demand: Full strategy report
- Reports available in desktop UI and sent via Telegram/WhatsApp

---

## Strategy Statuses

```
discovered → backtesting → backtested → risk_reviewed → pending_approval
    → approved → live → monitoring → completed
    → rejected (at any stage)
    → paused (manual pause)
    → stopped (kill switch)
```

---

## Auto-Optimization (Future)

The Strategy Discovery Agent can iteratively improve strategies:
1. Run initial backtest
2. Analyze weak periods
3. Adjust parameters
4. Re-backtest
5. Compare versions
6. Select best variant

This creates a feedback loop where strategies evolve over time based on performance data.
