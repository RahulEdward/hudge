# QUANT AI LAB — LLM Integration Documentation

## Overview

The system supports three LLM connection methods plus local models. All providers implement a unified interface so agents can work with any LLM transparently.

---

## Supported Providers

| Provider | Models | Auth Methods | Cost |
|----------|--------|-------------- |------|
| OpenAI | GPT-4, GPT-4 Turbo, GPT-3.5 Turbo | API Key, OAuth Login | Paid |
| Anthropic | Claude 3 Opus, Sonnet, Haiku | API Key, OAuth Login | Paid |
| Ollama (Local) | Mistral, Llama 3, CodeLlama, Gemma | None (local) | Free |

---

## Unified LLM Interface

Every provider implements these methods:

| Method | Description | Used By |
|--------|-------------|---------|
| `generate_text(prompt, system_prompt)` | General text generation | All agents |
| `analyze_market(data, context)` | Market analysis with structured output | Market Analysis Agent |
| `build_strategy(analysis, constraints)` | Strategy creation from market data | Strategy Discovery Agent |
| `reason_about_trades(positions, market)` | Trade decision reasoning | Risk Agent, Execution Agent |
| `stream_response(prompt)` | Streaming text generation | Chat Terminal |

**Provider Selection:**

```yaml
# configs/ai_config.yaml
llm_provider: "ollama"   # Switch between: openai / anthropic / ollama
```

All agents automatically use the configured provider. Individual agents can override:

```yaml
agents:
  market_analysis:
    llm_model: "openai"  # Override: use GPT-4 for market analysis
  reporting:
    llm_model: null      # null = use default provider
```

---

## OpenAI Connector (`openai_connector.py`)

### API Key Authentication
```yaml
openai:
  api_key: "sk-..."
  model: "gpt-4"
```

### OAuth Login
1. User clicks "Login with OpenAI" in Settings
2. App opens OAuth authorization URL in browser
3. User authorizes the application
4. Callback receives auth code
5. Exchange code for access token
6. Token stored encrypted in config

### Features
- Streaming responses (Server-Sent Events)
- Function calling (structured output)
- JSON mode for data extraction
- Retry with exponential backoff
- Token usage tracking and budgeting
- Rate limit handling

---

## Anthropic Connector (`anthropic_connector.py`)

### API Key Authentication
```yaml
anthropic:
  api_key: "sk-ant-..."
  model: "claude-3-sonnet-20240229"
```

### OAuth Login
Same flow as OpenAI OAuth.

### Features
- Claude's extended context window (200K tokens)
- System prompt for trading persona
- Streaming responses
- Structured output via tool use
- Multi-turn conversation support

### Trading Persona System Prompt
```
You are a senior quantitative trading analyst specializing in Indian markets 
(NIFTY, BANKNIFTY, FINNIFTY, Indian equities and options). You provide 
data-driven analysis using technical indicators, market regime detection, 
and risk-adjusted trade recommendations. Always include specific price 
levels, risk parameters, and confidence scores.
```

---

## Ollama / Local LLM Connector (`local_llm_connector.py`)

### Setup
1. Install Ollama: `winget install Ollama.Ollama`
2. Pull model: `ollama pull mistral`
3. Configure:
```yaml
ollama:
  base_url: "http://localhost:11434"
  model: "mistral"
```

### Supported Local Models

| Model | Size | Best For |
|-------|------|----------|
| Mistral 7B | 4.1 GB | General analysis, fast responses |
| Llama 3 8B | 4.7 GB | Reasoning, strategy building |
| Llama 3 70B | 40 GB | Complex analysis (requires GPU) |
| CodeLlama 7B | 3.8 GB | Code generation for strategies |
| Gemma 7B | 5.0 GB | Balanced performance |

### Features
- Zero API cost
- Full data privacy (nothing leaves local machine)
- No internet required after model download
- Streaming responses via Ollama API
- Automatic model warm-up on app start

### Limitations
- Slower than cloud APIs (depends on hardware)
- Smaller context window (typically 8K-32K)
- Less accurate for complex market reasoning vs GPT-4/Claude

---

## OAuth Handler (`oauth_handler.py`)

Manages OAuth 2.0 flows for OpenAI and Anthropic.

**Flow:**
```
User clicks "Login with OpenAI/Anthropic"
    │
    ▼
Generate Authorization URL with:
  - client_id, redirect_uri, scope, state, code_verifier (PKCE)
    │
    ▼
Open URL in system browser
    │
    ▼
User authorizes application on provider's website
    │
    ▼
Provider redirects to localhost callback with auth code
    │
    ▼
Exchange auth code for access_token + refresh_token
    │
    ▼
Store tokens encrypted in configs
    │
    ▼
Auto-refresh token before expiry
```

**Security:**
- PKCE (Proof Key for Code Exchange) for secure flow
- Tokens encrypted at rest with Fernet
- Refresh before expiry (proactive)
- Token revocation on logout

---

## LLM Usage Tracking

The system tracks LLM usage per agent:

| Metric | Description |
|--------|-------------|
| Total Tokens | Input + output tokens consumed |
| Cost (USD) | Estimated cost based on model pricing |
| Requests | Number of API calls |
| Latency | Average response time |
| Errors | Failed requests count |

Available in Settings → LLM Usage dashboard.

---

## Prompt Templates

Stored in `ai_core/prompts/`:

| Template | Purpose |
|----------|---------|
| `market_analysis.txt` | System prompt for market analysis |
| `strategy_discovery.txt` | Prompt for strategy generation |
| `risk_assessment.txt` | Prompt for risk evaluation |
| `trade_reasoning.txt` | Prompt for trade decision explanation |
| `report_generation.txt` | Prompt for generating reports |

Templates use variable substitution:
```
Analyze the following {symbol} data for {timeframe} timeframe:
{ohlcv_data}

Technical Indicators:
{indicators}

Provide: trend, regime, volatility level, key levels, and trading recommendation.
```
