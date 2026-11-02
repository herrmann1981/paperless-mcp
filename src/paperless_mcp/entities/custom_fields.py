"""Custom-field-specific Paperless API operations."""

from typing import Any

from fastmcp import FastMCP

from paperless_mcp.entities.base import EntityAPI
from paperless_mcp.icons import load_entity_icons


class CustomFieldsAPI(EntityAPI):
    """Custom-field definition API operations."""

    endpoint = "custom_fields/"
    plural_name = "custom_fields"
    singular_name = "custom_field"

    def register_tools(self, server: FastMCP) -> None:
        """Register custom-field tools with descriptions, tags, and icons."""
        entity = self
        icons = load_entity_icons("custom_fields")

        @server.tool(
            description=(
                "List Paperless custom-field definitions, with page and "
                "page_size controls."
            ),
            tags={"paperless", "custom_fields", "list"},
            icons=icons,
        )
        async def list_custom_fields(
            page: int = 1, page_size: int = 25
        ) -> dict[str, Any]:
            """List Paperless custom-field definitions with pagination."""
            return await entity.list(page=page, page_size=page_size)

        @server.tool(
            description=(
                "Search Paperless custom-field definitions by text with pagination."
            ),
            tags={"paperless", "custom_fields", "search"},
            icons=icons,
        )
        async def search_custom_fields(
            query: str, page: int = 1, page_size: int = 25
        ) -> dict[str, Any]:
            """Search Paperless custom-field definitions by query."""
            return await entity.list(search=query, page=page, page_size=page_size)

        @server.tool(
            description="Fetch a Paperless custom-field definition by its numeric ID.",
            tags={"paperless", "custom_fields", "read"},
            icons=icons,
        )
        async def read_custom_field(item_id: int) -> dict[str, Any]:
            """Read a Paperless custom-field definition by ID."""
            return await entity.read(item_id)

        @server.tool(
            description=(
                "Create a Paperless custom-field definition from the supplied fields."
            ),
            tags={"paperless", "custom_fields", "create"},
            icons=icons,
        )
        async def create_custom_field(data: dict[str, Any]) -> dict[str, Any]:
            """Create a Paperless custom-field definition."""
            return await entity.create(data)

        @server.tool(
            description="Patch fields on a Paperless custom-field definition by ID.",
            tags={"paperless", "custom_fields", "update"},
            icons=icons,
        )
        async def update_custom_field(
            item_id: int, updates: dict[str, Any]
        ) -> dict[str, Any]:
            """Update Paperless custom-field definition fields by ID."""
            return await entity.update(item_id, updates)

        @server.tool(
            description=(
                "Delete a custom-field definition by ID; requires confirm=true."
            ),
            tags={"paperless", "custom_fields", "delete"},
            icons=icons,
        )
        async def delete_custom_field(item_id: int, confirm: bool = False) -> Any:
            """Delete a custom-field definition only when confirm is true."""
            return await entity.delete(item_id, confirm)
