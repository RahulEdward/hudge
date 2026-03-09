from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, JSON, func
from .base import Base, TimestampMixin
import enum


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    PLACED = "placed"
    OPEN = "open"
    PARTIAL = "partial"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class OrderSide(str, enum.Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, enum.Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    SL = "SL"
    SL_M = "SL-M"


class ProductType(str, enum.Enum):
    INTRADAY = "INTRADAY"
    DELIVERY = "DELIVERY"
    MARGIN = "MARGIN"


class Order(Base, TimestampMixin):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String(100), unique=True, index=True)
    broker_order_id = Column(String(100))
    symbol = Column(String(50), nullable=False, index=True)
    exchange = Column(String(20), default="NSE")
    side = Column(String(10), nullable=False)
    order_type = Column(String(20), nullable=False)
    product_type = Column(String(20), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, default=0.0)
    trigger_price = Column(Float, default=0.0)
    filled_quantity = Column(Integer, default=0)
    average_price = Column(Float, default=0.0)
    status = Column(String(20), default=OrderStatus.PENDING)
    broker = Column(String(50))
    strategy_id = Column(String(100))
    agent_id = Column(String(50))
    is_paper = Column(Integer, default=1)
    rejection_reason = Column(String(500))
    meta = Column(JSON, default={})


class Trade(Base, TimestampMixin):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trade_id = Column(String(100), unique=True, index=True)
    order_id = Column(String(100), index=True)
    symbol = Column(String(50), nullable=False, index=True)
    exchange = Column(String(20), default="NSE")
    side = Column(String(10), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    broker = Column(String(50))
    strategy_id = Column(String(100))
    pnl = Column(Float, default=0.0)
    is_paper = Column(Integer, default=1)
    executed_at = Column(DateTime, default=func.now())
    meta = Column(JSON, default={})
