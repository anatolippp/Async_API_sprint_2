from __future__ import annotations
from typing import Any
from collections import defaultdict

from .config import ESFilm, ESFilmPerson, ESGenre, ESPerson

NA_VALUES = {"n/a", "N/A", "NA", "None", None, ""}


def _clean(value: Any) -> Any:
    if isinstance(value, str) and value.strip() in NA_VALUES:
        return None
    return value


def to_es_doc(row: dict) -> ESFilm:
    ppl = row.get("people") or []

    def pick(role: str) -> list[dict]:
        out: list[dict] = []
        for it in ppl:
            r = (it.get("role") or "").strip().lower()
            name = _clean(it.get("name"))
            pid = it.get("id")
            if r == role and name:
                out.append({"id": pid, "name": name})
        return out

    directors = pick("director")
    writers = pick("writer")
    actors = pick("actor")

    genres_raw = row.get("genres") or []
    genres: list[ESGenre] = []
    genre_names: list[str] = []
    for genre in genres_raw:
        gid = genre.get("id")
        name = _clean(genre.get("name"))
        if not gid or not name:
            continue
        description = _clean(genre.get("description"))
        genres.append(ESGenre(id=gid, name=name, description=description))
        genre_names.append(name)

    doc = ESFilm(
        id=row["id"],
        imdb_rating=float(row["imdb_rating"]) if row["imdb_rating"] is not None else 0.0,
        genres=genres,
        genre_names=genre_names,
        title=_clean(row.get("title")),
        description=_clean(row.get("description")),
        directors_names=[p["name"] for p in directors],
        actors_names=[p["name"] for p in actors],
        writers_names=[p["name"] for p in writers],
        directors=[ESFilmPerson(**p) for p in directors],
        actors=[ESFilmPerson(**p) for p in actors],
        writers=[ESFilmPerson(**p) for p in writers],
    )
    return doc


def to_genre_doc(row: dict) -> ESGenre:
    return ESGenre(
        id=row["id"],
        name=_clean(row.get("name")),
        description=_clean(row.get("description")),
    )


def to_person_docs(rows: list[dict]) -> list[ESPerson]:
    persons: dict[str, ESPerson] = {}

    for row in rows:
        pid = row.get("person_id")
        if not pid:
            continue
        full_name = _clean(row.get("full_name"))
        if not full_name:
            continue    
        if pid not in persons:
            persons[pid] = ESPerson(id=pid, full_name=full_name)
    return list(persons.values())