# QUANT AI LAB — AI Agent Documentation

## Agent Orchestrator

The Agent Orchestrator is the central coordinator that manages all specialized agents. It receives user requests, determines which agents to invoke, manages multi-step workflows, and aggregates results.

### Workflow Engine
- **Sequential Workflows**: Tasks that require ordered agent execution (e.g., analyze → backtest → risk check → execute)
- **Parallel Workflows**: Independent tasks run simultaneously (e.g., analyze multiple symbols)
- **Conditional Workflows**: Branch based on agent output (e.g., skip execution if risk too high)

### Task Scheduler
- Priority queue for agent tasks
- Timeout handling for long-running operations
- Retry logic for transient failures

---

## Agent Specifications

### 1. Market Analysis Agent

**Purpose**: Analyze market conditions and provide actionable insights.

**Functions**:
| Function | Description | Output |
|----------|-------------|--------|
| `detect_trend()` | Identify current market trend | `bullish / bearish / sideways` |
| `identify_volatility()` | Measure and classify volatility | `low / moderate / high / extreme` |
| `detect_liquidity_zones()` | Find support/resistance zones | `List[price_level]` |
| `detect_market_regime()` | Classify market regime | `trending / mean_reverting / volatile / quiet` |

**Data Sources**: OHLCV data, technical indicators (EMA, RSI, MACD, BB, ATR, ADX)

**LLM Integration**: Uses LLM for qualitative analysis — interprets technical signals with market context.

---

### 2. Strategy Discovery Agent

**Purpose**: Automatically create and optimize trading strategies using AI.

**Functions**:
| Function | Description | Output |
|----------|-------------|--------|
| `auto_create_strategy()` | Generate new strategy from market analysis | `Strategy` object |
| `combine_indicators()` | Find optimal indicator combinations | `IndicatorSet` |
| `generate_entry_rules()` | Create entry conditions | `List[Rule]` |
| `generate_exit_rules()` | Create exit conditions | `List[Rule]` |

**Process**:
1. Receives market analysis from Market Analysis Agent
2. Uses LLM to reason about potential strategies
3. Generates strategy parameters
4. Sends to Backtesting Agent for validation

**No manual strategy builder** — all strategies are AI-discovered.

---

### 3. Backtesting Agent

**Purpose**: Run historical backtests on strategies using VectorBT.

**Engine**: VectorBT Pro (vectorized backtesting for speed)

**Metrics Computed**:
| Metric | Description |
|--------|-------------|
| Win Rate | Percentage of profitable trades |
| Sharpe Ratio | Risk-adjusted return measure |
| Max Drawdown | Largest peak-to-trough decline |
| Profit Factor | Gross profit / gross loss |
| Expectancy | Average expected profit per trade |
| Sortino Ratio | Downside risk-adjusted return |
| Calmar Ratio | Return / max drawdown |
| Total Trades | Number of trades executed |
| Avg Trade Duration | Mean holding period |

**Output**: Full backtest report with equity curve, trade log, and performance metrics.

---

### 4. Risk Management Agent

**Purpose**: Ensure all trades comply with risk parameters.

**Functions**:
| Function | Description |
|----------|-------------|
| `calculate_position_size()` | Optimal lot size based on risk % |
| `validate_risk()` | Check trade against risk limits |
| `check_daily_limits()` | Verify daily loss/trade limits |
| `allocate_capital()` | Distribute capital across strategies |

**Risk Parameters**:
- Max risk per trade: configurable (default 1%)
- Max daily loss: configurable (default 3%)
- Max concurrent positions: configurable
- Max drawdown kill switch: emergency stop at 10% portfolio DD

**Veto Power**: Can block any trade that violates risk parameters.

---

### 5. Execution Agent

**Purpose**: Route approved trades to the broker gateway.

**Functions**:
| Function | Description |
|----------|-------------|
| `execute_trade()` | Send order to broker |
| `route_order()` | Select optimal broker/mode |
| `confirm_execution()` | Verify order filled |

**Modes**: Live (real broker), Paper (simulated)

---

### 6. Portfolio Manager Agent

**Purpose**: Monitor and manage the overall portfolio.

**Functions**:
| Function | Description |
|----------|-------------|
| `get_portfolio_summary()` | Current holdings and P&L |
| `analyze_allocation()` | Asset allocation analysis |
| `suggest_rebalance()` | Rebalancing recommendations |
| `track_performance()` | Historical performance tracking |

---

### 7. Monitoring Agent

**Purpose**: Real-time monitoring of active trades.

**Functions**:
| Function | Description |
|----------|-------------|
| `monitor_positions()` | Watch all open positions |
| `update_trailing_stop()` | Adjust trailing SL dynamically |
| `check_exit_conditions()` | Evaluate exit triggers |
| `send_alert()` | Push alerts to all channels |

**Runs Continuously**: Background loop checking positions every N seconds.

---

### 8. Reporting Agent

**Purpose**: Generate performance reports.

**Reports**:
| Report | Frequency | Contents |
|--------|-----------|----------|
| Daily Report | End of day | P&L, trades, metrics |
| Weekly Report | End of week | Weekly summary, strategy performance |
| Strategy Comparison | On demand | Side-by-side strategy metrics |
| Risk Report | On demand | Exposure, drawdown, risk metrics |

**Output Format**: JSON data + rendered HTML/PDF via frontend.

---

### 9. Data Agent

**Purpose**: Fetch and preprocess market data for other agents.

**Functions**:
| Function | Description |
|----------|-------------|
| `fetch_live_data()` | Real-time market quotes |
| `fetch_historical()` | Historical OHLCV data |
| `compute_indicators()` | Calculate technical indicators |
| `prepare_features()` | Generate ML features |

---

## Agent Communication Flow

```
User Message
    │
    ▼
Command Parser (NLP intent detection)
    │
    ▼
Agent Orchestrator
    │
    ├──▶ Market Analysis Agent ──▶ Strategy Discovery Agent
    │                                    │
    │                                    ▼
    │                            Backtesting Agent
    │                                    │
    │                                    ▼
    │                            Risk Management Agent
    │                                    │
    │                              ┌─────┴─────┐
    │                              │ Approved?  │
    │                              └─────┬─────┘
    │                             Yes    │    No
    │                              │     │     │
    │                              ▼     │     ▼
    │                         Execution  │  Reject
    │                           Agent    │
    │                              │     │
    ├──▶ Monitoring Agent ◀────────┘     │
    ├──▶ Portfolio Agent                 │
    ├──▶ Reporting Agent                 │
    └──▶ Data Agent                      │
         │
         ▼
    Response to User (Desktop / Telegram / WhatsApp)
```

## Memory System

### Vector Store
- ChromaDB or FAISS for semantic search
- Stores agent observations, market analysis, strategy results

### Strategy Memory
- SQLite-backed storage for all discovered strategies
- Performance history and parameter evolution

### Conversation Memory
- Chat history with context windowing
- Per-user memory isolation
