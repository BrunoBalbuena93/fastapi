from fastapi import FastAPI
from .routers import items, users, query_params, simple_path

app = FastAPI()

app.include_router(simple_path.router)
app.include_router(query_params.router)
app.include_router(users.router)
app.include_router(items.router)
