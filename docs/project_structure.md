# QUANT AI LAB — Project Structure Documentation

## Root Directory: `quant-ai-lab/`

Complete directory-by-directory and file-by-file explanation.

---

## `desktop_app/` — Electron Desktop Application

### `electron_main/` — Electron Main Process
| File | Description |
|------|-------------|
| `main.ts` | Electron app entry point. On launch, checks for existing valid session. If no session → shows Login Popup. If session valid → shows main window. Spawns the Python backend as a child process, manages app lifecycle (ready, activate, close), handles auto-updates. |
| `window_manager.ts` | Manages all windows: **Login Popup** (frameless 450×550px, "Continue with Google" button), **main app window** (full-size), settings popup, QR scanner. Handles window state persistence (size, position), tray icon, and minimize-to-tray. |
| `ipc_router.ts` | Routes IPC messages between the renderer process and the backend. Maps frontend API calls to HTTP/WebSocket requests against the FastAPI backend. Handles bi-directional data flow. |
| `auth_handler.ts` | Google OAuth 2.0 flow handler. On "Continue with Google" click: generates OAuth URL with PKCE, starts local HTTP server on port 5789, opens system browser for Google sign-in, catches redirect callback, exchanges auth code for tokens (access_token, refresh_token, id_token), decodes user profile, stores tokens in Electron `safeStorage` (OS-level encryption), signals window_manager to close popup and show main window. Handles auto-refresh of tokens before expiry. |

### `ui/` — Page-Level UI Components (React/Next.js)

| Directory | Description |
|-----------|-------------|
| `dashboard/` | Main dashboard page: portfolio overview KPIs (total P&L, win rate, capital deployed), mini equity curve chart, active positions summary, market status tiles (NIFTY/BANKNIFTY/FINNIFTY live prices), and recent agent activity feed. |
| `charts/` | Plotly.js chart components: candlestick charts with indicator overlays, equity curve, drawdown chart, portfolio allocation pie, daily P&L bar chart, heatmaps. All charts use dark theme with trading-specific color schemes. |
| `agents/` | Agent interaction pages: AI Chat Terminal (streaming chat with agent selector), Agent Builder (create custom agents with template selection, prompt editor, tool assignment), agent status monitor. |
| `broker_accounts/` | Broker management UI: connect/disconnect brokers, credential entry forms (encrypted on save), connection status indicators, broker selection dropdown, login flow with TOTP support. |
| `strategy_results/` | Strategy Lab page: list of AI-discovered strategies with performance metrics, strategy detail view (entry/exit rules, indicators, parameters), approve/reject workflow, strategy comparison table. |
| `settings/` | Settings pages: LLM provider configuration (OpenAI/Anthropic/Ollama with API key or OAuth), risk parameters form, notification preferences, WhatsApp QR scanner, Telegram bot token, theme toggle. |

### `components/` — Reusable Shared Components

| Directory | Description |
|-----------|-------------|
| `chat_terminal/` | Streaming AI chat widget. Features: agent context selector, message history with markdown rendering, code block display, data table rendering, voice input button, loading indicators, copy-to-clipboard. |
| `trade_panel/` | Order entry panel: symbol search, order type selector (Market/Limit/SL/TP), quantity input, price input, broker selector, paper/live mode toggle, submit button with confirmation dialog. |
| `backtest_view/` | Backtesting results viewer: metrics cards (win rate, Sharpe, MDD, profit factor, expectancy), Plotly equity curve, drawdown chart, trade log table with filters, export buttons. |
| `logs_view/` | System log viewer: real-time log streaming, filter by level (INFO/WARN/ERROR), filter by source (agent/broker/system), search, timestamp display, auto-scroll toggle. |

---

## `backend/` — Python FastAPI Backend

### `api_server/` — HTTP & WebSocket Server

