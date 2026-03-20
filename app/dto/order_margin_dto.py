from pydantic import BaseModel
from typing import Optional


class OrderMarginRequestDTO(BaseModel):
    trading_symbol: str
    transaction_type: str
    quantity: int
    price: Optional[float] = None
    order_type: str
    product: str
    exchange: str
