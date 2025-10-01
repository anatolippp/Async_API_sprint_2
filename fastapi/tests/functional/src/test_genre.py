from __future__ import annotations

import uuid
from http import HTTPStatus
import pytest

from tests.functional.settings import test_settings
from tests.functional.testdata import es_data

@pytest.mark.asyncio
async def test_genre_details_validation_error(http_session, service_url):
    url = f"{service_url}/api/v1/genres/not-a-uuid"
    async with http_session.get(url) as response:
        assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY

@pytest.mark.asyncio
async def test_genres_list_validation_errors(load_genres, http_session, service_url):
    await load_genres()

    url = f"{service_url}/api/v1/genres/"
    invalid_params = [
        {"page_size": 0},
        {"page_number": 0},
        {"page_size": 1001},
    ]
    for params in invalid_params:
        async with http_session.get(url, params=params) as response:
            assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_genre_details(load_genres, http_session, service_url):
    await load_genres()

    genre_id = es_data.GENRES[0]["id"]
    url = f"{service_url}/api/v1/genres/{genre_id}"
    async with http_session.get(url) as response:
        assert response.status == HTTPStatus.OK
        payload = await response.json()

    assert payload == {
        "uuid": genre_id,
        "name": es_data.GENRES[0]["name"],
        "description": es_data.GENRES[0]["description"],
    }


@pytest.mark.asyncio
async def test_genre_not_found(load_genres, http_session, service_url):
    await load_genres()

    url = f"{service_url}/api/v1/genres/{uuid.uuid4()}"
    async with http_session.get(url) as response:
        assert response.status == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_genres_list(load_genres, http_session, service_url):
    await load_genres()

    url = f"{service_url}/api/v1/genres/"
    params = {"page_size": 10}
    async with http_session.get(url, params=params) as response:
        assert response.status == HTTPStatus.OK
        payload = await response.json()

    assert len(payload) == len(es_data.GENRES)
    assert {item["name"] for item in payload} == {
        genre["name"] for genre in es_data.GENRES
    }


@pytest.mark.asyncio
async def test_genre_details_cached(load_genres, http_session, es_client, service_url):
    await load_genres()

    genre_id = es_data.GENRES[1]["id"]
    url = f"{service_url}/api/v1/genres/{genre_id}"
    async with http_session.get(url) as response:
        assert response.status == HTTPStatus.OK
        cached = await response.json()

    await es_client.indices.delete(index=test_settings.es_genres_index)

    async with http_session.get(url) as second:
        assert second.status == HTTPStatus.OK
        payload = await second.json()


    assert payload == cached