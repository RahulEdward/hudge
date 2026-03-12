# 🚀 Quant AI Lab

**AI-powered autonomous trading platform for Indian markets (NSE/BSE).**

Built with FastAPI, Electron, React/Next.js, and a multi-agent AI system powered by OpenAI, Anthropic Claude, or Ollama (local/free).

---

## ✨ Features

### 🤖 AI Engine
- **9 Specialized Agents** — Market Analysis, Strategy Discovery, Backtesting, Risk Management, Execution, Portfolio Manager, Monitoring, Reporting, Data
- **Agent Orchestrator** — Intent detection, task routing, conversation history, LLM fallback
- **Workflow Engine** — Sequential, parallel, and conditional multi-step agent workflows
- **Task Scheduler** — Priority queue with timeout, retry logic, and dead-letter handling
- **Memory System** — ChromaDB vector store, strategy memory, conversation memory

### 📊 ML Models
- **Trend Prediction** — XGBoost/Random Forest for next-bar direction
- **Regime Detection** — HMM-based market regime classification
- **Volatility Forecasting** — LightGBM hybrid for realized volatility prediction
- **Feature Engineering** — 60+ features from OHLCV (returns, EMAs, RSI, MACD, BB, ATR, volume, statistical)

### 🏦 Broker Gateway
| Broker | Status | Library |
|--------|--------|---------|
| Angel One | ✅ Full | `smartapi-python` |
| Zerodha | ✅ Full | `kiteconnect` |
| Dhan | ✅ Built | `dhanhq` |
| Fyers | ✅ Built | `fyers-apiv3` |
| Paper Trading | ✅ Built-in | Simulated execution |

### 📈 Trading & Backtesting
- **Order Engine** — Execution engine, risk engine, SL/TP manager, order router
- **Paper Trading** — Virtual execution with slippage and commission
- **Backtesting Engine** — Historical simulation with performance metrics
- **Portfolio Simulator** — Cash, positions, margin, P&L, equity curve tracking
- **Report Generator** — JSON metrics, trade summary, CSV export

### 💬 Communication
- **Desktop App** — Electron + React/Next.js with dark fintech UI
- **Telegram Bot** — Command handler with slash commands
- **WhatsApp Bot** — Baileys bridge with voice message transcription
- **Notification System** — Trade alerts, daily summaries, kill switch notifications
- **Command Parser** — NLP intent detection with entity extraction

### 🔌 Plugin System
- **Plugin Manager** — Install, configure, enable/disable plugins
- **Plugin Marketplace** — Browse, install, uninstall from registry
- **Skill Registry** — Agents register callable skills discoverable by other agents
- **Agent Templates** — Pre-built templates for custom agent creation

### 🖥️ Desktop App (12 Pages)
| Page | Description |
|------|-------------|
| Dashboard | System overview with key metrics |
| AI Chat | Conversational interface to all agents |
| Charts | Candlestick charts with indicators |
| Broker Accounts | Connect/disconnect brokers |
| Strategy Lab | Strategy management |
| Backtest Lab | Run and review backtests |
| Live Trading | Active order management |
| Portfolio | Holdings, positions, P&L |
| Agent Builder | Create custom agents with templates |
| Plugin Marketplace | Browse and install plugins |
| Settings | Configuration management |
| Logs | Real-time system logs |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Git

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
python run.py
```
Backend starts at **http://localhost:8000** (API docs at `/docs`)

### Frontend
```bash
cd desktop_app
npm install
npx next dev -p 3000
```
Frontend starts at **http://localhost:3000**

### Both Together
```bash
# Terminal 1
cd backend && venv\Scripts\python.exe run.py

