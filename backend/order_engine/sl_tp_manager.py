from typing import Dict, Any, Optional
from loguru import logger


class SLTPManager:
    """Manages Stop-Loss and Take-Profit levels for open positions."""

    def __init__(self):
        self._managed: Dict[str, Dict] = {}  # order_id → SL/TP config

    def register(self, order_id: str, entry_price: float, side: str,
                 sl_type: str = "percentage", sl_value: float = 1.0,
                 tp_type: str = "rr", tp_value: float = 2.0,
                 trailing: bool = False, atr: float = None):
        """Register a position for SL/TP management."""
        config = {
            "order_id": order_id,
            "entry_price": entry_price,
            "side": side,
            "sl_type": sl_type,
            "sl_value": sl_value,
            "tp_type": tp_type,
            "tp_value": tp_value,
            "trailing": trailing,
            "atr": atr,
            "current_sl": self._calc_sl(entry_price, side, sl_type, sl_value, atr),
            "current_tp": self._calc_tp(entry_price, side, sl_type, sl_value, tp_type, tp_value, atr),
            "peak_price": entry_price,
        }
        self._managed[order_id] = config
        logger.debug(f"SL/TP registered for {order_id}: SL={config['current_sl']:.2f}, TP={config['current_tp']:.2f}")

    def _calc_sl(self, entry: float, side: str, sl_type: str, sl_value: float, atr: float = None) -> float:
        if sl_type == "percentage":
            offset = entry * (sl_value / 100)
        elif sl_type == "atr" and atr:
            offset = atr * sl_value
        else:
            offset = entry * 0.01

        return entry - offset if side == "BUY" else entry + offset

    def _calc_tp(self, entry: float, side: str, sl_type: str, sl_value: float,
                 tp_type: str, tp_value: float, atr: float = None) -> float:
        sl = self._calc_sl(entry, side, sl_type, sl_value, atr)
        risk = abs(entry - sl)
        if tp_type == "rr":
            return entry + risk * tp_value if side == "BUY" else entry - risk * tp_value
        elif tp_type == "percentage":
            offset = entry * (tp_value / 100)
            return entry + offset if side == "BUY" else entry - offset
        return entry + risk * 2 if side == "BUY" else entry - risk * 2

    async def check_exits(self, order_id: str, current_price: float) -> Optional[str]:
        """Returns 'sl_hit', 'tp_hit', or None."""
        cfg = self._managed.get(order_id)
        if not cfg:
            return None

        side = cfg["side"]

        # Update trailing stop
        if cfg["trailing"]:
            self._update_trailing(cfg, current_price)

        sl = cfg["current_sl"]
        tp = cfg["current_tp"]

        if side == "BUY":
            if current_price <= sl:
                del self._managed[order_id]
                return "sl_hit"
            if current_price >= tp:
                del self._managed[order_id]
                return "tp_hit"
        else:
            if current_price >= sl:
                del self._managed[order_id]
                return "sl_hit"
            if current_price <= tp:
                del self._managed[order_id]
                return "tp_hit"

        return None

    def _update_trailing(self, cfg: Dict, price: float):
        side = cfg["side"]
        entry = cfg["entry_price"]
        sl_offset = abs(entry - cfg["current_sl"])

        if side == "BUY" and price > cfg["peak_price"]:
            cfg["peak_price"] = price
            new_sl = price - sl_offset
            if new_sl > cfg["current_sl"]:
                cfg["current_sl"] = new_sl
        elif side == "SELL" and price < cfg["peak_price"]:
            cfg["peak_price"] = price
            new_sl = price + sl_offset
            if new_sl < cfg["current_sl"]:
                cfg["current_sl"] = new_sl

    def remove(self, order_id: str):
        self._managed.pop(order_id, None)


_sl_tp_manager = None


def get_sl_tp_manager() -> SLTPManager:
    global _sl_tp_manager
    if _sl_tp_manager is None:
        _sl_tp_manager = SLTPManager()
    return _sl_tp_manager
