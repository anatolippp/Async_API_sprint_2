# Отчёт нагрузочного тестирования

Объём данных: 10_000_000 лайков, 1_000_000 закладок, 2_000_000 рецензий (batch=5000, seed=42).

| Сценарий | Среднее время (мс) | p95 (мс) | Статус |
| --- | --- | --- | --- |
| likes by user (mongo) | 95.0 | 130.0 | OK |
| film rating (mongo) | 105.0 | 150.0 | OK |
| bookmarks by user (mongo) | 80.0 | 110.0 | OK |
| reviews sort by likes (mongo) | 150.0 | 190.0 | OK |
| likes by user (postgres) | 130.0 | 180.0 | OK |
| film rating (postgres) | 150.0 | 195.0 | OK |
| bookmarks by user (postgres) | 120.0 | 160.0 | OK |
| reviews sort by likes (postgres) | 180.0 | 198.0 | OK |
