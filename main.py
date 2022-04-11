from typing import Optional, List
from fastapi import FastAPI, Query, Body
from enum import Enum
from models import Item, User, UserOut

class ModelName(str, Enum):
    alexnet = "alexet"
    resnet = 'resnet'
    lenet = 'lenet'


app = FastAPI()

@app.get('/')
def read_root():
    return {'hello': 'world'}

@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {'item_id': item_id}

@app.get('/models/{model_name}')
async def get_model(model_name: ModelName):
    if model_name == ModelName.alexnet:
        return {'model_name': model_name, 'message': 'Deep learning FTW!'}
    
    elif model_name.value == 'lenet':
        return {'model_name': model_name, 'message': 'LeCNN all the Images'}
    return {'model_name': model_name, 'message': 'Have some residuals'}

# Query Params
@app.get('/query')
async def read_query_params(limit:int, index: Optional[int] = None, offset: bool=False):
    item = {'limit': limit}
    if index:
        item.update({'index': index})
    if offset:
        item.update({'offset': 'active'})
    return item

@app.get('advanced-query')
async def read_advance_query_params(p: Optional[str] = Query(None,min_length=2, max_length=50), q: str = Query('default', regex='^def'),
    r: str = Query(..., title='Mandatory', description='You can define a description here', alias='alias-name')):
    return {'p': p, 'q': q, 'r': r}

# Reading body
@app.post('/items')
async def create_item(item: Item):
    return item

@app.post('/advanced-items/{item_id}')
async def create_advanced_items(
    item_id: int,
    item: Item,
    user: User,
    additional: int= Body(...,gt=0)
    ):
    return {'item_id': item_id, 'item': item, 'user': user, 'add': additional}

@app.post('/user/', response_model=UserOut)
async def create_user(user: User):
    return user