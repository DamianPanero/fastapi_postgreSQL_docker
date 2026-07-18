import os
from contextlib import asynccontextmanager
from typing import Annotated, AsyncGenerator
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import select

# lee la variable de entorno que definiste en docker-compose
# si no existe usa SQLite como fallback para desarrollo local sin Docker
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///local.db")
DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

class Item(Base):
    __tablename__ = "items"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(nullable=False)

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield

class ItemCreate(BaseModel):
    nombre: str

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

DBSession = Annotated[AsyncSession, Depends(get_db)]

app = FastAPI(lifespan=lifespan)

@app.get("/items")
async def get_items(session: DBSession):
    result = await session.execute(select(Item))
    items = result.scalars().all()
    if not items:
        raise HTTPException(status_code=404, detail="No hay items")
    return [{"id": i.id, "nombre": i.nombre} for i in items]

@app.get("/items/{item_id}")
async def get_item(item_id: int, session: DBSession):
    item = await session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    return {"id": item.id, "nombre": item.nombre}

@app.post("/items", status_code=201)
async def create_item(data: ItemCreate, session: DBSession):
    item = Item(nombre=data.nombre)
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return {"id": item.id, "nombre": item.nombre}

@app.patch("/items/{item_id}")
async def update_item(item_id: int, data: ItemCreate, session: DBSession):
    item = await session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    item.nombre = data.nombre
    await session.commit()
    return {"id": item.id, "nombre": item.nombre}

@app.delete("/items/{item_id}")
async def delete_item(item_id: int, session: DBSession):
    item = await session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    await session.delete(item)
    await session.commit()
    return {"message": "Item eliminado correctamente"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000, reload=True)