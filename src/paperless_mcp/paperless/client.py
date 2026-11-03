"""HTTP client for the Paperless-ngx REST API."""

import logging
from typing import Any

import httpx

from paperless_mcp.config import Settings

logger = logging.getLogger(__name__)


class PaperlessAPIError(RuntimeError):
    """An error returned by the Paperless API."""


class PaperlessClient:
    """Small async client that centralizes authentication and API errors."""

    def __init__(
        self,
        settings: Settings,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        """Create an authenticated async client for the Paperless API."""
        self._http = httpx.AsyncClient(
            base_url=f"{settings.base_url}/api/",
            headers={"Authorization": f"Token {settings.api_key}"},
            timeout=30.0,
            transport=transport,
        )

    async def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        await self._http.aclose()

    async def request(self, method: str, endpoint: str, **kwargs: Any) -> Any:
        """Make an API request and return its decoded JSON response."""
        try:
            response = await self._http.request(method, endpoint, **kwargs)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code
            log_method = logger.warning if status_code < 500 else logger.error
            log_method(
                "Paperless API request failed: %s %s returned HTTP %s",
                method,
                endpoint,
                status_code,
            )
            message = exc.response.text[:500]
            raise PaperlessAPIError(
                f"Paperless API request failed with status {status_code}: {message}"
            ) from exc
        except httpx.RequestError as exc:
            logger.error(
                "Paperless API request failed: %s %s could not reach the server",
                method,
                endpoint,
            )
            raise PaperlessAPIError(f"Paperless API request failed: {exc}") from exc

        logger.info(
            "Paperless API request completed: %s %s returned HTTP %s",
            method,
            endpoint,
            response.status_code,
        )
        if response.status_code == httpx.codes.NO_CONTENT:
            return None
        return response.json()

    async def request_bytes(self, method: str, endpoint: str) -> bytes:
        """Make an API request and return its raw response body."""
        try:
            response = await self._http.request(method, endpoint)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code
            log_method = logger.warning if status_code < 500 else logger.error
            log_method(
                "Paperless API request failed: %s %s returned HTTP %s",
                method,
                endpoint,
                status_code,
            )
            raise PaperlessAPIError(
                f"Paperless API request failed with status {status_code}"
            ) from exc
        except httpx.RequestError as exc:
            logger.error(
                "Paperless API request failed: %s %s could not reach the server",
                method,
                endpoint,
            )
            raise PaperlessAPIError(f"Paperless API request failed: {exc}") from exc

        logger.info(
            "Paperless API request completed: %s %s returned HTTP %s",
            method,
            endpoint,
            response.status_code,
        )
        return response.content
