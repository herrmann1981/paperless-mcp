"""Storage-path-specific Paperless API operations."""

from typing import Any

from fastmcp import FastMCP

from paperless_mcp.entities.base import EntityAPI
from paperless_mcp.icons import load_entity_icons


class StoragePathsAPI(EntityAPI):
    """Storage path API operations for Paperless document storage directories."""

    endpoint = "storage_paths/"
    plural_name = "storage_paths"
    singular_name = "storage_path"

    def register_tools(self, server: FastMCP) -> None:
        """Register storage-path tools with descriptions, tags, and icons.

        Args:
            server: FastMCP server instance to register with.
        """
        entity = self
        icons = load_entity_icons("storage_paths")

        @server.tool(
            description=("List Paperless storage paths, with page and page_size controls."),
            tags={"paperless", "storage_paths", "list"},
            icons=icons,
        )
        async def list_storage_paths(page: int = 1, page_size: int = 100) -> dict[str, Any]:
            """List Paperless storage paths with pagination.

            Args:
                page: 1-based page number to retrieve.
                page_size: Number of items to include per page.

            Returns:
                dict[str, Any]: Paginated storage path list from the API.
            """
            return await entity.list(page=page, page_size=page_size)

        @server.tool(
            description="Search Paperless storage paths by text with pagination.",
            tags={"paperless", "storage_paths", "search"},
            icons=icons,
        )
        async def search_storage_paths(query: str, page: int = 1, page_size: int = 100) -> dict[str, Any]:
            """Search Paperless storage paths by query.

            Args:
                query: Search string used to filter storage paths.
                page: 1-based page number to retrieve.
                page_size: Number of items to include per page.

            Returns:
                dict[str, Any]: Matching storage paths returned by the API.
            """
            return await entity.list(search=query, page=page, page_size=page_size)

        @server.tool(
            description="Fetch a Paperless storage path by its numeric ID.",
            tags={"paperless", "storage_paths", "read"},
            icons=icons,
        )
        async def read_storage_path(item_id: int) -> dict[str, Any]:
            """Read a Paperless storage path by ID.

            Args:
                item_id: Numeric identifier of the storage path to fetch.

            Returns:
                dict[str, Any]: Storage path payload returned by the API.
            """
            return await entity.read(item_id)

        @server.tool(
            description="Create a Paperless storage path from the supplied fields.",
            tags={"paperless", "storage_paths", "create"},
            icons=icons,
        )
        async def create_storage_path(data: dict[str, Any]) -> dict[str, Any]:
            """Create a Paperless storage path.

            Args:
                data: Field values to use when creating the storage path.

            Returns:
                dict[str, Any]: Newly created storage path returned by the API.
            """
            return await entity.create(data)

        @server.tool(
            description="Patch fields on a Paperless storage path by ID.",
            tags={"paperless", "storage_paths", "update"},
            icons=icons,
        )
        async def update_storage_path(item_id: int, updates: dict[str, Any]) -> dict[str, Any]:
            """Update Paperless storage-path fields by ID.

            Args:
                item_id: Numeric identifier of the storage path to update.
                updates: Field names and values to patch.

            Returns:
                dict[str, Any]: Updated storage path payload returned by the API.
            """
            return await entity.update(item_id, updates)

        @server.tool(
            description="Delete a storage path by ID; requires confirm=true.",
            tags={"paperless", "storage_paths", "delete"},
            icons=icons,
        )
        async def delete_storage_path(item_id: int, confirm: bool = False) -> Any:
            """Delete a storage path only when confirm is true.

            Args:
                item_id: Numeric identifier of the storage path to delete.
                confirm: Whether deletion is explicitly confirmed.

            Returns:
                Any: API response or None for an empty response.
            """
            return await entity.delete(item_id, confirm)
