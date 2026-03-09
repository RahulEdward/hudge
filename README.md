# Quant AI Lab

AI-powered autonomous trading platform for Indian markets (NSE/BSE).

## Features
- 9 specialized AI agents (Market Analysis, Strategy Discovery, Risk, Execution, Portfolio, Monitoring, Reporting, Data, Backtesting)
- Multi-broker support: Angel One, Zerodha, Dhan, Fyers
- Paper trading simulation engine
- Backtesting with VectorBT + performance metrics
- ML models: Trend prediction, Regime detection, Volatility forecasting
- Multi-channel alerts: Desktop, Telegram, WhatsApp
- Electron desktop app with React/Next.js UI
- LLM support: OpenAI, Anthropic Claude, Ollama (local/free)

## Quick Start

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

### Frontend
```bash
cd desktop_app
npm install
npm run dev
```

## Architecture
- **Backend**: Python FastAPI + WebSocket
- **Frontend**: Electron + React + Next.js + TailwindCSS
- **Database**: SQLite (local) + Redis (optional cache)
- **AI**: Multi-agent orchestrator with LangGraph-inspired state machine
