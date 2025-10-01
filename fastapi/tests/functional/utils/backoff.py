from __future__ import annotations

import asyncio
import logging
import random
from collections.abc import Awaitable, Callable, Iterable
from functools import wraps
from typing import TypeVar

ReturnType = TypeVar("ReturnType")
AsyncCallable = Callable[..., Awaitable[ReturnType]]


def async_backoff(
    exceptions: Iterable[type[BaseException]] = (Exception,),
    tries: int = 5,
    base: float = 0.5,
    factor: float = 2.0,
    max_sleep: float = 30.0,
    jitter: float = 0.1,
    logger: logging.Logger | None = None,
) -> Callable[[AsyncCallable], AsyncCallable]:
    exceptions_tuple = tuple(exceptions)

    def decorator(func: AsyncCallable) -> AsyncCallable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            attempts_left = tries
            delay = base
            while True:
                try:
                    return await func(*args, **kwargs)
                except exceptions_tuple as error:  
                    attempts_left -= 1
                    if attempts_left <= 0:
                        if logger:
                            logger.error("Backoff exhausted: %s", error)
                        raise
                    sleep_for = min(delay, max_sleep) + random.random() * jitter
                    if logger:
                        logger.warning(
                            "Error %s; retry in %.2fs (left=%s)",
                            type(error).__name__,
                            sleep_for,
                            attempts_left,
                        )
                    await asyncio.sleep(sleep_for)
                    delay *= factor
        return wrapper  

    return decorator