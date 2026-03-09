# QUANT AI LAB SYSTEM — Architecture Document

## Overview

QUANT AI LAB is a production-grade, AI-powered autonomous trading platform for Indian markets. It combines a multi-agent AI system, machine learning lab, and multi-channel communication into a single Windows desktop application.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    DESKTOP APP (Electron)                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────────┐  │
│  │Dashboard │ │AI Chat   │ │Strategy  │ │Backtest Lab   │  │
│  │          │ │Terminal  │ │Lab       │ │(Plotly Charts)│  │
│  └──────────┘ └──────────┘ └──────────┘ └───────────────┘  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────────┐  │
│  │Live      │ │Portfolio │ │Agent     │ │Plugin         │  │
│  │Trading   │ │          │ │Builder   │ │Marketplace    │  │
│  └──────────┘ └──────────┘ └──────────┘ └───────────────┘  │
└─────────────────────┬───────────────────────────────────────┘
                      │ IPC / HTTP / WebSocket
┌─────────────────────▼───────────────────────────────────────┐
│                   BACKEND (FastAPI)                           │
│  ┌────────────┐ ┌────────────┐ ┌─────────────────────────┐  │
│  │REST API    │ │WebSocket   │ │Authentication &         │  │
│  │Server      │ │Server      │ │Security Layer           │  │
│  └────────────┘ └────────────┘ └─────────────────────────┘  │
└─────────────────────┬───────────────────────────────────────┘
                      │
    ┌─────────────────┼─────────────────────────┐
    │                 │                         │
┌───▼──────┐  ┌──────▼──────┐  ┌──────────────▼──────────┐
│AI CORE   │  │DATA ENGINE  │  │BROKER GATEWAY           │
│          │  │             │  │                         │
│Orchestr. │  │Market Stream│  │Angel One │ Zerodha      │
│9 Agents  │  │Historical   │  │Dhan      │ Fyers        │
│LLM Layer │  │Tick Storage │  │                         │
│ML Lab    │  │Data Cache   │  │Order Engine              │
│Memory    │  │             │  │Paper Trading             │
└──────────┘  └─────────────┘  └──────────────────────────┘
    │
┌───▼──────────────────────────────────────────────────────┐
│              COMMUNICATION LAYER                          │
│  ┌──────────┐  ┌──────────────┐  ┌────────────────────┐  │
│  │Telegram  │  │WhatsApp Web  │  │Notification        │  │
│  │Bot       │  │(Baileys/QR)  │  │System              │  │
│  └──────────┘  └──────────────┘  └────────────────────┘  │
└──────────────────────────────────────────────────────────┘
    │
┌───▼──────────────────────────────────────────────────────┐
│              DATABASE & STORAGE                           │
│  ┌──────┐  ┌──────────┐  ┌───────┐  ┌────────────────┐  │
│  │SQLite│  │PostgreSQL│  │Redis  │  │Vector DB       │  │
│  │(local)│  │(optional)│  │(cache)│  │(agent memory)  │  │
│  └──────┘  └──────────┘  └───────┘  └────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

## Component Details

### Desktop Application (Electron + React + Next.js)
- **Tech**: Electron.js, React 18, Next.js 14, TailwindCSS, ShadCN UI
- **Charts**: Plotly.js for all trading visualizations
- **IPC**: Electron IPC for main ↔ renderer communication
- **Pages**: Dashboard, AI Chat, Strategy Lab, Backtest Lab, Live Trading, Portfolio, Agent Builder, Plugin Marketplace, Settings, Logs

### Backend (FastAPI)
- **Framework**: FastAPI with async support
- **API**: RESTful endpoints + WebSocket for real-time streaming
- **Auth**: JWT-based authentication with Fernet encryption for credentials
- **Middleware**: CORS, rate limiting, request logging

### AI Core
- **Orchestrator**: Central agent coordinator using LangGraph-inspired workflow engine
- **Agents**: 9 specialized agents (Market Analysis, Strategy Discovery, Backtesting, Risk Management, Execution, Portfolio Manager, Monitoring, Reporting, Data)
- **LLM**: Unified interface supporting OpenAI, Anthropic, and Ollama (local)
- **Memory**: Vector store for conversation memory, strategy memory, and contextual recall

### ML Lab
- **Models**: XGBoost, LightGBM, Random Forest, LSTM, Transformer
- **Features**: 60+ engineered features from OHLCV data
- **Capabilities**: Trend prediction, regime detection, volatility forecast, alpha discovery

### Broker Gateway
- **Brokers**: Angel One, Zerodha, Dhan, Fyers
- **Interface**: Unified abstract `BrokerBase` class
- **Order Types**: Market, Limit, Stop-Loss, Take-Profit, Trailing Stop
- **Paper Trading**: Full simulation engine for risk-free testing

### Communication Layer
- **Telegram**: Bot with slash commands for trading operations
- **WhatsApp**: Web-based QR auth via Baileys, voice message support
- **Notifications**: Multi-channel alerts (desktop, Telegram, WhatsApp)
- **NLP**: Natural language command parser for intent detection

### Database
- **Primary**: SQLite for local storage
- **Scale**: PostgreSQL for multi-user deployment
- **Cache**: Redis for data caching and message queues
- **Memory**: ChromaDB/FAISS for vector storage

## Data Flow

```
Market Data → Data Engine → AI Agents → Strategy Discovery
    → Backtesting → Risk Analysis → User Approval
    → Order Execution → Monitoring → Reporting
```

## Security Model

- Fernet symmetric encryption for API keys and broker credentials
- JWT tokens for API authentication
- Secure session storage for WhatsApp/Telegram
- Environment variable isolation for sensitive config
