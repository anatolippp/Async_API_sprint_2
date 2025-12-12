from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Конфигурация API.

    Параметры читаются из ``.env``. Мы специально разрешаем
    дополнительные переменные окружения, чтобы docker-compose мог
    прокидывать настройки, используемые сидером и бенчмарком
    (например, ``POSTGRES_DSN`` или размеры датасета), не ломая
    загрузку приложения.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    mongo_url: str = Field(
        default="mongodb://app:app@mongo:27017/ugc?authSource=admin",
        alias="MONGO_URL",
        description="Mongo connection string",
    )
    sentry_dsn: str | None = Field(default=None, alias="SENTRY_DSN")


def get_settings() -> Settings:
    return Settings()


settings = get_settings()
