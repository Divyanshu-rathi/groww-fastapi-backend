from pydantic import BaseModel
from typing import Literal, Optional

class BulkCancelRequestDTO(BaseModel):
    symbol: str
    segment: Literal["CASH", "FNO"]
    page: int = 0
    page_size: int = 100


class BulkModifyActionRequestDTO(BaseModel):
    symbol: str
    segment: Literal["CASH", "FNO"]
    action: Literal["+", "-"] = "+"
    step: float = 2.0

    # what to modify
    price_field: Literal["PRICE", "TRIGGER"] = "PRICE"

    # optional safety filters
    only_order_type: Optional[Literal["LIMIT", "STOP_LOSS", "STOP_LOSS_MARKET"]] = None

    page: int = 0
    page_size: int = 100



class BulkModifyRequestDTO(BaseModel):

    symbol: str
    segment: str

    quantity: int
    order_type: str

    price: Optional[float] = None
    trigger_price: Optional[float] = None

    page: int = 0
    page_size: int = 50