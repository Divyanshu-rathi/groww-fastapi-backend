from pydantic import BaseModel
from typing import Optional

class UIOrderResponseDTO(BaseModel):
    exchange_order_id: Optional[str]
    status: str
    order_id: str
    tradingsymbol: str
    price: Optional[str]
    quantity: Optional[str]
    transaction_type: Optional[str]
    product: Optional[str]
    exchange: Optional[str]
    status_message: Optional[str]