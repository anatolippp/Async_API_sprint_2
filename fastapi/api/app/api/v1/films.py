from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from ...core.dependencies import (
    get_cache_service,
    get_film_service,
)
from ...core.security import ResilientCurrentUser
from ...db.serializers.film import FilmDetailSerializer, FilmShortSerializer
from ...services.cache import CacheService
from ...services.films import FilmService
from ...utils.pagination import PageParams, get_pagination_params

router = APIRouter(prefix="/films", tags=["Фильмы"])


@router.get("/", 
            response_model=list[FilmShortSerializer],
            summary="Список кинопроизведений",
            description="Получение списка кинопроизведений",)
async def films_list(
    request: Request,
    _: ResilientCurrentUser,
    params: PageParams = Depends(get_pagination_params),
    sort: str | None = Query(None, description="Сортировка фильмов по рейтингу"),
    genre: uuid.UUID | None = Query(None, description="Genre UUID для фильтра"),
    film_service: FilmService = Depends(get_film_service),
    cache: CacheService = Depends(get_cache_service),
) -> list[dict[str, Any]]:
    cache_key = cache.build_key(
        "films:list",
        {
            "path": str(request.url.path),
            "params": sorted(request.query_params.multi_items()),
        },
    )
    cached = await cache.get(cache_key)
    if cached is not None:
        return cached

    items = await film_service.list_films(
        page_size=params.page_size,
        page_number=params.page_number,
        sort=sort,
        genre=str(genre) if genre else None,
    )
    await cache.set(cache_key, items)
    return items


@router.get("/search/", 
            response_model=list[FilmShortSerializer],
            summary="Поиск кинопроизведений",
            description="Полнотекстовый поиск по кинопроизведениям",
            response_description="Название и рейтинг фильма"
            )
async def films_search(
    request: Request,
    _: ResilientCurrentUser,
    query: str = Query(..., min_length=1, description="Поисковая фраза"),
    params: PageParams = Depends(get_pagination_params),
    film_service: FilmService = Depends(get_film_service),
    cache: CacheService = Depends(get_cache_service),
) -> list[dict[str, Any]]:
    cache_key = cache.build_key(
        "films:search",
        {
            "path": str(request.url.path),
            "params": sorted(request.query_params.multi_items()),
        },
    )
    cached = await cache.get(cache_key)
    if cached is not None:
        return cached

    items = await film_service.search_films(
        query=query,
        page_size=params.page_size,
        page_number=params.page_number,
    )
    await cache.set(cache_key, items)
    return items


@router.get("/{film_id}", 
            response_model=FilmDetailSerializer,
            summary="Поиск фильма",
            description="Получение описания фильма")
async def film_details(
    film_id: uuid.UUID,
     _: ResilientCurrentUser,
    film_service: FilmService = Depends(get_film_service),
    cache: CacheService = Depends(get_cache_service),
) -> dict[str, Any]:
    cache_key = cache.build_key("films:detail", {"film_id": str(film_id)})
    cached = await cache.get(cache_key)
    if cached is not None:
        return cached

    document = await film_service.get_film(str(film_id))
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Фильм не найден")
    await cache.set(cache_key, document)
    return document
