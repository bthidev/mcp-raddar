# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MCP Raddar is a Model Context Protocol (MCP) server that provides a unified interface for managing Sonarr (TV series) and Radarr (movies) through 18 MCP tools. Built with Python 3.14+ and the uv package manager, it supports multiple instances of each service and runs in Docker.

## Development Commands

### Setup
```bash
# Install dependencies
uv sync

# Create environment file
cp .env.example .env
# Edit .env to configure your Sonarr/Radarr instances
```

### Running the Server
```bash
# Local development (Streamable HTTP mode)
uv run python -m src.server

# With Docker Compose
docker-compose up -d
docker-compose logs -f mcp-raddar
# Access at http://localhost:8000/mcp
```

### Code Quality (Not Yet Configured)
```bash
# Format code
uv run black src/

# Type checking
uv run mypy src/

# Linting
uv run ruff check src/
```

## Architecture

### Configuration System (`src/config.py`)

Multi-instance configuration through environment variables with dynamic discovery:
- Scans for numbered env vars: `SONARR_URL_1`, `SONARR_API_KEY_1`, `SONARR_URL_2`, etc.
- Uses Pydantic for validation with `InstanceConfig` and `Config` models
- **Critical**: Both URL and API key must be present for each instance, or configuration fails
- Validates on startup (fail-fast approach)

### Client Architecture

**Three-layer pattern:**

1. **Base Client** (`src/clients/base.py`):
   - `BaseArrClient` provides HTTP session with retry logic
   - Retry strategy: Exponential backoff for 429, 5xx errors
   - Does NOT retry on 4xx errors (except 429)
   - Custom exceptions: `ArrClientError`, `ArrNetworkError`, `ArrAPIError`

2. **Service Clients** (`src/clients/sonarr.py`, `src/clients/radarr.py`):
   - Inherit from `BaseArrClient`
   - Implement service-specific API v3 endpoints
   - **Image URL transformation**: Convert relative paths (e.g., `/api/v3/mediacover/123/poster.jpg`) to absolute URLs by prepending `base_url`
   - This transformation happens in `_transform_images()` method

3. **MCP Tools** (`src/tools/sonarr_tools.py`, `src/tools/radarr_tools.py`):
   - Wrapper classes (`SonarrTools`, `RadarrTools`) that manage multiple client instances
   - Async methods that map MCP tool calls to client methods
   - Format API responses into JSON strings for MCP protocol
   - Handle `instance_id` parameter for multi-instance support

### MCP Server (`src/server.py`)

- Uses `FastMCP` with Streamable HTTP transport (protocol version 2025-03-26+)
- Built with Starlette web framework and Uvicorn ASGI server
- Exposes single unified endpoint: `/mcp` (handles both GET and POST)
- Registers 18 tools (9 Sonarr + 9 Radarr)
- Tool registration via helper functions `_register_sonarr_tools()` and `_register_radarr_tools()`
- Tools use `@mcp.tool()` decorator with type hints for schema generation
- Session management via lifespan context manager
- Loads config once on startup, creates all client instances
- Configurable via `MCP_PORT` (default: 8000) and `MCP_HOSTNAME` (default: 0.0.0.0)
- Supports stateless mode (`stateless_http=True`) and JSON responses (`json_response=True`)

### Request Flow Example

```
MCP Client → server.py (call_tool)
  → sonarr_tools.py (search_series)
    → sonarr.py (search_series + _transform_images)
      → base.py (_make_request with retry)
        → Sonarr API
```

## Key Implementation Details

### Multi-Instance Support
- Environment variables use numbered suffixes: `{SERVICE}_URL_{N}`, `{SERVICE}_API_KEY_{N}`
- Tools accept `instance_id` parameter (defaults to 1)
- Config discovery scans from 1-100, stops at first gap
- Each tool method validates `instance_id` exists before use

### Instance ID Parameter Behavior

**Dynamic Parameter Visibility** (Updated Dec 22):
- Tools automatically hide `instance_id` parameter when only one instance is configured
- Multi-instance setups show the parameter with default value of 1
- `_get_client()` methods accept `None` and auto-select first available instance

