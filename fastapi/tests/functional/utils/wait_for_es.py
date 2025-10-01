from __future__ import annotations

import asyncio
import logging

from elastic_transport import ConnectionError, ConnectionTimeout
from elasticsearch import AsyncElasticsearch

from tests.functional.settings import test_settings
from tests.functional.utils.backoff import async_backoff

logger = logging.getLogger(__name__)


@async_backoff(
    exceptions=(ConnectionError, ConnectionTimeout, asyncio.TimeoutError, RuntimeError),
    tries=10,
    logger=logger,
)
async def _ping(client: AsyncElasticsearch) -> None:
    if not await client.ping():
        raise RuntimeError("Elasticsearch ping returned False")


async def wait_for_es(timeout: int = 60) -> None:
    client = AsyncElasticsearch(hosts=[test_settings.es_host], verify_certs=False)
    try:
        await asyncio.wait_for(_ping(client), timeout=timeout)
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(wait_for_es())