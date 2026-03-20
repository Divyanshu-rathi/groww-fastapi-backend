from pydantic import BaseModel, Field

class CancelOrderRequestDto(BaseModel):
    order_id: str = Field(..., example="GROWW123456")
    segment: str = Field(..., example="CASH")

