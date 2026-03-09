from sqlalchemy import Column, Integer, String, Float, JSON, Text
from .base import Base, TimestampMixin


class MLModel(Base, TimestampMixin):
    __tablename__ = "ml_models"

    id = Column(Integer, primary_key=True, autoincrement=True)
    model_id = Column(String(100), unique=True, index=True)
    model_type = Column(String(50), nullable=False)
    name = Column(String(200))
    version = Column(String(20))
    symbol = Column(String(50))
    timeframe = Column(String(20))
    file_path = Column(String(500))
    accuracy = Column(Float)
    directional_accuracy = Column(Float)
    sharpe = Column(Float)
    metrics = Column(JSON, default={})
    feature_names = Column(JSON, default=[])
    is_active = Column(Integer, default=0)
    meta = Column(JSON, default={})
