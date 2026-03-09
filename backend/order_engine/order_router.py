import uuid
from typing import Dict, Any
from loguru import logger
from backend.config import get_broker_config

_order_router = None


class OrderRouter:
    """Routes orders to the appropriate broker (paper or live)."""

    async def place_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        # Risk check first
        from backend.order_engine.risk_engine import get_risk_engine
        risk = get_risk_engine()
        valid, reason = await risk.validate_order(order)
        if not valid:
            logger.warning(f"Order rejected by risk engine: {reason}")
            return {"status": "rejected", "reason": reason}

        # Generate internal order ID
        order["order_id"] = order.get("order_id") or str(uuid.uuid4())[:12].upper()

        # Route to broker
        from backend.broker_gateway.broker_manager import get_broker_manager
        bm = get_broker_manager()
        result = await bm.place_order(order)

        # Persist order to DB
        await self._save_order(order, result)

        # Update position count
        if result.get("status") in ("filled", "placed"):
            if order.get("side") == "BUY":
                risk.update_position_count(1)

        # Broadcast trade update
        try:
            from backend.api_server.websocket_server import get_ws_manager
            await get_ws_manager().broadcast({"type": "order_update", "data": result}, "trades")
        except Exception:
            pass

        return result

    async def cancel_order(self, order_id: str) -> Dict[str, Any]:
        from backend.broker_gateway.broker_manager import get_broker_manager
        bm = get_broker_manager()
        success = await bm.cancel_order(order_id)
        return {"status": "cancelled" if success else "failed", "order_id": order_id}

    async def _save_order(self, order: Dict, result: Dict):
        try:
            from backend.database.connection import get_session
            from backend.database.models.trade import Order
            async for session in get_session():
                db_order = Order(
                    order_id=order["order_id"],
                    broker_order_id=result.get("broker_order_id", ""),
                    symbol=order["symbol"],
                    side=order["side"],
                    order_type=order.get("order_type", "MARKET"),
                    product_type=order.get("product_type", "INTRADAY"),
                    quantity=order["quantity"],
                    price=order.get("price", 0),
                    trigger_price=order.get("trigger_price", 0),
                    filled_quantity=order.get("quantity") if result.get("status") == "filled" else 0,
                    average_price=result.get("fill_price", 0),
                    status=result.get("status", "pending"),
                    broker=result.get("broker", "paper"),
                    strategy_id=order.get("strategy_id"),
                    is_paper=1 if get_broker_config().mode == "paper" else 0,
                    rejection_reason=result.get("reason"),
                )
                session.add(db_order)
                await session.commit()
        except Exception as e:
            logger.error(f"Failed to save order to DB: {e}")


def get_order_router() -> OrderRouter:
    global _order_router
    if _order_router is None:
        _order_router = OrderRouter()
    return _order_router
