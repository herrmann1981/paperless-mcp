"""Document-type-specific Paperless API operations."""

from typing import Any

from fastmcp import FastMCP

from paperless_mcp.entities.base import EntityAPI
from paperless_mcp.icons import load_entity_icons


class DocumentTypesAPI(EntityAPI):
    """Document type API operations."""

    endpoint = "document_types/"
    plural_name = "document_types"
    singular_name = "document_type"

    def register_tools(self, server: FastMCP) -> None:
        """Register document-type tools with descriptions, tags, and icons."""
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
            page: int = 1, page_size: int = 25
        ) -> dict[str, Any]:
            """List Paperless document types with pagination."""
            return await entity.list(page=page, page_size=page_size)

        @server.tool(
            description="Search Paperless document types by text with pagination.",
            tags={"paperless", "document_types", "search"},
            icons=icons,
        )
        async def search_document_types(
            query: str, page: int = 1, page_size: int = 25
        ) -> dict[str, Any]:
            """Search Paperless document types by query."""
            return await entity.list(search=query, page=page, page_size=page_size)

        @server.tool(
            description="Fetch a Paperless document type by its numeric ID.",
            tags={"paperless", "document_types", "read"},
            icons=icons,
        )
        async def read_document_type(item_id: int) -> dict[str, Any]:
            """Read a Paperless document type by ID."""
            return await entity.read(item_id)

        @server.tool(
            description="Patch fields on a Paperless document type by ID.",
            tags={"paperless", "document_types", "update"},
            icons=icons,
        )
        async def update_document_type(
            item_id: int, updates: dict[str, Any]
        ) -> dict[str, Any]:
            """Update Paperless document-type fields by ID."""
            return await entity.update(item_id, updates)

        @server.tool(
            description="Delete a document type by ID; requires confirm=true.",
            tags={"paperless", "document_types", "delete"},
            icons=icons,
        )
        async def delete_document_type(item_id: int, confirm: bool = False) -> Any:
            """Delete a document type only when confirm is true."""
            return await entity.delete(item_id, confirm)
