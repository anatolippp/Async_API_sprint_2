from __future__ import annotations

from datetime import datetime

ACTION_ID = "76b0c4f2-3947-46fb-9ff3-7b2cd508c45f"
DRAMA_ID = "3ff7f25f-0ae3-42d7-8a5d-21099d5b1f82"
COMEDY_ID = "b9ff1ca1-4659-4920-a9de-999855af9dc7"

ACTOR_ONE_ID = "11c160c4-5b56-47b8-99c6-630abd48a2aa"
ACTOR_TWO_ID = "4a76a1b8-3bf5-4a64-9c63-93ec3b81d717"
WRITER_ID = "0877a13b-5c5a-4db7-9df9-2e2a9d8f930d"
DIRECTOR_ID = "fa8ec019-88f0-4d51-881d-484a59c21207"

GENRES = [
    {
        "id": ACTION_ID,
        "name": "Action",
        "description": "Action movies",
    },
    {
        "id": DRAMA_ID,
        "name": "Drama",
        "description": "Dramatic films",
    },
    {
        "id": COMEDY_ID,
        "name": "Comedy",
        "description": "Comedy films",
    },
]

PERSONS = [
    {"id": ACTOR_ONE_ID, "full_name": "Ann Black"},
    {"id": ACTOR_TWO_ID, "full_name": "Bob Green"},
    {"id": WRITER_ID, "full_name": "Chris White"},
    {"id": DIRECTOR_ID, "full_name": "Dora Brown"},
]

MOVIES = [
    {
        "id": "a4a4381d-7f0c-4a1f-9e2d-4a7e6371af86",
        "imdb_rating": 8.5,
        "title": "The Star Adventure",
        "description": "Space explorers discover a new star system.",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "genres": GENRES[:2],
        "actors": [
            {"id": ACTOR_ONE_ID, "name": "Ann Black"},
            {"id": ACTOR_TWO_ID, "name": "Bob Green"},
        ],
        "writers": [{"id": WRITER_ID, "name": "Chris White"}],
        "directors": [{"id": DIRECTOR_ID, "name": "Dora Brown"}],
        "actors_names": ["Ann Black", "Bob Green"],
        "writers_names": ["Chris White"],
        "directors_names": ["Dora Brown"],
    },
    {
        "id": "f0bdf1c9-8d97-41b4-a64f-4e80bc0489e6",
        "imdb_rating": 7.1,
        "title": "Lonely Planet",
        "description": "An introvert finds friendship across the galaxy.",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "genres": [GENRES[1], GENRES[2]],
        "actors": [{"id": ACTOR_ONE_ID, "name": "Ann Black"}],
        "writers": [{"id": WRITER_ID, "name": "Chris White"}],
        "directors": [{"id": DIRECTOR_ID, "name": "Dora Brown"}],
        "actors_names": ["Ann Black"],
        "writers_names": ["Chris White"],
        "directors_names": ["Dora Brown"],
    },
    {
        "id": "dd46ce5f-86e9-4d07-9d6d-5cf3998fbbce",
        "imdb_rating": 6.2,
        "title": "Starfall Comedy",
        "description": "A misfit crew accidentally becomes famous comedians.",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "genres": [GENRES[0], GENRES[2]],
        "actors": [{"id": ACTOR_TWO_ID, "name": "Bob Green"}],
        "writers": [{"id": WRITER_ID, "name": "Chris White"}],
        "directors": [{"id": DIRECTOR_ID, "name": "Dora Brown"}],
        "actors_names": ["Bob Green"],
        "writers_names": ["Chris White"],
        "directors_names": ["Dora Brown"],
    },
]