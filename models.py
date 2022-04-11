import imp
from typing import Optional, List
from fastapi import Body
from pydantic import BaseModel, Field


class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

class User(BaseModel):
    username : str = Field(..., title='Identificación', max_length=50)
    password: str = Field(min_length=6)
    email: str = Field(None, description='Este campo no es mandatorio')
 
class UserOut(BaseModel):
    username : str = Field(..., title='Identificación', max_length=50)
    email: str = Field(None, description='Este campo no es mandatorio')