from __future__ import annotations

import asyncio
import os

from redis.asyncio import from_url as redis_from_url


async def wait_for_redis(timeout: int = 60) -> None:
    host = os.getenv("REDIS_HOST", "127.0.0.1")
    port = int(os.getenv("REDIS_PORT", "6379"))
    db = int(os.getenv("REDIS_DB", "0"))
    url = f"redis://{host}:{port}/{db}"

    deadline = asyncio.get_event_loop().time() + timeout
    client = redis_from_url(url)
    try:
        while True:
            try:
                if await client.ping():
                    return
            except Exception:
                pass
            if asyncio.get_event_loop().time() >= deadline:
                raise TimeoutError("Redis is unavailable")
            await asyncio.sleep(1)
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(wait_for_redis())