"""Fyers API v3 adapter implementing BrokerBase."""

from typing import List, Dict, Any
from loguru import logger
from backend.broker_gateway.broker_base import BrokerBase


class FyersAdapter(BrokerBase):
    """Fyers broker adapter using fyers-apiv3 library."""

    name = "fyers"

    def __init__(self):
        self._client = None
        self._connected = False

    async def login(self, credentials: Dict[str, Any]) -> bool:
        try:
            from fyers_apiv3 import fyersModel
            client_id = credentials.get("client_id", "")
            access_token = credentials.get("access_token", "")
            self._client = fyersModel.FyersModel(
                client_id=client_id,
                token=access_token,
                is_async=False,
                log_path="logs/",
            )
            # Test connection
            profile = self._client.get_profile()
            if profile.get("s") == "ok":
                self._connected = True
                logger.info("Fyers: Connected successfully")
                return True
            else:
                logger.error(f"Fyers login failed: {profile}")
                return False
        except ImportError:
            logger.error("Fyers: fyers-apiv3 package not installed")
            return False
        except Exception as e:
            logger.error(f"Fyers login failed: {e}")
            return False

    async def logout(self) -> bool:
        self._client = None
        self._connected = False
        logger.info("Fyers: Disconnected")
        return True

    def is_connected(self) -> bool:
        return self._connected

    async def place_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        if not self._client:
            return {"error": "Not connected"}
        try:
            side_map = {"BUY": 1, "SELL": -1}
            type_map = {"MARKET": 2, "LIMIT": 1, "SL": 3, "SL-M": 4}
            product_map = {"INTRADAY": "INTRADAY", "DELIVERY": "CNC", "MARGIN": "MARGIN"}
            data = {
                "symbol": order.get("symbol", ""),
                "qty": order.get("quantity", 1),
                "type": type_map.get(order.get("order_type", "MARKET"), 2),
                "side": side_map.get(order.get("side", "BUY"), 1),
                "productType": product_map.get(order.get("product", "INTRADAY"), "INTRADAY"),
                "limitPrice": order.get("price", 0),
                "stopPrice": order.get("trigger_price", 0),
                "validity": "DAY",
                "offlineOrder": False,
            }
            result = self._client.place_order(data=data)
            return {"order_id": result.get("id", ""), "status": "placed", "raw": result}
        except Exception as e:
            logger.error(f"Fyers place_order failed: {e}")
            return {"error": str(e)}

    async def modify_order(self, order_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if not self._client:
            return {"error": "Not connected"}
        try:
            data = {"id": order_id, **params}
            result = self._client.modify_order(data=data)
            return {"order_id": order_id, "status": "modified", "raw": result}
        except Exception as e:
            return {"error": str(e)}

    async def cancel_order(self, order_id: str) -> bool:
        if not self._client:
            return False
        try:
            result = self._client.cancel_order(data={"id": order_id})
            return result.get("s") == "ok"
        except Exception as e:
            logger.error(f"Fyers cancel failed: {e}")
            return False

    async def get_order_status(self, order_id: str) -> Dict[str, Any]:
        if not self._client:
            return {"error": "Not connected"}
        try:
            result = self._client.orderBook()
            orders = result.get("orderBook", [])
            for o in orders:
                if o.get("id") == order_id:
                    return o
            return {"error": "Order not found"}
        except Exception as e:
            return {"error": str(e)}

    async def get_positions(self) -> List[Dict[str, Any]]:
        if not self._client:
            return []
        try:
            result = self._client.positions()
            return result.get("netPositions", [])
        except Exception as e:
            logger.error(f"Fyers get_positions failed: {e}")
            return []

    async def get_holdings(self) -> List[Dict[str, Any]]:
        if not self._client:
            return []
        try:
            result = self._client.holdings()
            return result.get("holdings", [])
        except Exception as e:
            return []

    async def get_funds(self) -> Dict[str, Any]:
        if not self._client:
            return {}
        try:
            result = self._client.funds()
            return result.get("fund_limit", [{}])
        except Exception as e:
            return {"error": str(e)}

    async def get_quote(self, symbol: str, exchange: str = "NSE") -> Dict[str, Any]:
        if not self._client:
            return {"symbol": symbol, "ltp": 0}
        try:
            data = {"symbols": f"{exchange}:{symbol}"}
            result = self._client.quotes(data=data)
            quotes = result.get("d", [{}])
            if quotes:
                q = quotes[0].get("v", {})
                return {
                    "symbol": symbol,
                    "ltp": q.get("lp", 0),
                    "open": q.get("open_price", 0),
                    "high": q.get("high_price", 0),
                    "low": q.get("low_price", 0),
                    "close": q.get("prev_close_price", 0),
                    "volume": q.get("volume", 0),
                }
            return {"symbol": symbol, "ltp": 0}
        except Exception as e:
            return {"symbol": symbol, "ltp": 0, "error": str(e)}

    async def get_historical_data(
        self, symbol: str, exchange: str, timeframe: str, from_date: str, to_date: str
    ) -> List[Dict[str, Any]]:
        if not self._client:
            return []
        try:
            tf_map = {"1m": "1", "5m": "5", "15m": "15", "1h": "60", "1D": "D"}
            data = {
                "symbol": f"{exchange}:{symbol}",
                "resolution": tf_map.get(timeframe, "D"),
                "date_format": "1",
                "range_from": from_date,
                "range_to": to_date,
                "cont_flag": "1",
            }
            result = self._client.history(data=data)
            candles = result.get("candles", [])
            return [
                {"timestamp": c[0], "open": c[1], "high": c[2], "low": c[3], "close": c[4], "volume": c[5]}
                for c in candles
            ]
        except Exception as e:
            logger.error(f"Fyers historical data failed: {e}")
            return []
