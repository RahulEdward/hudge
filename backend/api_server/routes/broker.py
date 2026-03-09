from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/broker", tags=["Broker"])


class BrokerConnectRequest(BaseModel):
    broker: str
    credentials: dict = {}


@router.get("/status")
async def broker_status():
    from backend.broker_gateway.broker_manager import get_broker_manager
    bm = get_broker_manager()
    return {"success": True, "status": bm.get_connection_status()}


@router.post("/connect")
async def connect_broker(req: BrokerConnectRequest):
    from backend.broker_gateway.broker_manager import get_broker_manager
    bm = get_broker_manager()
    result = await bm.connect(req.broker, req.credentials)
    return {"success": True, "result": result}


@router.post("/disconnect")
async def disconnect_broker(broker: str):
    from backend.broker_gateway.broker_manager import get_broker_manager
    bm = get_broker_manager()
    await bm.disconnect(broker)
    return {"success": True, "message": f"{broker} disconnected"}


@router.get("/funds")
async def get_funds():
    from backend.broker_gateway.broker_manager import get_broker_manager
    bm = get_broker_manager()
    funds = await bm.get_funds()
    return {"success": True, "funds": funds}
