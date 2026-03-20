from pydantic import BaseModel
from typing import Optional

class UIOrderRequestDTO(BaseModel):
    exchange: str
    tradingsymbol: str
    transactionType: str
    quantity: int
    price: Optional[float]
    product: Optional[str]
    orderType: str
    validity: Optional[str]

    disclosedQuantity: Optional[int] = None
    triggerPrice: Optional[float] = None
    squareoff: Optional[float] = None
    stoploss: Optional[float] = None
    target: Optional[float] = None
    trailingStoploss: Optional[float] = None
    tag: Optional[str] = None
    parentOrderId: Optional[str] = None
    validityTTL: Optional[int] = None
    icebergQuantity: Optional[int] = None
    icebergLegs: Optional[int] = None
    auctionNumber: Optional[str] = None

    # ignore extra safely
    class Config:
        extra = "ignore"