from pydantic import BaseModel, Field
from typing import Optional

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
 
class UserOut(BaseModel):
    username : str = Field(..., title='Identificación', max_length=50)
    email: str = Field(None, description='Este campo no es mandatorio')

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None