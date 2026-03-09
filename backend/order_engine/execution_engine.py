import asyncio
from typing import Dict, Any
from loguru import logger

_execution_engine = None


class ExecutionEngine:
    """Core order executor — bridges AI decisions to broker gateway."""

    async def execute_trade(self, trade_request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a trade from an AI agent decision."""
        from backend.order_engine.order_router import get_order_router
        router = get_order_router()
        result = await router.place_order(trade_request)

        if result.get("status") in ("filled", "placed"):
            # Register SL/TP management
            if trade_request.get("stop_loss") or trade_request.get("take_profit"):
                from backend.order_engine.sl_tp_manager import get_sl_tp_manager
                sltp = get_sl_tp_manager()
                fill_price = result.get("fill_price", trade_request.get("price", 0))
                sltp.register(
                    order_id=result["order_id"],
                    entry_price=fill_price,
                    side=trade_request["side"],
                    sl_value=trade_request.get("stop_loss_pct", 1.0),
                    tp_value=trade_request.get("take_profit_rr", 2.0),
                    trailing=trade_request.get("trailing_stop", False),
                )

            # Send alert
            try:
                from backend.communication_layer.notification_system.alert_manager import get_alert_manager
                am = get_alert_manager()
                await am.send_trade_alert(
                    f"{trade_request['side']} {trade_request['quantity']} {trade_request['symbol']} "
                    f"@ {result.get('fill_price', 'MKT')} — {result['status'].upper()}"
                )
            except Exception:
                pass

        logger.info(f"Trade executed: {result}")
        return result

    async def confirm_execution(self, order_id: str) -> Dict[str, Any]:
        from backend.broker_gateway.broker_manager import get_broker_manager
        bm = get_broker_manager()
        return await bm.get_active().get_order_status(order_id)


def get_execution_engine() -> ExecutionEngine:
    global _execution_engine
    if _execution_engine is None:
        _execution_engine = ExecutionEngine()
    return _execution_engine
