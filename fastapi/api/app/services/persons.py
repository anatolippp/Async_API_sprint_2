from __future__ import annotations

from typing import Any

from elasticsearch import AsyncElasticsearch

from ..core.config import Settings
from ..db.serializers.person import PersonDetailSerializer
from .elastic import ElasticService


class PersonService(ElasticService):
    def __init__(self, elastic: AsyncElasticsearch, settings: Settings) -> None:
        super().__init__(elastic=elastic, index=settings.es_persons_index)

    async def get_person(self, person_id: str) -> dict[str, Any] | None:
        document = await self.get_by_id(person_id)
        if document is None:
            return None
        return PersonDetailSerializer(**document).model_dump(by_alias=True)

    async def list_persons(
        self,
        *,
        page_size: int,
        page_number: int,
        sort: str | None = None,
    ) -> list[dict[str, Any]]:
        offset = (page_number - 1) * page_size
        query: dict[str, Any] = {"match_all": {}}
        sort_clause = self._build_sort(sort)
        response = await self.search(
            query=query, 
            size=page_size, 
            offset=offset, 
            sort=sort_clause
            )
        hits = response.get("hits", {}).get("hits", [])
        return [PersonDetailSerializer(**hit["_source"]).model_dump(by_alias=True) for hit in hits]

    async def search_persons(
        self,
        *,
        query: str,
        page_size: int,
        page_number: int,
    ) -> list[dict[str, Any]]:
        offset = (page_number - 1) * page_size
        es_query = {
            "bool": {
                "must": [
                    {
                        "multi_match": {
                            "query": query,
                            "fields": ["full_name^2"],
                            "fuzziness": "auto",
                        }
                    }
                ]
            }
        }
        response = await self.search(query=es_query, size=page_size, offset=offset)
        hits = response.get("hits", {}).get("hits", [])
        return [PersonDetailSerializer(**hit["_source"]).model_dump(by_alias=True) for hit in hits]

    async def film_participants(self, film_id: str) -> list[dict[str, Any]]:        
        return []

    @staticmethod
    def _build_sort(sort: str | None) -> list[dict[str, Any]] | None:
        if not sort:
            return None
        field = sort
        order = "asc"
        if sort.startswith("-"):
            field = sort[1:]
            order = "desc"
        if field != "full_name":
            return None
        return [{"full_name.raw": {"order": order}}]
