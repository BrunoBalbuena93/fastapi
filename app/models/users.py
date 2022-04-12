from pydantic import BaseModel, Field

class User(BaseModel):
    username : str = Field(..., title='Identificación', max_length=50)
    password: str = Field(min_length=6)
    email: str = Field(None, description='Este campo no es mandatorio')
 
class UserOut(BaseModel):
    username : str = Field(..., title='Identificación', max_length=50)
    email: str = Field(None, description='Este campo no es mandatorio')