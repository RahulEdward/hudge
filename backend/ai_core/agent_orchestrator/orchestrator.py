import asyncio
from typing import Dict, Any, List, AsyncGenerator, Optional
from loguru import logger

_orchestrator = None


class AgentOrchestrator:
    """Master orchestrator — routes messages to appropriate agents."""

    def __init__(self):
        self._agents: Dict[str, Any] = {}
        self._initialized = False

    async def initialize(self):
        """Load all enabled agents."""
        from backend.config import get_ai_config
        cfg = get_ai_config()
        agent_map = {
            "market_analysis": ("backend.ai_core.agents.market_analysis_agent.agent", "get_market_analysis_agent"),
            "strategy_discovery": ("backend.ai_core.agents.strategy_agent.agent", "get_strategy_agent"),
            "risk_management": ("backend.ai_core.agents.risk_agent.agent", "get_risk_agent"),
            "execution": ("backend.ai_core.agents.execution_agent.agent", "get_execution_agent"),
            "portfolio_manager": ("backend.ai_core.agents.portfolio_agent.agent", "get_portfolio_agent"),
            "monitoring": ("backend.ai_core.agents.monitoring_agent.agent", "get_monitoring_agent"),
            "reporting": ("backend.ai_core.agents.reporting_agent.agent", "get_reporting_agent"),
            "data_agent": ("backend.ai_core.agents.data_agent.agent", "get_data_agent"),
        }
        for name, (module_path, func_name) in agent_map.items():
            agent_cfg = cfg.agents.get(name)
            if agent_cfg and not agent_cfg.enabled:
                continue
            try:
                import importlib
                module = importlib.import_module(module_path)
                agent = getattr(module, func_name)()
                self._agents[name] = agent
                logger.info(f"Agent loaded: {name}")
            except Exception as e:
                logger.warning(f"Agent {name} not loaded: {e}")

        self._initialized = True
        logger.info(f"Orchestrator initialized with {len(self._agents)} agents")

    def get_status(self) -> Dict[str, Any]:
        return {
            name: {"status": "active", "type": type(agent).__name__}
            for name, agent in self._agents.items()
        }

    async def handle_message(self, message: str, session_id: str, channel: str = "desktop") -> str:
        """Route a user message to the appropriate agent."""
        # Save to conversation history
        await self._save_message(session_id, "user", message, channel)

        intent = self._detect_intent(message)
        agent_name = self._route_intent(intent)
        agent = self._agents.get(agent_name)

        if agent:
            try:
                response = await agent.handle(message, session_id)
            except Exception as e:
                response = f"Agent error: {e}"
        else:
            # Fallback: use LLM directly
            response = await self._llm_fallback(message, session_id)

        await self._save_message(session_id, "assistant", response, channel, agent_name)
        return response

    async def stream_message(self, message: str, session_id: str) -> AsyncGenerator[str, None]:
        """Stream response tokens for WebSocket."""
        from backend.ai_core.llm_connectors.provider import get_llm
        llm = get_llm()
        history = await self._get_history(session_id)
        prompt = self._build_prompt(message, history)
        async for chunk in llm.stream_response(prompt):
            yield chunk

    async def run_task(self, task_type: str, params: Dict[str, Any]) -> Any:
        """Run a specific agent task."""
        task_map = {
            "analyze_market": ("market_analysis", "analyze"),
            "discover_strategy": ("strategy_discovery", "discover"),
            "run_backtest": ("backtesting", "backtest"),
            "check_risk": ("risk_management", "check"),
            "generate_report": ("reporting", "generate"),
        }
        agent_name, method = task_map.get(task_type, (None, None))
        if agent_name and agent_name in self._agents:
            agent = self._agents[agent_name]
            if hasattr(agent, method):
                return await getattr(agent, method)(**params)
        return {"error": f"Unknown task: {task_type}"}

    def _detect_intent(self, message: str) -> str:
        msg = message.lower()
        if any(w in msg for w in ["analyze", "trend", "market", "nifty", "banknifty", "chart"]):
            return "market_analysis"
        if any(w in msg for w in ["strategy", "discover", "find strategy", "create strategy"]):
            return "strategy_discovery"
        if any(w in msg for w in ["backtest", "test strategy", "performance", "historical"]):
            return "backtesting"
        if any(w in msg for w in ["buy", "sell", "trade", "order", "execute"]):
            return "execution"
        if any(w in msg for w in ["portfolio", "holdings", "positions", "allocation"]):
            return "portfolio_manager"
        if any(w in msg for w in ["report", "summary", "pnl", "profit", "loss"]):
            return "reporting"
        if any(w in msg for w in ["risk", "stop loss", "drawdown"]):
            return "risk_management"
        return "general"

    def _route_intent(self, intent: str) -> str:
        return intent if intent in self._agents else "general"

    async def _llm_fallback(self, message: str, session_id: str) -> str:
        from backend.ai_core.llm_connectors.provider import get_llm
        llm = get_llm()
        history = await self._get_history(session_id)
        prompt = self._build_prompt(message, history)
        return await llm.generate_text(prompt)

    def _build_prompt(self, message: str, history: List[Dict]) -> str:
        ctx = "\n".join(f"{m['role'].upper()}: {m['content']}" for m in history[-10:])
        return f"{ctx}\nUSER: {message}\nASSISTANT:" if ctx else message

    async def _save_message(self, session_id: str, role: str, content: str, channel: str, agent_id: str = None):
        try:
            from backend.database.connection import get_session
            from backend.database.repositories import ConversationRepository
            async for session in get_session():
                repo = ConversationRepository(session)
                await repo.add_message(session_id, role, content, channel, agent_id)
        except Exception:
            pass

    async def _get_history(self, session_id: str) -> List[Dict]:
        try:
            from backend.database.connection import get_session
            from backend.database.repositories import ConversationRepository
            async for session in get_session():
                repo = ConversationRepository(session)
                msgs = await repo.get_session_history(session_id, limit=20)
                return [{"role": m.role, "content": m.content} for m in msgs]
        except Exception:
            return []


def get_orchestrator() -> AgentOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AgentOrchestrator()
    return _orchestrator
