# from pydantic import BaseModel, Field
# from typing import Optional

# class Traderequestdto(BaseModel):
#     symbol:str=Field(...,example="Idea")
#     quantity:int=Field(...,gt=0,example=1)
#     segment: Optional[str] = "CASH"  
#     product: Optional[str] = "MIS" 
    



from pydantic import BaseModel, Field
from typing import Optional

class Traderequestdto(BaseModel):
    symbol: str = Field(..., example="WIPRO")
    quantity: int = Field(..., gt=0, example=1)

    segment: Optional[str] = Field("CASH", example="CASH")      # CASH / FNO
    product: Optional[str] = Field(None, example="CNC")         # CNC / MIS / NRML (None => auto default)

    order_type: Optional[str] = Field("MARKET", example="LIMIT")  # MARKET / LIMIT / STOP_LOSS / STOP_LOSS_MARKET
    price: Optional[float] = Field(None, example=250.0)           # LIMIT or STOP_LOSS me required
    trigger_price: Optional[float] = Field(None, example=245.0)   # SL / SLM me required

    validity: Optional[str] = Field("DAY", example="DAY")         # currently only DAY used
    exchange: Optional[str] = Field("NSE", example="NSE")         # NSE / BSE / MCX

    order_reference_id: Optional[str] = Field(None, example="Ab-654321234-1628190")
