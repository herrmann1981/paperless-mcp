"""Document-specific Paperless API operations."""

from base64 import b64encode
from collections.abc import Sequence
from typing import Any

from fastmcp import FastMCP
from mcp.types import BlobResourceContents, EmbeddedResource

from paperless_mcp.entities.base import EntityAPI
from paperless_mcp.icons import load_entity_icons
from paperless_mcp.paperless import PaperlessAPIError, PaperlessClient


class BulkOperationError(RuntimeError):
    """Raised when a bulk operation stops after one or more successful requests."""

    def __init__(
        self,
        operation: str,
        completed_ids: list[int],
        failed_id: int,
        cause: PaperlessAPIError,
    ) -> None:
        """Initialize the error with the partial progress and root cause.

        Args:
            operation: Name of the bulk operation that was interrupted.
            completed_ids: IDs that completed successfully before the failure.
            failed_id: The ID that caused the operation to stop.
            cause: Underlying API error that triggered the bulk rollback.
        """
        self.completed_ids = completed_ids
        self.failed_id = failed_id
        super().__init__(
            f"Bulk {operation} stopped at ID {failed_id}; "
            f"completed IDs: {completed_ids}; error: {cause}"
        )


class DocumentsAPI(EntityAPI):
    """Document CRUD and bulk-action helpers for the Paperless API."""

    endpoint = "documents/"
    plural_name = "documents"
    singular_name = "document"

    def __init__(self, client: PaperlessClient) -> None:
        """Initialize document operations with the shared API client.

        Args:
            client: Shared Paperless HTTP client for all document requests.
        """
        super().__init__(client)

    async def bulk_update(
        self, document_ids: Sequence[int], updates: dict[str, Any]
    ) -> dict[str, list[int]]:
        """Update selected documents sequentially and report completed IDs.

        Args:
            document_ids: Sequence of document IDs to update.
            updates: Field values to patch for each document.

        Returns:
            dict[str, list[int]]: Mapping containing the IDs updated before failure.

        Raises:
            ValueError: If updates is empty or document_ids contains invalid values.
            BulkOperationError: If any patch request fails after earlier updates.
        """
        ids = self._validate_ids(document_ids)
        if not updates:
            raise ValueError("updates must contain at least one field")
        completed: list[int] = []
        for document_id in ids:
            try:
                await self.update(document_id, updates)
            except PaperlessAPIError as exc:
                raise BulkOperationError("update", completed, document_id, exc) from exc
            completed.append(document_id)
        return {"updated_ids": completed}

    async def download(self, document_id: int) -> EmbeddedResource:
        """Download a document PDF as MCP binary resource content.

        Args:
            document_id: Numeric identifier of the document to download.

        Returns:
            EmbeddedResource: MCP resource payload containing the PDF bytes.

        Raises:
            ValueError: If document_id is invalid.
            PaperlessAPIError: If the API response is not a PDF or the request fails.
        """
        self._validate_id(document_id)
        endpoint = f"{self.endpoint}{document_id}/download/"
        content = await self.client.request_bytes(
            "GET", endpoint, params={"original": "true"}
        )
        if not content.startswith(b"%PDF-"):
            raise PaperlessAPIError(
                f"Paperless document {document_id} download is not a PDF"
            )
        return EmbeddedResource(
            resource=BlobResourceContents(
                uri=f"paperless://documents/{document_id}/download",
                mimeType="application/pdf",
                blob=b64encode(content).decode("ascii"),
            )
        )

    async def bulk_delete(
        self, document_ids: Sequence[int], confirm: bool
    ) -> dict[str, list[int]]:
        """Delete selected documents sequentially after explicit confirmation.

        Args:
            document_ids: Sequence of document IDs to delete.
            confirm: Whether the destructive action is explicitly confirmed.

        Returns:
            dict[str, list[int]]: Mapping containing the IDs deleted before failure.

        Raises:
            ValueError: If confirm is false or document_ids contains invalid values.
            BulkOperationError: If any delete request fails after earlier deletions.
        """
        ids = self._validate_ids(document_ids)
        if not confirm:
            raise ValueError("Set confirm=true to delete these documents")
        completed: list[int] = []
        for document_id in ids:
            try:
                await self.delete(document_id, confirm=True)
            except PaperlessAPIError as exc:
                raise BulkOperationError("delete", completed, document_id, exc) from exc
            completed.append(document_id)
        return {"deleted_ids": completed}

    def register_tools(self, server: FastMCP) -> None:
        """Register document tools with descriptions, tags, and Paperless icons.

        Args:
            server: FastMCP server instance to register with.
        """
        entity = self
        icons = load_entity_icons("documents")

        @server.tool(
            description="List Paperless documents, with page and page_size controls.",
            tags={"paperless", "documents", "list"},
            icons=icons,
        )
        async def list_documents(page: int = 1, page_size: int = 100) -> dict[str, Any]:
            """List Paperless documents with pagination.

            Args:
                page: 1-based page number to retrieve.
                page_size: Number of items to include per page.

            Returns:
                dict[str, Any]: Paginated document list from the API.
            """
            return await entity.list(page=page, page_size=page_size)

        @server.tool(
            description="Search Paperless documents by text with pagination.",
            tags={"paperless", "documents", "search"},
            icons=icons,
        )
        async def search_documents(
            query: str, page: int = 1, page_size: int = 100
        ) -> dict[str, Any]:
            """Search Paperless documents by query.

            Args:
                query: Search string used to filter documents.
                page: 1-based page number to retrieve.
                page_size: Number of items to include per page.

            Returns:
                dict[str, Any]: Matching documents returned by the API.
            """
            return await entity.list(search=query, page=page, page_size=page_size)

        @server.tool(
            description="Fetch a Paperless document by its numeric ID.",
            tags={"paperless", "documents", "read"},
            icons=icons,
        )
        async def read_document(item_id: int) -> dict[str, Any]:
            """Read a Paperless document by ID.

            Args:
                item_id: Numeric identifier of the document to fetch.

            Returns:
                dict[str, Any]: Document payload returned by the API.
            """
            return await entity.read(item_id)

        @server.tool(
            description="Download the original Paperless document as a PDF file.",
            tags={"paperless", "documents", "download"},
            icons=icons,
        )
        async def download_document(item_id: int) -> EmbeddedResource:
            """Download a document PDF as an MCP binary resource.

            Args:
                item_id: Numeric identifier of the document to download.

            Returns:
                EmbeddedResource: PDF resource payload for the document.
            """
            return await entity.download(item_id)

        @server.tool(
            description="Patch fields on a Paperless document by ID.",
            tags={"paperless", "documents", "update"},
            icons=icons,
        )
        async def update_document(
            item_id: int, updates: dict[str, Any]
        ) -> dict[str, Any]:
            """Update Paperless document fields by ID.

            Args:
                item_id: Numeric identifier of the document to update.
                updates: Field names and values to patch.

            Returns:
                dict[str, Any]: Updated document payload returned by the API.
            """
            return await entity.update(item_id, updates)

        @server.tool(
            description="Delete a document by ID; requires confirm=true.",
            tags={"paperless", "documents", "delete"},
            icons=icons,
        )
        async def delete_document(item_id: int, confirm: bool = False) -> Any:
            """Delete a document only when confirm is true.

            Args:
                item_id: Numeric identifier of the document to delete.
                confirm: Whether deletion is explicitly confirmed.

            Returns:
                Any: API response or None for an empty response.
            """
            return await entity.delete(item_id, confirm)

        @server.tool(
            description=(
                "Patch selected document IDs sequentially. If an API request fails, "
                "the result reports IDs already updated."
            ),
            tags={"paperless", "documents", "bulk", "update"},
            icons=icons,
        )
        async def bulk_update_documents(
            document_ids: list[int], updates: dict[str, Any]
        ) -> dict[str, list[int]]:
            """Update selected documents, reporting partial success.

            Args:
                document_ids: Document IDs to patch in order.
                updates: Field names and values to apply to each document.

            Returns:
                dict[str, list[int]]: IDs updated before a failure stopped the bulk action.
            """
            return await entity.bulk_update(document_ids, updates)

        @server.tool(
            description=(
                "Delete selected document IDs sequentially; requires confirm=true. "
                "If a request fails, the result reports IDs already deleted."
            ),
            tags={"paperless", "documents", "bulk", "delete"},
            icons=icons,
        )
        async def bulk_delete_documents(
            document_ids: list[int], confirm: bool = False
        ) -> dict[str, list[int]]:
            """Delete selected documents, reporting partial success.

            Args:
                document_ids: Document IDs to delete in order.
                confirm: Whether the destructive bulk action is explicitly confirmed.

            Returns:
                dict[str, list[int]]: IDs deleted before a failure stopped the bulk action.
            """
            return await entity.bulk_delete(document_ids, confirm)

    @classmethod
    def _validate_ids(cls, item_ids: Sequence[int]) -> list[int]:
        """Validate a non-empty sequence of unique positive document IDs.

        Args:
            item_ids: Sequence of IDs to validate.

        Returns:
            list[int]: A list of validated document IDs.

        Raises:
            ValueError: If the sequence is empty, contains duplicates, or includes
                invalid IDs.
        """
        ids = list(item_ids)
        if not ids:
            raise ValueError("At least one ID must be provided")
        for item_id in ids:
            cls._validate_id(item_id)
        if len(set(ids)) != len(ids):
            raise ValueError("IDs must not contain duplicates")
        return ids
