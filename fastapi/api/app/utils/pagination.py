from __future__ import annotations

from dataclasses import dataclass

from fastapi import Query


@dataclass
class PageParams:
    page_size: int
    page_number: int


def get_pagination_params(
    page_size: int = Query(50, ge=1, le=1000),
    page_number: int = Query(1, ge=1),
) -> PageParams:
    return PageParams(page_size=page_size, page_number=page_number)
