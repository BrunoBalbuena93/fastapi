from typing import Optional
from pydantic import BaseModel, Field

class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None
