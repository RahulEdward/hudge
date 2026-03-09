from datetime import datetime, timedelta
from typing import Dict, Any
from loguru import logger
from backend.ai_core.agents.base_agent import BaseAgent

_agent = None


class ReportingAgent(BaseAgent):
    name = "reporting"

    async def handle(self, message: str, session_id: str) -> str:
        report = await self.generate_daily_report()
        return report.get("summary", "Report generated.")

    async def generate_daily_report(self) -> Dict[str, Any]:
        from backend.database.connection import get_session
        from backend.database.repositories import TradeRepository
        from backend.ai_core.agents.portfolio_agent.agent import get_portfolio_agent

        portfolio_agent = get_portfolio_agent()
        portfolio = await portfolio_agent.get_portfolio_summary()

        trades = []
        try:
            async for session in get_session():
                repo = TradeRepository(session)
                trades = await repo.get_recent(limit=50)
        except Exception:
            pass

        today_trades = [t for t in trades if t.executed_at and
                       t.executed_at.date() == datetime.utcnow().date()]

        total_pnl = sum(t.pnl for t in today_trades)
        win_trades = [t for t in today_trades if t.pnl > 0]
        win_rate = len(win_trades) / len(today_trades) * 100 if today_trades else 0

        summary = (
            f"**Daily Report — {datetime.now().strftime('%d %b %Y')}**\n"
            f"- Trades Today: {len(today_trades)}\n"
            f"- Win Rate: {win_rate:.1f}%\n"
            f"- Today's P&L: ₹{total_pnl:,.2f}\n"
            f"- Portfolio Value: ₹{portfolio.get('total_value', 0):,.2f}\n"
            f"- Open Positions: {portfolio.get('position_count', 0)}"
        )

        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "total_trades": len(today_trades),
            "win_rate": win_rate,
            "total_pnl": total_pnl,
            "portfolio": portfolio,
            "summary": summary,
        }

    async def generate(self, **kwargs) -> Dict[str, Any]:
        return await self.generate_daily_report()


def get_reporting_agent() -> ReportingAgent:
    global _agent
    if _agent is None:
        _agent = ReportingAgent()
    return _agent
