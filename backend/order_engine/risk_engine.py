from typing import Dict, Any, Tuple
from loguru import logger
from backend.config import get_system_config

_risk_engine = None


class RiskEngine:
    """Pre-trade risk validation and kill switch management."""

    def __init__(self):
        cfg = get_system_config().risk
        self.max_risk_per_trade = cfg.max_risk_per_trade
        self.max_daily_loss = cfg.max_daily_loss
        self.max_positions = cfg.max_positions
        self.kill_switch_drawdown = cfg.kill_switch_drawdown
        self._kill_switch_active = False
        self._daily_loss = 0.0
        self._daily_pnl = 0.0
        self._open_positions = 0

    def is_kill_switch_active(self) -> bool:
        return self._kill_switch_active

    async def activate_kill_switch(self):
        self._kill_switch_active = True
        logger.warning("KILL SWITCH ACTIVATED — all trading halted")
        try:
            from backend.api_server.websocket_server import get_ws_manager
            await get_ws_manager().broadcast(
                {"type": "kill_switch", "message": "Kill switch activated"}, "trades"
            )
        except Exception:
            pass

    def deactivate_kill_switch(self):
        self._kill_switch_active = False
        logger.info("Kill switch deactivated")

    async def validate_order(self, order: Dict[str, Any]) -> Tuple[bool, str]:
        """Returns (is_valid, rejection_reason)."""
        if self._kill_switch_active:
            return False, "Kill switch is active — trading halted"

        qty = order.get("quantity", 0)
        price = order.get("price") or 0
        symbol = order.get("symbol", "")

        if qty <= 0:
            return False, "Quantity must be positive"

        # Check daily loss limit
        if self._daily_loss >= self.max_daily_loss:
            return False, f"Daily loss limit reached ({self._daily_loss:.1%})"

        # Check max positions
        if self._open_positions >= self.max_positions and order.get("side") == "BUY":
            return False, f"Max concurrent positions ({self.max_positions}) reached"

        # Estimate trade risk
        if price > 0:
            try:
                from backend.broker_gateway.broker_manager import get_broker_manager
                funds = await get_broker_manager().get_funds()
                capital = funds.get("total_capital", 1000000)
                trade_value = qty * price
                trade_risk_pct = trade_value / capital
                if trade_risk_pct > self.max_risk_per_trade * 10:
                    return False, f"Trade size too large: {trade_risk_pct:.1%} of capital"
            except Exception:
                pass

        return True, ""

    def calculate_position_size(self, capital: float, risk_pct: float, entry: float, stop_loss: float) -> int:
        """Kelly/Risk-based position sizing."""
        if stop_loss <= 0 or entry <= 0:
            return 1
        risk_amount = capital * risk_pct
        risk_per_share = abs(entry - stop_loss)
        if risk_per_share == 0:
            return 1
        return max(1, int(risk_amount / risk_per_share))

    def update_daily_pnl(self, pnl: float):
        self._daily_pnl += pnl
        if pnl < 0:
            self._daily_loss += abs(pnl)

    def update_position_count(self, delta: int):
        self._open_positions = max(0, self._open_positions + delta)


def get_risk_engine() -> RiskEngine:
    global _risk_engine
    if _risk_engine is None:
        _risk_engine = RiskEngine()
    return _risk_engine
