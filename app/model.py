from pydantic import BaseModel
from typing import Union, List
from datetime import date

class Quote(BaseModel):
    vendor: str
    item: str
    model: str
    manufacturer: str
    price: float
    quantity: int
    date: date
