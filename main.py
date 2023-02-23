from databases import Database
from sqlalchemy import MetaData, Table, Column, Integer, String, create_engine, ForeignKey
from fastapi import FastAPI, Request
from config import config



DATABASE_URL = config.db_config.db_url

db = Database(DATABASE_URL)
metadata = MetaData()

books = Table(
    "books",
    metadata,
    Column('id', Integer, primary_key=True),
    Column('title', String),
    Column('author', String),
    Column('pages', Integer),
)

readers = Table(
    'readers',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('first_name', String),
    Column('last_name', String),
)

readers_books = Table(
    'readers_books',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('book_id', ForeignKey('books.id'), nullable=False),
    Column('reader_id', ForeignKey('readers.id'), nullable=False)
)


# engine = create_engine(DATABASE_URL)
# metadata.create_all(engine)

app = FastAPI()

@app.on_event("startup")
async def startup():
    await db.connect()

@app.on_event("shutdown")
async def shutdown():
    await db.disconnect()

@app.get('/books')
async def get_all_books():
    query = books.select()
    return await db.fetch_all(query)

@app.post('/books')
async def create_book(request: Request):
    data = await request.json()
    query = books.insert().values(**data)
    last_record_id = await db.execute(query)
    return dict(id=last_record_id)


@app.get('/readers')
async def get_all_readers():
    query = readers.select()
    return await db.fetch_all(query)


@app.post('/readers')
async def create_reader(request: Request):
    data = await request.json()
    query = readers.insert().values(**data)
    last_record_id = await db.execute(query)
    return dict(id=last_record_id)

