from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class BrokerBase(ABC):
    """Abstract base class for all broker adapters."""

    name: str = "base"

    @abstractmethod
    async def login(self, credentials: Dict[str, Any]) -> bool:
        """Authenticate with the broker."""

    @abstractmethod
    async def logout(self) -> bool:
        """Logout from broker."""

    @abstractmethod
    async def place_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """Place an order. Returns broker order details."""

    @abstractmethod
    async def modify_order(self, order_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Modify an existing order."""

    @abstractmethod
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an order."""

    @abstractmethod
    async def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """Get current status of an order."""

    @abstractmethod
    async def get_positions(self) -> List[Dict[str, Any]]:
        """Get all open positions."""

    @abstractmethod
    async def get_holdings(self) -> List[Dict[str, Any]]:
        """Get all holdings (delivery positions)."""

    @abstractmethod
    async def get_funds(self) -> Dict[str, Any]:
        """Get available funds/margin."""

    @abstractmethod
    async def get_quote(self, symbol: str, exchange: str = "NSE") -> Dict[str, Any]:
        """Get live quote for a symbol."""

    @abstractmethod
    async def get_historical_data(
        self, symbol: str, exchange: str, timeframe: str, from_date: str, to_date: str
    ) -> List[Dict[str, Any]]:
        """Fetch OHLCV historical data."""

    async def get_order_book(self) -> List[Dict[str, Any]]:
        return []

    def is_connected(self) -> bool:
        return False
