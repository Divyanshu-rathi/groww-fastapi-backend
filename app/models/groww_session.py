from sqlalchemy import Column, Integer, DateTime, ForeignKey, Text
from datetime import datetime
from app.db.base import Base

class GrowwSession(Base):
    __tablename__ = "groww_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    access_token = Column(Text, nullable=False)  
    created_at = Column(DateTime, default=datetime.utcnow)
