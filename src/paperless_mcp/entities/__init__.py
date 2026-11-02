"""Paperless API entity modules."""

from paperless_mcp.entities.custom_fields import CustomFieldsAPI
from paperless_mcp.entities.document_types import DocumentTypesAPI
from paperless_mcp.entities.documents import DocumentsAPI
from paperless_mcp.entities.storage_paths import StoragePathsAPI
from paperless_mcp.entities.tags import TagsAPI

ENTITY_APIS = (
    DocumentsAPI,
    TagsAPI,
    DocumentTypesAPI,
    StoragePathsAPI,
    CustomFieldsAPI,
)

__all__ = [
    "CustomFieldsAPI",
    "ENTITY_APIS",
    "DocumentTypesAPI",
    "DocumentsAPI",
    "StoragePathsAPI",
    "TagsAPI",
]
