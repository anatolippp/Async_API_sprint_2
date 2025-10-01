from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class TestSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    service_url: str = Field(default="http://127.0.0.1:8000", alias="SERVICE_URL")
    es_host: str = Field(default="http://127.0.0.1:9200", alias="ELASTIC_HOST")
    es_movies_index: str = Field(default="movies", alias="ES_MOVIES_INDEX")
    es_genres_index: str = Field(default="genres", alias="ES_GENRES_INDEX")
    es_persons_index: str = Field(default="persons", alias="ES_PERSONS_INDEX")
    redis_host: str = Field(default="127.0.0.1", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")
    redis_db: int = Field(default=0, alias="REDIS_DB")
    
    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"


test_settings = TestSettings()