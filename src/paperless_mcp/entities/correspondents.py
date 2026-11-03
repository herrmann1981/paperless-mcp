"""Correspondent-specific Paperless API operations."""

from typing import Any

from fastmcp import FastMCP

from paperless_mcp.entities.base import EntityAPI
from paperless_mcp.icons import load_entity_icons


class CorrespondentsAPI(EntityAPI):
    """Correspondent API operations for document sender and recipient records."""

    endpoint = "correspondents/"
    plural_name = "correspondents"
    singular_name = "correspondent"

    def register_tools(self, server: FastMCP) -> None:
        """Register correspondent tools with descriptions, tags, and icons.

        Args:
            server: FastMCP server instance to register with.
        """
        entity = self
        icons = load_entity_icons("correspondents")

        @server.tool(
            description="List Paperless correspondents, with page and page_size controls.",
            tags={"paperless", "correspondents", "list"},
            icons=icons,
        )
        async def list_correspondents(page: int = 1, page_size: int = 100) -> dict[str, Any]:
            """List Paperless correspondents with pagination.

            Args:
                page: 1-based page number to retrieve.
                page_size: Number of items to include per page.

            Returns:
                dict[str, Any]: Paginated correspondent list from the API.
            """
            return await entity.list(page=page, page_size=page_size)

        @server.tool(
            description="Search Paperless correspondents by text with pagination.",
            tags={"paperless", "correspondents", "search"},
            icons=icons,
        )
        async def search_correspondents(query: str, page: int = 1, page_size: int = 100) -> dict[str, Any]:
            """Search Paperless correspondents by query.

            Args:
                query: Search string used to filter correspondents.
                page: 1-based page number to retrieve.
                page_size: Number of items to include per page.

            Returns:
                dict[str, Any]: Matching correspondents returned by the API.
            """
            return await entity.list(search=query, page=page, page_size=page_size)

        @server.tool(
            description="Fetch a Paperless correspondent by its numeric ID.",
            tags={"paperless", "correspondents", "read"},
            icons=icons,
        )
        async def read_correspondent(item_id: int) -> dict[str, Any]:
            """Read a Paperless correspondent by ID.

            Args:
                item_id: Numeric identifier of the correspondent to fetch.

            Returns:
                dict[str, Any]: Correspondent payload returned by the API.
            """
            return await entity.read(item_id)

        @server.tool(
            description="Create a Paperless correspondent from the supplied fields.",
            tags={"paperless", "correspondents", "create"},
            icons=icons,
        )
        async def create_correspondent(data: dict[str, Any]) -> dict[str, Any]:
            """Create a Paperless correspondent.

            Args:
                data: Field values to use when creating the correspondent.

            Returns:
                dict[str, Any]: Newly created correspondent returned by the API.
            """
            return await entity.create(data)

        @server.tool(
            description="Patch fields on a Paperless correspondent by ID.",
            tags={"paperless", "correspondents", "update"},
            icons=icons,
        )
        async def update_correspondent(item_id: int, updates: dict[str, Any]) -> dict[str, Any]:
            """Update Paperless correspondent fields by ID.

            Args:
                item_id: Numeric identifier of the correspondent to update.
                updates: Field names and values to patch.

            Returns:
                dict[str, Any]: Updated correspondent payload returned by the API.
            """
            return await entity.update(item_id, updates)

        @server.tool(
            description="Delete a correspondent by ID; requires confirm=true.",
            tags={"paperless", "correspondents", "delete"},
            icons=icons,
        )
        async def delete_correspondent(item_id: int, confirm: bool = False) -> Any:
            """Delete a correspondent only when confirm is true.

            Args:
                item_id: Numeric identifier of the correspondent to delete.
                confirm: Whether deletion is explicitly confirmed.

            Returns:
                Any: API response or None for an empty response.
            """
            return await entity.delete(item_id, confirm)
