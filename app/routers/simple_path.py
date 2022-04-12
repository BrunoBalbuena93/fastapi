from fastapi import APIRouter
from enum import Enum

router = APIRouter()

class ModelName(str, Enum):
    alexnet = "alexet"
    resnet = 'resnet'
    lenet = 'lenet'


@router.get('/')
def read_root():
    return {'hello': 'world'}

@router.get("/items/{item_id}")
def read_item(item_id: int):
    return {'item_id': item_id}

@router.get('/models/{model_name}')
async def get_model(model_name: ModelName):
    if model_name == ModelName.alexnet:
        return {'model_name': model_name, 'message': 'Deep learning FTW!'}
    
    elif model_name.value == 'lenet':
        return {'model_name': model_name, 'message': 'LeCNN all the Images'}
    return {'model_name': model_name, 'message': 'Have some residuals'}