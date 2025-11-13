from __future__ import annotations

import uuid
from typing import Any, Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from ...core.dependencies import (
    get_cache_service,
    get_film_service,
    get_person_service,
)
from ...core.security import AuthenticatedUser, get_current_user_payload
from ...db.serializers.film import FilmShortSerializer
from ...db.serializers.person import PersonDetailSerializer
from ...services.cache import CacheService
from ...services.films import FilmService
from ...services.persons import PersonService
from ...utils.pagination import PageParams, get_pagination_params

router = APIRouter(prefix="/persons", tags=["Персоны"])


@router.get("/", 
            response_model=list[PersonDetailSerializer],
            summary="Список персон",
            description="Информация о персонах")
async def list_persons(
    request: Request,
    _: Annotated[AuthenticatedUser, Depends(get_current_user_payload)],
    params: PageParams = Depends(get_pagination_params),
    sort: str | None = Query(None, description="Сортировка персон по именам"),
    person_service: PersonService = Depends(get_person_service),
    cache: CacheService = Depends(get_cache_service),
) -> list[dict[str, Any]]:
    cache_key = cache.build_key(
        "persons:list",
        {
            "path": str(request.url.path),
            "params": sorted(request.query_params.multi_items()),
        },
    )
    cached = await cache.get(cache_key)
    if cached is not None:
        return cached

    persons = await person_service.list_persons(
        page_size=params.page_size,
        page_number=params.page_number,
        sort=sort,
    )
    await cache.set(cache_key, persons)
    return persons


@router.get("/search/", 
            response_model=list[PersonDetailSerializer],
            summary="Поиск персон",
            description="Полнотекстовый поиск по персонам фильмов")
async def search_persons(
    request: Request,
    _: Annotated[AuthenticatedUser, Depends(get_current_user_payload)],
    query: str = Query(..., min_length=1),
    params: PageParams = Depends(get_pagination_params),
    person_service: PersonService = Depends(get_person_service),
    cache: CacheService = Depends(get_cache_service),
) -> list[dict[str, Any]]:
    cache_key = cache.build_key(
        "persons:search",
        {
            "path": str(request.url.path),
            "params": sorted(request.query_params.multi_items()),
        },
    )
    cached = await cache.get(cache_key)
    if cached is not None:
        return cached

    persons = await person_service.search_persons(
        query=query,
        page_size=params.page_size,
        page_number=params.page_number,
    )
    await cache.set(cache_key, persons)
    return persons


@router.get("/{person_id}", 
            response_model=PersonDetailSerializer,
            summary="Поиск персоны",
            description="Информация о персоне")
async def person_details(
    person_id: uuid.UUID,
    _: Annotated[AuthenticatedUser, Depends(get_current_user_payload)],
    person_service: PersonService = Depends(get_person_service),
    cache: CacheService = Depends(get_cache_service),
) -> dict[str, Any]:
    cache_key = cache.build_key("persons:detail", {"person_id": str(person_id)})
    cached = await cache.get(cache_key)
    if cached is not None:
        return cached

    person = await person_service.get_person(str(person_id))
    if person is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Персона не найдена")
    await cache.set(cache_key, person)
    return person


@router.get("/{person_id}/film", 
            response_model=list[FilmShortSerializer],
            summary="Поиск персоны фильма",
            description="Получение информации о персонах фильма")
async def person_films(
    person_id: uuid.UUID,
    _: Annotated[AuthenticatedUser, Depends(get_current_user_payload)],
    params: PageParams = Depends(get_pagination_params),
    film_service: FilmService = Depends(get_film_service),
    cache: CacheService = Depends(get_cache_service),
) -> list[dict[str, Any]]:
    cache_key = cache.build_key(
        "persons:films",
        {
            "person_id": str(person_id),
            "page_size": params.page_size,
            "page_number": params.page_number,
        },
    )
    cached = await cache.get(cache_key)
    if cached is not None:
        return cached

    films = await film_service.films_by_person(
        str(person_id), page_size=params.page_size, page_number=params.page_number
    )
    await cache.set(cache_key, films)
    return films
