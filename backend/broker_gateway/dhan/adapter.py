"""Dhan API adapter implementing BrokerBase."""

from typing import List, Dict, Any
from loguru import logger
from backend.broker_gateway.broker_base import BrokerBase


class DhanAdapter(BrokerBase):
    """Dhan broker adapter using dhanhq library."""

    name = "dhan"

    def __init__(self):
        self._client = None
        self._connected = False

    async def login(self, credentials: Dict[str, Any]) -> bool:
        try:
            from dhanhq import dhanhq
            client_id = credentials.get("client_id", "")
            access_token = credentials.get("access_token", "")
            self._client = dhanhq(client_id, access_token)
            self._connected = True
            logger.info("Dhan: Connected successfully")
            return True
        except ImportError:
            logger.error("Dhan: dhanhq package not installed")
            return False
        except Exception as e:
            logger.error(f"Dhan login failed: {e}")
            return False

    async def logout(self) -> bool:
        self._client = None
        self._connected = False
        logger.info("Dhan: Disconnected")
        return True

    def is_connected(self) -> bool:
        return self._connected

    async def place_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        if not self._client:
            return {"error": "Not connected"}
        try:
            from dhanhq import dhanhq
            result = self._client.place_order(
                security_id=order.get("symbol", ""),
                exchange_segment=order.get("exchange", dhanhq.NSE),
                transaction_type=order.get("side", dhanhq.BUY),
                quantity=order.get("quantity", 1),
                order_type=order.get("order_type", dhanhq.MARKET),
                product_type=order.get("product", dhanhq.INTRA),
                price=order.get("price", 0),
                trigger_price=order.get("trigger_price", 0),
            )
            return {"order_id": result.get("orderId", ""), "status": "placed", "raw": result}
        except Exception as e:
            logger.error(f"Dhan place_order failed: {e}")
            return {"error": str(e)}

    async def modify_order(self, order_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if not self._client:
            return {"error": "Not connected"}
        try:
            result = self._client.modify_order(
                order_id=order_id,
                order_type=params.get("order_type", "MARKET"),
                quantity=params.get("quantity"),
                price=params.get("price", 0),
                trigger_price=params.get("trigger_price", 0),
                leg_name=params.get("leg_name"),
            )
            return {"order_id": order_id, "status": "modified", "raw": result}
        except Exception as e:
            return {"error": str(e)}

    async def cancel_order(self, order_id: str) -> bool:
        if not self._client:
            return False
        try:
            self._client.cancel_order(order_id=order_id)
            return True
        except Exception as e:
            logger.error(f"Dhan cancel failed: {e}")
            return False

    async def get_order_status(self, order_id: str) -> Dict[str, Any]:
        if not self._client:
            return {"error": "Not connected"}
        try:
            result = self._client.get_order_by_id(order_id)
            return result or {}
        except Exception as e:
            return {"error": str(e)}

    async def get_positions(self) -> List[Dict[str, Any]]:
        if not self._client:
            return []
        try:
            result = self._client.get_positions()
            return result.get("data", []) if isinstance(result, dict) else []
        except Exception as e:
            logger.error(f"Dhan get_positions failed: {e}")
            return []

    async def get_holdings(self) -> List[Dict[str, Any]]:
        if not self._client:
            return []
        try:
            result = self._client.get_holdings()
            return result.get("data", []) if isinstance(result, dict) else []
        except Exception as e:
            return []

    async def get_funds(self) -> Dict[str, Any]:
        if not self._client:
            return {}
        try:
            result = self._client.get_fund_limits()
            return result or {}
        except Exception as e:
            return {"error": str(e)}

    async def get_quote(self, symbol: str, exchange: str = "NSE") -> Dict[str, Any]:
        return {"symbol": symbol, "exchange": exchange, "ltp": 0, "message": "Use WebSocket for live quotes"}

    async def get_historical_data(
        self, symbol: str, exchange: str, timeframe: str, from_date: str, to_date: str
    ) -> List[Dict[str, Any]]:
        if not self._client:
            return []
        try:
            from dhanhq import dhanhq
            exchange_map = {"NSE": dhanhq.NSE, "BSE": dhanhq.BSE, "NFO": dhanhq.NSE_FNO}
            result = self._client.historical_daily_data(
                security_id=symbol,
                exchange_segment=exchange_map.get(exchange, dhanhq.NSE),
                instrument_type="EQUITY",
                from_date=from_date,
                to_date=to_date,
            )
            return result.get("data", []) if isinstance(result, dict) else []
        except Exception as e:
            logger.error(f"Dhan historical data failed: {e}")
            return []
