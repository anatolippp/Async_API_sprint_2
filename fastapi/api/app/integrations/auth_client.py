from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from http import HTTPStatus

import httpx
from pydantic import BaseModel, Field, ValidationError

logger = logging.getLogger(__name__)


class AuthServiceError(RuntimeError):
    """Base error for authentication service client."""


class AuthServiceUnavailableError(AuthServiceError):
    """Authentication service is unavailable."""


class AuthServiceUnauthorizedError(AuthServiceError):
    """Authentication failed due to invalid credentials or API key."""


class AuthServiceInvalidResponseError(AuthServiceError):
    """Authentication service returned malformed response."""


class AuthServiceClient:
    """HTTP client for communicating with the authentication service."""

    def __init__(
        self,
        base_url: str,
        *,
        introspection_path: str,
        internal_api_key: str | None = None,
        timeout: float = 5.0,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
    ) -> None:
        self._client = httpx.AsyncClient(base_url=base_url, timeout=timeout)
        self._introspection_path = introspection_path
        self._internal_api_key = internal_api_key
        self._max_retries = max(1, max_retries)
        self._backoff_factor = max(0.0, backoff_factor)

    async def close(self) -> None:
        await self._client.aclose()

    async def introspect_token(
        self,
        token: str,
        *,
        request_id: str | None = None,
        max_retries: int | None = None,
    ) -> "TokenIntrospectionResult":
        """Verify the provided token via the authentication service."""

        payload = {
            "token": token,
            "include_permissions": True,
            "include_roles": True,
        }

        headers: dict[str, str] = {}
        if self._internal_api_key:
            headers["X-Internal-Api-Key"] = self._internal_api_key
        if request_id:
            headers["X-Request-Id"] = request_id

        attempts_limit = max(1, max_retries or self._max_retries)

        for attempt in range(1, attempts_limit + 1):
            try:
                response = await self._client.post(
                    self._introspection_path,
                    json=payload,
                    headers=headers,
                )
            except httpx.RequestError as exc:
                logger.warning(
                    "Auth service request error on attempt %s: %s", attempt, exc
                )
                await self._maybe_sleep(attempt, attempts_limit)
                if attempt == attempts_limit:
                    raise AuthServiceUnavailableError("Authentication service unavailable") from exc
                continue

            if response.status_code == HTTPStatus.OK:
                try:
                    data = response.json()
                except ValueError as exc:
                    raise AuthServiceInvalidResponseError(
                        "Failed to decode authentication service response as JSON"
                    ) from exc

                try:
                    return TokenIntrospectionResult.model_validate(data)
                except ValidationError as exc:
                    raise AuthServiceInvalidResponseError(
                        "Authentication service returned unexpected payload"
                    ) from exc

            if response.status_code in {
                HTTPStatus.UNAUTHORIZED,
                HTTPStatus.FORBIDDEN,
            }:
                raise AuthServiceUnauthorizedError("Authentication failed")

            if response.status_code >= HTTPStatus.INTERNAL_SERVER_ERROR:
                logger.warning(
                    "Auth service error %s on attempt %s: %s",
                    response.status_code,
                    attempt,
                    response.text,
                )
                await self._maybe_sleep(attempt, attempts_limit)
                if attempt == attempts_limit:
                    raise AuthServiceUnavailableError("Authentication service unavailable")
                continue

            logger.error(
                "Unexpected response from auth service: %s %s",
                response.status_code,
                response.text,
            )
            raise AuthServiceError(
                f"Authentication service returned {response.status_code}"
            )

        raise AuthServiceUnavailableError("Authentication service unavailable")

    async def _maybe_sleep(self, attempt: int, attempts_limit: int) -> None:
        if attempt >= attempts_limit:
            return
        delay = self._backoff_factor * (2 ** (attempt - 1))
        if delay > 0:
            await asyncio.sleep(delay)


class IntrospectedRole(BaseModel):
    id: str
    name: str


class IntrospectedPermission(BaseModel):
    id: str
    resource: str
    action: str


class TokenIntrospectionResult(BaseModel):
    active: bool
    user_id: str | None = None
    username: str | None = None
    exp: datetime | None = None
    roles: list[IntrospectedRole] = Field(default_factory=list)
    permissions: list[IntrospectedPermission] = Field(default_factory=list)

    model_config = {
        "extra": "ignore",
    }


__all__ = [
    "AuthServiceClient",
    "AuthServiceError",
    "AuthServiceUnavailableError",
    "AuthServiceUnauthorizedError",
    "AuthServiceInvalidResponseError",
    "IntrospectedPermission",
    "IntrospectedRole",
    "TokenIntrospectionResult",
]