| File | Description |
|------|-------------|
| `main.py` | FastAPI application factory. Configures CORS, mounts routers, initializes database, sets up lifespan events (startup: connect to DB/Redis, shutdown: cleanup). Launches uvicorn server on configured port. |
| `router.py` | Central router that registers all API route modules: `/api/v1/health`, `/api/v1/agents/*`, `/api/v1/market/*`, `/api/v1/trades/*`, `/api/v1/portfolio/*`, `/api/v1/backtest/*`, `/api/v1/broker/*`, `/api/v1/ml/*`, `/api/v1/plugins/*`. |
| `websocket_server.py` | WebSocket endpoint manager. Handles three WS channels: `/ws/market` (real-time price ticks), `/ws/agent` (streaming agent responses), `/ws/trades` (order updates and alerts). Manages connection lifecycle and heartbeat. |
| `middleware/` | Custom middleware: request logging (every request with timing), CORS configuration, rate limiting (per-IP), authentication (JWT verification), error handler (standardized error responses). |

### `broker_gateway/` — Unified Broker Interface

| File/Directory | Description |
|----------------|-------------|
| `broker_manager.py` | Central broker manager: registers broker adapters, handles broker selection, manages connection pool, credential loading (decrypted from config), automatic reconnection on failure, failover logic. |
| `angelone/` | Angel One SmartAPI adapter. Implements `BrokerBase` using `smartapi-python`. Handles: API login with TOTP, order placement/modification/cancellation, position/holding/fund fetching, historical data download, live quote streaming. |
| `zerodha/` | Zerodha KiteConnect adapter. Implements `BrokerBase` using `kiteconnect`. Handles: API key + request token login, Kite Ticker WebSocket for live data, full order management, GTT orders. |
| `dhan/` | Dhan API adapter. Implements `BrokerBase` using `dhanhq`. Handles: token-based auth, order placement, position tracking, intraday/delivery mode. |
| `fyers/` | Fyers API v3 adapter. Implements `BrokerBase` using `fyers-apiv3`. Handles: OAuth-based login, order management, data API for historical/live data. |

### `order_engine/` — Order Execution Engine

| File | Description |
|------|-------------|
| `execution_engine.py` | Core order executor. Receives validated orders from the Execution Agent, routes to the active broker adapter (or paper engine), manages order lifecycle (placed → open → partial → filled/cancelled/rejected), raises events for the monitoring system. |
| `risk_engine.py` | Pre-trade risk checks. Validates: max risk per trade, daily loss limit, max concurrent positions, capital availability, kill switch status. Blocks orders that violate risk parameters with detailed rejection reason. |
| `sl_tp_manager.py` | Stop-loss and take-profit manager. Handles: fixed SL/TP placement, trailing stop logic (percentage-based and ATR-based), bracket order simulation, SL modification on partial fills, TP ladder (multiple targets). |
| `order_router.py` | Intelligent order routing. Determines: which broker to use (based on config or best execution), paper vs live mode, order splitting for large quantities, retry logic for transient failures. |

### `data_engine/` — Market Data Engine

| File | Description |
|------|-------------|
| `market_stream.py` | Real-time market data streaming. Connects to broker WebSocket feeds, normalizes tick data across brokers (unified format), publishes to internal event bus and Redis cache, handles reconnection and data gaps. |
| `historical_loader.py` | Historical data fetcher. Downloads OHLCV data from broker APIs, supports multiple timeframes (1m, 5m, 15m, 1h, 1D), handles pagination for large date ranges, caches to SQLite for re-use. |
| `tick_storage.py` | Tick data persistence. Stores raw tick data to SQLite with efficient compression, supports replay for backtesting, handles data cleanup (rolling window), aggregates ticks to OHLCV candles. |
| `data_cache.py` | Redis-backed data cache. Caches: live quotes (TTL 1s), OHLCV data (TTL varies by timeframe), technical indicators (computed on demand), reduces broker API calls through intelligent cache invalidation. |

### `backtesting_engine/` — Backtesting Framework

