"""Dataset generator for MongoDB и PostgreSQL с детерминированным seed."""

from __future__ import annotations

import argparse
import os
import random
from datetime import datetime
from typing import Dict, Iterable, Iterator, List, Sequence, Tuple, TypeVar

import psycopg2
import psycopg2.extras
from faker import Faker
from pymongo import ASCENDING, MongoClient
from pymongo.database import Database

faker = Faker()
T = TypeVar("T")


def chunked(items: Iterable[T], size: int) -> Iterator[List[T]]:
    """Yield items batched by ``size`` to keep память под контролем."""

    buffer: List[T] = []
    for item in items:
        buffer.append(item)
        if len(buffer) >= size:
            yield buffer
            buffer = []
    if buffer:
        yield buffer


def ensure_mongo(client: MongoClient) -> None:
    """Создаёт индексы MongoDB для ускорения чтения."""

    db = client.get_default_database()
    db.likes.create_index(
        [("user_id", ASCENDING), ("movie_id", ASCENDING)],
        unique=True,
    )
    db.likes.create_index([("movie_id", ASCENDING)])
    db.bookmarks.create_index(
        [("user_id", ASCENDING), ("movie_id", ASCENDING)],
        unique=True,
    )
    db.reviews.create_index([("movie_id", ASCENDING)])


def prepare_postgres(conn: psycopg2.extensions.connection) -> None:
    """Готовит таблицы PostgreSQL и индексы под сценарии чтения."""

    with conn.cursor() as cur:
        cur.execute(
            """
            create table if not exists likes (
                user_id varchar(36),
                movie_id varchar(36),
                score smallint,
                updated_at timestamp,
                primary key (user_id, movie_id)
            );
            create index if not exists idx_likes_movie on likes (movie_id);

            create table if not exists bookmarks (
                user_id varchar(36),
                movie_id varchar(36),
                created_at timestamp,
                primary key (user_id, movie_id)
            );
            create index if not exists idx_bookmarks_user on bookmarks (user_id);

            create table if not exists reviews (
                id serial primary key,
                user_id varchar(36),
                movie_id varchar(36),
                text text,
                created_at timestamp,
                likes integer default 0,
                dislikes integer default 0,
                score smallint
            );
            create index if not exists idx_reviews_movie on reviews (movie_id);
            create index if not exists idx_reviews_movie_likes on reviews (movie_id, likes desc);
            """,
        )
    conn.commit()


def generate_row(rng: random.Random, faker_local: Faker) -> Tuple[str, str]:
    """Возвращает детерминированные идентификаторы пользователя и фильма."""

    return faker_local.uuid4(), faker_local.uuid4()


def build_likes_dataset(
    base_seed: int,
    records: int,
    seed_offset: int = 0,
) -> Iterator[Dict[str, object]]:
    """Генерирует лайки, синхронные для обеих СУБД."""

    rng = random.Random(base_seed + seed_offset)
    faker_local = Faker()
    faker_local.seed_instance(base_seed + seed_offset)
    for _ in range(records):
        user_id, movie_id = generate_row(rng, faker_local)
        yield {
            "user_id": user_id,
            "movie_id": movie_id,
            "score": rng.randint(0, 10),
            "updated_at": datetime.utcnow(),
        }


