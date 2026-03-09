import json
import asyncio
from fastapi import WebSocket, WebSocketDisconnect
from loguru import logger
from typing import Set, Dict


class ConnectionManager:
    def __init__(self):
        self.market_connections: Set[WebSocket] = set()
        self.agent_connections: Set[WebSocket] = set()
        self.trade_connections: Set[WebSocket] = set()

    async def connect(self, ws: WebSocket, channel: str):
        await ws.accept()
        if channel == "market":
            self.market_connections.add(ws)
        elif channel == "agent":
            self.agent_connections.add(ws)
        elif channel == "trades":
            self.trade_connections.add(ws)

    def disconnect(self, ws: WebSocket, channel: str):
        if channel == "market":
            self.market_connections.discard(ws)
        elif channel == "agent":
            self.agent_connections.discard(ws)
        elif channel == "trades":
            self.trade_connections.discard(ws)

    async def broadcast(self, data: dict, channel: str):
        message = json.dumps(data)
        targets = {
            "market": self.market_connections,
            "agent": self.agent_connections,
            "trades": self.trade_connections,
        }.get(channel, set())
        dead = set()
        for ws in targets.copy():
            try:
                await ws.send_text(message)
            except Exception:
                dead.add(ws)
        targets -= dead


_manager = ConnectionManager()


def get_ws_manager() -> ConnectionManager:
    return _manager


async def websocket_market(ws: WebSocket):
    await _manager.connect(ws, "market")
    try:
        while True:
            data = await ws.receive_text()
            # Client can send subscription requests
    except WebSocketDisconnect:
        _manager.disconnect(ws, "market")


async def websocket_agent(ws: WebSocket):
    await _manager.connect(ws, "agent")
    try:
        while True:
            data = await ws.receive_text()
            msg = json.loads(data)
            if msg.get("type") == "chat":
                from backend.ai_core.agent_orchestrator.orchestrator import get_orchestrator
                orchestrator = get_orchestrator()
                session_id = msg.get("session_id", "ws-session")
                async for chunk in orchestrator.stream_message(msg["message"], session_id):
                    await ws.send_json({"type": "chunk", "content": chunk})
                await ws.send_json({"type": "done"})
    except WebSocketDisconnect:
        _manager.disconnect(ws, "agent")


async def websocket_trades(ws: WebSocket):
    await _manager.connect(ws, "trades")
    try:
        while True:
            await ws.receive_text()  # keep alive
    except WebSocketDisconnect:
        _manager.disconnect(ws, "trades")
