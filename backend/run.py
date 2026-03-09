"""Entry point for the Quant AI Lab backend."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if __name__ == "__main__":
    import uvicorn
    from backend.config import get_system_config
    from loguru import logger

    config = get_system_config()
    logger.remove()
    logger.add(sys.stdout, level=config.app.log_level, colorize=True)
    os.makedirs("logs", exist_ok=True)
    logger.add("logs/system.log", rotation="1 day", retention="7 days", level="DEBUG")

    logger.info(f"Starting {config.app.name} v{config.app.version}")
    uvicorn.run(
        "backend.api_server.main:app",
        host=config.app.host,
        port=config.app.port,
        reload=False,
        log_level=config.app.log_level.lower(),
    )
