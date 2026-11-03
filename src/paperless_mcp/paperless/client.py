"""HTTP client for the Paperless-ngx REST API."""

import logging
from typing import Any

import httpx

from paperless_mcp.config import Settings

logger = logging.getLogger(__name__)


class PaperlessAPIError(RuntimeError):
    """Raised when the Paperless API returns an error or cannot be reached."""


class PaperlessClient:
    """Async HTTP client that centralizes Paperless authentication and errors."""

    def __init__(
        self,
        settings: Settings,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        """Create an authenticated async client for the Paperless API.

        Args:
            settings: Server configuration including the base URL and API token.
            transport: Optional custom HTTP transport for testing or mocking.
        """
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
        """Make an API request and return a decoded JSON response.

        Args:
            method: HTTP method to use, such as GET or PATCH.
            endpoint: Relative API endpoint path, such as documents/.
            **kwargs: Additional keyword arguments forwarded to httpx.

        Returns:
            Any: Parsed JSON response body or None when the server responds with 204.

        Raises:
            PaperlessAPIError: If the request receives a non-success status or a
                transport-level failure.
        """
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
            raise PaperlessAPIError(f"Paperless API request failed with status {status_code}: {message}") from exc
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

    async def request_bytes(
        self,
        method: str,
        endpoint: str,
        params: dict[str, str] | None = None,
    ) -> bytes:
        """Make an API request and return its raw response body.

        Args:
            method: HTTP method to use, typically GET for file downloads.
            endpoint: Relative API endpoint path to fetch.
            params: Optional query parameters to include in the request.

        Returns:
            bytes: Response payload as raw binary data.

        Raises:
            PaperlessAPIError: If the request receives a non-success status or a
                transport-level failure.
        """
        try:
            response = await self._http.request(method, endpoint, params=params)
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
            raise PaperlessAPIError(f"Paperless API request failed with status {status_code}") from exc
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
