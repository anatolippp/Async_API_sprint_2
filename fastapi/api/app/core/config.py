from __future__ import annotations

from functools import lru_cache
from typing import Any
from urllib.parse import quote_plus

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    
    project_name: str = Field(alias="PROJECT_NAME")
    project_description: str = Field(alias="PROJECT_DESCRIPTION")
    project_version: str = Field(alias="PROJECT_VERSION")

    es_host: str = Field(alias="ES_HOST")
    es_port: int = Field(alias="ES_PORT")
    es_scheme: str | None = Field(default=None, alias="ES_SCHEME")
    es_movies_index: str = Field(alias="ES_MOVIES_INDEX")
    es_genres_index: str = Field(alias="ES_GENRES_INDEX")
    es_persons_index: str = Field(alias="ES_PERSONS_INDEX")

    redis_host: str = Field(alias="REDIS_HOST")
    redis_port: int = Field(alias="REDIS_PORT")
    redis_db: int = Field(alias="REDIS_DB")
    cache_expire: int = Field(alias="CACHE_EXPIRE_SECONDS")

    pg_host: str = Field(alias="POSTGRES_HOST")
    pg_port: int = Field(alias="POSTGRES_PORT")
    pg_db: str = Field(alias="POSTGRES_DB")
    pg_user: str = Field(alias="POSTGRES_USER")
    pg_password: str = Field(alias="POSTGRES_PASSWORD")
    pg_schema: str = Field(alias="POSTGRES_SCHEMA")
    pg_options: str | None = Field(default=None, alias="POSTGRES_OPTIONS")
    db_echo: bool = Field(default=False, alias="DB_ECHO")

    @property
    def es_url(self) -> str:
        scheme = self.es_scheme or "http"
        return f"{scheme}://{self.es_host}:{self.es_port}"        

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    @property
    def sqlalchemy_database_uri(self) -> str:
        password = quote_plus(self.pg_password)
        options = (
            f"?options={quote_plus(self.pg_options)}" if self.pg_options else ""
        )
        return (
            f"postgresql+asyncpg://{self.pg_user}:{password}"
            f"@{self.pg_host}:{self.pg_port}/{self.pg_db}{options}"
        )

    @property
    def sync_sqlalchemy_uri(self) -> str:
        password = quote_plus(self.pg_password)
        options = (
            f"?options={quote_plus(self.pg_options)}" if self.pg_options else ""
        )
        return (
            f"postgresql+psycopg://{self.pg_user}:{password}"
            f"@{self.pg_host}:{self.pg_port}/{self.pg_db}{options}"
        )

@lru_cache()
def get_settings() -> Settings:
    return Settings()  


settings = get_settings()
