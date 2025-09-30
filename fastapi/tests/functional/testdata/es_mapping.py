MOVIES_INDEX_MAPPING = {
    "settings": {
        "refresh_interval": "1s",
        "analysis": {
            "analyzer": {
                "ru_en": {
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                    ],
                }
            }
        },
    },
    "mappings": {
        "properties": {
            "id": {"type": "keyword"},
            "title": {
                "type": "text",
                "fields": {"raw": {"type": "keyword"}},
                "analyzer": "ru_en",
            },
            "imdb_rating": {"type": "float"},
            "description": {"type": "text", "analyzer": "ru_en"},
            "actors_names": {"type": "text", "analyzer": "ru_en"},
            "writers_names": {"type": "text", "analyzer": "ru_en"},
            "directors_names": {"type": "text", "analyzer": "ru_en"},
            "genres": {
                "type": "nested",
                "properties": {
                    "id": {"type": "keyword"},
                    "name": {
                        "type": "text",
                        "fields": {"raw": {"type": "keyword"}},
                    },
                    "description": {"type": "text", "analyzer": "ru_en"},
                },
            },
            "actors": {
                "type": "nested",
                "properties": {
                    "id": {"type": "keyword"},
                    "name": {
                        "type": "text",
                        "fields": {"raw": {"type": "keyword"}},
                    },
                },
            },
            "writers": {
                "type": "nested",
                "properties": {
                    "id": {"type": "keyword"},
                    "name": {
                        "type": "text",
                        "fields": {"raw": {"type": "keyword"}},
                    },
                },
            },
            "directors": {
                "type": "nested",
                "properties": {
                    "id": {"type": "keyword"},
                    "name": {
                        "type": "text",
                        "fields": {"raw": {"type": "keyword"}},
                    },
                },
            },
        }
    },
}

GENRES_INDEX_MAPPING = {
    "settings": {"refresh_interval": "1s"},
    "mappings": {
        "properties": {
            "id": {"type": "keyword"},
            "name": {
                "type": "text",
                "fields": {"raw": {"type": "keyword"}},
            },
            "description": {"type": "text"},
        }
    },
}

PERSONS_INDEX_MAPPING = {
    "settings": {"refresh_interval": "1s"},
    "mappings": {
        "properties": {
            "id": {"type": "keyword"},
            "full_name": {
                "type": "text",
                "fields": {"raw": {"type": "keyword"}},
            },
        }
    },
}