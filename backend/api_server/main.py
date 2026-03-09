import sys
import os

# Add backend parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from .router import register_routes
from .middleware.logging_middleware import LoggingMiddleware
from .middleware.error_handler import global_exception_handler
from backend.config import get_system_config
from backend.database import init_db, close_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    config = get_system_config()
    logger.info(f"Starting {config.app.name} v{config.app.version}")
    await init_db()

    # Start background services
    try:
        from backend.broker_gateway.broker_manager import get_broker_manager
        bm = get_broker_manager()
        await bm.initialize()
        logger.info("Broker manager initialized")
    except Exception as e:
        logger.warning(f"Broker manager init skipped: {e}")

    try:
        from backend.ai_core.agent_orchestrator.orchestrator import get_orchestrator
        orch = get_orchestrator()
        await orch.initialize()
        logger.info("Agent orchestrator initialized")
    except Exception as e:
        logger.warning(f"Orchestrator init skipped: {e}")

    logger.info(f"Server ready on port {config.app.port}")
    yield

    # Shutdown
    await close_db()
    logger.info("Server stopped")


def create_app() -> FastAPI:
    config = get_system_config()

    app = FastAPI(
        title=config.app.name,
        version=config.app.version,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(LoggingMiddleware)
    app.add_exception_handler(Exception, global_exception_handler)

    register_routes(app)
    return app


app = create_app()


if __name__ == "__main__":
    config = get_system_config()
    logger.remove()
    logger.add(sys.stdout, level=config.app.log_level)
    logger.add("logs/system.log", rotation="1 day", level="DEBUG")

    uvicorn.run(
        "api_server.main:app",
        host=config.app.host,
        port=config.app.port,
        reload=config.app.debug,
        log_level=config.app.log_level.lower(),
    )
