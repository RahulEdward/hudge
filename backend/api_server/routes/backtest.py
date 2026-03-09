from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api/v1/backtest", tags=["Backtesting"])


class BacktestRequest(BaseModel):
    strategy_id: str
    symbol: str
    timeframe: str = "1D"
    start_date: str
    end_date: str
    initial_capital: float = 1000000


@router.post("/run")
async def run_backtest(req: BacktestRequest):
    from backend.backtesting_engine.simulator import run_backtest
    result = await run_backtest(
        strategy_id=req.strategy_id,
        symbol=req.symbol,
        timeframe=req.timeframe,
        start_date=req.start_date,
        end_date=req.end_date,
        initial_capital=req.initial_capital,
    )
    return {"success": True, "result": result}


@router.get("/results")
async def list_results(strategy_id: Optional[str] = None, limit: int = 20):
    from backend.database.connection import get_session
    from backend.database.repositories import BacktestRepository
    async for session in get_session():
        repo = BacktestRepository(session)
        if strategy_id:
            results = await repo.get_by_strategy(strategy_id)
        else:
            results = await repo.get_all(limit=limit)
        return {"success": True, "results": [r.__dict__ for r in results]}


@router.get("/results/{result_id}")
async def get_result(result_id: str):
    from backend.database.connection import get_session
    from backend.database.repositories import BacktestRepository
    async for session in get_session():
        repo = BacktestRepository(session)
        result = await repo.get_by_result_id(result_id)
        if not result:
            raise HTTPException(status_code=404, detail="Result not found")
        return {"success": True, "result": result.__dict__}
