import importlib
import sys
import os
from typing import Dict, Any, List, Optional
from loguru import logger
from .plugin_base import PluginBase

_plugin_manager = None


class PluginManager:
    def __init__(self):
        self._plugins: Dict[str, PluginBase] = {}
        self._marketplace_dir = "plugin_system/marketplace"

    async def install(self, plugin_name: str, source_path: str = None) -> bool:
        logger.info(f"Installing plugin: {plugin_name}")
        return True

    async def load(self, plugin_name: str, config: Dict = None) -> bool:
        try:
            module = importlib.import_module(f"plugin_system.plugins.{plugin_name}")
            plugin_class = getattr(module, "Plugin")
            plugin = plugin_class()
            success = await plugin.initialize(config or {})
            if success:
                self._plugins[plugin_name] = plugin
                logger.info(f"Plugin loaded: {plugin_name}")
            return success
        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_name}: {e}")
            return False

    async def execute(self, plugin_name: str, params: Dict = None) -> Dict[str, Any]:
        plugin = self._plugins.get(plugin_name)
        if not plugin:
            return {"error": f"Plugin {plugin_name} not loaded"}
        return await plugin.execute(params or {})

    async def unload(self, plugin_name: str):
        plugin = self._plugins.pop(plugin_name, None)
        if plugin:
            await plugin.shutdown()

    def list_plugins(self) -> List[Dict[str, Any]]:
        return [
            {"name": name, "version": p.version, "description": p.description}
            for name, p in self._plugins.items()
        ]

    def get_marketplace(self) -> List[Dict[str, Any]]:
        """Return available plugins from marketplace registry."""
        return [
            {"name": "news_sentiment", "description": "Analyze news sentiment for trading signals", "installed": False},
            {"name": "options_chain", "description": "Options chain analysis, max pain, PCR", "installed": False},
            {"name": "liquidity_detector", "description": "Detect institutional activity zones", "installed": False},
            {"name": "macro_data", "description": "Economic indicators and FII/DII data", "installed": False},
        ]


def get_plugin_manager() -> PluginManager:
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager()
    return _plugin_manager
