from __future__ import annotations

import uuid

from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID

from ...core.config import settings


class UUIDMixin:
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


class TimeStampedMixin:
    created = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)
    modified = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=True
    )


class SchemaMixin:
    __table_args__ = {"schema": settings.pg_schema}
