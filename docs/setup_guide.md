# QUANT AI LAB — Setup & Deployment Guide

## Prerequisites

- Windows 10/11
- Python 3.11+
- Node.js 20+
- Git
- Redis (optional, for message queue)
- Ollama (optional, for local LLM)

## Quick Start

### 1. Clone & Setup

```bash
cd d:\quant-lab
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
cd desktop_app
npm install
```

### 4. Configuration

Copy and edit config files:
```bash
cp configs/system_config.example.yaml configs/system_config.yaml
cp configs/broker_config.example.yaml configs/broker_config.yaml
cp configs/ai_config.example.yaml configs/ai_config.yaml
```

### 5. Start Backend

```bash
cd backend/api_server
python main.py
# API available at http://localhost:8000
```

### 6. Start Desktop App

```bash
cd desktop_app
npm run dev
# Or for Electron:
npm start
```

## Configuration Details

### Broker Config (`configs/broker_config.yaml`)
```yaml
active_broker: "angel_one"
mode: "paper"  # paper / live
brokers:
  angel_one:
    api_key: "your_api_key"
    client_id: "your_client_id"
    password: "your_password"
    totp_secret: "your_totp"
```

### AI Config (`configs/ai_config.yaml`)
```yaml
llm_provider: "ollama"  # openai / anthropic / ollama
openai:
  api_key: ""
  model: "gpt-4"
anthropic:
  api_key: ""
  model: "claude-3-sonnet"
ollama:
  base_url: "http://localhost:11434"
  model: "mistral"
```

### System Config (`configs/system_config.yaml`)
```yaml
app:
  name: "Quant AI Lab"
  version: "1.0.0"
  port: 8000
  debug: false
database:
  sqlite_path: "database/quant_lab.db"
redis:
  host: "localhost"
  port: 6379
telegram:
  bot_token: ""
  enabled: false
whatsapp:
  enabled: false
  session_path: "configs/.whatsapp_session"
risk:
  max_risk_per_trade: 0.01
  max_daily_loss: 0.03
  max_positions: 5
  kill_switch_drawdown: 0.10
```

## Building Windows Executable

### 1. Bundle Backend
```bash
cd backend
pyinstaller --onedir --name quant-lab-backend main.py
```

### 2. Bundle Desktop App
```bash
cd desktop_app
npm run build
npm run package  # Electron Builder
```

### 3. Output
```
dist/
├── Quant AI Lab Setup.exe    # Windows installer
└── win-unpacked/             # Portable version
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 8000 in use | Change port in `system_config.yaml` |
| Broker login fails | Verify API credentials, check TOTP |
| Ollama not found | Install Ollama and pull model: `ollama pull mistral` |
| WhatsApp QR expired | Restart WhatsApp module, scan new QR |
| Redis not available | Install Redis or disable message queue in config |
