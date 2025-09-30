from __future__ import annotations

from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship

from ..base import Base
from .mixins import SchemaMixin, TimeStampedMixin, UUIDMixin


class Genre(UUIDMixin, TimeStampedMixin, SchemaMixin, Base):
    __tablename__ = "genre"

    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)

    film_works = relationship(
        "FilmWork",
        secondary="content.genre_film_work",
        back_populates="genres",
        lazy="selectin",
    )
