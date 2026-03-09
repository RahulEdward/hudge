from sqlalchemy import Column, Integer, String, Text, JSON
from .base import Base, TimestampMixin


class Alert(Base, TimestampMixin):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    alert_id = Column(String(100), unique=True, index=True)
    alert_type = Column(String(50), nullable=False)
    title = Column(String(200))
    message = Column(Text, nullable=False)
    priority = Column(String(20), default="normal")  # low / normal / high / critical
    channels = Column(JSON, default=["desktop"])
    delivered_to = Column(JSON, default=[])
    is_read = Column(Integer, default=0)
    meta = Column(JSON, default={})
