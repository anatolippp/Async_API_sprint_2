from __future__ import annotations

from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from ..base import Base
from .mixins import SchemaMixin, TimeStampedMixin, UUIDMixin


class Person(UUIDMixin, TimeStampedMixin, SchemaMixin, Base):
    __tablename__ = "person"

    full_name = Column(String(255), nullable=False, index=True)

    film_works = relationship(
        "FilmWork",
        secondary="content.person_film_work",
        back_populates="persons",
        lazy="selectin",
    )
