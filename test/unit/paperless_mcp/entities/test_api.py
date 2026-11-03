"""Paperless service tests using an in-memory HTTP transport."""

import asyncio
import json

import httpx
import pytest
from fastmcp import FastMCP
from mcp.types import EmbeddedResource

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


class TestEntityAPI:
    def test_list_defaults_to_maximum_page_size(self) -> None:
        """Use page size 100 when a caller does not specify it."""

        def handler(request: httpx.Request) -> httpx.Response:
            """Verify the default pagination values sent to Paperless."""
            assert request.url.params["page"] == "1"
            assert request.url.params["page_size"] == "100"
            return httpx.Response(200, json={"results": []})

        service, client, _ = make_service(handler)
        try:
            run(service.list())
        finally:
            run(client.close())

    def test_download_returns_pdf_as_embedded_mcp_resource(self) -> None:
        """Expose downloaded PDF bytes as a typed MCP binary resource."""
        pdf_bytes = b"%PDF-1.7\nexample"

        def handler(request: httpx.Request) -> httpx.Response:
            """Verify authenticated document-download request details."""
            assert request.method == "GET"
            assert request.url.path == "/api/documents/7/download/"
            assert request.url.params["original"] == "true"
            assert request.headers["Authorization"] == "Token test-token"
            return httpx.Response(200, content=pdf_bytes)

        service, client, _ = make_service(handler)
        server = FastMCP("test")
        service.register_tools(server)
        try:
            result = run(server.call_tool("download_document", {"item_id": 7}))
        finally:
            run(client.close())

        assert len(result.content) == 1
        resource = result.content[0]
        assert isinstance(resource, EmbeddedResource)
        assert resource.resource.uri == "paperless://documents/7/download"
        assert resource.resource.mime_type == "application/pdf"
        assert resource.resource.blob == "JVBERi0xLjcKZXhhbXBsZQ=="

    def test_download_rejects_non_pdf_response(self) -> None:
        """Reject a successful HTTP response that does not contain a PDF."""
        service, client, requests = make_service(lambda request: httpx.Response(200, content=b"not a PDF"))
        try:
            with pytest.raises(PaperlessAPIError, match="is not a PDF"):
                run(service.download(7))
        finally:
            run(client.close())

        assert len(requests) == 1

    def test_download_rejects_invalid_id_without_request(self) -> None:
        """Reject non-positive document IDs before attempting a download."""
        service, client, requests = make_service(lambda request: httpx.Response(200, content=b"%PDF-1.7"))
        try:
            with pytest.raises(ValueError, match="positive"):
                run(service.download(0))
        finally:
            run(client.close())

        assert requests == []

    def test_search_sends_auth_query_and_pagination(self) -> None:
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

    @pytest.mark.parametrize("page_size", [1, 1000])
    def test_list_accepts_page_size_boundaries(self, page_size: int) -> None:
        """Allow the configured minimum and maximum page sizes."""

        def handler(request: httpx.Request) -> httpx.Response:
            """Confirm boundary values are sent to Paperless unchanged."""
            assert request.url.params["page_size"] == str(page_size)
            return httpx.Response(200, json={"results": []})

        service, client, _ = make_service(handler)
        try:
            run(service.list(page_size=page_size))
        finally:
            run(client.close())

    def test_custom_field_definitions_use_the_custom_fields_endpoint(self) -> None:
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

    def test_update_uses_patch_and_provided_fields(self) -> None:
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

    def test_create_uses_post_and_provided_fields(self) -> None:
        """Create an entity using the JSON fields supplied by the caller."""

        def handler(request: httpx.Request) -> httpx.Response:
            """Validate the create request and return the new entity."""
            assert request.method == "POST"
            assert request.url.path == "/api/documents/"
            assert json.loads(request.content) == {"title": "New document"}
            return httpx.Response(201, json={"id": 12, "title": "New document"})

        service, client, _ = make_service(handler)
        try:
            result = run(service.create({"title": "New document"}))
        finally:
            run(client.close())

        assert result == {"id": 12, "title": "New document"}

    def test_create_rejects_empty_data_without_request(self) -> None:
        """Require at least one field before sending a create request."""
        service, client, requests = make_service(lambda request: httpx.Response(201, json={}))
        try:
            with pytest.raises(ValueError, match="at least one field"):
                run(service.create({}))
        finally:
            run(client.close())

    def test_delete_requires_confirmation_without_request(self) -> None:
        """Refuse an unconfirmed delete before making an HTTP request."""
        service, client, requests = make_service(lambda request: httpx.Response(204))
        try:
            with pytest.raises(ValueError, match="confirm=true"):
                run(service.delete(3, confirm=False))
        finally:
            run(client.close())

        assert requests == []

    def test_bulk_update_reports_partial_completion(self) -> None:
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

    def test_bulk_delete_requires_confirmation_and_targets_selected_ids(self) -> None:
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

    @pytest.mark.parametrize("page_size", [0, 1001])
    def test_list_rejects_out_of_range_page_size(self, page_size: int) -> None:
        """Reject invalid page sizes before attempting a Paperless request."""
        service, client, requests = make_service(lambda request: httpx.Response(200, json={}))
        try:
            with pytest.raises(ValueError, match="page_size"):
                run(service.list(page_size=page_size))
        finally:
            run(client.close())

        assert requests == []

    @pytest.mark.parametrize("page", [0, -1])
    def test_list_rejects_invalid_page(self, page: int) -> None:
        """Reject invalid page numbers before making a request."""
        service, client, requests = make_service(lambda request: httpx.Response(200, json={}))
        try:
            with pytest.raises(ValueError, match="page"):
                run(service.list(page=page))
        finally:
            run(client.close())

        assert requests == []

    @pytest.mark.parametrize("item_id", [0, -1])
    def test_read_rejects_invalid_id(self, item_id: int) -> None:
        """Reject non-positive IDs before making a request."""
        service, client, requests = make_service(lambda request: httpx.Response(200, json={}))
        try:
            with pytest.raises(ValueError, match="positive"):
                run(service.read(item_id))
        finally:
            run(client.close())

        assert requests == []

    def test_update_rejects_empty_updates_without_request(self) -> None:
        """Require update payloads to contain at least one field."""
        service, client, requests = make_service(lambda request: httpx.Response(200, json={}))
        try:
            with pytest.raises(ValueError, match="at least one field"):
                run(service.update(1, {}))
        finally:
            run(client.close())

        assert requests == []

    def test_confirmed_delete_targets_the_selected_entity(self) -> None:
        """Send a confirmed delete to the selected entity endpoint."""
        service, client, requests = make_service(lambda request: httpx.Response(204))
        try:
            result = run(service.delete(3, confirm=True))
        finally:
            run(client.close())

        assert result is None
        assert [(request.method, request.url.path) for request in requests] == [("DELETE", "/api/documents/3/")]

    @pytest.mark.parametrize("document_ids", [[], [1, 1], [0]])
    def test_bulk_delete_rejects_invalid_ids_without_requests(self, document_ids: list[int]) -> None:
        """Reject empty, duplicate, and non-positive bulk-delete IDs."""
        service, client, requests = make_service(lambda request: httpx.Response(204))
        try:
            with pytest.raises(ValueError):
                run(service.bulk_delete(document_ids, confirm=True))
        finally:
            run(client.close())

        assert requests == []

    @pytest.mark.parametrize(
        ("document_ids", "updates", "message"),
        [
            ([], {"title": "Updated"}, "At least one ID"),
            ([1, 1], {"title": "Updated"}, "duplicates"),
            ([0], {"title": "Updated"}, "positive"),
            ([1], {}, "at least one field"),
        ],
    )
    def test_bulk_update_rejects_invalid_input_without_requests(
        self,
        document_ids: list[int],
        updates: dict[str, str],
        message: str,
    ) -> None:
        """Validate bulk update inputs before making any partial changes."""
        service, client, requests = make_service(lambda request: httpx.Response(200, json={}))
        try:
            with pytest.raises(ValueError, match=message):
                run(service.bulk_update(document_ids, updates))
        finally:
            run(client.close())

        assert requests == []

    def test_bulk_delete_reports_partial_completion(self) -> None:
        """Report IDs deleted before an API error stops a bulk delete."""

        def handler(request: httpx.Request) -> httpx.Response:
            """Fail the second delete after allowing the first to succeed."""
            if request.url.path == "/api/documents/2/":
                return httpx.Response(500, text="server error")
            return httpx.Response(204)

        service, client, requests = make_service(handler)
        try:
            with pytest.raises(BulkOperationError, match="completed IDs: \\[1\\]"):
                run(service.bulk_delete([1, 2, 3], confirm=True))
        finally:
            run(client.close())

        assert [request.url.path for request in requests] == [
            "/api/documents/1/",
            "/api/documents/2/",
        ]
