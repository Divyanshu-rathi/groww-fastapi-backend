from sqlalchemy import Column, Integer, String, Boolean, JSON
from app.db.base import Base

class Instrument(Base):
    __tablename__ = "instruments"

    id = Column(Integer, primary_key=True, index=True)

    exchange = Column(String(20))
    exchange_token = Column(String(50), index=True)

    trading_symbol = Column(String(100))
    groww_symbol = Column(String(150))

    internal_trading_symbol = Column(String(100))

    is_reserved = Column(Boolean, default=False)
    buy_allowed = Column(Boolean, default=True)
    sell_allowed = Column(Boolean, default=True)

    raw_data = Column(JSON)
