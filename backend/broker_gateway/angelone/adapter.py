import pyotp
from typing import List, Dict, Any
from loguru import logger
from backend.broker_gateway.broker_base import BrokerBase


class AngelOneAdapter(BrokerBase):
    name = "angel_one"

    def __init__(self):
        self.smart_api = None
        self._connected = False

    def is_connected(self) -> bool:
        return self._connected

    async def login(self, credentials: Dict[str, Any]) -> bool:
        try:
            from SmartApi import SmartConnect
            api_key = credentials.get("api_key")
            client_id = credentials.get("client_id")
            password = credentials.get("password")
            totp_secret = credentials.get("totp_secret")

            self.smart_api = SmartConnect(api_key=api_key)
            totp = pyotp.TOTP(totp_secret).now()
            data = self.smart_api.generateSession(client_id, password, totp)
            if data["status"]:
                self._connected = True
                logger.info(f"AngelOne login successful for {client_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"AngelOne login failed: {e}")
            return False

    async def logout(self) -> bool:
        if self.smart_api:
            try:
                self.smart_api.terminateSession(self.smart_api.clientCode)
            except Exception:
                pass
        self._connected = False
        return True

    async def place_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        try:
            params = {
                "variety": "NORMAL",
                "tradingsymbol": order["symbol"],
                "symboltoken": order.get("symbol_token", ""),
                "transactiontype": order["side"],
                "exchange": order.get("exchange", "NSE"),
                "ordertype": order["order_type"],
                "producttype": "INTRADAY" if order.get("product_type") == "INTRADAY" else "DELIVERY",
                "duration": "DAY",
                "price": str(order.get("price", 0)),
                "squareoff": "0",
                "stoploss": "0",
                "quantity": str(order["quantity"]),
            }
            result = self.smart_api.placeOrder(params)
            return {"order_id": result["data"]["orderid"], "status": "placed", "broker": "angel_one"}
        except Exception as e:
            logger.error(f"AngelOne place_order failed: {e}")
            return {"status": "rejected", "reason": str(e)}

    async def modify_order(self, order_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            result = self.smart_api.modifyOrder({"orderid": order_id, **params})
            return {"status": "modified", "order_id": order_id}
        except Exception as e:
            return {"status": "error", "reason": str(e)}

    async def cancel_order(self, order_id: str) -> bool:
        try:
            self.smart_api.cancelOrder(order_id, "NORMAL")
            return True
        except Exception:
            return False

    async def get_order_status(self, order_id: str) -> Dict[str, Any]:
        try:
            orders = self.smart_api.orderBook()
            for o in orders.get("data", []):
                if o["orderid"] == order_id:
                    return o
        except Exception:
            pass
        return {}

    async def get_positions(self) -> List[Dict[str, Any]]:
        try:
            result = self.smart_api.position()
            return result.get("data", [])
        except Exception:
            return []

    async def get_holdings(self) -> List[Dict[str, Any]]:
        try:
            result = self.smart_api.holding()
            return result.get("data", [])
        except Exception:
            return []

    async def get_funds(self) -> Dict[str, Any]:
        try:
            result = self.smart_api.rmsLimit()
            return result.get("data", {})
        except Exception:
            return {}

    async def get_quote(self, symbol: str, exchange: str = "NSE") -> Dict[str, Any]:
        try:
            result = self.smart_api.ltpData(exchange, symbol, "")
            data = result.get("data", {})
            return {"symbol": symbol, "ltp": data.get("ltp", 0)}
        except Exception:
            return {"symbol": symbol, "ltp": 0}

    async def get_historical_data(
        self, symbol: str, exchange: str, timeframe: str, from_date: str, to_date: str
    ) -> List[Dict[str, Any]]:
        try:
            tf_map = {"1m": "ONE_MINUTE", "5m": "FIVE_MINUTE", "15m": "FIFTEEN_MINUTE",
                      "1h": "ONE_HOUR", "1D": "ONE_DAY"}
            params = {
                "exchange": exchange,
                "symboltoken": symbol,
                "interval": tf_map.get(timeframe, "ONE_DAY"),
                "fromdate": from_date,
                "todate": to_date,
            }
            result = self.smart_api.getCandleData(params)
            candles = result.get("data", [])
            return [
                {"timestamp": c[0], "open": c[1], "high": c[2], "low": c[3], "close": c[4], "volume": c[5]}
                for c in candles
            ]
        except Exception as e:
            logger.error(f"AngelOne historical data error: {e}")
            return []
