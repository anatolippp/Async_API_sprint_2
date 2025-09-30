UPDATED_FW_IDS = """
WITH updates AS (
  SELECT
    fw.id,
    GREATEST(
      COALESCE(fw.modified, 'epoch'::timestamp),
      COALESCE(MAX(g.modified), 'epoch'::timestamp),
      COALESCE(MAX(p.modified), 'epoch'::timestamp)
    ) AS updated_at
  FROM content.film_work fw
  LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
  LEFT JOIN content.genre g ON g.id = gfw.genre_id
  LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
  LEFT JOIN content.person p ON p.id = pfw.person_id
  GROUP BY fw.id
)
SELECT id, updated_at
FROM updates
WHERE updated_at > %(updated_after)s
ORDER BY updated_at, id
LIMIT %(limit)s;
"""

FW_BY_IDS = """
SELECT
  fw.id::text,
  fw.title,
  fw.description,
  fw.rating AS imdb_rating,
  COALESCE(
    JSON_AGG(
      DISTINCT JSONB_BUILD_OBJECT(
        'id', g.id::text,
        'name', g.name,
        'description', g.description
      )
    ) FILTER (WHERE g.id IS NOT NULL),
    '[]'::json
  ) AS genres,
  COALESCE(
    JSON_AGG(
      DISTINCT JSONB_BUILD_OBJECT(
        'id', p.id::text,
        'name', p.full_name,
        'role', pfw.role
      )
    ) FILTER (WHERE p.id IS NOT NULL),
    '[]'::json
  ) AS people
FROM content.film_work fw
LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
LEFT JOIN content.genre g ON g.id = gfw.genre_id
LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
LEFT JOIN content.person p ON p.id = pfw.person_id
WHERE fw.id = ANY(%(ids)s::uuid[])
GROUP BY fw.id;
"""

UPDATED_GENRE_IDS = """
WITH updates AS (
  SELECT
    g.id::text,
    GREATEST(
      COALESCE(g.modified, 'epoch'::timestamp),
      COALESCE(MAX(gfw.created), 'epoch'::timestamp),
      COALESCE(MAX(fw.modified), 'epoch'::timestamp)
    ) AS updated_at
  FROM content.genre g
  JOIN content.genre_film_work gfw ON gfw.genre_id = g.id
  JOIN content.film_work fw ON fw.id = gfw.film_work_id
  GROUP BY g.id
)
SELECT id, updated_at
FROM updates
WHERE updated_at > %(updated_after)s
ORDER BY updated_at, id
LIMIT %(limit)s;
"""

GENRES_BY_IDS = """
SELECT
  g.id::text,
  g.name,
  g.description
FROM content.genre g
JOIN content.genre_film_work gfw ON gfw.genre_id = g.id
JOIN content.film_work fw ON fw.id = gfw.film_work_id
WHERE g.id = ANY(%(ids)s::uuid[])
GROUP BY g.id, g.name, g.description;;
"""

UPDATED_PERSON_IDS = """
WITH updates AS (
  SELECT
    p.id::text,
    GREATEST(
      COALESCE(p.modified, 'epoch'::timestamp),
      COALESCE(MAX(fw.modified), 'epoch'::timestamp),
      COALESCE(MAX(pfw.created), 'epoch'::timestamp)
    ) AS updated_at
  FROM content.person p
  LEFT JOIN content.person_film_work pfw ON pfw.person_id = p.id
  LEFT JOIN content.film_work fw ON fw.id = pfw.film_work_id
  GROUP BY p.id
)
SELECT id, updated_at
FROM updates
WHERE updated_at > %(updated_after)s
ORDER BY updated_at, id
LIMIT %(limit)s;
"""

PERSONS_BY_IDS = """
SELECT
  p.id::text AS person_id,
  p.full_name,
  pfw.role,
  fw.id::text AS film_id,
  fw.title AS film_title,
  fw.rating AS imdb_rating
FROM content.person p
LEFT JOIN content.person_film_work pfw ON pfw.person_id = p.id
LEFT JOIN content.film_work fw ON fw.id = pfw.film_work_id
WHERE p.id = ANY(%(ids)s::uuid[])
ORDER BY p.id, fw.id;
"""
