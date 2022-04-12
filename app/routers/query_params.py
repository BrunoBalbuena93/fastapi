from fastapi import APIRouter, Query
from typing import Optional

router = APIRouter()

@router.get('/query')
async def read_query_params(limit:int, index: Optional[int] = None, offset: bool=False):
    item = {'limit': limit}
    if index:
        item.update({'index': index})
    if offset:
        item.update({'offset': 'active'})
    return item

@router.get('advanced-query')
async def read_advance_query_params(p: Optional[str] = Query(None,min_length=2, max_length=50), q: str = Query('default', regex='^def'),
    r: str = Query(..., title='Mandatory', description='You can define a description here', alias='alias-name')):
    return {'p': p, 'q': q, 'r': r}
