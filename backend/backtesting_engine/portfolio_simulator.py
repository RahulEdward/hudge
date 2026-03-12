"""Portfolio simulator for backtesting — tracks cash, positions, margin, P&L."""

from typing import Dict, Any, List
from loguru import logger


class PortfolioSimulator:
    """Virtual portfolio for backtesting with position tracking and P&L calculation."""

    def __init__(self, initial_capital: float = 1_000_000, commission_pct: float = 0.0003,
                 slippage_pct: float = 0.0005):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.commission_pct = commission_pct
        self.slippage_pct = slippage_pct
        self.positions: Dict[str, Dict] = {}
        self.trade_log: List[Dict] = []
        self.equity_curve: List[Dict] = []
        self._peak_equity = initial_capital

    @property
    def equity(self) -> float:
        unrealized = sum(
            p["quantity"] * (p["current_price"] - p["avg_price"])
            for p in self.positions.values()
        )
        return self.cash + unrealized

    @property
    def drawdown(self) -> float:
        equity = self.equity
        if equity > self._peak_equity:
            self._peak_equity = equity
        return (self._peak_equity - equity) / self._peak_equity if self._peak_equity > 0 else 0

    def open_position(self, symbol: str, side: str, quantity: int, price: float, timestamp: str = "") -> Dict:
        """Open or add to a position."""
        # Apply slippage
        fill_price = price * (1 + self.slippage_pct) if side == "BUY" else price * (1 - self.slippage_pct)
        commission = fill_price * quantity * self.commission_pct
        total_cost = fill_price * quantity + commission

        if side == "BUY" and total_cost > self.cash:
            return {"error": "Insufficient funds"}

        if symbol in self.positions:
            pos = self.positions[symbol]
            if side == "BUY":
                total_qty = pos["quantity"] + quantity
                pos["avg_price"] = ((pos["avg_price"] * pos["quantity"]) + (fill_price * quantity)) / total_qty
                pos["quantity"] = total_qty
            else:
                pos["quantity"] -= quantity
                if pos["quantity"] <= 0:
                    del self.positions[symbol]
        else:
            self.positions[symbol] = {
                "symbol": symbol,
                "side": side,
                "quantity": quantity,
                "avg_price": fill_price,
                "current_price": fill_price,
                "entry_time": timestamp,
            }

        self.cash -= total_cost if side == "BUY" else -(fill_price * quantity - commission)

        trade = {
            "symbol": symbol, "side": side, "quantity": quantity,
            "price": round(fill_price, 2), "commission": round(commission, 2),
            "timestamp": timestamp,
        }
        self.trade_log.append(trade)
        return trade

    def close_position(self, symbol: str, price: float, timestamp: str = "") -> Dict:
        """Close an entire position."""
        if symbol not in self.positions:
            return {"error": "No position to close"}

        pos = self.positions[symbol]
        side = "SELL" if pos["side"] == "BUY" else "BUY"
        fill_price = price * (1 - self.slippage_pct) if side == "SELL" else price * (1 + self.slippage_pct)
        commission = fill_price * pos["quantity"] * self.commission_pct
        pnl = (fill_price - pos["avg_price"]) * pos["quantity"] - commission

        self.cash += fill_price * pos["quantity"] - commission

        trade = {
            "symbol": symbol, "side": side, "quantity": pos["quantity"],
            "price": round(fill_price, 2), "pnl": round(pnl, 2),
            "commission": round(commission, 2), "timestamp": timestamp,
        }
        self.trade_log.append(trade)
        del self.positions[symbol]
        return trade

    def update_prices(self, prices: Dict[str, float], timestamp: str = ""):
        """Update current prices for all positions."""
        for symbol, price in prices.items():
            if symbol in self.positions:
                self.positions[symbol]["current_price"] = price

        self.equity_curve.append({
            "timestamp": timestamp,
            "equity": round(self.equity, 2),
            "cash": round(self.cash, 2),
            "drawdown": round(self.drawdown * 100, 2),
        })

    def get_summary(self) -> Dict:
        return {
            "initial_capital": self.initial_capital,
            "current_equity": round(self.equity, 2),
            "cash": round(self.cash, 2),
            "total_pnl": round(self.equity - self.initial_capital, 2),
            "return_pct": round((self.equity / self.initial_capital - 1) * 100, 2),
            "max_drawdown": round(self.drawdown * 100, 2),
            "open_positions": len(self.positions),
            "total_trades": len(self.trade_log),
        }

    def reset(self):
        self.cash = self.initial_capital
        self.positions.clear()
        self.trade_log.clear()
        self.equity_curve.clear()
        self._peak_equity = self.initial_capital
