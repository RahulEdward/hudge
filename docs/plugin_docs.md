# QUANT AI LAB — Plugin System Documentation

## Overview

The Plugin System allows users to extend the platform with custom agents, skills, and analysis tools. Plugins are self-contained modules registered through the Plugin Manager.

## Architecture

```
plugin_system/
├── plugin_manager.py      # Plugin lifecycle (install, load, unload)
├── skill_registry.py      # Skill registration and discovery
├── agent_templates/       # Base templates for custom agents
│   ├── base_plugin.py
│   └── templates/
└── marketplace/           # Plugin marketplace metadata
    └── registry.json
```

## Plugin Interface

Every plugin must implement:

```python
class PluginBase(ABC):
    name: str
    version: str
    description: str
    author: str
    
    @abstractmethod
    async def initialize(self, context: PluginContext) -> None:
        """Called when plugin is loaded"""
    
    @abstractmethod
    async def execute(self, params: dict) -> PluginResult:
        """Main execution entry point"""
    
    @abstractmethod
    async def shutdown(self) -> None:
        """Cleanup on unload"""
```

## Built-in Plugins

### 1. News Sentiment Analyzer
- Scrapes financial news for given symbols
- Runs sentiment analysis (positive/negative/neutral)
- Returns sentiment score and key headlines

### 2. Options Chain Analyzer
- Fetches live options chain data
- Calculates max pain, PCR, OI analysis
- Identifies key strike levels

### 3. Liquidity Detector
- Analyzes order book depth
- Detects high-volume price levels
- Identifies institutional activity zones

### 4. Macro Data Analyzer
- Fetches macroeconomic indicators
- Analyzes FII/DII data
- Monitors global market correlations

## Skill Registry

Skills are atomic capabilities that agents can use:

```python
@skill_registry.register("analyze_sentiment")
async def analyze_sentiment(text: str) -> SentimentResult:
    """Analyze market sentiment from text"""
    ...

@skill_registry.register("fetch_options_chain")
async def fetch_options_chain(symbol: str, expiry: str) -> OptionsData:
    """Fetch live options chain"""
    ...
```

## Creating Custom Plugins

1. Create a new Python file in `plugin_system/marketplace/`
2. Extend `PluginBase` class
3. Register with Plugin Manager
4. Plugin appears in desktop UI marketplace

## Plugin Manager API

```python
manager = PluginManager()
await manager.install("news_sentiment")    # Install
await manager.load("news_sentiment")       # Load into runtime
result = await manager.execute("news_sentiment", {"symbol": "NIFTY"})
await manager.unload("news_sentiment")     # Unload
await manager.uninstall("news_sentiment")  # Remove
plugins = manager.list_plugins()           # List all
```
