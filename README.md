# Paperless MCP

A Python [FastMCP](https://gofastmcp.com/) server exposing selected
Paperless-ngx API tools over stdio.

The server connects to an existing Paperless-ngx instance using its REST API.
It supports document search and metadata management, document PDF downloads,
and management of tags, document types, storage paths, and custom-field
definitions. It does not host Paperless-ngx or create documents from uploaded
files.

## Configuration

The server reads its configuration from the process environment:

- `PAPERLESS_BASE_URL`: Paperless server origin, for example
  `http://localhost:8000` (do not append `/api/`). It must be an absolute
  HTTP or HTTPS URL.
- `PAPERLESS_API_KEY`: API token created by Paperless-ngx.
- `PAPERLESS_LOG_LEVEL`: Optional Python logging level: `DEBUG`, `INFO`,
  `WARNING`, `ERROR`, or `CRITICAL`. Defaults to `INFO`.

Copy `.env.example` to `.env` and replace the placeholder token. The Python
process does not load `.env` files automatically: for a local `uv` run, export
the variables in the environment that starts the server. Docker's `--env-file`
option reads `.env` directly. Keep API tokens private and never commit `.env`.

## Run locally with uv

```powershell
uv sync --locked
$env:PAPERLESS_BASE_URL = "http://localhost:8000"
$env:PAPERLESS_API_KEY = "your-paperless-api-token"
uv run paperless-mcp
```

The project requires Python 3.10 or later. `uv sync --locked` installs the
project dependencies from `uv.lock`; `uv run paperless-mcp` starts the server.
Install [uv](https://docs.astral.sh/uv/) before following these steps.

## Run with Docker

```powershell
.\scripts\build-docker.ps1
docker run --rm --env-file .env paperless-mcp
```

The build script tags the image as `paperless-mcp:local` by default. To choose
a different Docker image name and tag, pass it as the first argument:

```powershell
.\scripts\build-docker.ps1 paperless-mcp:dev
```

You can also build directly with Docker using
`docker build -t paperless-mcp:local .`.

The image uses Python 3.12 and installs the locked runtime dependencies. The
server uses stdio transport, as expected by local MCP clients. Logs are written
to stderr so they do not interfere with the MCP protocol. API logs include
request methods, endpoint paths, and status codes, but exclude API keys,
request payloads, and response bodies.

## Configure in GitHub Copilot CLI

First, make sure the server's environment variables are available to the
process Copilot CLI launches. For local `uv` use, set
`PAPERLESS_BASE_URL`, `PAPERLESS_API_KEY`, and optionally
`PAPERLESS_LOG_LEVEL` in the environment where you start Copilot CLI. For
Docker, build the image and put the variables in a local `.env` file as
described above.

In Copilot CLI, run `/mcp` and add a local stdio server. Use one of these
launch configurations. Replace the example paths and environment values with
your local settings.

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

Build the Docker image first with `.\scripts\build-docker.ps1`. Keep `.env`
local and do not put API keys directly in the command arguments.

The server requires a running Paperless-ngx server and a valid API token.
Requests use the configured token for authentication, and Paperless permissions
continue to control which records the token can access or modify.

Example command:
```
docker run -i -rm --dns=IP_OF_DNS_SERVER_TO_RESOLVE_PAPERLESS -e PAPERLESS_BASE_URL=http://paperless.host:port -e PAPERLESS_API_KEY=API_KEY_FROM_PAPERLESS paperless-mcp:1.0.0
```

## Available tools

### Documents

| Tool | Description |
|---|---|
| `list_documents` | List document records. |
| `search_documents` | Search document records. |
| `read_document` | Read a document's Paperless API record by ID. |
| `download_document` | Download the original document's PDF as an MCP binary resource. |
| `update_document` | Update document metadata by ID. |
| `delete_document` | Delete a document by ID; requires `confirm=true`. |
| `bulk_update_documents` | Update an explicit list of document IDs. |
| `bulk_delete_documents` | Delete explicit document IDs; requires `confirm=true`. |

### Tags

| Tool | Description |
|---|---|
| `list_tags` | List tags. |
| `search_tags` | Search tags. |
| `read_tag` | Read a tag by ID. |
| `create_tag` | Create a tag from Paperless API fields. |
| `update_tag` | Update a tag by ID. |
| `delete_tag` | Delete a tag by ID; requires `confirm=true`. |

### Document types

| Tool | Description |
|---|---|
| `list_document_types` | List document types. |
| `search_document_types` | Search document types. |
| `read_document_type` | Read a document type by ID. |
| `create_document_type` | Create a document type from Paperless API fields. |
| `update_document_type` | Update a document type by ID. |
| `delete_document_type` | Delete a document type by ID; requires `confirm=true`. |

### Storage paths

| Tool | Description |
|---|---|
| `list_storage_paths` | List storage paths. |
| `search_storage_paths` | Search storage paths. |
| `read_storage_path` | Read a storage path by ID. |
| `create_storage_path` | Create a storage path from Paperless API fields. |
| `update_storage_path` | Update a storage path by ID. |
| `delete_storage_path` | Delete a storage path by ID; requires `confirm=true`. |

### Custom-field definitions

| Tool | Description |
|---|---|
| `list_custom_fields` | List Paperless custom-field definitions. |
| `search_custom_fields` | Search Paperless custom-field definitions. |
| `read_custom_field` | Read a custom-field definition by ID. |
| `create_custom_field` | Create a custom-field definition from Paperless API fields. |
| `update_custom_field` | Update a custom-field definition by ID. |
| `delete_custom_field` | Delete a custom-field definition by ID; requires `confirm=true`. |

All list and search tools accept `page` (default `1`) and `page_size` (default
`100`, maximum `1000`). Search tools also require a `query`. Create tools accept
a `data` object and update tools accept an `updates` object; both use fields
supported by the corresponding Paperless API endpoint. `download_document`
returns PDF bytes as an MCP resource with the `application/pdf` media type.
Document creation is a separate Paperless file-upload workflow and is not
exposed as a JSON create tool.

Delete tools require explicit `confirm=true`. Bulk document operations process
the supplied IDs sequentially, not transactionally; if a later request fails,
earlier changes may already have succeeded.

## Development

### Setup and checks

Install Python 3.10 or later and [uv](https://docs.astral.sh/uv/), then sync
the development dependencies:

```powershell
uv sync --locked --group dev
```

Run the unit tests and static checks:

```powershell
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

Install `pre-commit` separately to run the same hooks locally:

```powershell
uv tool install pre-commit
pre-commit run --all-files
```

### Tests

Unit tests are under `test/unit/paperless_mcp/` and run by default. Pytest
configuration excludes tests marked `integration`. Run the integration tests
explicitly:

```powershell
uv run pytest -m integration
```

You can run only the unit tests with `uv run pytest test/unit`.

The integration suite in `test/integration/` starts an isolated Paperless-ngx,
PostgreSQL, and Redis stack with Docker Compose, obtains a token for the
disposable test administrator, then removes the stack and its volumes. Docker
and the Docker Compose plugin are required. The fixture selects an available
host port automatically; set `PAPERLESS_TEST_PORT` to request a specific port.
The compose file uses the latest Paperless-ngx image, so integration behavior
is verified against that image at test time.

### Code organization

```text
src/paperless_mcp/
  config.py                 Environment settings and validation
  server.py                 FastMCP server construction and stdio entry point
  logging_config.py         Stderr logging configuration
  icons.py                  Packaged server and entity icons
  entities/
    base.py                 Shared list, read, create, update, and delete logic
    documents.py            Document tools, PDF download, and bulk operations
    tags.py                 Tag tools
    document_types.py       Document-type tools
    storage_paths.py        Storage-path tools
    custom_fields.py        Custom-field definition tools
  paperless/
    client.py               Authenticated async HTTP client and API errors
test/
  unit/paperless_mcp/       Isolated unit tests
  integration/              Tests against a disposable Paperless stack
.github/
  agents/                   Repository-specific Copilot agent profiles
  workflows/                CI checks and tag publishing
```

`.github/agents/` contains specialized profiles for Python implementation,
documentation, pytest testing, code review, and project planning. Source style
uses Ruff with an 88-character line length, Python 3.10 target, and the `E`,
`F`, `I`, `UP`, and `B` lint rules.

The entity modules register tools with the server; common entity CRUD requests
are implemented in `entities/base.py`. `DocumentsAPI` adds PDF download and
bulk operations. The HTTP client centralizes authentication, response decoding,
and API error handling.

## Continuous integration and releases

`.github/workflows/test.yml` runs for pushes and pull requests. It installs
Python 3.12 and the locked development dependencies, runs pre-commit, and runs
the default pytest suite (unit tests; integration tests are excluded).

Pushing a Git tag beginning with `v` starts
`.github/workflows/tag.yml`. It builds the Docker image and publishes tag and
`latest` tags to GitHub Container Registry (`ghcr.io/<owner>/<repository>`),
then creates a GitHub Release with generated notes and a ZIP source archive of
the tagged commit attached.

The MCP server version is defined by `__version__` in
`src/paperless_mcp/__init__.py`; update it for releases. The server and entity
icons are packaged in `src/paperless_mcp/assets/` as light/dark SVGs and
embedded in MCP metadata as data URIs.
