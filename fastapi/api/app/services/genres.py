from __future__ import annotations

from typing import Any

from elasticsearch import AsyncElasticsearch

from ..core.config import Settings
from ..db.serializers.genre import GenreSerializer
from .elastic import ElasticService


class GenreService(ElasticService):
    def __init__(self, elastic: AsyncElasticsearch, settings: Settings) -> None:
        super().__init__(elastic=elastic, index=settings.es_genres_index)

    async def get_genre(self, genre_id: str) -> dict[str, Any] | None:
        document = await self.get_by_id(genre_id)
        if document is None:
            return None
        return GenreSerializer(**document).model_dump(by_alias=True)

    async def list_genres(
        self,
        *,
        page_size: int,
        page_number: int,
        sort: str | None = None,
    ) -> list[dict[str, Any]]:
        offset = (page_number - 1) * page_size
        query: dict[str, Any] = {"match_all": {}}
        sort_clause = self._build_sort(sort)
        response = await self.search(query=query, size=page_size, offset=offset, sort=sort_clause)
        hits = response.get("hits", {}).get("hits", [])
        return [GenreSerializer(**hit["_source"]).model_dump(by_alias=True) for hit in hits]

    @staticmethod
    def _build_sort(sort: str | None) -> list[dict[str, Any]] | None:
        if not sort:
            return None
        field = sort
        order = "asc"
        if sort.startswith("-"):
            field = sort[1:]
            order = "desc"
        if field != "name":
            return None
        return [{"name.raw": {"order": order}}]
