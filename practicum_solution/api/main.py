from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
import sentry_sdk

from .config import settings
from .routers.bookmarks import router as bookmarks_router
from .routers.likes import router as likes_router
from .routers.movies import router as movies_router
from .routers.reviews import router as reviews_router

app = FastAPI(title="UGC prototype")


@app.on_event("startup")
async def startup() -> None:
    if settings.sentry_dsn:
        sentry_sdk.init(dsn=settings.sentry_dsn, traces_sample_rate=0.1)

    client = AsyncIOMotorClient(settings.mongo_url)
    db = client.get_default_database()
    await db.likes.create_index([("user_id", 1), ("movie_id", 1)], unique=True)
    await db.bookmarks.create_index([("user_id", 1), ("movie_id", 1)], unique=True)
    await db.reviews.create_index([("movie_id", 1)])
    app.state.db = db
    app.state.client = client


@app.on_event("shutdown")
async def shutdown() -> None:
    client = getattr(app.state, "client", None)
    if client is not None:
        client.close()


app.include_router(likes_router)
app.include_router(movies_router)
app.include_router(reviews_router)
app.include_router(bookmarks_router)
