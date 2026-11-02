"""Storage-path-specific Paperless API operations."""

from typing import Any

from fastmcp import FastMCP

from paperless_mcp.entities.base import EntityAPI
from paperless_mcp.icons import load_entity_icons


class StoragePathsAPI(EntityAPI):
    """Storage path API operations."""

    endpoint = "storage_paths/"
    plural_name = "storage_paths"
    singular_name = "storage_path"

    def register_tools(self, server: FastMCP) -> None:
        """Register storage-path tools with descriptions, tags, and icons."""
        entity = self
        icons = load_entity_icons("storage_paths")

        @server.tool(
            description=(
                "List Paperless storage paths, with page and page_size controls."
            ),
            tags={"paperless", "storage_paths", "list"},
            icons=icons,
        )
        async def list_storage_paths(
            page: int = 1, page_size: int = 25
        ) -> dict[str, Any]:
            """List Paperless storage paths with pagination."""
            return await entity.list(page=page, page_size=page_size)

        @server.tool(
            description="Search Paperless storage paths by text with pagination.",
            tags={"paperless", "storage_paths", "search"},
            icons=icons,
        )
        async def search_storage_paths(
            query: str, page: int = 1, page_size: int = 25
        ) -> dict[str, Any]:
            """Search Paperless storage paths by query."""
            return await entity.list(search=query, page=page, page_size=page_size)

        @server.tool(
            description="Fetch a Paperless storage path by its numeric ID.",
            tags={"paperless", "storage_paths", "read"},
            icons=icons,
        )
        async def read_storage_path(item_id: int) -> dict[str, Any]:
            """Read a Paperless storage path by ID."""
            return await entity.read(item_id)

        @server.tool(
            description="Create a Paperless storage path from the supplied fields.",
            tags={"paperless", "storage_paths", "create"},
            icons=icons,
        )
        async def create_storage_path(data: dict[str, Any]) -> dict[str, Any]:
            """Create a Paperless storage path."""
            return await entity.create(data)

        @server.tool(
            description="Patch fields on a Paperless storage path by ID.",
            tags={"paperless", "storage_paths", "update"},
            icons=icons,
        )
        async def update_storage_path(
            item_id: int, updates: dict[str, Any]
        ) -> dict[str, Any]:
            """Update Paperless storage-path fields by ID."""
            return await entity.update(item_id, updates)

        @server.tool(
            description="Delete a storage path by ID; requires confirm=true.",
            tags={"paperless", "storage_paths", "delete"},
            icons=icons,
        )
        async def delete_storage_path(item_id: int, confirm: bool = False) -> Any:
            """Delete a storage path only when confirm is true."""
            return await entity.delete(item_id, confirm)
