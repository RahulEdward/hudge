from typing import Optional, List
from loguru import logger

_bot = None


class TelegramBot:
    def __init__(self, token: str, authorized_users: List[int]):
        self.token = token
        self.authorized_users = authorized_users
        self.app = None
        self._chat_ids = set()

    async def start(self):
        try:
            from telegram.ext import Application, CommandHandler, MessageHandler, filters
            self.app = Application.builder().token(self.token).build()
            self.app.add_handler(CommandHandler("start", self._cmd_start))
            self.app.add_handler(CommandHandler("analyze", self._cmd_analyze))
            self.app.add_handler(CommandHandler("portfolio", self._cmd_portfolio))
            self.app.add_handler(CommandHandler("status", self._cmd_status))
            self.app.add_handler(CommandHandler("report", self._cmd_report))
            self.app.add_handler(CommandHandler("stop", self._cmd_stop_trading))
            self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message))
            await self.app.initialize()
            await self.app.start()
            await self.app.updater.start_polling(drop_pending_updates=True)
            logger.info("Telegram bot started")
        except Exception as e:
            logger.error(f"Telegram bot failed to start: {e}")

    async def stop(self):
        if self.app:
            await self.app.stop()

    async def broadcast(self, message: str):
        if not self.app:
            return
        for chat_id in list(self._chat_ids):
            try:
                await self.app.bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown")
            except Exception as e:
                logger.warning(f"Telegram send failed to {chat_id}: {e}")

    def _is_authorized(self, user_id: int) -> bool:
        return not self.authorized_users or user_id in self.authorized_users

    async def _cmd_start(self, update, context):
        user_id = update.effective_user.id
        self._chat_ids.add(update.effective_chat.id)
        if not self._is_authorized(user_id):
            await update.message.reply_text("Unauthorized.")
            return
        await update.message.reply_text(
            "🤖 *Quant AI Lab Bot*\n\nCommands:\n"
            "/analyze SYMBOL - Market analysis\n"
            "/portfolio - Portfolio summary\n"
            "/status - System status\n"
            "/report - Daily report\n"
            "/stop - Activate kill switch",
            parse_mode="Markdown"
        )

    async def _cmd_analyze(self, update, context):
        if not self._is_authorized(update.effective_user.id):
            return
        symbol = context.args[0].upper() if context.args else "NIFTY"
        await update.message.reply_text(f"Analyzing {symbol}...")
        try:
            from backend.ai_core.agents.market_analysis_agent.agent import get_market_analysis_agent
            agent = get_market_analysis_agent()
            analysis = await agent.analyze(symbol)
            await update.message.reply_text(analysis.get("summary", "Analysis complete."))
        except Exception as e:
            await update.message.reply_text(f"Error: {e}")

    async def _cmd_portfolio(self, update, context):
        if not self._is_authorized(update.effective_user.id):
            return
        try:
            from backend.ai_core.agents.portfolio_agent.agent import get_portfolio_agent
            agent = get_portfolio_agent()
            await update.message.reply_text(await agent.handle("portfolio", "tg"), parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(f"Error: {e}")

    async def _cmd_status(self, update, context):
        if not self._is_authorized(update.effective_user.id):
            return
        from backend.order_engine.risk_engine import get_risk_engine
        risk = get_risk_engine()
        await update.message.reply_text(
            f"*System Status*\n- Kill Switch: {'ON' if risk.is_kill_switch_active() else 'OFF'}\n"
            f"- Mode: Paper Trading",
            parse_mode="Markdown"
        )

    async def _cmd_report(self, update, context):
        if not self._is_authorized(update.effective_user.id):
            return
        try:
            from backend.ai_core.agents.reporting_agent.agent import get_reporting_agent
            agent = get_reporting_agent()
            report = await agent.generate_daily_report()
            await update.message.reply_text(report.get("summary", ""), parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(f"Error: {e}")

    async def _cmd_stop_trading(self, update, context):
        if not self._is_authorized(update.effective_user.id):
            return
        from backend.order_engine.risk_engine import get_risk_engine
        await get_risk_engine().activate_kill_switch()
        await update.message.reply_text("🛑 Kill switch activated. All trading halted.")

    async def _handle_message(self, update, context):
        if not self._is_authorized(update.effective_user.id):
            return
        message = update.message.text
        self._chat_ids.add(update.effective_chat.id)
        try:
            from backend.ai_core.agent_orchestrator.orchestrator import get_orchestrator
            orch = get_orchestrator()
            session_id = f"tg_{update.effective_user.id}"
            response = await orch.handle_message(message, session_id, "telegram")
            await update.message.reply_text(response)
        except Exception as e:
            await update.message.reply_text(f"Error: {e}")


def get_telegram_bot() -> Optional[TelegramBot]:
    return _bot


async def start_telegram_bot():
    global _bot
    from backend.config import get_system_config
    cfg = get_system_config()
    if not cfg.telegram.enabled or not cfg.telegram.bot_token:
        logger.info("Telegram bot disabled or no token configured")
        return
    _bot = TelegramBot(cfg.telegram.bot_token, cfg.telegram.authorized_users)
    await _bot.start()
