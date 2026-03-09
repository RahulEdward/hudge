import asyncio
from typing import Dict, Any, List
from loguru import logger
from backend.ai_core.agents.base_agent import BaseAgent

_agent = None


class MonitoringAgent(BaseAgent):
    name = "monitoring"
    _running = False

    async def handle(self, message: str, session_id: str) -> str:
        return f"Monitoring Agent is {'running' if self._running else 'stopped'}. Watching all open positions."

    async def start_monitoring(self):
        self._running = True
        asyncio.create_task(self._monitoring_loop())
        logger.info("Monitoring agent started")

    async def stop_monitoring(self):
        self._running = False

    async def _monitoring_loop(self):
        while self._running:
            try:
                await self._check_positions()
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
            await asyncio.sleep(5)

    async def _check_positions(self):
        from backend.broker_gateway.broker_manager import get_broker_manager
        from backend.order_engine.sl_tp_manager import get_sl_tp_manager
        from backend.data_engine.data_cache import get_cache

        bm = get_broker_manager()
        sltp = get_sl_tp_manager()
        cache = get_cache()

        positions = await bm.get_positions()
        for pos in positions:
            symbol = pos.get("symbol")
            quote = await cache.get_quote(symbol) or {}
            current_price = quote.get("ltp", pos.get("average_price", 0))

            # Check SL/TP for managed positions
            for order_id in list(sltp._managed.keys()):
                cfg = sltp._managed.get(order_id, {})
                if cfg.get("symbol") == symbol or True:  # match by order
                    exit_type = await sltp.check_exits(order_id, current_price)
                    if exit_type:
                        await self._handle_exit(pos, exit_type, current_price)

    async def _handle_exit(self, position: Dict, exit_type: str, current_price: float):
        symbol = position.get("symbol")
        qty = position.get("quantity", 0)
        logger.info(f"{exit_type.upper()} triggered for {symbol} @ {current_price}")

        # Execute exit order
        from backend.order_engine.execution_engine import get_execution_engine
        engine = get_execution_engine()
        await engine.execute_trade({
            "symbol": symbol,
            "side": "SELL",
            "quantity": abs(qty),
            "order_type": "MARKET",
        })

        # Send alert
        try:
            from backend.communication_layer.notification_system.alert_manager import get_alert_manager
            am = get_alert_manager()
            await am.send_trade_alert(f"{exit_type.replace('_', ' ').title()} — {symbol} @ {current_price:.2f}")
        except Exception:
            pass


def get_monitoring_agent() -> MonitoringAgent:
    global _agent
    if _agent is None:
        _agent = MonitoringAgent()
    return _agent
