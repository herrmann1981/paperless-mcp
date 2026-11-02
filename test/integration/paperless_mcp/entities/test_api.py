"""End-to-end tests against a real Paperless-ngx API."""

import uuid

import pytest

from paperless_mcp.entities.custom_fields import CustomFieldsAPI
from paperless_mcp.entities.document_types import DocumentTypesAPI
from paperless_mcp.entities.documents import DocumentsAPI
from paperless_mcp.entities.tags import TagsAPI
from paperless_mcp.paperless import PaperlessClient

pytestmark = pytest.mark.integration


class TestPaperlessEntities:
    @pytest.mark.anyio
    async def test_document_list_and_search_use_real_paperless(
        self,
        paperless_service: PaperlessClient,
    ) -> None:
        """Verify document listing and search against the running Paperless API."""
        documents = DocumentsAPI(paperless_service)
        result = await documents.list(page_size=5)
        search_result = await documents.list(
            search=f"mcp-integration-{uuid.uuid4().hex}", page_size=5
        )

        assert {"count", "results"} <= result.keys()
        assert isinstance(result["results"], list)
        assert search_result["results"] == []

    @pytest.mark.anyio
    async def test_tag_create_read_update_delete_against_real_paperless(
        self,
        paperless_service: PaperlessClient,
    ) -> None:
        """Exercise tag creation, retrieval, update, search, and deletion."""
        tags = TagsAPI(paperless_service)
        tag_name = f"mcp-integration-{uuid.uuid4().hex}"
        created = await tags.create(
            {
                "name": tag_name,
                "color": "#a6cee3",
                "is_inbox_tag": False,
                "matching_algorithm": 0,
            },
        )
        tag_id = created["id"]

        try:
            read_tag = await tags.read(tag_id)
            assert read_tag["name"] == tag_name

            updated_name = f"{tag_name}-updated"
            updated_tag = await tags.update(tag_id, {"name": updated_name})
            assert updated_tag["name"] == updated_name

            search_result = await tags.list(search=updated_name, page_size=5)
            assert any(tag["id"] == tag_id for tag in search_result["results"])
        finally:
            await tags.delete(tag_id, confirm=True)

    @pytest.mark.anyio
    async def test_custom_field_create_read_update_search_delete_against_real_paperless(
        self,
        paperless_service: PaperlessClient,
    ) -> None:
        """Exercise custom-field operations against the real Paperless API."""
        custom_fields = CustomFieldsAPI(paperless_service)
        field_name = f"mcp-integration-{uuid.uuid4().hex}"
        created = await custom_fields.create(
            {"name": field_name, "data_type": "string"}
        )
        field_id = created["id"]

        try:
            read_field = await custom_fields.read(field_id)
            assert read_field["name"] == field_name
            assert read_field["data_type"] == "string"

            updated_name = f"{field_name}-updated"
            updated_field = await custom_fields.update(field_id, {"name": updated_name})
            assert updated_field["name"] == updated_name

            search_result = await custom_fields.list(search=updated_name, page_size=5)
            assert any(field["id"] == field_id for field in search_result["results"])
        finally:
            await custom_fields.delete(field_id, confirm=True)

    @pytest.mark.anyio
    async def test_document_type_create_read_update_delete_against_real_paperless(
        self,
        paperless_service: PaperlessClient,
    ) -> None:
        """Exercise document-type creation and management against Paperless."""
        document_types = DocumentTypesAPI(paperless_service)
        name = f"mcp-integration-{uuid.uuid4().hex}"
        created = await document_types.create({"name": name})

        try:
            document_type = await document_types.read(created["id"])
            assert document_type["name"] == name

            updated_name = f"{name}-updated"
            updated = await document_types.update(created["id"], {"name": updated_name})
            assert updated["name"] == updated_name
        finally:
            await document_types.delete(created["id"], confirm=True)
