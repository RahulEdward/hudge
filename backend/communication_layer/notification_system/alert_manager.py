import uuid
from datetime import datetime
from typing import List, Dict, Any
from loguru import logger
from backend.config import get_system_config

_alert_manager = None


class AlertManager:
    """Central alert dispatcher for multi-channel notifications."""

    async def send_alert(self, title: str, message: str, priority: str = "normal",
                         channels: List[str] = None, alert_type: str = "system") -> str:
        alert_id = str(uuid.uuid4())[:12]
        cfg = get_system_config()
        channels = channels or self._default_channels(cfg)

        # Save to DB
        await self._save_alert(alert_id, alert_type, title, message, priority, channels)

        # Desktop notification (logged)
        if "desktop" in channels:
            logger.info(f"[ALERT][{priority.upper()}] {title}: {message}")

        # Telegram
        if "telegram" in channels and cfg.telegram.enabled:
            await self._send_telegram(f"*{title}*\n{message}")

        return alert_id

    async def send_trade_alert(self, message: str):
        await self.send_alert("Trade Update", message, priority="high",
                               channels=["desktop", "telegram"], alert_type="trade")

    async def send_daily_report(self, report: str):
        await self.send_alert("Daily Report", report, priority="normal",
                               channels=["desktop", "telegram"], alert_type="report")

    def _default_channels(self, cfg) -> List[str]:
        channels = []
        if cfg.alerts.desktop:
            channels.append("desktop")
        if cfg.alerts.telegram and cfg.telegram.enabled:
            channels.append("telegram")
        if cfg.alerts.whatsapp and cfg.whatsapp.enabled:
            channels.append("whatsapp")
        return channels or ["desktop"]

    async def _send_telegram(self, message: str):
        try:
            from backend.communication_layer.telegram_bot.bot_handler import get_telegram_bot
            bot = get_telegram_bot()
            if bot:
                await bot.broadcast(message)
        except Exception as e:
            logger.warning(f"Telegram alert failed: {e}")

    async def _save_alert(self, alert_id: str, alert_type: str, title: str,
                           message: str, priority: str, channels: List[str]):
        try:
            from backend.database.connection import get_session
            from backend.database.models.alert import Alert
            async for session in get_session():
                alert = Alert(
                    alert_id=alert_id,
                    alert_type=alert_type,
                    title=title,
                    message=message,
                    priority=priority,
                    channels=channels,
                )
                session.add(alert)
                await session.commit()
        except Exception:
            pass

    async def broadcast_to_websocket(self, message: str, data: Dict[str, Any] = None):
        try:
            from backend.api_server.websocket_server import get_ws_manager
            ws = get_ws_manager()
            await ws.broadcast({"type": "alert", "message": message, "data": data or {}}, "trades")
        except Exception:
            pass


def get_alert_manager() -> AlertManager:
    global _alert_manager
    if _alert_manager is None:
        _alert_manager = AlertManager()
    return _alert_manager
