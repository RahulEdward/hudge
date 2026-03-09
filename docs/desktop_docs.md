# QUANT AI LAB — Desktop Application Documentation

## Overview

The desktop application is built with Electron.js + React + Next.js, styled with TailwindCSS and ShadCN UI. All charts use Plotly.js.

## Architecture

```
desktop_app/
├── electron_main/       # Electron main process
│   ├── main.ts         # App entry, auth check, window creation, backend spawning
│   ├── window_manager.ts  # Window lifecycle: login popup + main window + auth browser
│   ├── ipc_router.ts  # IPC message routing
│   └── auth_handler.ts # Google OAuth flow: local server, token exchange, safeStorage
│
├── ui/                 # Page-level components
│   ├── dashboard/      # Main dashboard with KPIs
│   ├── charts/         # Plotly chart components
│   ├── agents/         # Agent interaction pages
│   ├── broker_accounts/ # Broker connection UI
│   ├── strategy_results/ # Strategy lab & results
│   └── settings/       # App settings
│
└── components/         # Reusable UI components
    ├── chat_terminal/  # AI chat interface
    ├── trade_panel/    # Order entry panel
    ├── backtest_view/  # Backtest results viewer
    └── logs_view/      # System log viewer
```

## Screens

### 0. Login Popup (First Screen — Shown Before Main App)
- Appears on app launch if no valid session exists
- Frameless popup window: 450×550px, centered, dark glassmorphism design
- App logo with subtle glow animation
- Single button: **"Continue with Google"** (white bg, Google G icon)
- On click: opens system browser for Google OAuth sign-in
- After Google approval → browser redirects back → tokens stored → popup closes → main app loads
- Works exactly like Claude/Anthropic desktop app login
- Session persists across app restarts (Electron `safeStorage`)

### 1. Dashboard
- Real-time P&L card
- Portfolio allocation pie chart
- Today's trades summary
- Agent activity feed
- Market status indicators (NIFTY, BANKNIFTY, FINNIFTY)
- Top-right: user avatar + name (from Google profile) with logout dropdown

### 2. AI Chat Terminal
- Streaming chat interface
- Agent selector dropdown
- Conversation history sidebar
- Code/data rendering in responses
- Voice input button

### 3. Strategy Lab
- AI-discovered strategies list
- Strategy details with entry/exit rules
- Performance comparison table
- Approve/Reject buttons for live deployment

### 4. Backtesting Lab
- Symbol and timeframe selector
- Backtest parameters form
- Plotly equity curve chart
- Drawdown chart
- Trade log table
- Metrics cards (win rate, Sharpe, MDD)

### 5. Live Trading
- Active positions table
- Open orders with modify/cancel
- Real-time P&L streaming
- Kill switch button

### 6. Portfolio
- Holdings with current value
- Allocation breakdown (Plotly)
- Historical performance chart
- Daily returns heatmap

### 7. Agent Builder
- Agent template selector
- Custom prompt configuration
- Tool/function assignment
- Test agent button

### 8. Plugin Marketplace
- Browse available plugins
- Install/uninstall buttons
- Plugin configuration
- Custom plugin upload

### 9. Settings
- Broker API credentials
- LLM provider configuration (OpenAI / Anthropic / Ollama)
- Risk parameters
- Notification preferences (Desktop / Telegram / WhatsApp)
- Theme toggle (dark/light)

### 10. Logs
- System event log
- Agent activity log
- Trade execution log
- Error log with stack traces
- Filter and search

## IPC Communication

Electron IPC bridges the renderer (React) to the backend:

```typescript
// Renderer → Main → Backend
ipcRenderer.invoke('api:request', { method: 'GET', path: '/api/v1/market/quote/NIFTY' })

// Main → Renderer (events)
ipcMain.on('ws:message', (event, data) => mainWindow.webContents.send('ws:data', data))
```

## Design System

- **Theme**: Dark mode primary (professional trading aesthetic)
- **Colors**: Emerald green (#10B981) for profit, Rose red (#F43F5E) for loss
- **Typography**: Inter font family
- **Components**: ShadCN UI (Dialog, Sheet, Command, Toast, etc.)
- **Charts**: Plotly.js with dark theme, custom trading chart layouts
