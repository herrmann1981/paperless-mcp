# Paperless MCP

A Python [FastMCP](https://gofastmcp.com/) server exposing selected
Paperless-ngx API tools over stdio.

The MCP server metadata reports the package `__version__` from
`src/paperless_mcp/__init__.py`. Update that value when releasing a new server
version. Theme-specific example icons are packaged in
`src/paperless_mcp/assets/paperless-mcp-light.svg` and
`src/paperless_mcp/assets/paperless-mcp-dark.svg` and embedded in the server
metadata as data URIs. Each entity's tools also use distinct light/dark
examples: `paperless-mcp-documents-*.svg`,
`paperless-mcp-tags-*.svg`, `paperless-mcp-document_types-*.svg`,
`paperless-mcp-storage_paths-*.svg`, and
`paperless-mcp-custom_fields-*.svg`.

## Configuration

Set these environment variables:

- `PAPERLESS_BASE_URL`: Paperless server URL, for example `http://localhost:8000`
- `PAPERLESS_API_KEY`: Paperless API token
- `PAPERLESS_LOG_LEVEL`: Python logging level (`DEBUG`, `INFO`, `WARNING`,
  `ERROR`, or `CRITICAL`); defaults to `INFO`

Copy `.env.example` to `.env` and replace the placeholder token. Do not commit
the `.env` file.

## Run with uv

```powershell
uv sync
uv run paperless-mcp
```

## Run with Docker

```powershell
docker build -t paperless-mcp .
docker run --rm --env-file .env paperless-mcp
```

The server uses stdio transport, as expected by local MCP clients. Configure
the client to launch `uv run paperless-mcp` or the Docker command above.
Logs are written to stderr so they do not interfere with the MCP stdio
protocol. API logs include request methods, endpoint paths, and status codes,
but do not include API keys, request payloads, or response bodies.

## Configure in GitHub Copilot CLI

First, make sure the server's environment variables are available to the
process Copilot CLI launches. For local `uv` use, set
`PAPERLESS_BASE_URL`, `PAPERLESS_API_KEY`, and optionally
`PAPERLESS_LOG_LEVEL` in the environment where you start Copilot CLI. For
Docker, build the image and put the variables in a local `.env` file as
described above.

In Copilot CLI, run `/mcp` and add a local stdio server. Use one of these
launch configurations:

**Run with uv**

- Command: `uv`
- Arguments: `--directory`, the absolute path to this project, `run`,
  `paperless-mcp`
- Environment: `PAPERLESS_BASE_URL`, `PAPERLESS_API_KEY`, and optionally
  `PAPERLESS_LOG_LEVEL`

For example, the arguments on Windows are `--directory`,
`C:\work\paperless-mcp`, `run`, `paperless-mcp`.

**Run with Docker**

- Command: `docker`
- Arguments: `run`, `--rm`, `-i`, `--env-file`, the absolute path to this
  project's `.env` file, `paperless-mcp:local`
- No separate environment entries are needed; Docker reads them from `.env`.

The Docker image must already be built with `docker build -t paperless-mcp:local .`.
Keep `.env` local and do not put API keys directly in the command arguments.

## Available tools

| Tool | Description |
|---|---|
| `list_documents` | List documents. |
| `search_documents` | Search documents. |
| `read_document` | Read a document by ID. |
| `update_document` | Update a document by ID. |
| `delete_document` | Delete a document by ID; requires `confirm=true`. |
| `bulk_update_documents` | Update selected document IDs. |
| `bulk_delete_documents` | Delete selected document IDs; requires `confirm=true`. |
| `list_tags` | List tags. |
| `search_tags` | Search tags. |
| `read_tag` | Read a tag by ID. |
| `create_tag` | Create a tag from Paperless API fields. |
| `update_tag` | Update a tag by ID. |
| `delete_tag` | Delete a tag by ID; requires `confirm=true`. |
| `list_document_types` | List document types. |
| `search_document_types` | Search document types. |
| `read_document_type` | Read a document type by ID. |
| `create_document_type` | Create a document type from Paperless API fields. |
| `update_document_type` | Update a document type by ID. |
| `delete_document_type` | Delete a document type by ID; requires `confirm=true`. |
| `list_storage_paths` | List storage paths. |
| `search_storage_paths` | Search storage paths. |
| `read_storage_path` | Read a storage path by ID. |
| `create_storage_path` | Create a storage path from Paperless API fields. |
| `update_storage_path` | Update a storage path by ID. |
| `delete_storage_path` | Delete a storage path by ID; requires `confirm=true`. |
| `list_custom_fields` | List Paperless custom-field definitions. |
| `search_custom_fields` | Search Paperless custom-field definitions. |
| `read_custom_field` | Read a custom-field definition by ID. |
| `create_custom_field` | Create a custom-field definition from Paperless API fields. |
| `update_custom_field` | Update a custom-field definition by ID. |
| `delete_custom_field` | Delete a custom-field definition by ID; requires `confirm=true`. |

List and search tools accept `page` and `page_size` parameters; page size is
limited to 100. Search tools take a `query` parameter. Update tools accept an
`updates` object, which is sent as a Paperless API PATCH request. Bulk document
updates and deletes take explicit ID lists and process IDs one at a time, so
earlier changes may already have succeeded if a later request fails.
Create tools accept a `data` object containing fields supported by the
corresponding Paperless API endpoint. Document creation is a separate file
upload workflow and is not exposed as a JSON entity-creation tool.

Entity-specific API operations and MCP tool registration are organized in
`src/paperless_mcp/entities/`: `documents.py`, `tags.py`,
`document_types.py`, `storage_paths.py`, and `custom_fields.py`. The
`custom_fields` tools use the Paperless custom-field definition API. Shared
HTTP and CRUD behavior is in `entities/base.py`. The authenticated Paperless
HTTP client and API errors are in `src/paperless_mcp/paperless/`.

## Tests and style

```powershell
uv run pytest
uv run pytest -m integration
uv run ruff check .
uv run ruff format --check .
```

Unit tests live in `test/unit` and run by default. The integration suite in
`test/integration` starts an isolated Paperless-ngx, PostgreSQL, and Redis
stack with Docker Compose, obtains an API token using the test admin account,
and removes that stack after the run. Docker and the Docker Compose plugin are
required. The default Paperless host port is `8010`; set `PAPERLESS_TEST_PORT`
to use another available port.
