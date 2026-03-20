from pydantic import BaseModel
from typing import Optional

class InstrumentSchema(BaseModel):
    id: int
    exchange: Optional[str]
    exchange_token: Optional[str]
    trading_symbol: Optional[str]
    groww_symbol: Optional[str]
    is_reserved: Optional[bool]
    buy_allowed: Optional[bool]
    sell_allowed: Optional[bool]
    internal_trading_symbol: Optional[str]

    class Config:
        orm_mode = True
