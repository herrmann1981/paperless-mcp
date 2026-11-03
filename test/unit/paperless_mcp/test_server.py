"""MCP tool registration tests."""

import asyncio
import logging

from paperless_mcp import __version__
from paperless_mcp.config import Settings
from paperless_mcp.server import create_server


class TestServer:
    def test_registers_tools_for_all_resources_and_document_bulk_operations(
        self,
    ) -> None:
        """Expose the complete entity and document bulk MCP tool set."""
        server = create_server(Settings("http://paperless.test", "test-token"))

        tools = asyncio.run(server.list_tools())

        assert {tool.name for tool in tools} == {
            "list_documents",
            "search_documents",
            "read_document",
            "download_document",
            "update_document",
            "delete_document",
            "list_tags",
            "search_tags",
            "read_tag",
            "update_tag",
            "delete_tag",
            "list_document_types",
            "search_document_types",
            "read_document_type",
            "create_document_type",
            "update_document_type",
            "delete_document_type",
            "list_storage_paths",
            "search_storage_paths",
            "read_storage_path",
            "create_storage_path",
            "update_storage_path",
            "delete_storage_path",
            "list_custom_fields",
            "search_custom_fields",
            "read_custom_field",
            "create_custom_field",
            "update_custom_field",
            "delete_custom_field",
            "create_tag",
            "bulk_update_documents",
            "bulk_delete_documents",
        }

    def test_each_tool_has_description_tags_and_light_dark_icons(self) -> None:
        """Provide discovery metadata for every registered MCP tool."""
        server = create_server(Settings("http://paperless.test", "test-token"))
        tools = asyncio.run(server.list_tools())

        for tool in tools:
            assert tool.description
            assert tool.tags
            assert "paperless" in tool.tags
            assert {icon.theme for icon in tool.icons} == {"light", "dark"}

        assert "documents" in next(
            tool.tags for tool in tools if tool.name == "bulk_delete_documents"
        )

        for tool_name in (
            "list_documents",
            "search_documents",
            "list_tags",
            "search_tags",
            "list_document_types",
            "search_document_types",
            "list_storage_paths",
            "search_storage_paths",
            "list_custom_fields",
            "search_custom_fields",
        ):
            tool = next(tool for tool in tools if tool.name == tool_name)
            assert tool.parameters["properties"]["page_size"]["default"] == 100

    def test_each_entity_uses_its_own_icon_set(self) -> None:
        """Use one distinct themed icon set per entity across its tools."""
        server = create_server(Settings("http://paperless.test", "test-token"))
        tools = asyncio.run(server.list_tools())
        entity_icon_sources = {}

        for entity in (
            "documents",
            "tags",
            "document_types",
            "storage_paths",
            "custom_fields",
        ):
            matching_tools = [tool for tool in tools if entity in tool.tags]
            assert matching_tools
            sources = {
                tuple(icon.src for icon in tool.icons) for tool in matching_tools
            }
            assert len(sources) == 1
            entity_icon_sources[entity] = next(iter(sources))

        assert len(set(entity_icon_sources.values())) == 5

    def test_server_configures_logging_from_settings(self) -> None:
        """Apply the configured log level when building the MCP server."""
        root_logger = logging.getLogger()
        previous_level = root_logger.level
        try:
            create_server(Settings("http://paperless.test", "test-token", "WARNING"))
            assert root_logger.level == logging.WARNING
        finally:
            root_logger.setLevel(previous_level)

    def test_server_exposes_version_and_light_dark_icons(self) -> None:
        """Expose the package version and both packaged server icon themes."""
        server = create_server(Settings("http://paperless.test", "test-token"))

        assert server.version == __version__
        assert "custom-field definitions" in server.instructions
        assert {icon.theme for icon in server.icons} == {"light", "dark"}
        assert all(icon.mime_type == "image/svg+xml" for icon in server.icons)
        assert all(
            icon.src.startswith("data:image/svg+xml;base64,") for icon in server.icons
        )
