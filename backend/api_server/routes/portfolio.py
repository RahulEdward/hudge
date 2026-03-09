from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/portfolio", tags=["Portfolio"])


@router.get("/summary")
async def portfolio_summary():
    from backend.ai_core.agents.portfolio_agent.agent import get_portfolio_agent
    agent = get_portfolio_agent()
    summary = await agent.get_portfolio_summary()
    return {"success": True, "summary": summary}


@router.get("/holdings")
async def get_holdings():
    from backend.broker_gateway.broker_manager import get_broker_manager
    bm = get_broker_manager()
    holdings = await bm.get_holdings()
    return {"success": True, "holdings": holdings}


@router.get("/performance")
async def get_performance(period: str = "1M"):
    from backend.database.connection import get_session
    from backend.database.repositories import TradeRepository
    async for session in get_session():
        repo = TradeRepository(session)
        trades = await repo.get_recent(limit=500)
        total_pnl = sum(t.pnl for t in trades)
        return {"success": True, "period": period, "total_pnl": total_pnl, "trade_count": len(trades)}
