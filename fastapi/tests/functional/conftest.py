from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Awaitable, Callable

import aiohttp
import pytest
import pytest_asyncio
from elasticsearch import AsyncElasticsearch
from redis.asyncio import Redis, from_url as redis_from_url

from .settings import test_settings
from .testdata import es_data
from .testdata.es_mapping import (
    GENRES_INDEX_MAPPING,
    MOVIES_INDEX_MAPPING,
    PERSONS_INDEX_MAPPING,
)
from .utils.helpers import flush_redis, load_bulk, recreate_index


@pytest_asyncio.fixture(scope="function")
async def es_client() -> AsyncElasticsearch:
    client = AsyncElasticsearch(hosts=[test_settings.es_host], verify_certs=False)
    try:
        yield client
    finally:
        await client.close()


@pytest_asyncio.fixture(scope="function")
async def redis_client() -> Redis:
    client = redis_from_url(test_settings.redis_url)
    try:
        yield client
    finally:
        await client.aclose()


@pytest_asyncio.fixture
async def http_session():
    session = aiohttp.ClientSession()
    try:
        yield session
    finally:
        await session.close()


@pytest_asyncio.fixture(autouse=True)
async def clean_cache(redis_client: Redis) -> None:
    await flush_redis(redis_client)
    yield
    await flush_redis(redis_client)


def _ensure_documents(
    documents: Iterable[dict[str, Any]] | None,
    fallback: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if documents is None:
        return list(fallback)
    return list(documents)


@pytest.fixture
def load_movies(
    es_client: AsyncElasticsearch,
) -> Callable[[Iterable[dict[str, Any]] | None], Awaitable[None]]:
    async def loader(documents: Iterable[dict[str, Any]] | None = None) -> None:
        docs = _ensure_documents(documents, es_data.MOVIES)
        await recreate_index(
            es_client,
            test_settings.es_movies_index,
            MOVIES_INDEX_MAPPING,
        )
        await load_bulk(es_client, test_settings.es_movies_index, docs)

    return loader


@pytest.fixture
def load_genres(
    es_client: AsyncElasticsearch,
) -> Callable[[Iterable[dict[str, Any]] | None], Awaitable[None]]:
    async def loader(documents: Iterable[dict[str, Any]] | None = None) -> None:
        docs = _ensure_documents(documents, es_data.GENRES)
        await recreate_index(
            es_client,
            test_settings.es_genres_index,
            GENRES_INDEX_MAPPING,
        )
        await load_bulk(es_client, test_settings.es_genres_index, docs)

    return loader


@pytest.fixture
def load_persons(
    es_client: AsyncElasticsearch,
) -> Callable[[Iterable[dict[str, Any]] | None], Awaitable[None]]:
    async def loader(documents: Iterable[dict[str, Any]] | None = None) -> None:
        docs = _ensure_documents(documents, es_data.PERSONS)
        await recreate_index(
            es_client,
            test_settings.es_persons_index,
            PERSONS_INDEX_MAPPING,
        )
        await load_bulk(es_client, test_settings.es_persons_index, docs)

    return loader


@pytest.fixture
def load_all_data(
    load_movies: Callable[[Iterable[dict[str, Any]] | None], Awaitable[None]],
    load_genres: Callable[[Iterable[dict[str, Any]] | None], Awaitable[None]],
    load_persons: Callable[[Iterable[dict[str, Any]] | None], Awaitable[None]],
) -> Callable[[], Awaitable[None]]:
    async def loader() -> None:
        await load_movies()
        await load_genres()
        await load_persons()

    return loader


@pytest.fixture
def service_url() -> str:
    return test_settings.service_url
