"""FastMCP server entry point."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastmcp import FastMCP

from paperless_mcp import __version__
from paperless_mcp.config import Settings
from paperless_mcp.entities import ENTITY_APIS
from paperless_mcp.icons import load_server_icons
from paperless_mcp.logging_config import configure_logging
from paperless_mcp.paperless import PaperlessClient

logger = logging.getLogger(__name__)


def create_server(settings: Settings | None = None) -> FastMCP:
    """Create and configure the Paperless MCP server.

    Args:
        settings: Optional environment configuration to use instead of loading from
            the process environment.

    Returns:
        FastMCP: A configured server with all Paperless entity tools registered.
    """
    settings = settings or Settings.from_env()
    configure_logging(settings.log_level)
    logger.info("Starting Paperless MCP server")
    client = PaperlessClient(settings)

    @asynccontextmanager
    async def client_lifespan(_: FastMCP) -> AsyncIterator[dict[str, Any]]:
        try:
            yield {}
        finally:
            await client.close()

    server = FastMCP(
        name="paperless",
        instructions=(
            "Search and manage Paperless documents, tags, correspondents, document "
            "types, storage paths, and custom-field definitions."
        ),
        version=__version__,
        icons=load_server_icons(),
        lifespan=client_lifespan,
    )
    for api_class in ENTITY_APIS:
        api_class(client).register_tools(server)
    return server


def main() -> None:
    """Run the server over stdio for MCP clients.

    Raises:
        ValueError: If server settings cannot be loaded from the environment.
    """
    create_server().run()


if __name__ == "__main__":
    main()
