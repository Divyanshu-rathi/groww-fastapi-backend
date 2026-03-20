from pydantic import BaseModel, Field
from typing import Optional, Literal

class GTTOrderRequestDTO(BaseModel):
    symbol: str = Field(..., example="TCS")
    quantity: int = Field(..., gt=0, example=10)

    transaction_type: str = Field(..., example="BUY")  # BUY / SELL

    trigger_price: float = Field(..., example=3985.00)
    limit_price: float = Field(..., example=3990.00)

    # Optional: generally BUY->DOWN, SELL->UP auto set if None
    trigger_direction: Optional[str] = Field(None, example="DOWN")  # UP / DOWN

    product_type: Optional[str] = Field("CNC", example="CNC")
    reference_id: Optional[str] = None




class OCORequestDTO(BaseModel):
    symbol: str = Field(..., example="TCS")
    quantity: int = Field(..., gt=0, example=10)

    segment: str = Field(..., example="CASH")  # CASH / FNO
    product_type: Optional[str] = Field(None, example="MIS")

    target_trigger_price: float = Field(..., example= 4050)
    target_price: float = Field(..., example=4060)

    stoploss_trigger_price: float = Field(..., example=3920)
    


class ModifyGTTRequestDTO(BaseModel):
    smart_order_id: str = Field(..., example="gtt_91a7f4")          
    quantity: int = Field(..., gt=0, example=12)
    trigger_price: float = Field(..., example=3980.00)
    limit_price: float = Field(..., example=3985.00)

    transaction_type: str = Field(..., example="BUY")

###
class ModifyGTTActionDTO(BaseModel):
    smart_order_id: str
    current_trigger_price: float
    limit_price: float
    quantity: int
    transaction_type: Literal["BUY", "SELL"]
    action: Literal["+", "-"]
###



class ModifyOCORequestDTO(BaseModel):
    smart_order_id: str = Field(..., example="oco_91a7f4")

    quantity: int = Field(..., gt=0, example=10)

    target_trigger_price: float = Field(..., example=4050.0)
    target_price: float = Field(..., example=4060.0)

    stoploss_trigger_price: float = Field(..., example=3920.0)

class ModifyOCOActionDTO(BaseModel):
    smart_order_id: str
    quantity: int

    current_target_trigger_price: float
    current_stoploss_trigger_price: float
    target_price: float  # LIMIT price (unchanged)

    action: Literal["+", "-"]
    price_type: Literal["TARGET", "STOPLOSS"]


class CancelSmartOrderRequestDTO(BaseModel):
    smart_order_id: str = Field(..., example="oco_91a7f4")

