"""WhatsApp message router — routes incoming messages to orchestrator."""

from typing import Dict, Any
from loguru import logger


class WhatsAppMessageRouter:
    """Routes incoming WhatsApp messages through command parser to orchestrator."""

    def __init__(self):
        self._orchestrator = None

    async def route_message(self, message: Dict[str, Any]) -> str:
        """Parse and route an incoming WhatsApp message."""
        content = message.get("content", "")
        sender = message.get("sender", "unknown")

        # Parse intent
        from backend.communication_layer.command_parser import get_command_parser
        parser = get_command_parser()
        parsed = parser.parse(content)

        # Route to orchestrator
        from backend.ai_core.agent_orchestrator.orchestrator import get_orchestrator
        orchestrator = get_orchestrator()
        session_id = f"whatsapp_{sender}"

        try:
            response = await orchestrator.handle_message(content, session_id, channel="whatsapp")
        except Exception as e:
            logger.error(f"WhatsApp routing error: {e}")
            response = "Sorry, I encountered an error processing your message."

        # Format for WhatsApp
        return self._format_response(response, parsed.get("intent", "general"))

    def _format_response(self, response: str, intent: str) -> str:
        """Format response for WhatsApp with emojis and line breaks."""
        icon_map = {
            "market_analysis": "📊",
            "backtest_request": "📈",
            "trade_execution": "⚡",
            "portfolio_request": "💼",
            "strategy_request": "🎯",
            "risk_query": "🛡️",
            "status_query": "🖥️",
            "stop_command": "🛑",
            "report_request": "📋",
        }
        icon = icon_map.get(intent, "🤖")
        return f"{icon} {response}"
