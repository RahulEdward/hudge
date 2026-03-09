from sqlalchemy import Column, Integer, String, Text, JSON
from .base import Base, TimestampMixin


class Conversation(Base, TimestampMixin):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(100), index=True)
    channel = Column(String(50), default="desktop")  # desktop / telegram / whatsapp
    role = Column(String(20), nullable=False)  # user / assistant / system
    content = Column(Text, nullable=False)
    agent_id = Column(String(50))
    meta = Column(JSON, default={})
