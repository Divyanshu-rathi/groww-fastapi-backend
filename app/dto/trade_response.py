from pydantic import BaseModel

class Traderesponsedto(BaseModel):
    status:str
    order_id:str
    