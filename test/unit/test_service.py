"""Paperless service tests using an in-memory HTTP transport."""

import asyncio
import json
import logging

import httpx
import pytest

from paperless_mcp.config import Settings
from paperless_mcp.entities.custom_fields import CustomFieldsAPI
from paperless_mcp.entities.documents import BulkOperationError, DocumentsAPI
from paperless_mcp.entities.tags import TagsAPI
from paperless_mcp.paperless import PaperlessAPIError, PaperlessClient


def run(coro):
    """Run a coroutine for synchronous unit-test assertions."""
    return asyncio.run(coro)


def make_service(handler, api_type=DocumentsAPI):
    """Build an entity API with a mock HTTP handler and request recorder."""
    requests: list[httpx.Request] = []

    def record(request: httpx.Request) -> httpx.Response:
        """Record a request before passing it to the supplied handler."""
        requests.append(request)
        return handler(request)

    client = PaperlessClient(
        Settings("http://paperless.test", "test-token"),
        transport=httpx.MockTransport(record),
    )
    return api_type(client), client, requests


def test_search_sends_auth_query_and_pagination() -> None:
    """Send search and pagination parameters with the API token."""

    def handler(request: httpx.Request) -> httpx.Response:
        """Validate the request and return a representative result."""
        assert request.url.path == "/api/documents/"
        assert request.headers["Authorization"] == "Token test-token"
        assert request.url.params["search"] == "invoice"
        assert request.url.params["page"] == "2"
        assert request.url.params["page_size"] == "10"
        return httpx.Response(200, json={"results": [{"id": 8}]})

    service, client, _ = make_service(handler)
    try:
        result = run(service.list(search="invoice", page=2, page_size=10))
    finally:
        run(client.close())

    assert result == {"results": [{"id": 8}]}


def test_custom_field_definitions_use_the_custom_fields_endpoint() -> None:
    """Use Paperless's custom-fields endpoint with shared pagination behavior."""

    def handler(request: httpx.Request) -> httpx.Response:
        """Validate the custom-field request and return a representative result."""
        assert request.method == "GET"
        assert request.url.path == "/api/custom_fields/"
        assert request.url.params["page"] == "2"
        assert request.url.params["page_size"] == "10"
        return httpx.Response(200, json={"results": [{"id": 8}]})

    service, client, _ = make_service(handler, CustomFieldsAPI)
    try:
        result = run(service.list(page=2, page_size=10))
    finally:
        run(client.close())

    assert result == {"results": [{"id": 8}]}


def test_update_uses_patch_and_provided_fields() -> None:
    """Patch the selected entity with only the provided fields."""

    def handler(request: httpx.Request) -> httpx.Response:
        """Validate the PATCH request and return the updated record."""
        assert request.method == "PATCH"
        assert request.url.path == "/api/tags/4/"
        assert json.loads(request.content) == {"name": "Invoices"}
        return httpx.Response(200, json={"id": 4, "name": "Invoices"})

    service, client, _ = make_service(handler, TagsAPI)
    try:
        result = run(service.update(4, {"name": "Invoices"}))
    finally:
        run(client.close())

    assert result["name"] == "Invoices"


def test_delete_requires_confirmation_without_request() -> None:
    """Refuse an unconfirmed delete before making an HTTP request."""
    service, client, requests = make_service(lambda request: httpx.Response(204))
    try:
        with pytest.raises(ValueError, match="confirm=true"):
            run(service.delete(3, confirm=False))
    finally:
        run(client.close())

    assert requests == []


def test_bulk_update_reports_partial_completion() -> None:
    """Stop a bulk update and report completed IDs after an API error."""

    def handler(request: httpx.Request) -> httpx.Response:
        """Fail on the second document to simulate a partial operation."""
        if request.url.path == "/api/documents/2/":
            return httpx.Response(500, text="server error")
        return httpx.Response(200, json={"id": 1})

    service, client, requests = make_service(handler)
    try:
        with pytest.raises(BulkOperationError, match="completed IDs: \\[1\\]"):
            run(service.bulk_update([1, 2, 3], {"title": "Updated"}))
    finally:
        run(client.close())

    assert [request.url.path for request in requests] == [
        "/api/documents/1/",
        "/api/documents/2/",
    ]


def test_bulk_delete_requires_confirmation_and_targets_selected_ids() -> None:
    """Require confirmation and delete only the requested document IDs."""
    service, client, requests = make_service(lambda request: httpx.Response(204))
    try:
        with pytest.raises(ValueError, match="confirm=true"):
            run(service.bulk_delete([5, 6], confirm=False))
        assert requests == []

        result = run(service.bulk_delete([5, 6], confirm=True))
    finally:
        run(client.close())

    assert result == {"deleted_ids": [5, 6]}
    assert [request.url.path for request in requests] == [
        "/api/documents/5/",
        "/api/documents/6/",
    ]


def test_api_errors_are_reported_without_credentials() -> None:
    """Raise an API error when Paperless rejects the authorization."""
    service, client, _ = make_service(
        lambda request: httpx.Response(401, text="Unauthorized")
    )
    try:
        with pytest.raises(PaperlessAPIError, match="status 401"):
            run(service.read(9))
    finally:
        run(client.close())


def test_api_requests_log_info_and_warning_without_secrets(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Log successful and client-error requests without sensitive data."""
    service, client, _ = make_service(
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
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Log server-side API failures at error level without response contents."""
    service, client, _ = make_service(
        lambda request: httpx.Response(503, text="internal details")
    )
    caplog.set_level(logging.INFO, logger="paperless_mcp.paperless.client")
    try:
        with pytest.raises(PaperlessAPIError):
            run(service.read(1))
    finally:
        run(client.close())

    assert "ERROR" in caplog.text
    assert "GET documents/1/ returned HTTP 503" in caplog.text
    assert "internal details" not in caplog.text


@pytest.mark.parametrize("page_size", [0, 101])
def test_list_rejects_out_of_range_page_size(page_size: int) -> None:
    """Reject invalid page sizes before attempting a Paperless request."""
    service, client, requests = make_service(
        lambda request: httpx.Response(200, json={})
    )
    try:
        with pytest.raises(ValueError, match="page_size"):
            run(service.list(page_size=page_size))
    finally:
        run(client.close())

    assert requests == []
