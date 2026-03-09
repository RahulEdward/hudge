from sqlalchemy import Column, Integer, String, Text, JSON
from .base import Base, TimestampMixin


class Plugin(Base, TimestampMixin):
    __tablename__ = "plugins"

    id = Column(Integer, primary_key=True, autoincrement=True)
    plugin_id = Column(String(100), unique=True, index=True)
    name = Column(String(200), nullable=False)
    version = Column(String(20))
    description = Column(Text)
    author = Column(String(100))
    is_active = Column(Integer, default=0)
    config = Column(JSON, default={})
    meta = Column(JSON, default={})
