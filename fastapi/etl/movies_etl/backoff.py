from __future__ import annotations
import time
import random
import logging
from functools import wraps
from typing import Callable, Type, Iterable


def backoff(
    exceptions: Iterable[Type[BaseException]] = (Exception,),
    tries: int = 5,
    base: float = 0.5,
    factor: float = 2.0,
    max_sleep: float = 30.0,
    jitter: float = 0.1,
    logger: logging.Logger | None = None,
) -> Callable:
    def deco(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            _tries = tries
            delay = base
            while True:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    _tries -= 1
                    if _tries <= 0:
                        if logger:
                            logger.error("Backoff exhausted: %s", e)
                        raise
                    sleep_for = min(delay, max_sleep) + random.random() * jitter
                    if logger:
                        logger.warning(
                            "Error %s; retry in %.2fs (left=%s)",
                            type(e).__name__, sleep_for, _tries
                        )
                    time.sleep(sleep_for)
                    delay *= factor
        return wrapper
    return deco
