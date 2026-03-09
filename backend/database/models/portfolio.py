from sqlalchemy import Column, Integer, String, Float, JSON
from .base import Base, TimestampMixin


class Portfolio(Base, TimestampMixin):
    __tablename__ = "portfolio"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(50), nullable=False, index=True)
    exchange = Column(String(20), default="NSE")
    quantity = Column(Integer, default=0)
    average_price = Column(Float, default=0.0)
    current_price = Column(Float, default=0.0)
    pnl = Column(Float, default=0.0)
    pnl_pct = Column(Float, default=0.0)
    product_type = Column(String(20))
    broker = Column(String(50))
    strategy_id = Column(String(100))
    is_paper = Column(Integer, default=1)
    meta = Column(JSON, default={})
