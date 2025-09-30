from __future__ import annotations

import logging
from datetime import datetime
from typing import Sequence

import psycopg2
import psycopg2.extras

from .backoff import backoff
from .sql import (
    UPDATED_FW_IDS,
    UPDATED_GENRE_IDS,
    UPDATED_PERSON_IDS,
    FW_BY_IDS,
    GENRES_BY_IDS,
    PERSONS_BY_IDS,
)

logger = logging.getLogger(__name__)


class PG:
    def __init__(self, **dsn) -> None:
        self._dsn = dsn
        self._conn: psycopg2.extensions.connection | None = None

    @backoff(logger=logger)
    def connect(self) -> None:
        if self._conn:
            return
        self._conn = psycopg2.connect(**self._dsn)
        self._conn.autocommit = True

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None

    @backoff(logger=logger)
    def fetch_updated_ids(
        self, updated_after: datetime, limit: int
    ) -> list[tuple[str, datetime]]:
        self.connect()
        assert self._conn
        with self._conn.cursor() as cur:
            cur.execute(
                UPDATED_FW_IDS,
                {"updated_after": updated_after, "limit": limit},
            )
            rows = cur.fetchall()
        return [(r[0], r[1]) for r in rows]

    @backoff(logger=logger)
    def fetch_films(self, ids: Sequence[str]) -> list[dict]:
        if not ids:
            return []
        self.connect()
        assert self._conn
        with self._conn.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor
        ) as cur:
            cur.execute(FW_BY_IDS, {"ids": list(ids)})
            rows = cur.fetchall()
        return [dict(r) for r in rows]

    @backoff(logger=logger)
    def fetch_updated_genre_ids(
        self, updated_after: datetime, limit: int
    ) -> list[tuple[str, datetime]]:
        self.connect()
        assert self._conn
        with self._conn.cursor() as cur:
            cur.execute(
                UPDATED_GENRE_IDS,
                {"updated_after": updated_after, "limit": limit},
            )
            rows = cur.fetchall()
        return [(r[0], r[1]) for r in rows]

    @backoff(logger=logger)
    def fetch_genres(self, ids: Sequence[str]) -> list[dict]:
        if not ids:
            return []
        self.connect()
        assert self._conn
        with self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(GENRES_BY_IDS, {"ids": list(ids)})
            rows = cur.fetchall()
        return [dict(r) for r in rows]

    @backoff(logger=logger)
    def fetch_updated_person_ids(
        self, updated_after: datetime, limit: int
    ) -> list[tuple[str, datetime]]:
        self.connect()
        assert self._conn
        with self._conn.cursor() as cur:
            cur.execute(
                UPDATED_PERSON_IDS,
                {"updated_after": updated_after, "limit": limit},
            )
            rows = cur.fetchall()
        return [(r[0], r[1]) for r in rows]

    @backoff(logger=logger)
    def fetch_persons(self, ids: Sequence[str]) -> list[dict]:
        if not ids:
            return []
        self.connect()
        assert self._conn
        with self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(PERSONS_BY_IDS, {"ids": list(ids)})
            rows = cur.fetchall()
        return [dict(r) for r in rows]
