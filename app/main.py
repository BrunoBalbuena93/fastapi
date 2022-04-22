from fastapi import FastAPI
from .routers import items, users, query_params, simple_path, background, orm
from .orm import crud, models, schemas
from .orm.database import engine, SessionLocal

models.Base.metadata.create_all(bind=engine)


app = FastAPI()

app.include_router(simple_path.router)
app.include_router(query_params.router)
app.include_router(users.router)
app.include_router(items.router)
app.include_router(background.router)
app.include_router(orm.router)
