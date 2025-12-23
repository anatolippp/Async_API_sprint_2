from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Notification(Base):
    __tablename__ = "notifications"

    notification_type: Mapped[str] = mapped_column(String(32))
    template_id: Mapped[Optional[int]] = mapped_column(ForeignKey("templates.id"), nullable=True)
    content_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    subject: Mapped[str] = mapped_column(String(255))
    payload: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    repeat_cron: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    template = relationship("Template", back_populates="notifications")
    delivery_logs = relationship("DeliveryLog", back_populates="notification")


class DeliveryLog(Base):
    __tablename__ = "delivery_logs"

    notification_id: Mapped[int] = mapped_column(ForeignKey("notifications.id"))
    user_id: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32), default="queued")
    channel: Mapped[str] = mapped_column(String(16), default="email")
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    notification = relationship("Notification", back_populates="delivery_logs")
