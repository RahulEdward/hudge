from typing import Dict, Any, List
from loguru import logger
from backend.ai_core.agents.base_agent import BaseAgent

_agent = None


class PortfolioManagerAgent(BaseAgent):
    name = "portfolio_manager"

    async def handle(self, message: str, session_id: str) -> str:
        summary = await self.get_portfolio_summary()
        return (
            f"**Portfolio Summary**\n"
            f"- Total Value: ₹{summary.get('total_value', 0):,.2f}\n"
            f"- Available Cash: ₹{summary.get('available_cash', 0):,.2f}\n"
            f"- Open Positions: {summary.get('position_count', 0)}\n"
            f"- Total P&L: ₹{summary.get('total_pnl', 0):,.2f} ({summary.get('pnl_pct', 0):.2f}%)"
        )

    async def get_portfolio_summary(self) -> Dict[str, Any]:
        from backend.broker_gateway.broker_manager import get_broker_manager
        bm = get_broker_manager()
        funds = await bm.get_funds()
        positions = await bm.get_positions()

        total_pnl = sum(p.get("pnl", 0) for p in positions)
        capital = funds.get("total_capital", 1000000)

        return {
            "total_value": funds.get("portfolio_value", capital),
            "available_cash": funds.get("available_cash", capital),
            "used_margin": funds.get("used_margin", 0),
            "total_capital": capital,
            "position_count": len(positions),
            "total_pnl": total_pnl,
            "pnl_pct": (total_pnl / capital * 100) if capital else 0,
            "positions": positions,
        }

    async def analyze_allocation(self) -> Dict[str, Any]:
        positions = await self._get_positions()
        total = sum(abs(p.get("quantity", 0) * p.get("average_price", 0)) for p in positions)
        allocation = {}
        for p in positions:
            value = abs(p.get("quantity", 0) * p.get("average_price", 0))
            allocation[p["symbol"]] = round(value / total * 100, 2) if total else 0
        return {"allocation": allocation, "total_invested": total}

    async def _get_positions(self) -> List[Dict]:
        from backend.broker_gateway.broker_manager import get_broker_manager
        return await get_broker_manager().get_positions()


def get_portfolio_agent() -> PortfolioManagerAgent:
    global _agent
    if _agent is None:
        _agent = PortfolioManagerAgent()
    return _agent
