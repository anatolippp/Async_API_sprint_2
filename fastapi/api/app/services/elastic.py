from __future__ import annotations

from typing import Any, Iterable

from elasticsearch import AsyncElasticsearch, NotFoundError


class ElasticService:
    def __init__(self, elastic: AsyncElasticsearch, index: str) -> None:
        self.elastic = elastic
        self.index = index

    async def get_by_id(self, doc_id: str) -> dict[str, Any] | None:
        try:
            document = await self.elastic.get(index=self.index, id=doc_id)
        except NotFoundError:
            return None
        return document.get("_source")

    async def search(
        self,
        query: dict[str, Any],
        *,
        size: int,
        offset: int,
        sort: Iterable[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        body = {"query": query}
        if sort:
            body["sort"] = list(sort)
        response = await self.elastic.search(
            index=self.index,
            body=body,
            size=size,
            from_=offset,
        )
        return response
