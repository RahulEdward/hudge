"""NLP command parser — intent detection and entity extraction from user messages."""

import re
from typing import Dict, Any, Optional, List
from loguru import logger


class CommandParser:
    """Parses user messages and slash commands into structured intents."""

    INTENT_KEYWORDS = {
        "market_analysis": ["analyze", "analysis", "trend", "market", "outlook", "nifty", "banknifty", "chart"],
        "backtest_request": ["backtest", "test strategy", "historical", "simulate"],
        "trade_execution": ["execute", "buy", "sell", "trade", "order", "place order"],
        "portfolio_request": ["portfolio", "holdings", "positions", "allocation", "what do i hold"],
        "strategy_request": ["strategy", "discover", "find strategy", "create strategy"],
        "risk_query": ["risk", "exposure", "drawdown", "set max risk", "stop loss"],
        "status_query": ["status", "system", "agents", "active trades", "running"],
        "stop_command": ["stop", "kill", "halt", "emergency", "kill switch"],
        "report_request": ["report", "summary", "pnl", "profit", "loss", "daily report"],
    }

    SLASH_COMMANDS = {
        "/start": "status_query",
        "/analyze": "market_analysis",
        "/backtest": "backtest_request",
        "/trade": "trade_execution",
        "/portfolio": "portfolio_request",
        "/status": "status_query",
        "/stop": "stop_command",
        "/report": "report_request",
        "/strategy": "strategy_request",
        "/risk": "risk_query",
    }

    KNOWN_SYMBOLS = [
        "NIFTY", "BANKNIFTY", "FINNIFTY", "RELIANCE", "TCS", "INFY", "HDFCBANK",
        "ICICIBANK", "SBIN", "HINDUNILVR", "ITC", "LT", "KOTAKBANK", "AXISBANK",
        "BHARTIARTL", "BAJFINANCE", "MARUTI", "TATAMOTORS", "TITAN", "WIPRO",
    ]

    def parse(self, message: str) -> Dict[str, Any]:
        """Parse a message into intent + entities."""
        message = message.strip()

        # Check slash commands first
        if message.startswith("/"):
            return self._parse_slash_command(message)

        # NLP-based intent detection
        intent = self._detect_intent(message)
        entities = self._extract_entities(message)

        return {
            "intent": intent,
            "entities": entities,
            "raw_message": message,
            "confidence": 0.8 if intent != "general" else 0.3,
        }

    def _parse_slash_command(self, message: str) -> Dict[str, Any]:
        parts = message.split(maxsplit=2)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        extra = parts[2] if len(parts) > 2 else ""

        intent = self.SLASH_COMMANDS.get(command, "general")
        entities = self._extract_entities(f"{args} {extra}")

        return {
            "intent": intent,
            "entities": entities,
            "raw_message": message,
            "command": command,
            "confidence": 0.95,
        }

    def _detect_intent(self, message: str) -> str:
        msg_lower = message.lower()
        best_intent = "general"
        best_score = 0

        for intent, keywords in self.INTENT_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in msg_lower)
            if score > best_score:
                best_score = score
                best_intent = intent

        return best_intent

    def _extract_entities(self, message: str) -> Dict[str, Any]:
        entities: Dict[str, Any] = {}
        msg_upper = message.upper()

        # Extract symbols
        symbols = [s for s in self.KNOWN_SYMBOLS if s in msg_upper]
        if symbols:
            entities["symbol"] = symbols[0]
            entities["symbols"] = symbols

        # Extract timeframe
        tf_patterns = {
            r"(\d+)\s*(?:year|yr|y)": lambda m: f"{m.group(1)}Y",
            r"(\d+)\s*(?:month|mo|m(?!in))": lambda m: f"{m.group(1)}M",
            r"(\d+)\s*(?:day|d)": lambda m: f"{m.group(1)}D",
            r"(\d+)\s*(?:hour|hr|h)": lambda m: f"{m.group(1)}h",
            r"(\d+)\s*(?:min|minute)": lambda m: f"{m.group(1)}m",
        }
        for pattern, formatter in tf_patterns.items():
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                entities["timeframe"] = formatter(match)
                break

        # Extract risk percentage
        risk_match = re.search(r"(\d+(?:\.\d+)?)\s*%\s*risk", message, re.IGNORECASE)
        if risk_match:
            entities["risk_pct"] = float(risk_match.group(1)) / 100

        # Extract quantity
        qty_match = re.search(r"(\d+)\s*(?:lot|share|qty|quantity)", message, re.IGNORECASE)
        if qty_match:
            entities["quantity"] = int(qty_match.group(1))

        # Extract side
        msg_lower = message.lower()
        if "buy" in msg_lower or "long" in msg_lower:
            entities["side"] = "BUY"
        elif "sell" in msg_lower or "short" in msg_lower:
            entities["side"] = "SELL"

        return entities


_parser = None


def get_command_parser() -> CommandParser:
    global _parser
    if _parser is None:
        _parser = CommandParser()
    return _parser
