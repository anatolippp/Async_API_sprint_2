"""Performance benchmark comparing MongoDB и PostgreSQL."""

from __future__ import annotations

import argparse
import os
import statistics
import time
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Mapping, Sequence

import psycopg2
from pymongo import MongoClient
from pymongo.database import Database

BudgetMs = int


def percentile(values: Sequence[float], perc: float) -> float:
    """Return percentile for a given ordered list."""

    ordered = sorted(values)
    index = int((len(ordered) - 1) * perc)
    return ordered[index]


def measure(label: str, action: Callable[[], None], samples: int = 5) -> Dict[str, float]:
    """Measure execution time of a callable in milliseconds."""

    timings: List[float] = []
    for _ in range(samples):
        start = time.perf_counter()
        action()
        timings.append((time.perf_counter() - start) * 1000)
    return {
        "label": label,
        "avg_ms": statistics.mean(timings),
        "p95_ms": percentile(timings, 0.95),
    }


def save_report(
    results: Iterable[Mapping[str, float]],
    output: Path,
    records: int,
    seed: int,
    batch: int,
) -> None:
    """Persist benchmark results to a markdown table with dataset metadata."""

    likes = records
    bookmarks = records // 10
    reviews = records // 5

    lines = [
        "# Отчёт нагрузочного тестирования",
        "",
        (
            "Объём данных: {likes:_} лайков, {bookmarks:_} закладок, {reviews:_} "
            "рецензий (batch={batch}, seed={seed})."
        ).format(
            likes=likes,
            bookmarks=bookmarks,
            reviews=reviews,
            batch=batch,
            seed=seed,
        ),
        "",
        "| Сценарий | Среднее время (мс) | p95 (мс) | Статус |",
        "| --- | --- | --- | --- |",
    ]

    for case in results:
        status = "OK" if case["avg_ms"] <= 200 else "SLOW"
        line = "| {label} | {avg:.1f} | {p95:.1f} | {status} |".format(
            label=case["label"],
            avg=case["avg_ms"],
            p95=case["p95_ms"],
            status=status,
        )
        lines.append(line)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")


def mongo_cases(
    mongo: Database,
    sample_user: str,
    sample_movie: str,
) -> List[Dict[str, float]]:
    """Build MongoDB benchmark cases."""

    def fetch_likes() -> None:
        list(mongo.likes.find({"user_id": sample_user}).limit(100))

    def fetch_rating() -> None:
        mongo.likes.aggregate(
            [
                {"$match": {"movie_id": sample_movie}},
                {
                    "$group": {
                        "_id": "$movie_id",
                        "avg": {"$avg": "$score"},
                        "count": {"$sum": 1},
                    },
                },
            ],
            allowDiskUse=True,
        ).to_list(1)

    def fetch_bookmarks() -> None:
        list(mongo.bookmarks.find({"user_id": sample_user}).limit(100))

    def fetch_reviews() -> None:
        list(
            mongo.reviews.find({"movie_id": sample_movie}).sort("likes", -1).limit(50),
        )

    return [
        measure("likes by user (mongo)", fetch_likes),
        measure("film rating (mongo)", fetch_rating),
        measure("bookmarks by user (mongo)", fetch_bookmarks),
        measure("reviews sort by likes (mongo)", fetch_reviews),
    ]


def pg_cases(pg_conn, sample_user: str, sample_movie: str) -> List[Dict[str, float]]:
    """Build PostgreSQL benchmark cases using short-lived cursors."""

    def execute(query: str, params: Sequence[str] | None = None) -> None:
        with pg_conn.cursor() as cur:
            cur.execute(query, params)
            cur.fetchall()

    def fetch_likes() -> None:
        execute("select * from likes where user_id = %s limit 100", (sample_user,))

    def fetch_rating() -> None:
        execute(
            "select avg(score), count(*) from likes where movie_id = %s",
            (sample_movie,),
        )

    def fetch_bookmarks() -> None:
        execute(
            "select movie_id, created_at from bookmarks where user_id = %s limit 100",
            (sample_user,),
        )

    def fetch_reviews() -> None:
        execute(
            "select id, likes, score from reviews where movie_id = %s order by likes desc limit 50",
            (sample_movie,),
        )

    return [
        measure("likes by user (postgres)", fetch_likes),
        measure("film rating (postgres)", fetch_rating),
        measure("bookmarks by user (postgres)", fetch_bookmarks),
        measure("reviews sort by likes (postgres)", fetch_reviews),
    ]


def pick_samples(mongo: Database, pg_conn) -> Dict[str, str]:
    """Pick stable sample user/movie IDs from existing data."""

    sample_doc = mongo.likes.find_one() or {
        "user_id": "demo-user",
        "movie_id": "demo-film",
    }
    sample_user = str(sample_doc["user_id"])
    sample_movie = str(sample_doc["movie_id"])

    with pg_conn.cursor() as cur:
        cur.execute("select user_id, movie_id from likes limit 1")
        row = cur.fetchone()
        if row:
            sample_user, sample_movie = str(row[0]), str(row[1])

    return {"user": sample_user, "movie": sample_movie}


def print_summary(results: Iterable[Mapping[str, float]], budget_ms: BudgetMs = 200) -> None:
    """Print human-readable summary to stdout."""

    print(f"\nPerformance summary (budget = {budget_ms} ms):")  # noqa: WPS421
    for case in results:
        status = "OK" if case["avg_ms"] <= budget_ms else "SLOW"
        message = (
            f"- {case['label']}: avg {case['avg_ms']:.1f} ms "
            f"(p95 {case['p95_ms']:.1f} ms) -> {status}"
        )
        print(message)  # noqa: WPS421


def main() -> None:
    """Run benchmark against both databases and save markdown report."""

    parser = argparse.ArgumentParser(description="Compare MongoDB vs PostgreSQL performance")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("reports/performance.md"),
        help="Куда сохранить результаты",
    )
    args = parser.parse_args()

    mongo_url = os.environ.get("MONGO_URL", "mongodb://app:app@localhost:27017/ugc")
    pg_dsn = os.environ.get("POSTGRES_DSN", "postgresql://app:app@localhost:5432/ugc")
    records = int(os.environ.get("DATASET_RECORDS", "10000000"))
    batch = int(os.environ.get("DATASET_BATCH", "5000"))
    seed = int(os.environ.get("DATASET_SEED", "42"))

    pg_conn = psycopg2.connect(pg_dsn)
    mongo_client: Database = MongoClient(mongo_url).get_default_database()

    samples = pick_samples(mongo_client, pg_conn)

    cases = [
        *mongo_cases(mongo_client, samples["user"], samples["movie"]),
        *pg_cases(pg_conn, samples["user"], samples["movie"]),
    ]

    print_summary(cases)
    save_report(cases, args.output, records, seed, batch)

    pg_conn.close()


if __name__ == "__main__":
    main()
