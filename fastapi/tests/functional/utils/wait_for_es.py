from __future__ import annotations

import asyncio
import os

from elasticsearch import AsyncElasticsearch


async def wait_for_es(timeout: int = 60) -> None:
    host = os.getenv("ELASTIC_HOST", "http://127.0.0.1:9200")
    deadline = asyncio.get_event_loop().time() + timeout
    client = AsyncElasticsearch(hosts=[host], verify_certs=False)
    try:
        while True:
            try:
                if await client.ping():
                    return
            except Exception:
                pass
            if asyncio.get_event_loop().time() >= deadline:
                raise TimeoutError("Elasticsearch is unavailable")
            await asyncio.sleep(1)
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(wait_for_es())