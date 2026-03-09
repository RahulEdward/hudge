from typing import Dict, Any
from loguru import logger
from backend.ai_core.agents.base_agent import BaseAgent

_agent = None


class ExecutionAgent(BaseAgent):
    name = "execution"

    async def handle(self, message: str, session_id: str) -> str:
        # Parse trade intent from message
        llm = await self.get_llm()
        prompt = f"""Parse this trading instruction and extract JSON with fields:
symbol, side (BUY/SELL), quantity, order_type (MARKET/LIMIT), price (0 if MARKET)

Instruction: {message}

Return ONLY JSON."""
        response = await llm.generate_text(prompt)
        try:
            import json, re
            match = re.search(r'\{.*\}', response, re.DOTALL)
            if match:
                order = json.loads(match.group())
                result = await self.execute_trade(order)
                return f"Trade executed: {result.get('status', 'unknown').upper()} — {result}"
        except Exception as e:
            pass
        return "Could not parse trade instruction. Please specify: symbol, side (BUY/SELL), quantity."

    async def execute_trade(self, trade_request: Dict[str, Any]) -> Dict[str, Any]:
        from backend.order_engine.execution_engine import get_execution_engine
        engine = get_execution_engine()
        return await engine.execute_trade(trade_request)

    async def confirm_execution(self, order_id: str) -> Dict[str, Any]:
        from backend.order_engine.execution_engine import get_execution_engine
        engine = get_execution_engine()
        return await engine.confirm_execution(order_id)


def get_execution_agent() -> ExecutionAgent:
    global _agent
    if _agent is None:
        _agent = ExecutionAgent()
    return _agent
