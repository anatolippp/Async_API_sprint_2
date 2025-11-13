from __future__ import annotations

from fastapi import Depends, Request
from elasticsearch import AsyncElasticsearch
from redis.asyncio import Redis

from .config import settings
from ..integrations.auth_client import AuthServiceClient
from ..services.cache import CacheService
from ..services.films import FilmService
from ..services.genres import GenreService
from ..services.persons import PersonService


async def get_redis(request: Request) -> Redis:
    redis: Redis | None = getattr(request.app.state, "redis", None)
    if redis is None:
        raise RuntimeError("Redis connection is not initialised")
    return redis


async def get_elastic(request: Request) -> AsyncElasticsearch:
    client: AsyncElasticsearch | None = getattr(request.app.state, "elastic", None)
    if client is None:
        raise RuntimeError("Elasticsearch client is not initialised")
    return client


def get_cache_service(redis: Redis = Depends(get_redis)) -> CacheService:
    return CacheService(redis=redis, ttl=settings.cache_expire)


async def get_auth_service_client(request: Request) -> AuthServiceClient:
    client: AuthServiceClient | None = getattr(request.app.state, "auth_client", None)
    if client is None:
        raise RuntimeError("Auth service client is not initialised")
    return client


def get_film_service(
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(elastic=elastic, settings=settings)


def get_genre_service(
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(elastic=elastic, settings=settings)


def get_person_service(
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(elastic=elastic, settings=settings)
