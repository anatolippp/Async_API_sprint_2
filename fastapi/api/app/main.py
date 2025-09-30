from __future__ import annotations
import asyncio
from pathlib import Path
from fastapi import FastAPI
from elasticsearch import AsyncElasticsearch
from redis.asyncio import Redis, from_url as redis_from_url
from app.api.v1 import films, genres, persons
from app.core.config import settings
from app.db import models 


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.project_name,
        description=settings.project_description,
        version=settings.project_version,
    )

    app.include_router(films.router, prefix="/api/v1")
    app.include_router(genres.router, prefix="/api/v1")
    app.include_router(persons.router, prefix="/api/v1")

    @app.on_event("startup")
    async def startup() -> None:        
        app.state.elastic = AsyncElasticsearch(hosts=[settings.es_url])
        app.state.redis = redis_from_url(settings.redis_url)

    @app.on_event("shutdown")
    async def shutdown() -> None:
        elastic: AsyncElasticsearch | None = getattr(app.state, "elastic", None)
        if elastic is not None:
            await elastic.close()
        redis: Redis | None = getattr(app.state, "redis", None)
        if redis is not None:
            await redis.close()

    return app

app = create_app()
