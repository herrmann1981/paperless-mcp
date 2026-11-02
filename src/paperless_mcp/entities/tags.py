"""Tag-specific Paperless API operations."""

from typing import Any

from fastmcp import FastMCP

from paperless_mcp.entities.base import EntityAPI
from paperless_mcp.icons import load_entity_icons


class TagsAPI(EntityAPI):
    """Tag API operations."""

    endpoint = "tags/"
    plural_name = "tags"
    singular_name = "tag"

    def register_tools(self, server: FastMCP) -> None:
        """Register tag tools with descriptions, tags, and Paperless icons."""
        entity = self
        icons = load_entity_icons("tags")

        @server.tool(
            description="List Paperless tags, with page and page_size controls.",
            tags={"paperless", "tags", "list"},
            icons=icons,
        )
        async def list_tags(page: int = 1, page_size: int = 25) -> dict[str, Any]:
            """List Paperless tags with pagination."""
            return await entity.list(page=page, page_size=page_size)

        @server.tool(
            description="Search Paperless tags by text with pagination.",
            tags={"paperless", "tags", "search"},
            icons=icons,
        )
        async def search_tags(
            query: str, page: int = 1, page_size: int = 25
        ) -> dict[str, Any]:
            """Search Paperless tags by query."""
            return await entity.list(search=query, page=page, page_size=page_size)

        @server.tool(
            description="Fetch a Paperless tag by its numeric ID.",
            tags={"paperless", "tags", "read"},
            icons=icons,
        )
        async def read_tag(item_id: int) -> dict[str, Any]:
            """Read a Paperless tag by ID."""
            return await entity.read(item_id)

        @server.tool(
            description="Create a Paperless tag from the supplied fields.",
            tags={"paperless", "tags", "create"},
            icons=icons,
        )
        async def create_tag(data: dict[str, Any]) -> dict[str, Any]:
            """Create a Paperless tag."""
            return await entity.create(data)

        @server.tool(
            description="Patch fields on a Paperless tag by ID.",
            tags={"paperless", "tags", "update"},
            icons=icons,
        )
        async def update_tag(item_id: int, updates: dict[str, Any]) -> dict[str, Any]:
            """Update Paperless tag fields by ID."""
            return await entity.update(item_id, updates)

        @server.tool(
            description="Delete a tag by ID; requires confirm=true.",
            tags={"paperless", "tags", "delete"},
            icons=icons,
        )
        async def delete_tag(item_id: int, confirm: bool = False) -> Any:
            """Delete a tag only when confirm is true."""
            return await entity.delete(item_id, confirm)
