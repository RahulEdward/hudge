from typing import Dict, Any
from loguru import logger
from backend.ai_core.agents.base_agent import BaseAgent

_agent = None


class RiskManagementAgent(BaseAgent):
    name = "risk_management"

    async def handle(self, message: str, session_id: str) -> str:
        from backend.order_engine.risk_engine import get_risk_engine
        risk = get_risk_engine()
        return (
            f"**Risk Status**\n"
            f"- Kill Switch: {'ACTIVE' if risk.is_kill_switch_active() else 'OFF'}\n"
            f"- Daily Loss: {risk._daily_loss:.1%}\n"
            f"- Open Positions: {risk._open_positions}/{risk.max_positions}\n"
            f"- Max Risk/Trade: {risk.max_risk_per_trade:.1%}"
        )

    async def check(self, order: Dict[str, Any]) -> Dict[str, Any]:
        from backend.order_engine.risk_engine import get_risk_engine
        risk = get_risk_engine()
        valid, reason = await risk.validate_order(order)
        return {"valid": valid, "reason": reason}

    async def calculate_position_size(self, capital: float, entry: float,
                                      stop_loss: float, risk_pct: float = 1.0) -> int:
        from backend.order_engine.risk_engine import get_risk_engine
        risk = get_risk_engine()
        return risk.calculate_position_size(capital, risk_pct / 100, entry, stop_loss)

    async def get_risk_score(self, strategy: Dict[str, Any]) -> float:
        """Score 0-100 (lower = safer)."""
        llm = await self.get_llm()
        prompt = f"Rate the risk of this trading strategy from 0-100 (0=safest): {strategy}"
        response = await llm.generate_text(prompt)
        try:
            import re
            nums = re.findall(r'\d+\.?\d*', response)
            score = float(nums[0]) if nums else 50.0
            return min(100, max(0, score))
        except Exception:
            return 50.0


def get_risk_agent() -> RiskManagementAgent:
    global _agent
    if _agent is None:
        _agent = RiskManagementAgent()
    return _agent
