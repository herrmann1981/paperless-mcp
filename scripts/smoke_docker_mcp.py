"""Verify that a Docker image completes the MCP stdio initialization handshake."""

import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def check_image(image: str) -> None:
    """Start an image and initialize an MCP session over stdio.

    Args:
        image: Docker image reference to smoke test.
    """
    server = StdioServerParameters(
        command="docker",
        args=[
            "run",
            "--rm",
            "-i",
            "-e",
            "PAPERLESS_BASE_URL=http://paperless.invalid",
            "-e",
            "PAPERLESS_API_KEY=smoke-test-token",
            image,
        ],
    )
    async with stdio_client(server) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            result = await session.initialize()
            if result.server_info.name != "paperless":
                raise RuntimeError(f"Unexpected MCP server name: {result.server_info.name}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: smoke_docker_mcp.py IMAGE")
    asyncio.run(check_image(sys.argv[1]))
