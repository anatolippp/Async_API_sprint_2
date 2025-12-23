from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine

from .db import engine
from .models.base import Base
from .routes import campaigns, notifications, templates

app = FastAPI(title="Notification service")
app.include_router(notifications.router)
app.include_router(templates.router)
app.include_router(campaigns.router)


@app.on_event("startup")
async def on_startup():
    await init_models(engine)


async def init_models(db_engine: AsyncEngine) -> None:
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
