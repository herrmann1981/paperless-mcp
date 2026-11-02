"""Shared operations and MCP tool registration for Paperless entities."""

from typing import Any

from paperless_mcp.paperless import PaperlessClient


class EntityAPI:
    """Common list, search, read, create, update, and delete operations."""

    endpoint: str
    plural_name: str
    singular_name: str

    def __init__(self, client: PaperlessClient) -> None:
        """Initialize the entity API with a shared HTTP client."""
        self.client = client

    async def list(
        self,
        search: str | None = None,
        page: int = 1,
        page_size: int = 25,
    ) -> dict[str, Any]:
        """List or search entity records with bounded pagination."""
        if page < 1:
            raise ValueError("page must be at least 1")
        if not 1 <= page_size <= 100:
            raise ValueError("page_size must be between 1 and 100")
        params: dict[str, Any] = {"page": page, "page_size": page_size}
        if search:
            params["search"] = search
        return await self.client.request("GET", self.endpoint, params=params)

    async def read(self, item_id: int) -> dict[str, Any]:
        """Fetch one entity record by its positive ID."""
        self._validate_id(item_id)
        return await self.client.request("GET", f"{self.endpoint}{item_id}/")

    async def create(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create an entity record from the supplied Paperless API fields."""
        if not data:
            raise ValueError("data must contain at least one field")
        return await self.client.request("POST", self.endpoint, json=data)

    async def update(self, item_id: int, updates: dict[str, Any]) -> dict[str, Any]:
        """Patch one entity record with the supplied fields."""
        self._validate_id(item_id)
        if not updates:
            raise ValueError("updates must contain at least one field")
        return await self.client.request(
            "PATCH", f"{self.endpoint}{item_id}/", json=updates
        )

    async def delete(self, item_id: int, confirm: bool) -> dict[str, Any] | None:
        """Delete one entity record only after explicit confirmation."""
        self._validate_id(item_id)
        if not confirm:
            raise ValueError("Set confirm=true to delete this resource")
        return await self.client.request("DELETE", f"{self.endpoint}{item_id}/")

    @staticmethod
    def _validate_id(item_id: int) -> None:
        """Reject entity IDs that are not positive."""
        if item_id < 1:
            raise ValueError("IDs must be positive integers")
