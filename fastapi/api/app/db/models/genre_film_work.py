from __future__ import annotations

from sqlalchemy import Column, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID

from ..base import Base
from ...core.config import settings
from .mixins import UUIDMixin


class GenreFilmWork(UUIDMixin, Base):
    __tablename__ = "genre_film_work"
    __table_args__ = (
        UniqueConstraint("genre_id", "film_work_id", name="genre_film_work_unique"),
        {"schema": settings.pg_schema},
    )

    film_work_id = Column(
        UUID(as_uuid=True), ForeignKey("content.film_work.id", ondelete="CASCADE"), nullable=False
    )
    genre_id = Column(
        UUID(as_uuid=True), ForeignKey("content.genre.id", ondelete="CASCADE"), nullable=False
    )
    created = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)
