from __future__ import annotations

import hashlib
import json
from typing import Any

from redis.asyncio import Redis


class CacheService:
    def __init__(self, redis: Redis, ttl: int) -> None:
        self._redis = redis
        self._ttl = ttl

    async def get(self, key: str) -> Any | None:
        cached = await self._redis.get(key)
        if cached is None:
            return None
        if isinstance(cached, bytes):
            cached = cached.decode("utf-8")
        return json.loads(cached)

    async def set(self, key: str, value: Any) -> None:
        payload = json.dumps(value, ensure_ascii=False)
        await self._redis.set(key, payload, ex=self._ttl)

    @staticmethod
    def build_key(namespace: str, data: Any) -> str:
        raw = json.dumps(data, ensure_ascii=False, sort_keys=True)
        digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        return f"{namespace}:{digest}"
