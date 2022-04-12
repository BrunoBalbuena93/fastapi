from fastapi import APIRouter, status, Form, Depends
from app.dependencies import CommonQueryParams
from app.models.users import User, UserOut

router = APIRouter()


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