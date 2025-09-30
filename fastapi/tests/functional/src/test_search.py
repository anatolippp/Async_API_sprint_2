from __future__ import annotations

import pytest

from ..settings import test_settings
from ..testdata import es_data


@pytest.mark.asyncio
async def test_search_validation_errors(http_session, service_url):
    url = f"{service_url}/api/v1/films/search/"
    async with http_session.get(url) as response:
        assert response.status == 422

    query_params = [
        {"query": "", "page_size": 1, "page_number": 1},
        {"query": "star", "page_size": 0, "page_number": 1},
        {"query": "star", "page_size": 1001, "page_number": 1},
        {"query": "star", "page_size": 1, "page_number": 0},
    ]

    for params in query_params:
        async with http_session.get(url, params=params) as response:
            assert response.status == 422


@pytest.mark.asyncio
async def test_search_returns_limited_number_of_records(load_movies, http_session, service_url):
    await load_movies()

    url = f"{service_url}/api/v1/films/search/"
    params = {"query": "star", "page_size": 2}
    async with http_session.get(url, params=params) as response:
        assert response.status == 200


        body = await response.json()  
    assert len(body) == 2      
    assert all("uuid" in item for item in body)


@pytest.mark.asyncio
async def test_search_finds_records_by_phrase(load_movies, http_session, service_url):
    await load_movies()

    url = f"{service_url}/api/v1/films/search/"
    params = {"query": "galaxy"}
    async with http_session.get(url, params=params) as response:
        assert response.status == 200
        body = await response.json()

    assert {item["title"] for item in body} == {es_data.MOVIES[1]["title"]}


@pytest.mark.asyncio
async def test_search_uses_cache(load_movies, http_session, es_client, service_url):
    await load_movies()

    url = f"{service_url}/api/v1/films/search/"
    params = {"query": "star"}
    async with http_session.get(url, params=params) as response:
        assert response.status == 200
        initial_payload = await response.json()

    await es_client.indices.delete(index=test_settings.es_movies_index)

    async with http_session.get(url, params=params) as cached_response:
        assert cached_response.status == 200
        cached_payload = await cached_response.json()
    assert cached_payload == initial_payload