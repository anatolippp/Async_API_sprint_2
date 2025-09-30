from __future__ import annotations

from typing import Any

from elasticsearch import AsyncElasticsearch

from ..core.config import Settings
from ..db.serializers.film import FilmDetailSerializer, FilmShortSerializer
from .elastic import ElasticService


class FilmService(ElasticService):
    def __init__(self, elastic: AsyncElasticsearch, settings: Settings) -> None:
        super().__init__(elastic=elastic, index=settings.es_movies_index)

    async def get_film(self, film_id: str) -> dict[str, Any] | None:
        document = await self.get_by_id(film_id)
        if document is None:
            return None
        payload = FilmDetailSerializer(**document)
        return payload.model_dump(by_alias=True)

    async def list_films(
        self,
        *,
        page_size: int,
        page_number: int,
        genre: str | None = None,
        sort: str | None = None,
    ) -> list[dict[str, Any]]:
        offset = (page_number - 1) * page_size
        query: dict[str, Any]
        filters: list[dict[str, Any]] = []
        if genre:
            filters.append(
                {
                    "nested": {
                        "path": "genres",
                        "query": {"term": {"genres.id": genre}},
                    }
                }
            )
        if filters:
            query = {"bool": {"filter": filters}}
        else:
            query = {"match_all": {}}

        sort_clause = self._build_sort(sort)
        response = await self.search(
            query=query,
            size=page_size,
            offset=offset,
            sort=sort_clause,
        )
        hits = response.get("hits", {}).get("hits", [])
        return [FilmShortSerializer(**hit["_source"]).model_dump(by_alias=True) for hit in hits]

    async def search_films(
        self,
        *,
        query: str,
        page_size: int,
        page_number: int,
    ) -> list[dict[str, Any]]:
        offset = (page_number - 1) * page_size
        full_text_match = {
            "multi_match": {
                "query": query,
                "fields": [
                    "title^2",
                    "description",
                    "actors_names",
                    "writers_names",
                ],
                "fuzziness": "auto",
            }
        }
        prefix_match = {
            "multi_match": {
                "query": query,
                "fields": [
                    "title^2",
                    "description",
                    "actors_names",
                    "writers_names",
                ],
                "type": "phrase_prefix",
            }
        }
        search_query = {
            "bool": {
                "should": [full_text_match, prefix_match],
                "minimum_should_match": 1,
            }
        }
        response = await self.search(query=search_query, size=page_size, offset=offset)
        hits = response.get("hits", {}).get("hits", [])
        return [FilmShortSerializer(**hit["_source"]).model_dump(by_alias=True) for hit in hits]

    async def films_by_person(
        self,
        person_id: str,
        *,
        page_size: int,
        page_number: int,
    ) -> list[dict[str, Any]]:
        offset = (page_number - 1) * page_size
        query = {
            "bool": {
                "should": [
                    {
                        "nested": {
                            "path": path,
                            "query": {"term": {f"{path}.id": person_id}},
                        }
                    }
                    for path in ("actors", "writers", "directors")
                ],
                "minimum_should_match": 1,
            }
        }
        response = await self.search(query=query, size=page_size, offset=offset)
        hits = response.get("hits", {}).get("hits", [])
        return [FilmShortSerializer(**hit["_source"]).model_dump(by_alias=True) for hit in hits]

    @staticmethod
    def _build_sort(sort: str | None) -> list[dict[str, Any]] | None:
        if not sort:
            return None
        field = sort
        order = "asc"
        if sort.startswith("-"):
            field = sort[1:]
            order = "desc"
        if field not in {"imdb_rating", "title"}:
            return None
        es_field = field
        if field == "title":
            es_field = "title.raw"
        return [{es_field: {"order": order, "missing": "_last"}}]
