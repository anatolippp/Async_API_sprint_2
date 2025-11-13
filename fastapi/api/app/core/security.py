from __future__ import annotations

import hashlib
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import ValidationError
from redis.asyncio import Redis

from .config import settings
from .dependencies import get_auth_service_client, get_redis
from ..integrations.auth_client import (
    AuthServiceClient,
    AuthServiceError,
    AuthServiceUnauthorizedError,
    AuthServiceUnavailableError,
    TokenIntrospectionResult,
)

http_bearer = HTTPBearer(auto_error=False)


async def _load_cached_payload(
    redis: Redis, token: str
) -> TokenIntrospectionResult | None:
    cached = await redis.get(_token_cache_key(token))
    if not cached:
        return None

    try:
        payload = TokenIntrospectionResult.model_validate_json(cached)
    except (ValidationError, TypeError, ValueError):
        await redis.delete(_token_cache_key(token))
        return None

    if not payload.active or not payload.user_id:
        return None
    return payload


async def _store_payload(redis: Redis, token: str, payload: TokenIntrospectionResult) -> None:
    ttl = max(0, settings.auth_cache_ttl_seconds)
    if ttl == 0:
        return
    await redis.setex(_token_cache_key(token), ttl, payload.model_dump_json())


def _token_cache_key(token: str) -> str:
    digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
    return f"auth:introspection:{digest}"


async def get_current_user_payload(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(http_bearer),
    ],
    auth_client: AuthServiceClient = Depends(get_auth_service_client),
    redis: Redis = Depends(get_redis),
) -> TokenIntrospectionResult:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    cached = await _load_cached_payload(redis, token)
    if cached is not None:
        return cached

    try:
        payload = await auth_client.introspect_token(token)
    except AuthServiceUnauthorizedError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except AuthServiceUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unavailable",
        ) from exc
    except AuthServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to verify authentication token",
        ) from exc

    if not payload.active or not payload.user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    await _store_payload(redis, token, payload)
    return payload


AuthenticatedUser = TokenIntrospectionResult
CurrentUser = Annotated[AuthenticatedUser, Depends(get_current_user_payload)]


async def get_optional_user_payload(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(http_bearer),
    ],
    auth_client: AuthServiceClient = Depends(get_auth_service_client),
    redis: Redis = Depends(get_redis),
) -> TokenIntrospectionResult | None:
    if credentials is None:
        return None

    token = credentials.credentials
    cached = await _load_cached_payload(redis, token)
    if cached is not None:
        return cached

    try:
        payload = await auth_client.introspect_token(token)
    except AuthServiceUnauthorizedError:
        return None
    except AuthServiceUnavailableError:
        return None
    except AuthServiceError:
        return None

    if not payload.active or not payload.user_id:
        return None

    await _store_payload(redis, token, payload)
    return payload


OptionalCurrentUser = Annotated[
    TokenIntrospectionResult | None,
    Depends(get_optional_user_payload),
]

__all__ = [
    "AuthenticatedUser",
    "CurrentUser",
    "OptionalCurrentUser",
    "get_current_user_payload",
    "get_optional_user_payload",
]
