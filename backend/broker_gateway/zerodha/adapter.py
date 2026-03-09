from typing import List, Dict, Any
from loguru import logger
from backend.broker_gateway.broker_base import BrokerBase


class ZerodhaAdapter(BrokerBase):
    name = "zerodha"

    def __init__(self):
        self.kite = None
        self._connected = False

    def is_connected(self) -> bool:
        return self._connected

    async def login(self, credentials: Dict[str, Any]) -> bool:
        try:
            from kiteconnect import KiteConnect
            api_key = credentials.get("api_key")
            request_token = credentials.get("request_token")
            api_secret = credentials.get("api_secret")
            self.kite = KiteConnect(api_key=api_key)
            data = self.kite.generate_session(request_token, api_secret=api_secret)
            self.kite.set_access_token(data["access_token"])
            self._connected = True
            logger.info("Zerodha login successful")
            return True
        except Exception as e:
            logger.error(f"Zerodha login failed: {e}")
            return False

    async def logout(self) -> bool:
        if self.kite:
            try:
                self.kite.invalidate_access_token()
            except Exception:
                pass
        self._connected = False
        return True

    async def place_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        try:
            order_id = self.kite.place_order(
                tradingsymbol=order["symbol"],
                exchange=order.get("exchange", "NSE"),
                transaction_type=order["side"],
                quantity=order["quantity"],
                order_type=order["order_type"],
                product="MIS" if order.get("product_type") == "INTRADAY" else "CNC",
                price=order.get("price"),
                trigger_price=order.get("trigger_price"),
                variety=self.kite.VARIETY_REGULAR,
            )
            return {"order_id": str(order_id), "status": "placed", "broker": "zerodha"}
        except Exception as e:
            return {"status": "rejected", "reason": str(e)}

    async def modify_order(self, order_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            self.kite.modify_order(variety=self.kite.VARIETY_REGULAR, order_id=order_id, **params)
            return {"status": "modified"}
        except Exception as e:
            return {"status": "error", "reason": str(e)}

    async def cancel_order(self, order_id: str) -> bool:
        try:
            self.kite.cancel_order(variety=self.kite.VARIETY_REGULAR, order_id=order_id)
            return True
        except Exception:
            return False

    async def get_order_status(self, order_id: str) -> Dict[str, Any]:
        try:
            orders = self.kite.orders()
            for o in orders:
                if o["order_id"] == order_id:
                    return o
        except Exception:
            pass
        return {}

    async def get_positions(self) -> List[Dict[str, Any]]:
        try:
            return self.kite.positions().get("net", [])
        except Exception:
            return []

    async def get_holdings(self) -> List[Dict[str, Any]]:
        try:
            return self.kite.holdings()
        except Exception:
            return []

    async def get_funds(self) -> Dict[str, Any]:
        try:
            margins = self.kite.margins()
            return margins.get("equity", {})
        except Exception:
            return {}

    async def get_quote(self, symbol: str, exchange: str = "NSE") -> Dict[str, Any]:
        try:
            key = f"{exchange}:{symbol}"
            data = self.kite.quote([key])
            q = data.get(key, {})
            return {"symbol": symbol, "ltp": q.get("last_price", 0)}
        except Exception:
            return {"symbol": symbol, "ltp": 0}

    async def get_historical_data(
        self, symbol: str, exchange: str, timeframe: str, from_date: str, to_date: str
    ) -> List[Dict[str, Any]]:
        try:
            tf_map = {"1m": "minute", "5m": "5minute", "15m": "15minute", "1h": "60minute", "1D": "day"}
            instrument = self.kite.ltp(f"{exchange}:{symbol}")
            token = list(instrument.values())[0]["instrument_token"]
            candles = self.kite.historical_data(token, from_date, to_date, tf_map.get(timeframe, "day"))
            return [
                {"timestamp": c["date"].isoformat(), "open": c["open"], "high": c["high"],
                 "low": c["low"], "close": c["close"], "volume": c["volume"]}
                for c in candles
            ]
        except Exception as e:
            logger.error(f"Zerodha historical data error: {e}")
            return []
