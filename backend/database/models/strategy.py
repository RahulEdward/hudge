from sqlalchemy import Column, Integer, String, Float, JSON, Text
from .base import Base, TimestampMixin


class Strategy(Base, TimestampMixin):
    __tablename__ = "strategies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    strategy_id = Column(String(100), unique=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    symbol = Column(String(50), index=True)
    timeframe = Column(String(20))
    entry_rules = Column(JSON, default={})
    exit_rules = Column(JSON, default={})
    parameters = Column(JSON, default={})
    indicators = Column(JSON, default=[])
    status = Column(String(50), default="discovered")
    risk_score = Column(Float)
    backtest_result_id = Column(String(100))
    approved_by = Column(String(100))
    meta = Column(JSON, default={})
