from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class NotificationBase(BaseModel):
    notification_type: str
    template_id: Optional[int] = None
    content_id: Optional[str] = None
    subject: str
    payload: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    repeat_cron: Optional[str] = Field(default=None, description="CRON-выражение для повторяющихся отправок")


class NotificationCreate(NotificationBase):
    pass


class DeliveryLogResponse(BaseModel):
    user_id: str
    status: str
    channel: str
    error: Optional[str] = None
    created_at: datetime


class NotificationResponse(NotificationBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
