from sqlalchemy import Column, Integer, String, Text, DateTime
from app.db.database import Base
from datetime import datetime

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    sources = Column(Text, nullable=True) # JSON string of sources
    created_at = Column(DateTime, default=datetime.utcnow)
