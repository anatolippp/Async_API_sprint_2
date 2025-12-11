from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    mongo_url: str = Field(
        default="mongodb://app:app@localhost:27017/ugc",
        alias="MONGO_URL",
        description="Mongo connection string",
    )
    sentry_dsn: str | None = Field(default=None, alias="SENTRY_DSN")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def get_settings() -> Settings:
    return Settings()


settings = get_settings()
