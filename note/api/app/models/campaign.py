from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Campaign(Base):
    __tablename__ = "campaigns"

    name: Mapped[str] = mapped_column(String(128))
    template_id: Mapped[int] = mapped_column(ForeignKey("templates.id"))
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    repeat_cron: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    audience: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    template = relationship("Template")
