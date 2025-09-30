from __future__ import annotations

from sqlalchemy import Column, DateTime, ForeignKey, String, UniqueConstraint, func, Index
from sqlalchemy.dialects.postgresql import UUID

from ..base import Base
from ...core.config import settings
from .mixins import UUIDMixin


class PersonFilmWork(UUIDMixin, Base):
    __tablename__ = "person_film_work"
    __table_args__ = (
        UniqueConstraint("person_id", "film_work_id", "role", name="person_film_work_unique"),
        Index("person_film_work_film_idx", "film_work_id"),
        {"schema": settings.pg_schema},
    )

    film_work_id = Column(
        UUID(as_uuid=True), ForeignKey("content.film_work.id", ondelete="CASCADE"), nullable=False
    )
    person_id = Column(
        UUID(as_uuid=True), ForeignKey("content.person.id", ondelete="CASCADE"), nullable=False
    )
    role = Column(String(255), nullable=False)
    created = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)
