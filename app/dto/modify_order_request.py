from pydantic import BaseModel, Field
from typing import Optional, Literal

class ModifyOrderRequestDto(BaseModel):
    order_id: str
    quantity: int
    segment: str
    order_type: str  # LIMIT / STOP_LOSS / STOP_LOSS_MARKET
    price: Optional[float] = None
    trigger_price: Optional[float] = None

    

class ModifyOrderActionDTO(BaseModel):
    order_id: str
    quantity: int
    segment: Literal["CASH", "FNO"]

    order_type: Literal[
        "LIMIT",
        "STOP_LOSS",
        "STOP_LOSS_MARKET"
    ]

    # current values (UI se aayengi)
    current_price: Optional[float] = None
    current_trigger_price: Optional[float] = None

    # kya change karna hai
    price_field: Literal["PRICE", "TRIGGER"]
    action: Literal["+", "-"]




