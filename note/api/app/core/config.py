from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_name: str = Field(..., validation_alias="POSTGRES_DB")
    db_user: str = Field(..., validation_alias="POSTGRES_USER")
    db_password: str = Field(..., validation_alias="POSTGRES_PASSWORD")
    db_host: str = Field(..., validation_alias="POSTGRES_HOST")
    db_port: int = Field(5432, validation_alias="POSTGRES_PORT")

    rabbit_host: str = Field(..., validation_alias="RABBIT_HOST")
    rabbit_port: int = Field(5672, validation_alias="RABBIT_PORT")

    redis_host: str = Field(..., validation_alias="REDIS_HOST")
    redis_port: int = Field(6379, validation_alias="REDIS_PORT")

    api_port: int = Field(8083, validation_alias="API_PORT")

    auth_service_url: str = Field(..., validation_alias="AUTH_SERVICE_URL")
    content_service_url: str = Field(..., validation_alias="CONTENT_SERVICE_URL")

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
