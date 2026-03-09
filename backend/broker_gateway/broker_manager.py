from typing import Dict, Any, Optional
from loguru import logger
from .broker_base import BrokerBase
from .paper_broker import PaperBroker
from backend.config import get_broker_config

_broker_manager: Optional["BrokerManager"] = None


class BrokerManager:
    def __init__(self):
        self.brokers: Dict[str, BrokerBase] = {}
        self.active_broker: Optional[BrokerBase] = None
        self._initialized = False

    async def initialize(self):
        cfg = get_broker_config()
        # Always register paper broker
        paper = PaperBroker()
        self.brokers["paper"] = paper

        # Register real brokers if enabled
        if cfg.brokers.get("angel_one", {}) and getattr(cfg.brokers.get("angel_one", {}), "enabled", False):
            try:
                from backend.broker_gateway.angelone.adapter import AngelOneAdapter
                self.brokers["angel_one"] = AngelOneAdapter()
            except Exception as e:
                logger.warning(f"AngelOne adapter not loaded: {e}")

        if cfg.brokers.get("zerodha", {}) and getattr(cfg.brokers.get("zerodha", {}), "enabled", False):
            try:
                from backend.broker_gateway.zerodha.adapter import ZerodhaAdapter
                self.brokers["zerodha"] = ZerodhaAdapter()
            except Exception as e:
                logger.warning(f"Zerodha adapter not loaded: {e}")

        # Set active broker
        active_name = cfg.active_broker if cfg.mode != "paper" else "paper"
        self.active_broker = self.brokers.get(active_name, paper)
        self._initialized = True
        logger.info(f"BrokerManager initialized. Active: {self.active_broker.name}")

    def get_active(self) -> BrokerBase:
        if not self.active_broker:
            paper = PaperBroker()
            self.active_broker = paper
        return self.active_broker

    async def connect(self, broker_name: str, credentials: Dict[str, Any]) -> Dict[str, Any]:
        broker = self.brokers.get(broker_name)
        if not broker:
            return {"error": f"Broker {broker_name} not registered"}
        success = await broker.login(credentials)
        if success:
            self.active_broker = broker
            return {"status": "connected", "broker": broker_name}
        return {"status": "failed", "broker": broker_name}

    async def disconnect(self, broker_name: str):
        broker = self.brokers.get(broker_name)
        if broker:
            await broker.logout()
            if self.active_broker == broker:
                self.active_broker = self.brokers.get("paper")

    def get_connection_status(self) -> Dict[str, Any]:
        return {
            name: broker.is_connected()
            for name, broker in self.brokers.items()
        }

    async def get_positions(self):
        return await self.get_active().get_positions()

    async def get_holdings(self):
        return await self.get_active().get_holdings()

    async def get_funds(self):
        return await self.get_active().get_funds()

    async def get_quote(self, symbol: str, exchange: str = "NSE"):
        return await self.get_active().get_quote(symbol, exchange)

    async def place_order(self, order: Dict[str, Any]):
        return await self.get_active().place_order(order)

    async def cancel_order(self, order_id: str):
        return await self.get_active().cancel_order(order_id)


def get_broker_manager() -> BrokerManager:
    global _broker_manager
    if _broker_manager is None:
        _broker_manager = BrokerManager()
    return _broker_manager