# Terminal 2
cd desktop_app && npx next dev -p 3000
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Desktop App (Electron)                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐ │
│  │ Dashboard │  │ AI Chat  │  │ Charts   │  │Settings│ │
│  └──────────┘  └──────────┘  └──────────┘  └────────┘ │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐ │
│  │ Brokers  │  │Strategies│  │ Backtest │  │ Plugins│ │
│  └──────────┘  └──────────┘  └──────────┘  └────────┘ │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP + WebSocket
┌──────────────────────▼──────────────────────────────────┐
│                  Backend (FastAPI)                       │
│  ┌──────────────────────────────────────────────────┐   │
│  │  API Server (REST + WebSocket + Middleware)       │   │
│  │  Auth · Rate Limiter · Error Handler · CORS       │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐ │
│  │ AI Core  │  │  Order   │  │  Data    │  │ Plugin │ │
│  │ 9 Agents │  │  Engine  │  │  Engine  │  │ System │ │
│  │ ML Models│  │  Risk    │  │  Tick    │  │ Skills │ │
│  │ Memory   │  │  SL/TP   │  │  Storage │  │ Market │ │
│  │ Workflow │  │  Router  │  │  Cache   │  │ place  │ │
│  └──────────┘  └──────────┘  └──────────┘  └────────┘ │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐ │
│  │ Broker   │  │ Backtest │  │   Communication      │ │
│  │ Gateway  │  │ Engine   │  │ Telegram · WhatsApp  │ │
│  │ 4 Adapt. │  │ Simulate │  │ Alerts · Parser      │ │
│  └──────────┘  └──────────┘  └──────────────────────┘ │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Database: SQLite + Redis (optional) + ChromaDB   │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.10+, FastAPI, Uvicorn, SQLAlchemy, Alembic |
| **Frontend** | Electron, React, Next.js, TailwindCSS, ShadCN UI |
| **AI/ML** | XGBoost, LightGBM, Scikit-learn, HMM, Pandas, NumPy |
| **LLM** | OpenAI GPT, Anthropic Claude, Ollama (local) |
| **Database** | SQLite (local), PostgreSQL (optional), Redis, ChromaDB |
| **Brokers** | Angel One, Zerodha, Dhan, Fyers APIs |
| **Charts** | Plotly.js, Custom candlestick renderer |

---

## 📁 Project Structure

```
quant-lab/
├── backend/
│   ├── ai_core/
│   │   ├── agents/           # 9 specialized agents
│   │   ├── agent_orchestrator/ # orchestrator + workflow + scheduler
│   │   ├── llm_connectors/   # OpenAI, Anthropic, Ollama
│   │   ├── memory/           # vector_store, strategy, conversation
│   │   └── ml_models/        # trend, regime, volatility, features
│   ├── api_server/
│   │   ├── routes/           # 12 REST route files
│   │   ├── middleware/       # auth, rate_limiter, error_handler
│   │   └── websocket_server.py
│   ├── broker_gateway/       # angelone, zerodha, dhan, fyers, paper
│   ├── backtesting_engine/   # simulator, metrics, portfolio, reports
│   ├── communication_layer/  # telegram, whatsapp, alerts, parser
│   ├── data_engine/          # market_stream, historical, tick_storage
│   ├── database/             # models, repositories, connection
│   ├── order_engine/         # execution, risk, sl_tp, router
│   ├── plugin_system/        # plugins, skills, marketplace
│   └── run.py                # Entry point
├── desktop_app/
│   ├── electron_main/        # main.js, preload, ipc_router, auth
│   ├── src/
│   │   ├── app/              # Next.js root layout + page
│   │   ├── dashboard/        # Dashboard page
│   │   ├── agents/           # AI Chat page
│   │   ├── charts/           # Charts page
│   │   ├── broker_accounts/  # Broker Accounts page
│   │   ├── strategy_results/ # Strategy Lab page
│   │   ├── backtest_lab/     # Backtest page
│   │   ├── live_trading/     # Live Trading page
│   │   ├── portfolio/        # Portfolio page
│   │   ├── agent_builder/    # Agent Builder page
│   │   ├── plugin_marketplace/ # Plugin Marketplace page
│   │   ├── settings/         # Settings page
│   │   ├── logs_view/        # Logs page
│   │   └── components/       # Sidebar, ChatTerminal, TradePanel, etc.
│   └── package.json
├── docs/                     # 18+ documentation files
└── README.md
```

---

## 📚 Documentation

All docs are in the `docs/` folder:

| Doc | Description |
|-----|-------------|
| [architecture.md](docs/architecture.md) | System architecture & component diagram |
| [api_docs.md](docs/api_docs.md) | REST & WebSocket API reference |
| [agent_docs.md](docs/agent_docs.md) | 9 AI agents, orchestrator, memory system |
| [broker_docs.md](docs/broker_docs.md) | Broker adapters configuration |
| [database_docs.md](docs/database_docs.md) | Schema, models, repositories |
| [build_docs.md](docs/build_docs.md) | Build & packaging guide |
| [setup_guide.md](docs/setup_guide.md) | Installation & setup |
| [implementation_walkthrough.md](docs/implementation_walkthrough.md) | What was built & how |

---

## 🔒 Security
- JWT authentication with Google OAuth
- Fernet encryption for broker credentials
- Rate limiting middleware
- Context isolation in Electron
- No credentials in code — all from environment/encrypted storage

---

## 📄 License

Private — All rights reserved.
