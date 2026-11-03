"""Shared operations and MCP tool registration for Paperless entities."""

from typing import Any

from paperless_mcp.paperless import PaperlessClient


class EntityAPI:
    """Common CRUD operations for a Paperless entity API."""

    endpoint: str
    plural_name: str
    singular_name: str

    def __init__(self, client: PaperlessClient) -> None:
        """Initialize the entity API with the shared Paperless HTTP client.

        Args:
            client: Shared client used for all requests made by this API adapter.
        """
        self.client = client

    async def list(
        self,
        search: str | None = None,
        page: int = 1,
        page_size: int = 100,
    ) -> dict[str, Any]:
        """List or search entity records with bounded pagination.

        Args:
            search: Optional full-text search term to filter results.
            page: 1-based page number to retrieve.
            page_size: Number of items to return per page, between 1 and 100.

        Returns:
            dict[str, Any]: The decoded API response containing paginated records.

        Raises:
            ValueError: If page or page_size are outside the supported range.
        """
        if page < 1:
            raise ValueError("page must be at least 1")
        if not 1 <= page_size <= 100:
            raise ValueError("page_size must be between 1 and 100")
        params: dict[str, Any] = {"page": page, "page_size": page_size}
        if search:
            params["search"] = search
        return await self.client.request("GET", self.endpoint, params=params)

    async def read(self, item_id: int) -> dict[str, Any]:
        """Fetch one entity record by its positive ID.

        Args:
            item_id: Numeric identifier of the entity to fetch.

        Returns:
            dict[str, Any]: The decoded API response for the requested entity.

        Raises:
            ValueError: If item_id is not a positive integer.
        """
        self._validate_id(item_id)
        return await self.client.request("GET", f"{self.endpoint}{item_id}/")

    async def create(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create an entity record from the supplied Paperless API fields.

        Args:
            data: Fields to send in the create request payload.

        Returns:
            dict[str, Any]: The created entity returned by the API.

        Raises:
            ValueError: If the payload does not contain any fields.
        """
        if not data:
            raise ValueError("data must contain at least one field")
        return await self.client.request("POST", self.endpoint, json=data)

    async def update(self, item_id: int, updates: dict[str, Any]) -> dict[str, Any]:
        """Patch one entity record with the supplied fields.

        Args:
            item_id: Numeric identifier of the entity to update.
            updates: Mapping of field names to new values.

        Returns:
            dict[str, Any]: The updated entity returned by the API.

        Raises:
            ValueError: If item_id is invalid or updates is empty.
        """
        self._validate_id(item_id)
        if not updates:
            raise ValueError("updates must contain at least one field")
        return await self.client.request(
            "PATCH", f"{self.endpoint}{item_id}/", json=updates
        )

    async def delete(self, item_id: int, confirm: bool) -> dict[str, Any] | None:
        """Delete one entity record after explicit confirmation.

        Args:
            item_id: Numeric identifier of the entity to delete.
            confirm: Whether the caller explicitly confirms the destructive action.

        Returns:
            dict[str, Any] | None: The API response body or None for empty responses.

        Raises:
            ValueError: If item_id is invalid or confirm is false.
        """
        self._validate_id(item_id)
        if not confirm:
            raise ValueError("Set confirm=true to delete this resource")
        return await self.client.request("DELETE", f"{self.endpoint}{item_id}/")

    @staticmethod
    def _validate_id(item_id: int) -> None:
        """Reject entity IDs that are not positive.

        Args:
            item_id: Identifier to validate.

        Raises:
            ValueError: If item_id is not a positive integer.
        """
        if item_id < 1:
            raise ValueError("IDs must be positive integers")
