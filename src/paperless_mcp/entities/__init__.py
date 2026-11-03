"""Paperless API entity modules."""

from paperless_mcp.entities.correspondents import CorrespondentsAPI
from paperless_mcp.entities.custom_fields import CustomFieldsAPI
from paperless_mcp.entities.document_types import DocumentTypesAPI
from paperless_mcp.entities.documents import DocumentsAPI
from paperless_mcp.entities.storage_paths import StoragePathsAPI
from paperless_mcp.entities.tags import TagsAPI

ENTITY_APIS = (
    DocumentsAPI,
    TagsAPI,
    CorrespondentsAPI,
    DocumentTypesAPI,
    StoragePathsAPI,
    CustomFieldsAPI,
)

__all__ = [
    "CustomFieldsAPI",
    "CorrespondentsAPI",
    "ENTITY_APIS",
    "DocumentTypesAPI",
    "DocumentsAPI",
    "StoragePathsAPI",
    "TagsAPI",
]
