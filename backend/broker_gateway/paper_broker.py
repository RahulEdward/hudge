import uuid
from datetime import datetime
from typing import List, Dict, Any
from loguru import logger
from .broker_base import BrokerBase
from backend.config import get_broker_config


class PaperBroker(BrokerBase):
    """Full paper trading simulation engine."""

    name = "paper"

    def __init__(self):
        cfg = get_broker_config().paper_trading
        self.capital = cfg.initial_capital
        self.available_cash = cfg.initial_capital
        self.slippage_pct = cfg.slippage_pct / 100
        self.commission = cfg.commission_per_order
        self.positions: Dict[str, Dict] = {}
        self.orders: Dict[str, Dict] = {}
        self._connected = True

    def is_connected(self) -> bool:
        return self._connected

    async def login(self, credentials: Dict[str, Any]) -> bool:
        self._connected = True
        return True

    async def logout(self) -> bool:
        return True

    async def place_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        order_id = str(uuid.uuid4())[:12].upper()
        symbol = order["symbol"]
        side = order["side"]
        qty = order["quantity"]
        price = order.get("price", 0.0)

        # Apply slippage
        quote = await self.get_quote(symbol)
        ltp = quote.get("ltp", price or 100.0)
        if side == "BUY":
            fill_price = ltp * (1 + self.slippage_pct)
        else:
            fill_price = ltp * (1 - self.slippage_pct)

        cost = fill_price * qty + self.commission

        if side == "BUY":
            if cost > self.available_cash:
                return {"status": "rejected", "reason": "Insufficient funds", "order_id": order_id}
            self.available_cash -= cost
            if symbol in self.positions:
                pos = self.positions[symbol]
                total_qty = pos["quantity"] + qty
                pos["average_price"] = (pos["average_price"] * pos["quantity"] + fill_price * qty) / total_qty
                pos["quantity"] = total_qty
            else:
                self.positions[symbol] = {
                    "symbol": symbol,
                    "quantity": qty,
                    "average_price": fill_price,
                    "side": "BUY",
                    "product_type": order.get("product_type", "INTRADAY"),
                }
        else:  # SELL
            if symbol in self.positions and self.positions[symbol]["quantity"] >= qty:
                pos = self.positions[symbol]
                pnl = (fill_price - pos["average_price"]) * qty - self.commission
                self.available_cash += fill_price * qty - self.commission
                pos["quantity"] -= qty
                if pos["quantity"] == 0:
                    del self.positions[symbol]
            else:
                return {"status": "rejected", "reason": "Insufficient position", "order_id": order_id}

        result = {
            "order_id": order_id,
            "broker_order_id": f"PAPER-{order_id}",
            "status": "filled",
            "fill_price": round(fill_price, 2),
            "quantity": qty,
            "symbol": symbol,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.orders[order_id] = result
        logger.info(f"[Paper] {side} {qty} {symbol} @ {fill_price:.2f}")
        return result

    async def modify_order(self, order_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "modified", "order_id": order_id}

    async def cancel_order(self, order_id: str) -> bool:
        if order_id in self.orders:
            self.orders[order_id]["status"] = "cancelled"
            return True
        return False

    async def get_order_status(self, order_id: str) -> Dict[str, Any]:
        return self.orders.get(order_id, {"status": "not_found"})

    async def get_positions(self) -> List[Dict[str, Any]]:
        return list(self.positions.values())

    async def get_holdings(self) -> List[Dict[str, Any]]:
        return [p for p in self.positions.values() if p.get("product_type") == "DELIVERY"]

    async def get_funds(self) -> Dict[str, Any]:
        equity = sum(
            p["quantity"] * p["average_price"] for p in self.positions.values()
        )
        return {
            "available_cash": round(self.available_cash, 2),
            "total_capital": round(self.capital, 2),
            "used_margin": round(self.capital - self.available_cash, 2),
            "portfolio_value": round(self.available_cash + equity, 2),
        }

    async def get_quote(self, symbol: str, exchange: str = "NSE") -> Dict[str, Any]:
        # Paper mode returns a dummy/cached quote
        from backend.data_engine.data_cache import get_cache
        try:
            cache = get_cache()
            q = await cache.get_quote(symbol)
            if q:
                return q
        except Exception:
            pass
        return {"symbol": symbol, "ltp": 100.0, "open": 99.0, "high": 101.0, "low": 98.0, "close": 100.0}

    async def get_historical_data(
        self, symbol: str, exchange: str, timeframe: str, from_date: str, to_date: str
    ) -> List[Dict[str, Any]]:
        return []

    async def get_order_book(self) -> List[Dict[str, Any]]:
        return list(self.orders.values())
