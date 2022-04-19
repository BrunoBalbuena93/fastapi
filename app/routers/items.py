from fastapi import APIRouter, Body, Depends
from app.dependencies import common_parrameters
from app.authentication import oauth2_scheme
from app.models.items import Item
from app.models.users import User

router = APIRouter(
    prefix='/items',
    responses={404: {'description': 'Not Found'}}
)


@router.post('/')
async def create_item(item: Item):
    return item

@router.get('/')
async def read_items(commons: dict = Depends(oauth2_scheme)):
    return commons

@router.post('/{item_id}')
async def create_advanced_items(
    item_id: int,
    item: Item,
    user: User,
    additional: int= Body(...,gt=0)
    ):
    return {'item_id': item_id, 'item': item, 'user': user, 'add': additional}
