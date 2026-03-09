from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api/v1/trades", tags=["Trading"])


class OrderRequest(BaseModel):
    symbol: str
    side: str  # BUY / SELL
    order_type: str = "MARKET"
    quantity: int
    price: float = 0.0
    trigger_price: float = 0.0
    product_type: str = "INTRADAY"
    exchange: str = "NSE"
    strategy_id: Optional[str] = None


@router.post("/order")
async def place_order(req: OrderRequest):
    from backend.order_engine.order_router import get_order_router
    router_svc = get_order_router()
    result = await router_svc.place_order(req.dict())
    return {"success": True, "order": result}


@router.get("/orders")
async def list_orders(status: Optional[str] = None, limit: int = 50):
    from backend.database.connection import get_session
    from backend.database.repositories import OrderRepository
    async for session in get_session():
        repo = OrderRepository(session)
        if status:
            orders = await repo.get_by_status(status)
        else:
            orders = await repo.get_all(limit=limit)
        return {"success": True, "orders": [o.__dict__ for o in orders]}


@router.get("/positions")
async def get_positions():
    from backend.broker_gateway.broker_manager import get_broker_manager
    bm = get_broker_manager()
    positions = await bm.get_positions()
    return {"success": True, "positions": positions}


@router.delete("/order/{order_id}")
async def cancel_order(order_id: str):
    from backend.order_engine.order_router import get_order_router
    router_svc = get_order_router()
    result = await router_svc.cancel_order(order_id)
    return {"success": True, "result": result}


@router.post("/kill-switch")
async def activate_kill_switch():
    from backend.order_engine.risk_engine import get_risk_engine
    risk = get_risk_engine()
    await risk.activate_kill_switch()
    return {"success": True, "message": "Kill switch activated — all trading halted"}
