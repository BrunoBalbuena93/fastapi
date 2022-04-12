from typing import Optional


async def common_parrameters(q: Optional[str] = None, skip: int = 0, limit: int = 10):
    return {'q': q, 'skip': skip, 'limit': limit}

class CommonQueryParams:
    def __init__(self, q: Optional[str] = None, skip: int = 0, limit: int = 100):
        self.q = q
        self.skip = skip
        self.limit = limit
