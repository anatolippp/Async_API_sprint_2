import asyncio
from typing import Any

import aiohttp
from celery import Celery
from pydantic import Field
from pydantic_settings import BaseSettings
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.models.notification import DeliveryLog, Notification
from app.models.template import Template
from app.models.user_preferences import UserPreference


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

    auth_service_url: str = Field(..., validation_alias="AUTH_SERVICE_URL")

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()

celery_app = Celery(
    "note-worker",
    broker=f"amqp://guest:guest@{settings.rabbit_host}:{settings.rabbit_port}//",
    backend=f"redis://{settings.redis_host}:{settings.redis_port}/0",
)
celery_app.conf.task_default_queue = "notifications"

DATABASE_URL = (
    f"postgresql+asyncpg://{settings.db_user}:{settings.db_password}"
    f"@{settings.db_host}:{settings.db_port}/{settings.db_name}"
)
engine = create_async_engine(DATABASE_URL, echo=False, future=True)
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def fetch_user_profile(user_id: str) -> dict[str, Any]:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{settings.auth_service_url}/api/v1/users/{user_id}") as resp:
            if resp.status != 200:
                return {}
            return await resp.json()


async def send_email(address: str, subject: str, body: str) -> None:
    print(f"Отправлено письмо на {address}: {subject}\n{body}")


@celery_app.task(name="tasks.send_notification")
def send_notification(notification_id: int, user_id: str) -> None:
    asyncio.run(handle_notification(notification_id, user_id))


async def handle_notification(notification_id: int, user_id: str) -> None:
    async with AsyncSessionLocal() as db:
        notification = await db.get(Notification, notification_id)
        if not notification:
            return

        preferences = await db.execute(select(UserPreference).where(UserPreference.user_id == user_id))
        pref = preferences.scalar_one_or_none()
        if pref and not pref.email_enabled:
            await persist_log(db, notification_id, user_id, "skipped", "email", "email disabled")
            return

        template = await db.get(Template, notification.template_id) if notification.template_id else None
        user_profile = await fetch_user_profile(user_id)
        email = user_profile.get("email", "debug@example.com")
        full_name = f"{user_profile.get('first_name', '')} {user_profile.get('last_name', '')}".strip()

        subject = notification.subject
        body = notification.payload or ""
        if template:
            subject = template.subject_template.format(name=full_name)
            body = template.body_template.format(name=full_name, content_id=notification.content_id or "")

        await send_email(email, subject, body)
        await persist_log(db, notification_id, user_id, "delivered", template.channel if template else "email")


async def persist_log(db: AsyncSession, notification_id: int, user_id: str, status: str, channel: str, error: str | None = None) -> None:
    log = DeliveryLog(
        notification_id=notification_id,
        user_id=user_id,
        status=status,
        channel=channel,
        error=error,
    )
    db.add(log)
    await db.commit()


if __name__ == "__main__":
    celery_app.worker_main()
