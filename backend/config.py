import os
import yaml
from pathlib import Path
from functools import lru_cache
from pydantic import BaseModel
from typing import Optional, List, Dict, Any


def _load_yaml(filename: str) -> dict:
    base = Path(__file__).parent.parent / "configs"
    path = base / filename
    if path.exists():
        with open(path, "r") as f:
            return yaml.safe_load(f) or {}
    return {}


# ─── System Config ────────────────────────────────────────────────────────────

class AppConfig(BaseModel):
    name: str = "Quant AI Lab"
    version: str = "1.0.0"
    port: int = 8000
    host: str = "0.0.0.0"
    debug: bool = False
    log_level: str = "INFO"


class DatabaseConfig(BaseModel):
    sqlite_path: str = "database/quant_lab.db"
    echo: bool = False


class RedisConfig(BaseModel):
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    enabled: bool = False


class RiskConfig(BaseModel):
    max_risk_per_trade: float = 0.01
    max_daily_loss: float = 0.03
    max_positions: int = 5
    kill_switch_drawdown: float = 0.10
    default_mode: str = "paper"


class TelegramConfig(BaseModel):
    bot_token: str = ""
    enabled: bool = False
    authorized_users: List[int] = []


class WhatsappConfig(BaseModel):
    enabled: bool = False
    session_path: str = "configs/.whatsapp_session"


class AlertsConfig(BaseModel):
    desktop: bool = True
    telegram: bool = False
    whatsapp: bool = False


class SystemConfig(BaseModel):
    app: AppConfig = AppConfig()
    database: DatabaseConfig = DatabaseConfig()
    redis: RedisConfig = RedisConfig()
    risk: RiskConfig = RiskConfig()
    telegram: TelegramConfig = TelegramConfig()
    whatsapp: WhatsappConfig = WhatsappConfig()
    alerts: AlertsConfig = AlertsConfig()


# ─── AI Config ────────────────────────────────────────────────────────────────

class OpenAIConfig(BaseModel):
    api_key: str = ""
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 4096


class AnthropicConfig(BaseModel):
    api_key: str = ""
    model: str = "claude-3-sonnet-20240229"
    temperature: float = 0.7
    max_tokens: int = 4096


class OllamaConfig(BaseModel):
    base_url: str = "http://localhost:11434"
    model: str = "mistral"
    temperature: float = 0.7


class AgentConfig(BaseModel):
    enabled: bool = True
    llm_model: Optional[str] = None


class MemoryConfig(BaseModel):
    vector_store: str = "chroma"
    embedding_model: str = "all-MiniLM-L6-v2"
    chroma_path: str = "database/chroma_db"
    max_conversation_history: int = 50


class AIConfig(BaseModel):
    llm_provider: str = "ollama"
    openai: OpenAIConfig = OpenAIConfig()
    anthropic: AnthropicConfig = AnthropicConfig()
    ollama: OllamaConfig = OllamaConfig()
    agents: Dict[str, AgentConfig] = {}
    memory: MemoryConfig = MemoryConfig()


# ─── Broker Config ────────────────────────────────────────────────────────────

class BrokerCredentials(BaseModel):
    enabled: bool = False
    api_key: str = ""
    client_id: str = ""
    password: str = ""
    totp_secret: str = ""
    api_secret: str = ""
    request_token: str = ""
    access_token: str = ""
    app_id: str = ""
    secret_key: str = ""
    redirect_url: str = ""


class PaperTradingConfig(BaseModel):
    initial_capital: float = 1000000
    slippage_pct: float = 0.05
    commission_per_order: float = 20


class BrokerConfig(BaseModel):
    active_broker: str = "paper"
    mode: str = "paper"
    brokers: Dict[str, BrokerCredentials] = {}
    paper_trading: PaperTradingConfig = PaperTradingConfig()


# ─── Loaders ─────────────────────────────────────────────────────────────────

@lru_cache(maxsize=1)
def get_system_config() -> SystemConfig:
    data = _load_yaml("system_config.yaml")
    return SystemConfig(**data)


@lru_cache(maxsize=1)
def get_ai_config() -> AIConfig:
    data = _load_yaml("ai_config.yaml")
    return AIConfig(**data)


@lru_cache(maxsize=1)
def get_broker_config() -> BrokerConfig:
    data = _load_yaml("broker_config.yaml")
    return BrokerConfig(**data)


def reload_configs():
    get_system_config.cache_clear()
    get_ai_config.cache_clear()
    get_broker_config.cache_clear()
