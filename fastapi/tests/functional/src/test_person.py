from __future__ import annotations

import uuid
from http import HTTPStatus
import pytest

from tests.functional.settings import test_settings
from tests.functional.testdata import es_data

@pytest.mark.asyncio
async def test_person_details_validation_error(http_session, service_url):
    url = f"{service_url}/api/v1/persons/not-a-uuid"
    async with http_session.get(url) as response:
        assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_person_search_validation_errors(load_persons, http_session, service_url):
    await load_persons()

    url = f"{service_url}/api/v1/persons/search/"
    invalid_params = [
        {},
        {"query": ""},
        {"query": "ann", "page_size": 0},
        {"query": "ann", "page_number": 0},
    ]
    for params in invalid_params:
        async with http_session.get(url, params=params) as response:
            assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_person_details(load_persons, http_session, service_url):
    await load_persons()

    person_id = es_data.PERSONS[0]["id"]
    url = f"{service_url}/api/v1/persons/{person_id}"
    async with http_session.get(url) as response:
        assert response.status == HTTPStatus.OK
        payload = await response.json()

    assert payload == {
        "uuid": person_id,
        "full_name": es_data.PERSONS[0]["full_name"],
    }


@pytest.mark.asyncio
async def test_person_not_found(load_persons, http_session, service_url):
    await load_persons()

    url = f"{service_url}/api/v1/persons/{uuid.uuid4()}"
    async with http_session.get(url) as response:
        assert response.status == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_persons_list(load_persons, http_session, service_url):
    await load_persons()

    url = f"{service_url}/api/v1/persons/"
    params = {"page_size": 10}
    async with http_session.get(url, params=params) as response:
        assert response.status == HTTPStatus.OK
        payload = await response.json()

    assert len(payload) == len(es_data.PERSONS)
    assert {item["full_name"] for item in payload} == {
        person["full_name"] for person in es_data.PERSONS
    }


@pytest.mark.asyncio
async def test_persons_search(load_persons, http_session, service_url):
    await load_persons()

    url = f"{service_url}/api/v1/persons/search/"
    params = {"query": "ann"}
    async with http_session.get(url, params=params) as response:
        assert response.status == HTTPStatus.OK
        payload = await response.json()

    assert [item["uuid"] for item in payload] == [es_data.ACTOR_ONE_ID]


@pytest.mark.asyncio
async def test_person_films(load_movies, load_persons, http_session, service_url):
    await load_movies()
    await load_persons()

    person_id = es_data.ACTOR_ONE_ID
    url = f"{service_url}/api/v1/persons/{person_id}/film"
    async with http_session.get(url) as response:
        assert response.status == HTTPStatus.OK
        payload = await response.json()

    assert {item["uuid"] for item in payload} == {
        es_data.MOVIES[0]["id"],
        es_data.MOVIES[1]["id"],
    }


@pytest.mark.asyncio
async def test_person_details_cached(load_persons, http_session, es_client, service_url):
    await load_persons()

    person_id = es_data.PERSONS[1]["id"]
    url = f"{service_url}/api/v1/persons/{person_id}"
    async with http_session.get(url) as response:
        assert response.status == HTTPStatus.OK
        cached = await response.json()

    await es_client.indices.delete(index=test_settings.es_persons_index)

    async with http_session.get(url) as second:
        assert second.status == HTTPStatus.OK
        payload = await second.json()

    assert payload == cached