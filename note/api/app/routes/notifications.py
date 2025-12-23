from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db
from ..schemas.notification import DeliveryLogResponse, NotificationCreate, NotificationResponse
from ..schemas.preferences import PreferenceResponse, PreferenceUpdate
from ..services.notifications import (
    create_notification,
    enqueue_delivery,
    get_delivery_history,
    list_notifications,
    upsert_preference,
)

router = APIRouter(prefix="/api/v1", tags=["notifications"])


@router.post("/events/instant", response_model=NotificationResponse)
async def create_instant_event(data: NotificationCreate, db: AsyncSession = Depends(get_db)):
    notification = await create_notification(db, data)
    enqueue_delivery(notification, users=["*"])
    return NotificationResponse.model_validate(notification)


@router.post("/events/bulk", response_model=NotificationResponse)
async def create_bulk_event(data: NotificationCreate, users: List[str], db: AsyncSession = Depends(get_db)):
    notification = await create_notification(db, data)
    enqueue_delivery(notification, users=users)
    return NotificationResponse.model_validate(notification)


@router.post("/events/personal", response_model=NotificationResponse)
async def create_personal_event(data: NotificationCreate, user_id: str, db: AsyncSession = Depends(get_db)):
    notification = await create_notification(db, data)
    enqueue_delivery(notification, users=[user_id])
    return NotificationResponse.model_validate(notification)


@router.get("/notifications", response_model=List[NotificationResponse])
async def get_notifications(db: AsyncSession = Depends(get_db)):
    return await list_notifications(db)


@router.post("/users/{user_id}/preferences", response_model=PreferenceResponse)
async def set_user_preferences(user_id: str, data: PreferenceUpdate, db: AsyncSession = Depends(get_db)):
    pref = await upsert_preference(
        db,
        user_id=user_id,
        email=data.email_enabled,
        sms=data.sms_enabled,
        push=data.push_enabled,
    )
    return PreferenceResponse.model_validate(pref)


@router.get("/deliveries/{user_id}", response_model=List[DeliveryLogResponse])
async def get_user_deliveries(user_id: str, db: AsyncSession = Depends(get_db)):
    logs = await get_delivery_history(db, user_id)
    return [
        DeliveryLogResponse(
            user_id=log.user_id,
            status=log.status,
            channel=log.channel,
            error=log.error,
            created_at=log.created_at,
        )
        for log in logs
    ]
