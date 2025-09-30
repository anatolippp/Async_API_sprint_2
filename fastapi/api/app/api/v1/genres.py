from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from ...core.dependencies import get_cache_service, get_genre_service
from ...db.serializers.genre import GenreSerializer
from ...services.cache import CacheService
from ...services.genres import GenreService
from ...utils.pagination import PageParams, get_pagination_params

router = APIRouter(prefix="/genres", tags=["Жанры"])


@router.get("/", 
            response_model=list[GenreSerializer],
            summary="Список жанров фильмов",
            description="Информация о жанрах фильмов")
async def list_genres(
    request: Request,
    params: PageParams = Depends(get_pagination_params),
    sort: str | None = Query(None, description="Сортировка жанров фильмов по названию"),
    genre_service: GenreService = Depends(get_genre_service),
    cache: CacheService = Depends(get_cache_service),
) -> list[dict[str, Any]]:
    cache_key = cache.build_key(
        "genres:list",
        {
            "path": str(request.url.path),
            "params": sorted(request.query_params.multi_items()),
        },
    )
    cached = await cache.get(cache_key)
    if cached is not None:
        return cached

    genres = await genre_service.list_genres(
        page_size=params.page_size,
        page_number=params.page_number,
        sort=sort,
    )
    await cache.set(cache_key, genres)
    return genres


@router.get("/{genre_id}", 
            response_model=GenreSerializer,
            summary="Поиск жанра фильма",
            description="Информация о жанре фильма")
async def genre_details(
    genre_id: uuid.UUID,
    genre_service: GenreService = Depends(get_genre_service),
    cache: CacheService = Depends(get_cache_service),
) -> dict[str, Any]:
    cache_key = cache.build_key("genres:detail", {"genre_id": str(genre_id)})
    cached = await cache.get(cache_key)
    if cached is not None:
        return cached

    genre = await genre_service.get_genre(str(genre_id))
    if genre is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Жанр не найден")
    await cache.set(cache_key, genre)
    return genre
