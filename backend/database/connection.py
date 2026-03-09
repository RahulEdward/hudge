import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from loguru import logger

from .models.base import Base

_engine = None
_session_factory = None


def get_db_url() -> str:
    db_path = os.environ.get("SQLITE_PATH", "database/quant_lab.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True) if os.path.dirname(db_path) else None
    return f"sqlite+aiosqlite:///{db_path}"


async def init_db():
    global _engine, _session_factory
    db_url = get_db_url()
    _engine = create_async_engine(db_url, echo=False, future=True)
    _session_factory = async_sessionmaker(_engine, class_=AsyncSession, expire_on_commit=False)
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info(f"Database initialized: {db_url}")


async def get_session() -> AsyncSession:
    if _session_factory is None:
        await init_db()
    async with _session_factory() as session:
        yield session


async def close_db():
    global _engine
    if _engine:
        await _engine.dispose()
        logger.info("Database connection closed")
