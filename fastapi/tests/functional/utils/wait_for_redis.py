from __future__ import annotations

import asyncio
import logging

from redis.asyncio import Redis, from_url as redis_from_url
from redis.exceptions import ConnectionError as RedisConnectionError
from redis.exceptions import TimeoutError as RedisTimeoutError

from tests.functional.settings import test_settings
from tests.functional.utils.backoff import async_backoff


logger = logging.getLogger(__name__)


@async_backoff(
    exceptions=(
        RedisConnectionError, 
        RedisTimeoutError, 
        asyncio.TimeoutError, 
        RuntimeError, 
        OSError
        ),
    tries=10,
    logger=logger,
)
async def _ping(client: Redis) -> None:
    if not await client.ping():
        raise RuntimeError("Redis ping returned False")

async def wait_for_redis(timeout: int = 60) -> None:
    client = redis_from_url(test_settings.redis_url)  
    try:
        await asyncio.wait_for(_ping(client), timeout=timeout)
    finally:
        await client.aclose()


if __name__ == "__main__":
    asyncio.run(wait_for_redis())