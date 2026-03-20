from sqlalchemy import Column, Integer, String, Boolean, Text
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(150), unique=True, nullable=False)

    password_hash = Column(String(255), nullable=False)

    groww_api_key = Column(Text, nullable=False)
    groww_secret_key = Column(Text, nullable=False)

    is_active = Column(Boolean, default=True)
