# QUANT AI LAB — Backtesting Engine Documentation

## Overview

The Backtesting Engine validates AI-discovered strategies against historical market data using VectorBT for high-performance vectorized simulation.

---

## Architecture

```
Strategy Rules (from Strategy Discovery Agent)
    │
    ▼
Historical Data Loader (data_engine)
    │
    ▼
Signal Generation (apply entry/exit rules)
    │
    ▼
VectorBT Simulator (simulate trades)
    │
    ▼
Performance Metrics Calculator
    │
    ▼
Portfolio Simulator (track equity)
    │
    ▼
Report Generator (charts + data)
```

---

## Components

### 1. Simulator (`simulator.py`)

VectorBT-powered backtesting simulator.

**Input:**
```
{
  "strategy": {
    "entry_rules": [...],
    "exit_rules": [...],
    "indicators": [...]
  },
  "symbol": "NIFTY",
  "timeframe": "1h",
  "start_date": "2024-01-01",
  "end_date": "2025-12-31",
  "initial_capital": 1000000,
  "risk_per_trade": 0.01,
  "commission": 20,
  "slippage_pct": 0.05
}
```

**Process:**
1. Load historical OHLCV data for symbol + timeframe
2. Compute required technical indicators
3. Generate entry signals (boolean array)
4. Generate exit signals (boolean array)
5. Run VectorBT portfolio simulation
6. Apply commission and slippage
7. Generate trade log and equity curve

**Execution Assumptions:**
- Entry on next bar's open after signal bar closes
- Exit on next bar's open after exit signal
- Slippage applied to both entry and exit
- Commission deducted per trade (round-trip)

---

### 2. Performance Metrics (`performance_metrics.py`)

**Computed Metrics:**

| Metric | Formula | Description |
|--------|---------|-------------|
| Win Rate | wins / total_trades × 100 | Percentage of profitable trades |
| Sharpe Ratio | (mean_return - risk_free) / std_return × √252 | Risk-adjusted return (annualized) |
| Sortino Ratio | (mean_return - risk_free) / downside_std × √252 | Downside risk-adjusted return |
| Calmar Ratio | annual_return / max_drawdown | Return per unit max DD |
| Max Drawdown | max(peak - trough) / peak × 100 | Largest peak-to-trough decline |
| Profit Factor | gross_profit / gross_loss | Profit per unit loss |
| Expectancy | (win_rate × avg_win) - (loss_rate × avg_loss) | Expected profit per trade |
| Avg Trade Duration | mean(trade_end - trade_start) | Average holding period |
| Max Consecutive Wins | longest winning streak | Streak analysis |
| Max Consecutive Losses | longest losing streak | Streak analysis |
| Recovery Factor | net_profit / max_drawdown | Capital recovery efficiency |
| Payoff Ratio | avg_win / avg_loss | Win size vs loss size |

**Monthly Breakdown:**
- Monthly returns table (Jan-Dec × Year)
- Best month, worst month
- Percentage of profitable months

---

### 3. Portfolio Simulator (`portfolio_simulator.py`)

Virtual portfolio that tracks equity throughout the backtest.

**Tracking:**
- Cash balance
- Open positions (symbol, qty, avg_price, current_price, pnl)
- Equity curve (timestamp → portfolio_value)
- Drawdown curve (timestamp → drawdown_pct)
- Trade log (entry_time, exit_time, entry_price, exit_price, pnl, pnl_pct)

**Position Sizing Modes:**
| Mode | Description |
|------|-------------|
| Fixed Quantity | Same lots per trade |
| Fixed Fraction | X% of capital per trade |
| Kelly Criterion | Optimal f based on edge |
| Risk-Based | Fixed risk amount (e.g., risk ₹10,000 per trade) |

---

### 4. Report Generator (`report_generator.py`)

Generates comprehensive backtest reports.

**Output Formats:**
- **JSON**: Raw metrics and trade data (consumed by API/UI)
- **HTML**: Rendered report with embedded Plotly charts
- **CSV**: Trade log export

**Report Contents:**

#### Summary Section
- Strategy name and description
- Symbol, timeframe, date range
- Initial capital and risk settings

#### Metrics Section
- All performance metrics in table format
- Comparison to benchmark (buy-and-hold NIFTY)

#### Charts Section (Plotly)
1. **Equity Curve**: Portfolio value over time vs benchmark
2. **Drawdown Chart**: Underwater equity chart
3. **Monthly Returns Heatmap**: Color-coded monthly returns
4. **Trade Distribution**: Histogram of trade P&L
5. **Win/Loss Streak**: Bar chart of consecutive wins/losses
6. **Rolling Sharpe**: 90-day rolling Sharpe ratio

#### Trade Log Section
- Full table of all trades with entry/exit details
- Filterable by profitable/losing, date range
- Sortable by P&L, duration, size

---

## Walk-Forward Analysis

Optional advanced validation:

```
Full Period: [────────────────────────────────────]
Window 1:   [██████ Train ██] [█ Test █]
Window 2:        [██████ Train ██] [█ Test █]
Window 3:             [██████ Train ██] [█ Test █]
```

- Trains strategy on in-sample window
- Tests on out-of-sample window
- Slides forward and repeats
- Reports aggregate OOS performance
- Detects overfitting

---

## Multi-Symbol & Multi-Timeframe

The backtesting engine supports:
- **Multi-symbol**: Test same strategy across NIFTY, BANKNIFTY, FINNIFTY, individual stocks
- **Multi-timeframe**: Test on 1m, 5m, 15m, 1h, 4h, 1D
- **Comparison**: Side-by-side metrics across symbols/timeframes