**Implementation Details**:
- Configuration scans for numbered env vars: `{SERVICE}_URL_{N}`, `{SERVICE}_API_KEY_{N}`
- Scans from 1-100, stops at first gap
- Both URL and API key must be present, or configuration fails
- Each tool method validates `instance_id` exists before use

**Example Behavior**:

Single instance configuration:
```python
# .env
SONARR_URL_1=http://sonarr:8989
SONARR_API_KEY_1=abc123

# Tool schema - instance_id hidden
{
  "name": "sonarr_search_series",
  "parameters": {
    "query": "Breaking Bad"  # No instance_id parameter
  }
}
```

Multi-instance configuration:
```python
# .env
SONARR_URL_1=http://sonarr:8989
SONARR_API_KEY_1=abc123
SONARR_URL_2=http://sonarr-4k:8989
SONARR_API_KEY_2=def456

# Tool schema - instance_id visible
{
  "name": "sonarr_search_series",
  "parameters": {
    "query": "Breaking Bad",
    "instance_id": 1  # Now visible with default
  }
}
```

**Migration Impact**:
With FastMCP, `instance_id` is always present in tool schemas (minor UX regression from dynamic behavior, but simpler and clearer).

### Image URL Transformation
**Critical feature**: All image URLs must be absolute for n8n/external use.

Sonarr/Radarr APIs return:
```json
{"images": [{"coverType": "poster", "url": "/api/v3/mediacover/123/poster.jpg"}]}
```

Server transforms to:
```json
{"images": [{"type": "poster", "url": "http://sonarr:8989/api/v3/mediacover/123/poster.jpg"}]}
```

Implementation in `_transform_images()` checks if URL starts with `/` before prepending `base_url`.

### Error Handling Philosophy
- **Configuration errors**: Raise exceptions, fail startup
- **Network/API errors**: Catch in tools layer, return error string to MCP client
- **Validation errors**: Raised before API calls (e.g., invalid instance_id)
- All errors logged with context (instance_id, endpoint, parameters)

### Add Operations Special Behavior
Both `add_series` and `add_movie`:
1. First call search/lookup endpoint to get full metadata
2. Extract required fields (title, titleSlug, images, etc.)
3. Merge with user parameters (quality_profile_id, root_folder_path)
4. POST complete payload to add endpoint

This two-step process is required because Sonarr/Radarr need full series/movie objects, not just IDs.

## Environment Variable Format

```bash
# Server config
MCP_SERVER_NAME=mcp-raddar
MCP_LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
MCP_PORT=8000  # HTTP server port
MCP_HOSTNAME=0.0.0.0  # HTTP server hostname

# Multi-instance format (N = 1, 2, 3...)
SONARR_URL_1=http://sonarr:8989
SONARR_API_KEY_1=abc123
RADARR_URL_1=http://radarr:7878
RADARR_API_KEY_1=def456

# Request tuning
REQUEST_TIMEOUT=30
REQUEST_MAX_RETRIES=3
REQUEST_BACKOFF_FACTOR=0.5
```

## n8n Integration

Server runs in Streamable HTTP mode (MCP 2025-03-26+), making it directly compatible with n8n and other MCP clients:
- Connect to `http://localhost:8000/mcp` for unified MCP endpoint
- Single endpoint handles all MCP communication (no separate GET/POST endpoints)
- Returns JSON responses for quick operations (stateless_http=True, json_response=True)
- Includes session management via `MCP-Session-Id` header
- Protocol version support: 2025-03-26, 2025-06-18, 2025-11-25, draft
- Configure port and hostname via `MCP_PORT` and `MCP_HOSTNAME` environment variables
- No need for `mcp-remote` or additional bridging
- Stateless mode enabled by default for scalability

## Testing Notes

No tests currently implemented. When adding:
- Mock API responses in client tests
- Test multi-instance configuration scenarios
- Test image URL transformation
- Test error handling paths (401, 404, 500, network errors)
- Validate MCP tool input schemas
