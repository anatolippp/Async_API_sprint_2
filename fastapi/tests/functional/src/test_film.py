from __future__ import annotations

import uuid

import pytest

from tests.functional.settings import test_settings
from tests.functional.testdata import es_data


@pytest.mark.asyncio
async def test_films_list_validation_errors(load_movies, http_session, service_url):
    await load_movies()

    url = f"{service_url}/api/v1/films/"
    invalid_params = [
        {"page_size": 0},
        {"page_number": 0},
        {"page_size": 1001},
    ]
    for params in invalid_params:
        async with http_session.get(url, params=params) as response:
            assert response.status == 422


@pytest.mark.asyncio
async def test_film_details_validation_error(http_session, service_url):
    url = f"{service_url}/api/v1/films/not-a-uuid"
    async with http_session.get(url) as response:
        assert response.status == 422


@pytest.mark.asyncio
async def test_film_details_returns_film(load_all_data, http_session, service_url):
    await load_all_data()

    film_id = es_data.MOVIES[0]["id"]
    url = f"{service_url}/api/v1/films/{film_id}"
    async with http_session.get(url) as response:
        assert response.status == 200
        payload = await response.json()

    assert payload["uuid"] == film_id
    assert payload["title"] == es_data.MOVIES[0]["title"]
    assert isinstance(payload["genre"], list) and payload["genre"]
    assert {person["uuid"] for person in payload["actors"]} == {
        es_data.ACTOR_ONE_ID,
        es_data.ACTOR_TWO_ID,
    }


@pytest.mark.asyncio
async def test_film_details_not_found(load_movies, http_session, service_url):
    await load_movies()

    url = f"{service_url}/api/v1/films/{uuid.uuid4()}"
    async with http_session.get(url) as response:
        assert response.status == 404


@pytest.mark.asyncio
async def test_films_list_returns_all_movies(load_movies, http_session, service_url):
    await load_movies()

    url = f"{service_url}/api/v1/films/"
    params = {"page_size": 10}
    async with http_session.get(url, params=params) as response:
        assert response.status == 200
        body = await response.json()

    assert len(body) == len(es_data.MOVIES)


@pytest.mark.asyncio
async def test_film_details_cached(load_movies, http_session, es_client, service_url):
    await load_movies()

    film_id = es_data.MOVIES[1]["id"]
    url = f"{service_url}/api/v1/films/{film_id}"
    async with http_session.get(url) as response:
        assert response.status == 200
        first = await response.json()


    await es_client.indices.delete(index=test_settings.es_movies_index)

    async with http_session.get(url) as cached_response:
        assert cached_response.status == 200
        cached = await cached_response.json()


    assert cached == first