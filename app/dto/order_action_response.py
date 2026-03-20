from pydantic import BaseModel
from typing import Optional

class OrderActionResponseDto(BaseModel):
    status: str
    groww_order_id: Optional[str] = None
    remark: Optional[str] = None
