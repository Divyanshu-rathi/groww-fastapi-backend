from pydantic import BaseModel
from typing import List

class Instrument(BaseModel):
    exchange: str
    segment: str
    exchange_token: str

class SubscribeLTPRequest(BaseModel):
    instruments: List[Instrument]
