from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid

router = APIRouter(prefix="/api/v1/agents", tags=["Agents"])


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    agent_id: Optional[str] = "orchestrator"
    channel: Optional[str] = "desktop"


class TaskRequest(BaseModel):
    task_type: str
    params: dict = {}


@router.post("/chat")
async def chat(req: ChatRequest):
    from backend.ai_core.agent_orchestrator.orchestrator import get_orchestrator
    orchestrator = get_orchestrator()
    session_id = req.session_id or str(uuid.uuid4())
    response = await orchestrator.handle_message(req.message, session_id, req.channel)
    return {"success": True, "session_id": session_id, "response": response}


@router.get("/status")
async def agent_status():
    from backend.ai_core.agent_orchestrator.orchestrator import get_orchestrator
    orchestrator = get_orchestrator()
    return {"success": True, "agents": orchestrator.get_status()}


@router.post("/task")
async def run_task(req: TaskRequest):
    from backend.ai_core.agent_orchestrator.orchestrator import get_orchestrator
    orchestrator = get_orchestrator()
    result = await orchestrator.run_task(req.task_type, req.params)
    return {"success": True, "result": result}
