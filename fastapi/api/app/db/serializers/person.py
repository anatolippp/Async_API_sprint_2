from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, AliasChoices


class PersonBaseSerializer(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    uuid: str = Field(alias="id", serialization_alias="uuid")
    full_name: str = Field(
        validation_alias=AliasChoices("full_name", "name"),
        serialization_alias="full_name",
    )


class PersonShortSerializer(PersonBaseSerializer):
    pass



class PersonDetailSerializer(PersonBaseSerializer):
    pass


class PersonFilmSerializer(PersonBaseSerializer):
    pass
