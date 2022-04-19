from datetime import timedelta
from fastapi import APIRouter, status, Form, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from app.dependencies import CommonQueryParams
from app.models.users import Token, User, UserOut
from app.authentication import authenticate_user, create_access_token, get_current_active_user
from app.mock_data import fake_users_db
from app.settings import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()

# Used for auth example
# @router.post("/token")
# async def login(form_data: OAuth2PasswordRequestForm = Depends()):
#     user_dict = fake_users_db.get(form_data.username)
#     if not user_dict:
#         raise HTTPException(status_code=400, detail="Incorrect username or password")
#     user = UserInDB(**user_dict)
#     hashed_password = fake_hash_password(form_data.password)
#     if not hashed_password == user.hashed_password:
#         raise HTTPException(status_code=400, detail="Incorrect username or password")

#     return {"access_token": user.username, "token_type": "bearer"}

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post('/user/', response_model=UserOut)
async def create_user(user: User):
    return user

@router.post('/form-data', status_code=status.HTTP_202_ACCEPTED)
async def read_form_data(
    username: str = Form(...), password: str = Form(...)
    ):
    return {'username': username, 'password': password}

# Utilizando dependencias
@router.get('/users/')
async def read_users(commons: CommonQueryParams = Depends(CommonQueryParams)):
    return commons

@router.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user