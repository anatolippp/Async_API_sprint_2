from datetime import datetime
from typing import Iterable, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import DeliveryLog, Notification, Template, UserPreference
from ..schemas.notification import NotificationCreate, NotificationResponse
from .queue import celery_app


async def create_notification(db: AsyncSession, data: NotificationCreate) -> Notification:
    notification = Notification(**data.model_dump())
    db.add(notification)
    await db.commit()
    await db.refresh(notification)
    return notification


def enqueue_delivery(notification: Notification, users: Iterable[str]) -> None:
    for user_id in users:
        celery_app.send_task(
            "tasks.send_notification",
            kwargs={
                "notification_id": notification.id,
                "user_id": user_id,
            },
        )


async def list_notifications(db: AsyncSession) -> List[NotificationResponse]:
    result = await db.execute(select(Notification))
    notifications = result.scalars().all()
    return [NotificationResponse.model_validate(item) for item in notifications]


async def upsert_preference(db: AsyncSession, user_id: str, email: bool, sms: bool, push: bool) -> UserPreference:
    result = await db.execute(select(UserPreference).where(UserPreference.user_id == user_id))
    pref = result.scalar_one_or_none()
    if pref:
        pref.email_enabled = email
        pref.sms_enabled = sms
        pref.push_enabled = push
    else:
        pref = UserPreference(user_id=user_id, email_enabled=email, sms_enabled=sms, push_enabled=push)
        db.add(pref)
    await db.commit()
    await db.refresh(pref)
    return pref


async def get_delivery_history(db: AsyncSession, user_id: str) -> List[DeliveryLog]:
    result = await db.execute(select(DeliveryLog).where(DeliveryLog.user_id == user_id))
    return result.scalars().all()


async def log_delivery(db: AsyncSession, notification_id: int, user_id: str, status: str, channel: str, error: str | None = None) -> DeliveryLog:
    log = DeliveryLog(
        notification_id=notification_id,
        user_id=user_id,
        status=status,
        channel=channel,
        error=error,
    )
    db.add(log)
    await db.commit()
    await db.refresh(log)
    return log


async def ensure_template(db: AsyncSession, name: str, subject: str, body: str) -> Template:
    result = await db.execute(select(Template).where(Template.name == name))
    template = result.scalar_one_or_none()
    if template:
        return template

    template = Template(name=name, subject_template=subject, body_template=body)
    db.add(template)
    await db.commit()
    await db.refresh(template)
    return template


async def due_notifications(db: AsyncSession, now: datetime) -> list[Notification]:
    result = await db.execute(
        select(Notification).where(
            Notification.scheduled_at != None,  # noqa: E711
            Notification.scheduled_at <= now,
        )
    )
    return result.scalars().all()
