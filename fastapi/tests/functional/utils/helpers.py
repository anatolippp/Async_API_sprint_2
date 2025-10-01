from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any

from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
from redis.asyncio import Redis


async def recreate_index(
    client: AsyncElasticsearch,
    index: str,
    mapping: dict[str, Any],
) -> None:
    exists = await client.indices.exists(index=index)
    if exists:
        await client.indices.delete(index=index)
    await client.indices.create(index=index, **mapping)


async def load_bulk(
    client: AsyncElasticsearch,
    index: str,
    documents: Iterable[dict[str, Any]],
) -> None:
    actions: list[dict[str, Any]] = []
    for document in documents:
        actions.append({"_index": index, "_id": document["id"], "_source": document})

    if actions:
        success, errors = await async_bulk(
            client=client,
            actions=actions,
            refresh="wait_for",
        )
        if errors:
            raise RuntimeError(f"Failed to load data to index {index}: {errors}")
        if success != len(actions):
            raise RuntimeError(
                f"Unexpected number of indexed documents: {success} != {len(actions)}"
            )   


async def flush_redis(redis: Redis) -> None:
    await redis.flushall()


async def with_index(
    client: AsyncElasticsearch,
    index: str,
    mapping: dict[str, Any],
    loader: Callable[[], Iterable[dict[str, Any]]],
) -> None:
    await recreate_index(client, index, mapping)
    await load_bulk(client, index, loader())