from __future__ import annotations

from enum import Enum

from sqlalchemy import Column, Date, Float, String, Text
from sqlalchemy.orm import relationship

from ..base import Base
from .mixins import SchemaMixin, TimeStampedMixin, UUIDMixin


class FilmType(str, Enum):
    MOVIE = "movie"
    TV_SHOW = "tv_show"


class FilmWork(UUIDMixin, TimeStampedMixin, SchemaMixin, Base):
    __tablename__ = "film_work"

    title = Column(Text, nullable=False, index=True)
    description = Column(Text, nullable=True)
    creation_date = Column(Date, nullable=True)
    rating = Column(Float, nullable=True)
    type = Column(String(50), nullable=False)
    certificate = Column(String(512), nullable=True)
    file_path = Column(String(1024), nullable=True)

    genres = relationship(
        "Genre",
        secondary="content.genre_film_work",
        back_populates="film_works",
        lazy="selectin",
    )
    persons = relationship(
        "Person",
        secondary="content.person_film_work",
        back_populates="film_works",
        lazy="selectin",
    )