def build_bookmarks_dataset(
    base_seed: int,
    records: int,
    seed_offset: int = 1000,
) -> Iterator[Dict[str, object]]:
    """Генерирует закладки с повторяемым порядком."""

    rng = random.Random(base_seed + seed_offset)
    faker_local = Faker()
    faker_local.seed_instance(base_seed + seed_offset)
    for _ in range(records // 10):
        user_id, movie_id = generate_row(rng, faker_local)
        yield {
            "user_id": user_id,
            "movie_id": movie_id,
            "created_at": datetime.utcnow(),
        }


def build_reviews_dataset(
    base_seed: int,
    records: int,
    seed_offset: int = 2000,
) -> Iterator[Dict[str, object]]:
    """Генерирует рецензии с оценками и реакциями."""

    rng = random.Random(base_seed + seed_offset)
    faker_local = Faker()
    faker_local.seed_instance(base_seed + seed_offset)
    for _ in range(records // 5):
        user_id, movie_id = generate_row(rng, faker_local)
        yield {
            "user_id": user_id,
            "movie_id": movie_id,
            "text": faker_local.sentence(nb_words=12),
            "created_at": datetime.utcnow(),
            "likes": rng.randint(0, 50),
            "dislikes": rng.randint(0, 10),
            "score": rng.randint(0, 10),
        }


def persist_likes_postgres(
    cur: psycopg2.extensions.cursor, batch: Sequence[Dict[str, object]],
) -> None:
    """Пишет партию лайков в PostgreSQL."""

    params: Sequence[Tuple[object, ...]] = [
        (
            row["user_id"],
            row["movie_id"],
            row["score"],
            row["updated_at"],
        )
        for row in batch
    ]
    psycopg2.extras.execute_batch(
        cur,
        (
            "insert into likes (user_id, movie_id, score, updated_at) values "
            "(%s, %s, %s, %s) on conflict (user_id, movie_id) do update set "
            "score = excluded.score, updated_at = excluded.updated_at"
        ),
        params,
    )


def persist_bookmarks_postgres(
    cur: psycopg2.extensions.cursor, batch: Sequence[Dict[str, object]],
) -> None:
    """Пишет партию закладок в PostgreSQL."""

    params = [
        (row["user_id"], row["movie_id"], row["created_at"]) for row in batch
    ]
    psycopg2.extras.execute_batch(
        cur,
        (
            "insert into bookmarks (user_id, movie_id, created_at) values "
            "(%s, %s, %s) on conflict (user_id, movie_id) do nothing"
        ),
        params,
    )


def persist_reviews_postgres(
    cur: psycopg2.extensions.cursor, batch: Sequence[Dict[str, object]],
) -> None:
    """Пишет партию рецензий в PostgreSQL."""

    params = [
        (
            row["user_id"],
            row["movie_id"],
            row["text"],
            row["created_at"],
            row["likes"],
            row["dislikes"],
            row["score"],
        )
        for row in batch
    ]
    psycopg2.extras.execute_batch(
        cur,
        (
            "insert into reviews (user_id, movie_id, text, created_at, "
            "likes, dislikes, score) values (%s, %s, %s, %s, %s, %s, %s)"
        ),
        params,
    )


def seed_streamed(
    mongo_db,
    pg_conn: psycopg2.extensions.connection,
    records: int,
    batch: int,
    base_seed: int,
) -> None:
    """Стримово пишет одинаковые данные в MongoDB и PostgreSQL."""

    likes_source = build_likes_dataset(base_seed, records)
    bookmarks_source = build_bookmarks_dataset(base_seed, records)
    reviews_source = build_reviews_dataset(base_seed, records)

    with pg_conn.cursor() as cur:
        for like_batch in chunked(likes_source, batch):
            mongo_db.likes.insert_many(like_batch)
            persist_likes_postgres(cur, like_batch)

        for bookmark_batch in chunked(bookmarks_source, batch):
            mongo_db.bookmarks.insert_many(bookmark_batch)
            persist_bookmarks_postgres(cur, bookmark_batch)

        for review_batch in chunked(reviews_source, batch):
            mongo_db.reviews.insert_many(review_batch)
            persist_reviews_postgres(cur, review_batch)

    pg_conn.commit()


def main() -> None:
    """Генерирует и загружает синтетические данные без пиков по памяти."""

    parser = argparse.ArgumentParser(
        description="Seed MongoDB и PostgreSQL синтетическими данными",
    )
    parser.add_argument(
        "--records",
        type=int,
        default=10_000_000,
        help="Количество записей лайков (остальные пропорционально)",
    )
    parser.add_argument("--batch", type=int, default=5_000, help="Размер пачки вставки")
    args = parser.parse_args()

    mongo_url = os.environ.get("MONGO_URL", "mongodb://app:app@localhost:27017/ugc")
    pg_dsn = os.environ.get("POSTGRES_DSN", "postgresql://app:app@localhost:5432/ugc")
    base_seed = int(os.environ.get("DATASET_SEED", 42))

    mongo_client = MongoClient(mongo_url)
    ensure_mongo(mongo_client)
    db = mongo_client.get_default_database()

    pg_conn = psycopg2.connect(pg_dsn)
    prepare_postgres(pg_conn)

    seed_streamed(db, pg_conn, args.records, args.batch, base_seed)


if __name__ == "__main__":
    main()
