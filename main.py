import databases
import enum
import sqlalchemy
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, validator
from email_validator import validate_email as email_validation, EmailNotValidError
from fastapi import FastAPI
from passlib.context import CryptContext
from config import config


DATABASE_URL = config.db_config.db_url

database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("email", sqlalchemy.String(120), unique=True),
    sqlalchemy.Column("password", sqlalchemy.String(255)),
    sqlalchemy.Column("full_name", sqlalchemy.String(200)),
    sqlalchemy.Column("phone", sqlalchemy.String(13)),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, nullable=False, server_default=sqlalchemy.func.now()),
    sqlalchemy.Column(
        "last_modified_at",
        sqlalchemy.DateTime,
        nullable=False,
        server_default=sqlalchemy.func.now(),
        onupdate=sqlalchemy.func.now(),
    ),
)


class ColorEnum(enum.Enum):
    pink = "pink"
    black = "black"
    white = "white"
    yellow = "yellow"


class SizeEnum(enum.Enum):
    xs = "xs"
    s = "s"
    m = "m"
    l = "l"
    xl = "xl"
    xxl = "xxl"

clothes = sqlalchemy.Table(
    "clothes",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String(120)),
    sqlalchemy.Column("color", sqlalchemy.Enum(ColorEnum), nullable=False),
    sqlalchemy.Column("size", sqlalchemy.Enum(SizeEnum), nullable=False),
    sqlalchemy.Column("photo_url", sqlalchemy.String(255)),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, nullable=False, server_default=sqlalchemy.func.now()),
    sqlalchemy.Column(
        "last_modified_at",
        sqlalchemy.DateTime,
        nullable=False,
        server_default=sqlalchemy.func.now(),
        onupdate=sqlalchemy.func.now(),
    ),
)



class EmailField(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value) -> str:
        try:
            email_validation(value)
            return value
        except EmailNotValidError:
            raise ValueError(f'{value} is not a valid email')


class BaseUser(BaseModel):
    email: EmailField
    full_name: str
    
    @validator('full_name')
    def validate_full_name(cls, value) -> str:
        try:
            fist_name, last_name = value.split()
            return value
        except Exception:
            raise ValueError(f'You should provide at least 2 names')


class UserSignIn(BaseUser):
    password: str
    phone: Optional[str]

class UserSignOut(BaseUser):
    phone: Optional[str]
    created_at: datetime
    last_modified_at: datetime

app = FastAPI()
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.post('/register', response_model=UserSignOut)
async def create_user(user: UserSignIn):
    user.password = pwd_context.hash(user.password)
    query = users.insert().values(**user.dict())
    id_ = await database.execute(query)
    created_user = await database.fetch_one(users.select().where(users.c.id == id_))
    return created_user

@app.put('/register/{user_id}', response_model=UserSignOut)
async def edit_user(user: UserSignIn):
    user = await database.fetch_one(users.select().where(users.c.email == user.email))
    return