from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class TestSettings:
    service_url: str = os.getenv("SERVICE_URL", "http://127.0.0.1:8000")
    es_host: str = os.getenv("ELASTIC_HOST", "http://127.0.0.1:9200")
    es_movies_index: str = os.getenv("ES_MOVIES_INDEX", "movies")
    es_genres_index: str = os.getenv("ES_GENRES_INDEX", "genres")
    es_persons_index: str = os.getenv("ES_PERSONS_INDEX", "persons")
    redis_host: str = os.getenv("REDIS_HOST", "127.0.0.1")
    redis_port: int = int(os.getenv("REDIS_PORT", "6379"))
    redis_db: int = int(os.getenv("REDIS_DB", "0"))

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"


test_settings = TestSettings()