| File | Description |
|------|-------------|
| `simulator.py` | VectorBT-powered backtesting simulator. Accepts strategy rules (entry/exit signals), runs against historical data, simulates order execution with configurable slippage and commission, produces trade log and equity curve. |
| `performance_metrics.py` | Compute all backtest metrics: win rate, Sharpe ratio, Sortino ratio, Calmar ratio, max drawdown, profit factor, expectancy, average trade duration, max consecutive wins/losses, monthly returns breakdown. |
| `portfolio_simulator.py` | Virtual portfolio for backtesting. Tracks: cash, positions, margin, P&L, equity curve. Simulates: order fills, partial fills, margin requirements, corporate actions. |
| `report_generator.py` | Generates backtest reports. Outputs: JSON metrics, HTML report with Plotly charts (equity curve, drawdown, monthly returns), trade log CSV, strategy summary. |

---

## `ai_core/` — AI Intelligence Layer

### `agent_orchestrator/` — Central Agent Coordination

| File | Description |
|------|-------------|
| `orchestrator.py` | Master orchestrator. Receives user tasks, determines agent routing (single-agent or multi-agent workflow), manages agent communication, aggregates results, handles errors and fallbacks. Uses LangGraph-inspired state machine for complex workflows. |
| `workflow_engine.py` | Defines and executes multi-step workflows. Example: `analyze → discover_strategy → backtest → risk_check → (approve/reject) → execute`. Supports: sequential, parallel, and conditional branching. Persists workflow state for resume. |
| `task_scheduler.py` | Queues and schedules agent tasks. Features: priority queue (critical trades before reports), timeout management, retry logic, concurrent task limiting, dead-letter queue for failed tasks. |

### `agents/` — Specialized AI Agents

| Directory | Description |
|-----------|-------------|
| `strategy_agent/` | **Strategy Discovery Agent**. AI-driven strategy creation: analyzes market conditions (from Market Analysis Agent), uses LLM to reason about viable strategies, generates indicator combinations, creates entry/exit rules, outputs complete `Strategy` objects. No manual strategy building — everything is AI-discovered. |
| `market_analysis_agent/` | **Market Analysis Agent**. Functions: `detect_trend()` (EMA crossovers, ADX), `identify_volatility()` (ATR-based classification), `detect_liquidity_zones()` (volume profile support/resistance), `detect_market_regime()` (trending/mean-reverting/volatile/quiet). Uses LLM for qualitative synthesis. |
| `risk_agent/` | **Risk Management Agent**. Functions: `calculate_position_size()` (Kelly criterion / fixed percent), `validate_risk()` (pre-trade checks), `check_daily_limits()` (loss/trade count limits), `allocate_capital()` (across strategies). Has veto power to block risky trades. |
| `portfolio_agent/` | **Portfolio Manager Agent**. Functions: `get_portfolio_summary()`, `analyze_allocation()`, `suggest_rebalance()`, `track_performance()`. Monitors overall portfolio health, generates rebalancing alerts, tracks NAV over time. |
| `execution_agent/` | **Execution Agent**. Bridges AI decisions to broker gateway. Functions: `execute_trade()` (route to broker), `confirm_execution()` (verify fill), `handle_rejection()` (retry or escalate). Supports paper and live modes. |
| `monitoring_agent/` | **Monitoring Agent**. Runs as background loop. Functions: `monitor_positions()` (watch all open trades), `update_trailing_stop()` (dynamic SL adjustment), `check_exit_conditions()` (time-based, indicator-based exits), `send_alert()` (push to all channels). |
| `reporting_agent/` | **Reporting Agent**. Generates: daily performance summary (P&L, trades, metrics), weekly roll-up report, strategy comparison report, risk exposure report. Outputs JSON data consumed by desktop UI or sent via Telegram/WhatsApp. |

### `ml_models/` — Machine Learning Models

