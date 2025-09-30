from __future__ import annotations
import sys
import time
import logging
from datetime import datetime, timedelta
from logging import StreamHandler
from importlib.resources import files

from movies_etl.config import Settings
from movies_etl.state import JSONState
from movies_etl.extract import PG
from movies_etl.transform import to_es_doc, to_genre_doc, to_person_docs
from movies_etl.load import ES

logging.basicConfig(
    level=logging.INFO,
    handlers=[StreamHandler(sys.stdout)],
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("etl")


def parse_iso(s: str | None) -> datetime:
    if not s:
        return datetime(1970, 1, 1)
    return datetime.fromisoformat(s)


def main() -> None:
    cfg = Settings()

    state = JSONState(cfg.state_file)
    updated_after = parse_iso(state.get("movies_updated_after") or state.get("updated_after"))
    genres_updated_after = parse_iso(state.get("genres_updated_after"))
    persons_updated_after = parse_iso(state.get("persons_updated_after"))

    pg = PG(
        host=cfg.pg_host,
        port=cfg.pg_port,
        dbname=cfg.pg_db,
        user=cfg.pg_user,
        password=cfg.pg_password,
    )

    movies_es = ES(cfg.es_url, cfg.es_movies_index)
    genres_es = ES(cfg.es_url, cfg.es_genres_index)
    persons_es = ES(cfg.es_url, cfg.es_persons_index)

    movies_es.ensure_index(str(files("movies_etl").joinpath("movies_index.json")))
    genres_es.ensure_index(str(files("movies_etl").joinpath("genres_index.json")))
    persons_es.ensure_index(str(files("movies_etl").joinpath("persons_index.json")))

    logger.info(
        "Start ETL: films=%s genres=%s persons=%s",
        updated_after.isoformat(),
        genres_updated_after.isoformat(),
        persons_updated_after.isoformat(),
    )

    while True:
        processed = False

        movie_rows = pg.fetch_updated_ids(updated_after, cfg.batch_size)
        if movie_rows:
            processed = True
            ids = [r[0] for r in movie_rows]
            batch_max_updated = max(r[1] for r in movie_rows)

            films = pg.fetch_films(ids)
            docs = [to_es_doc(row).model_dump(mode="json") for row in films]
            if docs:
                movies_es.bulk_index(docs)

            safe_point = batch_max_updated - timedelta(microseconds=1)
            state.set("movies_updated_after", safe_point.isoformat())
            updated_after = safe_point
            logger.info("Indexed %s films; state=%s", len(docs), updated_after.isoformat())

        genre_rows = pg.fetch_updated_genre_ids(genres_updated_after, cfg.batch_size)
        if genre_rows:
            processed = True
            ids = [r[0] for r in genre_rows]
            batch_max_updated = max(r[1] for r in genre_rows)
            genres = pg.fetch_genres(ids)
            docs = [to_genre_doc(row).model_dump(mode="json") for row in genres]
            if docs:
                genres_es.bulk_index(docs)

            safe_point = batch_max_updated - timedelta(microseconds=1)
            state.set("genres_updated_after", safe_point.isoformat())
            genres_updated_after = safe_point
            logger.info("Indexed %s genres; state=%s", len(docs), genres_updated_after.isoformat())

        person_rows = pg.fetch_updated_person_ids(persons_updated_after, cfg.batch_size)
        if person_rows:
            processed = True
            ids = [r[0] for r in person_rows]
            batch_max_updated = max(r[1] for r in person_rows)
            persons = pg.fetch_persons(ids)
            docs = [doc.model_dump(mode="json") for doc in to_person_docs(persons)]
            if docs:
                persons_es.bulk_index(docs)

            safe_point = batch_max_updated - timedelta(microseconds=1)
            state.set("persons_updated_after", safe_point.isoformat())
            persons_updated_after = safe_point
            logger.info(
                "Indexed %s persons; state=%s", len(docs), persons_updated_after.isoformat()
            )

        if not processed:
            logger.info("No new data. Sleep 5s…")
            time.sleep(5)


if __name__ == "__main__":
    main()
