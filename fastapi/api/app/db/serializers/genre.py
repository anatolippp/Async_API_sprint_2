from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class GenreSerializer(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    uuid: str = Field(alias="id", serialization_alias="uuid")
    name: str
    description: str | None = None
