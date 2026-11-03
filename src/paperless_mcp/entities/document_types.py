"""Document-type-specific Paperless API operations."""

from typing import Any

from fastmcp import FastMCP

from paperless_mcp.entities.base import EntityAPI
from paperless_mcp.icons import load_entity_icons


class DocumentTypesAPI(EntityAPI):
    """Document type API operations for Paperless metadata categories."""

    endpoint = "document_types/"
    plural_name = "document_types"
    singular_name = "document_type"

    def register_tools(self, server: FastMCP) -> None:
        """Register document-type tools with descriptions, tags, and icons.

        Args:
            server: FastMCP server instance to register with.
        """
        entity = self
        icons = load_entity_icons("document_types")

        @server.tool(
            description=(
                "List Paperless document types, with page and page_size controls."
            ),
            tags={"paperless", "document_types", "list"},
            icons=icons,
        )
        async def list_document_types(
            page: int = 1, page_size: int = 100
        ) -> dict[str, Any]:
            """List Paperless document types with pagination.

            Args:
                page: 1-based page number to retrieve.
                page_size: Number of items to include per page.

            Returns:
                dict[str, Any]: Paginated document-type list from the API.
            """
            return await entity.list(page=page, page_size=page_size)

        @server.tool(
            description="Search Paperless document types by text with pagination.",
            tags={"paperless", "document_types", "search"},
            icons=icons,
        )
        async def search_document_types(
            query: str, page: int = 1, page_size: int = 100
        ) -> dict[str, Any]:
            """Search Paperless document types by query.

            Args:
                query: Search string used to filter document types.
                page: 1-based page number to retrieve.
                page_size: Number of items to include per page.

            Returns:
                dict[str, Any]: Matching document types returned by the API.
            """
            return await entity.list(search=query, page=page, page_size=page_size)

        @server.tool(
            description="Fetch a Paperless document type by its numeric ID.",
            tags={"paperless", "document_types", "read"},
            icons=icons,
        )
        async def read_document_type(item_id: int) -> dict[str, Any]:
            """Read a Paperless document type by ID.

            Args:
                item_id: Numeric identifier of the document type to fetch.

            Returns:
                dict[str, Any]: Document type payload returned by the API.
            """
            return await entity.read(item_id)

        @server.tool(
            description="Create a Paperless document type from the supplied fields.",
            tags={"paperless", "document_types", "create"},
            icons=icons,
        )
        async def create_document_type(data: dict[str, Any]) -> dict[str, Any]:
            """Create a Paperless document type.

            Args:
                data: Field values to use when creating the document type.

            Returns:
                dict[str, Any]: Newly created document type returned by the API.
            """
            return await entity.create(data)

        @server.tool(
            description="Patch fields on a Paperless document type by ID.",
            tags={"paperless", "document_types", "update"},
            icons=icons,
        )
        async def update_document_type(
            item_id: int, updates: dict[str, Any]
        ) -> dict[str, Any]:
            """Update Paperless document-type fields by ID.

            Args:
                item_id: Numeric identifier of the document type to update.
                updates: Field names and values to patch.

            Returns:
                dict[str, Any]: Updated document type payload returned by the API.
            """
            return await entity.update(item_id, updates)

        @server.tool(
            description="Delete a document type by ID; requires confirm=true.",
            tags={"paperless", "document_types", "delete"},
            icons=icons,
        )
        async def delete_document_type(item_id: int, confirm: bool = False) -> Any:
            """Delete a document type only when confirm is true.

            Args:
                item_id: Numeric identifier of the document type to delete.
                confirm: Whether deletion is explicitly confirmed.

            Returns:
                Any: API response or None for an empty response.
            """
            return await entity.delete(item_id, confirm)
