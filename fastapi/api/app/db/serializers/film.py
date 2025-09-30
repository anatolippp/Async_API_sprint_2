from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from .genre import GenreSerializer
from .person import PersonFilmSerializer, PersonShortSerializer


class FilmShortSerializer(BaseModel):
    model_config = ConfigDict(populate_by_name=True, json_encoders={})

    uuid: str = Field(alias="id", serialization_alias="uuid")
    title: str
    imdb_rating: float | None = Field(default=None)


class FilmDetailSerializer(FilmShortSerializer):
    description: str | None = None
    genre: list[GenreSerializer] = Field(
        default_factory=list,
        validation_alias="genres",
        serialization_alias="genre",
    )
    actors: list[PersonShortSerializer] = Field(default_factory=list)
    writers: list[PersonShortSerializer] = Field(default_factory=list)
    directors: list[PersonShortSerializer] = Field(default_factory=list)


class FilmWithPersonsSerializer(FilmShortSerializer):
    persons: list[PersonFilmSerializer] = Field(default_factory=list)
