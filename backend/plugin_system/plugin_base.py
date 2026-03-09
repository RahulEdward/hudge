from abc import ABC, abstractmethod
from typing import Dict, Any


class PluginBase(ABC):
    """Base class for all Quant AI Lab plugins."""

    name: str = "base_plugin"
    version: str = "1.0.0"
    description: str = ""
    author: str = ""

    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the plugin with configuration."""

    @abstractmethod
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the plugin's main function."""

    @abstractmethod
    async def shutdown(self):
        """Clean up resources."""
