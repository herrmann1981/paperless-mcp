"""Load packaged Paperless MCP server and entity icons."""

from base64 import b64encode
from importlib.resources import files
from typing import Literal

from mcp.types import Icon

EntityName = Literal[
    "documents", "tags", "document_types", "storage_paths", "custom_fields"
]


def _load_icons(asset_prefix: str) -> list[Icon]:
    """Load the light and dark SVG assets for the requested icon prefix.

    Args:
        asset_prefix: The icon asset name prefix without the theme suffix.

    Returns:
        list[Icon]: A pair of theme-specific icons ready to register with FastMCP.
    """
    assets = files("paperless_mcp").joinpath("assets")
    icons = []
    for theme in ("light", "dark"):
        image = assets.joinpath(f"{asset_prefix}-{theme}.svg").read_bytes()
        source = f"data:image/svg+xml;base64,{b64encode(image).decode('ascii')}"
        icons.append(
            Icon(src=source, mimeType="image/svg+xml", sizes=["any"], theme=theme)
        )
    return icons


def load_server_icons() -> list[Icon]:
    """Return the general Paperless server icons for both themes.

    Returns:
        list[Icon]: Light and dark variants of the server icon set.
    """
    return _load_icons("paperless-mcp")


def load_entity_icons(entity: EntityName) -> list[Icon]:
    """Return entity-specific light- and dark-theme SVG icons.

    Args:
        entity: The Paperless entity name used to select the icon asset bundle.

    Returns:
        list[Icon]: Light and dark variants for the requested entity icon set.
    """
    return _load_icons(f"paperless-mcp-{entity}")
