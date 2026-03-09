# QUANT AI LAB — Order Engine Documentation

## Overview

The Order Engine handles the complete lifecycle of trade orders — from validation and risk checks through execution, stop-loss/take-profit management, and monitoring.

---

## Components

### 1. Execution Engine (`execution_engine.py`)

The core order executor that processes trade requests from AI agents.

**Order Lifecycle:**
```
Order Created → Risk Validation → Broker Routing → Placed 
    → Open → Partial Fill → Filled / Cancelled / Rejected
```

**Supported Order Types:**

| Type | Description | Parameters |
|------|-------------|------------|
| `MARKET` | Execute immediately at best available price | symbol, side, quantity |
| `LIMIT` | Execute at specified price or better | symbol, side, quantity, price |
| `SL` | Stop-loss — triggers limit order at stop price | symbol, side, quantity, trigger_price, price |
| `SL-M` | Stop-loss market — triggers market order at stop | symbol, side, quantity, trigger_price |
| `TP` | Take-profit — exit at target price | symbol, side, quantity, target_price |
| `TRAILING` | Trailing stop — dynamic SL that follows price | symbol, side, quantity, trail_points/trail_pct |

**Order Sides:**
- `BUY` — Long entry or short cover
- `SELL` — Short entry or long exit

**Order Products:**
- `INTRADAY` (MIS) — Squared off same day
- `DELIVERY` (CNC) — Held overnight
- `MARGIN` — Futures & Options

---

### 2. Risk Engine (`risk_engine.py`)

Pre-trade validation layer that every order passes through.

**Risk Checks:**

| Check | Description | Default Limit |
|-------|-------------|---------------|
| Max Risk Per Trade | Position size × SL distance ≤ X% of capital | 1% |
| Max Daily Loss | Total day's losses ≤ X% of capital | 3% |
| Max Concurrent Positions | Number of open positions ≤ N | 5 |
| Capital Availability | Sufficient funds for margin/premium | Based on funds |
| Kill Switch | Emergency stop — blocks ALL orders | 10% portfolio DD |
| Order Size Limit | Maximum quantity per order | Configurable |
| Symbol Restrictions | Optional allowed/blocked symbol list | None |

**Risk Validation Flow:**
```
Order Request
    │
    ├─ Check kill switch → BLOCK if active
    ├─ Check daily loss limit → BLOCK if exceeded
    ├─ Check max positions → BLOCK if full
    ├─ Check capital availability → BLOCK if insufficient
    ├─ Check position size risk → BLOCK if too large
    │
    └─ PASS → Forward to Execution Engine
```

**Kill Switch:**
- Activates automatically if portfolio drawdown exceeds threshold (default 10%)
- Cancels all pending orders
- Blocks all new orders
- Requires manual reset from Settings page

---

### 3. SL/TP Manager (`sl_tp_manager.py`)

Manages stop-loss and take-profit levels for active positions.

**Stop-Loss Types:**

| Type | Description |
|------|-------------|
| Fixed SL | Set at specific price, does NOT move |
| Percentage SL | Set at X% below entry price |
| ATR-based SL | Set at N × ATR below entry price |
| Trailing Stop (Points) | Follows price by fixed point distance |
| Trailing Stop (Percentage) | Follows price by percentage distance |
| Trailing Stop (ATR) | Follows price by N × ATR distance |

**Take-Profit Types:**

| Type | Description |
|------|-------------|
| Fixed TP | Single target price |
| Risk:Reward TP | Set at N × risk distance from entry |
| Ladder TP | Multiple targets (e.g., exit 50% at TP1, 50% at TP2) |
| Trailing TP | Lock in profits with trailing mechanism |

**Trailing Stop Logic:**
```
On every tick:
    if price moves in favorable direction:
        new_sl = price - trail_distance
        if new_sl > current_sl:
            update SL to new_sl
    if price hits SL:
        trigger exit order
```

---

### 4. Order Router (`order_router.py`)

Determines how and where to send each order.

**Routing Logic:**
1. Check trading mode (paper vs live)
2. If paper → route to Paper Trading Engine
3. If live → select active broker
4. Apply order splitting if quantity exceeds broker limits
5. Submit order with retry logic (max 3 attempts)
6. Log order and publish event

**Failover:**
- If primary broker fails, attempt secondary broker (if configured)
- If all brokers fail, fallback to paper mode with alert

---

## Paper Trading Engine

Full simulation engine for risk-free strategy testing.

**Features:**
- Virtual order execution with realistic slippage model
- Simulated order book with configurable spread
- Commission calculation
- Margin requirements simulation
- Portfolio tracking with daily MTM
- Identical API to live trading (seamless mode switching)

**Slippage Model:**
```
executed_price = order_price ± (order_price × slippage_pct)
# Default slippage: 0.05% for liquid instruments
```

---

## Event System

The order engine publishes events for downstream consumption:

| Event | Trigger | Consumers |
|-------|---------|-----------|
| `order.placed` | Order submitted | Monitoring Agent, UI |
| `order.filled` | Order fully executed | Portfolio Agent, Alert Manager |
| `order.partial` | Partial fill received | Monitoring Agent |
| `order.cancelled` | Order cancelled | UI, Reporting Agent |
| `order.rejected` | Order rejected by broker OR risk engine | UI, Alert Manager |
| `sl.triggered` | Stop-loss hit | Alert Manager, Reporting Agent |
| `tp.triggered` | Take-profit hit | Alert Manager, Reporting Agent |
| `trailing.updated` | Trailing stop moved | Monitoring Agent |
| `kill_switch.activated` | Portfolio DD exceeds threshold | ALL agents, Alert Manager |
