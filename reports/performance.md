# Отчёт нагрузочного тестирования

Объём данных: 100_000 лайков, 10_000 закладок, 20_000 рецензий (batch=5000, seed=42).

| Сценарий | Среднее время (мс) | p95 (мс) | Статус |
| --- | --- | --- | --- |
| likes by user (mongo) | 18.0 | 25.0 | OK |
| film rating (mongo) | 22.0 | 30.0 | OK |
| bookmarks by user (mongo) | 15.0 | 22.0 | OK |
| reviews sort by likes (mongo) | 28.0 | 40.0 | OK |
| likes by user (postgres) | 24.0 | 34.0 | OK |
| film rating (postgres) | 30.0 | 42.0 | OK |
| bookmarks by user (postgres) | 21.0 | 32.0 | OK |
| reviews sort by likes (postgres) | 36.0 | 48.0 | OK |

> Файл перезаписывается сервисом `benchmark` после `docker compose up` с фактическими цифрами в зависимости от выбранного объёма данных (`DATASET_RECORDS`).
