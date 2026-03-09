from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/strategies", tags=["Strategies"])


@router.get("/")
async def list_strategies(status: str = None, limit: int = 50):
    from backend.database.connection import get_session
    from backend.database.repositories import StrategyRepository
    async for session in get_session():
        repo = StrategyRepository(session)
        if status:
            strategies = await repo.get_by_status(status)
        else:
            strategies = await repo.get_all(limit=limit)
        return {"success": True, "strategies": [s.__dict__ for s in strategies]}


@router.get("/{strategy_id}")
async def get_strategy(strategy_id: str):
    from backend.database.connection import get_session
    from backend.database.repositories import StrategyRepository
    async for session in get_session():
        repo = StrategyRepository(session)
        strategy = await repo.get_by_strategy_id(strategy_id)
        if not strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")
        return {"success": True, "strategy": strategy.__dict__}


@router.post("/{strategy_id}/approve")
async def approve_strategy(strategy_id: str):
    from backend.database.connection import get_session
    from backend.database.repositories import StrategyRepository
    async for session in get_session():
        repo = StrategyRepository(session)
        strategy = await repo.get_by_strategy_id(strategy_id)
        if not strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")
        strategy.status = "approved"
        await repo.save(strategy)
        return {"success": True, "message": f"Strategy {strategy_id} approved"}


@router.post("/{strategy_id}/reject")
async def reject_strategy(strategy_id: str):
    from backend.database.connection import get_session
    from backend.database.repositories import StrategyRepository
    async for session in get_session():
        repo = StrategyRepository(session)
        strategy = await repo.get_by_strategy_id(strategy_id)
        if not strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")
        strategy.status = "rejected"
        await repo.save(strategy)
        return {"success": True, "message": f"Strategy {strategy_id} rejected"}
