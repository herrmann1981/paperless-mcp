"""HTTP client tests using an in-memory transport."""

import asyncio
import logging

import httpx
import pytest

from paperless_mcp.config import Settings
from paperless_mcp.entities.documents import DocumentsAPI
from paperless_mcp.paperless import PaperlessAPIError, PaperlessClient


def run(coro):
    """Run a coroutine for synchronous test assertions."""
    return asyncio.run(coro)


def make_service(handler):
    """Build a document API client with a mock HTTP transport."""
    client = PaperlessClient(
        Settings("http://paperless.test", "test-token"),
        transport=httpx.MockTransport(handler),
    )
    return DocumentsAPI(client), client


class TestPaperlessClient:
    def test_api_errors_are_reported_without_credentials(self) -> None:
        """Raise an API error when Paperless rejects the authorization."""

        service, client = make_service(lambda request: httpx.Response(401, text="Unauthorized"))

        try:
            with pytest.raises(PaperlessAPIError, match="status 401"):
                run(service.read(9))

        finally:
            run(client.close())

    def test_api_requests_log_info_and_warning_without_secrets(
        self,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Log successful and client-error requests without sensitive data."""

        service, client = make_service(
            lambda request: (
                httpx.Response(200, json={})
                if request.method == "GET"
                else httpx.Response(401, text="sensitive response text")
            )
        )

        caplog.set_level(logging.INFO, logger="paperless_mcp.paperless.client")

        try:
            run(service.read(1))

            with pytest.raises(PaperlessAPIError):
                run(service.update(1, {"title": "secret payload"}))

        finally:
            run(client.close())

        assert "INFO" in caplog.text

        assert "WARNING" in caplog.text

        assert "GET documents/1/ returned HTTP 200" in caplog.text

        assert "PATCH documents/1/ returned HTTP 401" in caplog.text

        assert "test-token" not in caplog.text

        assert "secret payload" not in caplog.text

        assert "sensitive response text" not in caplog.text

    def test_server_errors_are_logged_at_error_level(
        self,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Log server-side API failures at error level without response contents."""

        service, client = make_service(lambda request: httpx.Response(503, text="internal details"))

        caplog.set_level(logging.INFO, logger="paperless_mcp.paperless.client")

        try:
            with pytest.raises(PaperlessAPIError):
                run(service.read(1))

        finally:
            run(client.close())

        assert "ERROR" in caplog.text

        assert "GET documents/1/ returned HTTP 503" in caplog.text

        assert "internal details" not in caplog.text

    def test_no_content_response_returns_none(self) -> None:
        """Treat HTTP 204 as a successful response without a JSON body."""
        service, client = make_service(lambda request: httpx.Response(204))
        try:
            result = run(service.delete(2, confirm=True))
        finally:
            run(client.close())

        assert result is None

    def test_connection_errors_are_reported_and_logged(
        self,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Wrap transport failures as API errors without leaking credentials."""

        def fail_request(request: httpx.Request) -> httpx.Response:
            """Simulate an unreachable Paperless server."""
            raise httpx.ConnectError("connection refused", request=request)

        service, client = make_service(fail_request)
        caplog.set_level(logging.ERROR, logger="paperless_mcp.paperless.client")
        try:
            with pytest.raises(PaperlessAPIError, match="could not reach|failed"):
                run(service.read(1))
        finally:
            run(client.close())

        assert "could not reach the server" in caplog.text
        assert "test-token" not in caplog.text