| Directory | Description |
|-----------|-------------|
| `auto_trend_model/` | Trend prediction using XGBoost/LightGBM ensemble. Features: price momentum, technical indicators, volume metrics. Target: next-bar direction. Retrained daily. Outputs: directional signal + confidence score. |
| `regime_detection/` | Market regime classifier. Uses Hidden Markov Model + K-Means clustering. Identifies 4 regimes: Trending, Mean-Reverting, High-Volatility, Low-Volatility. Output: current regime label + transition probability matrix. |
| `volatility_model/` | Volatility forecasting. GARCH model + LightGBM hybrid. Predicts realized volatility for next N bars. Used by: Risk Agent (position sizing), Strategy Agent (strategy selection), SL/TP Manager (dynamic levels). |
| `feature_engineering/` | Feature engineering pipeline. Generates 60+ features from raw OHLCV: price returns (1/5/10/20 bar), technical indicators (EMA, RSI, MACD, BB, ATR, ADX), volume features (OBV, volume ratio), statistical features (z-score, rolling stats, Hurst exponent), time features (hour, day, session). |

### `llm_connectors/` — LLM Provider Integrations

| File | Description |
|------|-------------|
| `openai_connector.py` | OpenAI GPT-4 integration. Supports: API key auth, OAuth login. Unified interface methods: `generate_text()`, `analyze_market()`, `build_strategy()`, `reason_about_trades()`. Handles streaming responses, retries, rate limits. |
| `anthropic_connector.py` | Anthropic Claude integration. Same unified interface. Claude-specific: longer context window, system prompts for trading persona. Supports API key and OAuth. |
| `local_llm_connector.py` | Ollama local LLM integration. Connects to local Ollama server. Supports models: Mistral, Llama, CodeLlama. Zero API cost, full privacy. Same unified interface. Handles model pulling, warm-up, and timeout. |
| `oauth_handler.py` | OAuth 2.0 flow handler for OpenAI and Anthropic. Manages: authorization URL generation, callback handling, token exchange, token refresh, secure token storage. |

### `memory/` — Agent Memory System

| Directory | Description |
|-----------|-------------|
| `vector_store/` | ChromaDB/FAISS vector database wrapper. Stores embeddings of: market analysis results, strategy descriptions, conversation history. Enables semantic search for agent context retrieval. Uses `sentence-transformers` for embedding generation. |
| `strategy_memory/` | SQLite-backed strategy persistence. Stores: all discovered strategies with parameters, backtest results history, approval/rejection status, performance tracking over time. Enables strategy evolution (learn from past results). |
| `conversation_memory/` | Chat history management. Features: per-user conversation isolation, context window management (last N messages), summary generation for long conversations, cross-channel memory (desktop → Telegram → WhatsApp share same context). |

---

## `communication_layer/` — External Communication

### `telegram_bot/` — Telegram Integration

| File | Description |
|------|-------------|
| `bot_handler.py` | Telegram bot main handler using `python-telegram-bot`. Registers command handlers, message handlers, and callback query handlers. Manages bot lifecycle, polling/webhook mode, authorized user validation. |
| `command_parser.py` | Parses Telegram commands and natural language messages. Maps: `/analyze NIFTY` → market_analysis intent, `/backtest NIFTY 2y` → backtest_request intent. Also handles free-text messages by detecting intent with keyword matching + LLM fallback. |

### `whatsapp_bot/` — WhatsApp Web Integration

| File | Description |
|------|-------------|
| `webhook_handler.py` | WhatsApp Web connection via Baileys (Node.js subprocess). Handles: QR code generation and display, session authentication, session persistence across app restarts, auto-reconnect on disconnect, incoming message listener (text + voice), outgoing message sender. Voice messages are transcribed via Whisper STT. |
| `message_router.py` | Routes incoming WhatsApp messages to the command parser and agent orchestrator. Handles: text message parsing, voice message transcription pipeline (OGG → FFmpeg → Whisper → text), media message handling (chart image sending), response formatting for WhatsApp (emoji, line breaks). |

