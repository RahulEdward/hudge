"""Trade update formatter — generates formatted alert messages for trade events."""

from typing import Dict, Any
from datetime import datetime


class TradeUpdates:
    """Formats trade event messages for multi-channel delivery."""

    def order_placed(self, order: Dict[str, Any]) -> str:
        symbol = order.get("symbol", "???")
        side = order.get("side", "???")
        qty = order.get("quantity", 0)
        price = order.get("price", "Market")
        mode = order.get("mode", "paper").upper()
        order_type = order.get("order_type", "MARKET")

        icon = "🟢" if side == "BUY" else "🔴"
        return (
            f"{icon} **Order Placed**\n"
            f"━━━━━━━━━━━━━━━\n"
            f"Symbol: {symbol}\n"
            f"Side: {side} | Type: {order_type}\n"
            f"Qty: {qty} | Price: ₹{price}\n"
            f"Mode: {mode}\n"
            f"Time: {datetime.now().strftime('%H:%M:%S')}"
        )

    def order_filled(self, order: Dict[str, Any]) -> str:
        symbol = order.get("symbol", "???")
        side = order.get("side", "???")
        qty = order.get("quantity", 0)
        fill_price = order.get("executed_price", order.get("price", 0))
        order_id = order.get("order_id", "N/A")

        icon = "✅"
        return (
            f"{icon} **Order Filled**\n"
            f"━━━━━━━━━━━━━━━\n"
            f"Symbol: {symbol}\n"
            f"Side: {side} | Qty: {qty}\n"
            f"Fill Price: ₹{fill_price}\n"
            f"Order ID: {order_id}\n"
            f"Time: {datetime.now().strftime('%H:%M:%S')}"
        )

    def sl_triggered(self, position: Dict[str, Any]) -> str:
        symbol = position.get("symbol", "???")
        sl_price = position.get("sl_price", 0)
        pnl = position.get("pnl", 0)
        pnl_icon = "📉" if pnl < 0 else "📈"

        return (
            f"🛑 **Stop-Loss Triggered**\n"
            f"━━━━━━━━━━━━━━━\n"
            f"Symbol: {symbol}\n"
            f"SL Price: ₹{sl_price}\n"
            f"P&L: {pnl_icon} ₹{pnl:,.2f}\n"
            f"Time: {datetime.now().strftime('%H:%M:%S')}"
        )

    def tp_triggered(self, position: Dict[str, Any]) -> str:
        symbol = position.get("symbol", "???")
        tp_price = position.get("tp_price", 0)
        pnl = position.get("pnl", 0)

        return (
            f"🎯 **Target Hit!**\n"
            f"━━━━━━━━━━━━━━━\n"
            f"Symbol: {symbol}\n"
            f"Target Price: ₹{tp_price}\n"
            f"P&L: 📈 ₹{pnl:,.2f}\n"
            f"Time: {datetime.now().strftime('%H:%M:%S')}"
        )

    def daily_summary(self, data: Dict[str, Any]) -> str:
        total_pnl = data.get("total_pnl", 0)
        trades = data.get("total_trades", 0)
        wins = data.get("wins", 0)
        losses = data.get("losses", 0)
        win_rate = (wins / trades * 100) if trades > 0 else 0

        pnl_icon = "🟢" if total_pnl >= 0 else "🔴"
        return (
            f"📋 **Daily Performance Summary**\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Date: {datetime.now().strftime('%d %b %Y')}\n"
            f"P&L: {pnl_icon} ₹{total_pnl:,.2f}\n"
            f"Trades: {trades} (W:{wins} L:{losses})\n"
            f"Win Rate: {win_rate:.1f}%\n"
            f"━━━━━━━━━━━━━━━━━━━━━━"
        )

    def kill_switch_activated(self, data: Dict[str, Any]) -> str:
        drawdown = data.get("drawdown", 0)
        return (
            f"🚨 **KILL SWITCH ACTIVATED** 🚨\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Portfolio drawdown: {drawdown:.1f}%\n"
            f"ALL trading has been STOPPED.\n"
            f"Manual reset required in Settings.\n"
            f"Time: {datetime.now().strftime('%H:%M:%S')}"
        )


_updates = None


def get_trade_updates() -> TradeUpdates:
    global _updates
    if _updates is None:
        _updates = TradeUpdates()
    return _updates
