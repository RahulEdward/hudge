"""Plugin marketplace — discovery, install, and distribution."""

import json
import os
from typing import List, Dict, Any, Optional
from loguru import logger

REGISTRY_PATH = os.path.join(os.path.dirname(__file__), "registry.json")


class PluginMarketplace:
    """Plugin discovery and management."""

    def __init__(self):
        self._installed: Dict[str, Dict] = {}
        self._registry: List[Dict] = []
        self._load_registry()

    def _load_registry(self):
        try:
            with open(REGISTRY_PATH, "r") as f:
                self._registry = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self._registry = []

    def browse(self, category: Optional[str] = None, query: Optional[str] = None) -> List[Dict]:
        """Browse available plugins with optional filters."""
        plugins = self._registry
        if category:
            plugins = [p for p in plugins if p.get("category") == category]
        if query:
            q = query.lower()
            plugins = [p for p in plugins if q in p.get("name", "").lower() or q in p.get("description", "").lower()]
        # Mark installed status
        for p in plugins:
            p["installed"] = p["name"] in self._installed
        return plugins

    def install(self, plugin_name: str) -> Dict[str, Any]:
        """Install a plugin from the marketplace."""
        plugin = next((p for p in self._registry if p["name"] == plugin_name), None)
        if not plugin:
            return {"error": f"Plugin '{plugin_name}' not found in marketplace"}
        if plugin_name in self._installed:
            return {"error": f"Plugin '{plugin_name}' is already installed"}

        self._installed[plugin_name] = {**plugin, "status": "installed"}
        logger.info(f"Plugin installed: {plugin_name}")
        return {"status": "installed", "plugin": plugin_name}

    def uninstall(self, plugin_name: str) -> Dict[str, Any]:
        """Uninstall a plugin."""
        if plugin_name not in self._installed:
            return {"error": f"Plugin '{plugin_name}' is not installed"}
        del self._installed[plugin_name]
        logger.info(f"Plugin uninstalled: {plugin_name}")
        return {"status": "uninstalled", "plugin": plugin_name}

    def list_installed(self) -> List[Dict]:
        """List all installed plugins."""
        return list(self._installed.values())

    def get_categories(self) -> List[str]:
        """Get all available categories."""
        return list(set(p.get("category", "other") for p in self._registry))