### `notification_system/` — Multi-Channel Alerts

| File | Description |
|------|-------------|
| `alert_manager.py` | Central alert dispatcher. Receives alerts from agents (trade executed, SL hit, target hit, daily report). Routes to configured channels (desktop notification, Telegram message, WhatsApp message). Supports: priority levels, quiet hours, batching. |
| `trade_updates.py` | Real-time trade update formatter. Generates formatted alert messages for: order placed, order filled, position opened, SL triggered, TP hit, daily P&L summary. Includes relevant data (price, quantity, P&L) in each alert. |

---

## `plugin_system/` — Extensibility Framework

| File/Directory | Description |
|----------------|-------------|
| `plugin_manager.py` | Plugin lifecycle manager. Functions: `install(plugin_name)`, `load(plugin_name)`, `execute(plugin_name, params)`, `unload(plugin_name)`, `uninstall(plugin_name)`, `list_plugins()`. Handles dependency resolution and version checking. |
| `skill_registry.py` | Skill registration system. Agents register callable skills (e.g., `analyze_sentiment`, `fetch_options_chain`). Skills are discoverable by other agents. Registry stores: skill name, description, input/output schema, owning agent/plugin. |
| `agent_templates/` | Base templates for building custom agents. Provides: `BasePlugin` class (must implement `initialize`, `execute`, `shutdown`), example templates with documentation, configuration schema. |
| `marketplace/` | Plugin discovery and distribution. Contains: `registry.json` with available plugins metadata, download/install mechanics, version management, plugin configuration UI integration. |

---

## `database/` — Data Persistence

| Directory | Description |
|-----------|-------------|
| `models/` | SQLAlchemy ORM models: `Trade`, `Order`, `Strategy`, `BacktestResult`, `Portfolio`, `MLModel`, `Conversation`, `Alert`, `Plugin`. Each model includes relationships, validators, and serialization methods. |
| `migrations/` | Alembic migration scripts for schema versioning. Auto-generated from model changes. Supports: upgrade, downgrade, and stamping for fresh installs. |
| `repositories/` | Data access layer. One repository per model: `TradeRepository`, `StrategyRepository`, etc. CRUD operations with filtering, pagination, and aggregation queries. Async-first using `aiosqlite`. |

---

## `configs/` — Configuration Files

| File | Description |
|------|-------------|
| `broker_config.yaml` | Broker credentials and settings. All secrets are encrypted at rest with Fernet. Keys: API keys, client IDs, passwords, TOTP secrets for each broker. Paper trading capital and slippage settings. |
| `ai_config.yaml` | LLM provider selection and settings. Keys: active provider (openai/anthropic/ollama), API keys, model names, temperature, max tokens. Agent enable/disable flags. Vector store config. |
| `system_config.yaml` | App-wide settings. Keys: server host/port, database path, Redis connection, risk parameters (max risk, daily loss limit, kill switch threshold), Telegram/WhatsApp enable flags, alert channel preferences. |

---

## `logs/` — Runtime Logs

Application logs stored with daily rotation:
- `system.log` — Application lifecycle, errors, startup/shutdown
- `agent.log` — Agent activity, decisions, reasoning traces
- `trade.log` — Order placement, execution, fills, rejections
- `api.log` — HTTP request/response logs with timing

Uses `loguru` for structured logging with JSON output option.

---

## `tests/` — Test Suite

| Area | Tests |
|------|-------|
| API | Route handlers, request validation, response formats |
| Agents | Agent initialization, task processing, response quality |
| Broker | Mock broker connections, order placement, error handling |
| Backtesting | Metric computation, simulator accuracy, edge cases |
| ML | Feature generation, model training, prediction accuracy |
| Communication | Command parsing, intent detection, message formatting |
| Database | CRUD operations, migrations, query performance |
| Integration | End-to-end flows: chat → agent → backtest → report |
