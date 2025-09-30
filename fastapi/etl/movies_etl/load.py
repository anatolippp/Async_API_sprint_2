from __future__ import annotations

import json
import logging
from typing import Iterable

from elasticsearch import Elasticsearch, helpers
from elasticsearch.exceptions import ConnectionError as ESConnectionError

from .backoff import backoff

logger = logging.getLogger(__name__)


class ES:
    def __init__(self, url: str, index: str) -> None:
        self.client = Elasticsearch(url)
        self.index = index

    @backoff(exceptions=(ESConnectionError,), logger=logger)
    def ensure_index(self, mapping_path: str) -> None:
        if self.client.indices.exists(index=self.index):
            return
        with open(mapping_path, "r", encoding="utf-8") as f:
            body = json.load(f)
        self.client.indices.create(index=self.index, body=body)

    @backoff(exceptions=(ESConnectionError,), logger=logger)
    def bulk_index(self, docs: Iterable[dict]) -> None:
        actions = (
            {
                "_index": self.index,
                "_id": doc["id"],
                "_source": doc,
            }
            for doc in docs
        )
        helpers.bulk(self.client, actions, stats_only=True)
