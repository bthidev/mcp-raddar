# MCP Raddar - Model Context Protocol Server

A unified MCP server providing **18 tools** for managing [Sonarr](https://sonarr.tv/) (TV series) and [Radarr](https://radarr.video/) (movies) through the Model Context Protocol.

Perfect for integrating your media automation with AI assistants, n8n workflows, and other MCP-compatible clients.

## Features

- 🎬 **9 Sonarr Tools** - Search, add, monitor TV series
- 🎥 **9 Radarr Tools** - Search, add, monitor movies
- 🔄 **Multi-instance Support** - Manage multiple Sonarr/Radarr instances
- 📡 **Streamable HTTP Transport** - Modern MCP protocol (2025-03-26+) for n8n and web clients
- 🖼️ **Image URL Transformation** - Absolute URLs for external use
- ⚡ **Built-in Retry Logic** - Robust error handling

## Quick Start

### 1. Pull the Image

```bash
docker pull YOUR_USERNAME/mcp-raddar:latest
```

### 2. Create Configuration

Create a `.env` file:

```env
# Sonarr Configuration
SONARR_URL_1=http://sonarr:8989
SONARR_API_KEY_1=your_sonarr_api_key_here

# Radarr Configuration
RADARR_URL_1=http://radarr:7878
RADARR_API_KEY_1=your_radarr_api_key_here

# Server Configuration
MCP_PORT=8000
MCP_HOSTNAME=0.0.0.0
MCP_LOG_LEVEL=INFO
```

### 3. Run the Container

```bash
docker run -d \
  --name mcp-raddar \
  --env-file .env \
  -p 8000:8000 \
  YOUR_USERNAME/mcp-raddar:latest
```

### 4. Test the Connection

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'
```

You should see a JSON response with server capabilities and protocol information.

## Available Tools

### Sonarr Tools (9)
- **sonarr_search_series** - Search for TV series by name or TVDB ID
- **sonarr_list_series** - List all series in library
- **sonarr_get_history** - Get download/import history
- **sonarr_add_series** - Add new series to library
- **sonarr_get_quality_profiles** - Get available quality profiles
- **sonarr_get_root_folders** - Get configured root folders
- **sonarr_get_queue** - Monitor current downloads
- **sonarr_get_calendar** - Get upcoming episodes
- **sonarr_get_system_status** - Get system information

### Radarr Tools (9)
- **radarr_search_movies** - Search for movies by title, TMDB or IMDB ID
- **radarr_list_movies** - List all movies in library
- **radarr_get_history** - Get download/import history
- **radarr_add_movie** - Add new movie to library
- **radarr_get_quality_profiles** - Get available quality profiles
- **radarr_get_root_folders** - Get configured root folders
- **radarr_get_queue** - Monitor current downloads
- **radarr_get_calendar** - Get upcoming movie releases
- **radarr_get_system_status** - Get system information

## Environment Variables

### Required

| Variable | Description | Example |
|----------|-------------|---------|
| `SONARR_URL_1` | Sonarr base URL | `http://sonarr:8989` |
| `SONARR_API_KEY_1` | Sonarr API key | `abc123...` |
| `RADARR_URL_1` | Radarr base URL | `http://radarr:7878` |
| `RADARR_API_KEY_1` | Radarr API key | `def456...` |

### Optional

| Variable | Description | Default |
|----------|-------------|---------|
| `MCP_PORT` | HTTP server port | `8000` |
| `MCP_HOSTNAME` | HTTP server bind address | `0.0.0.0` |
| `MCP_SERVER_NAME` | Server name | `mcp-raddar` |
| `MCP_LOG_LEVEL` | Logging level | `INFO` |
| `REQUEST_TIMEOUT` | API request timeout (seconds) | `30` |
| `REQUEST_MAX_RETRIES` | Max retry attempts | `3` |
| `REQUEST_BACKOFF_FACTOR` | Retry backoff factor | `0.5` |

## Multi-Instance Configuration

Support for multiple Sonarr/Radarr instances:

```env
# First Sonarr instance
SONARR_URL_1=http://sonarr1:8989
SONARR_API_KEY_1=key1

# Second Sonarr instance
SONARR_URL_2=http://sonarr2:8989
SONARR_API_KEY_2=key2

# First Radarr instance
RADARR_URL_1=http://radarr1:7878
RADARR_API_KEY_1=key3

# Second Radarr instance
RADARR_URL_2=http://radarr2:7878
RADARR_API_KEY_2=key4
```

When using multiple instances, tools accept an `instance_id` parameter (defaults to 1).

## Docker Compose Example

```yaml
version: '3.8'

services:
  mcp-raddar:
    image: YOUR_USERNAME/mcp-raddar:latest
    container_name: mcp-raddar
    ports:
      - "8000:8000"
    environment:
      SONARR_URL_1: http://sonarr:8989
      SONARR_API_KEY_1: ${SONARR_API_KEY}
      RADARR_URL_1: http://radarr:7878
      RADARR_API_KEY_1: ${RADARR_API_KEY}
      MCP_LOG_LEVEL: INFO
    restart: unless-stopped
    networks:
      - media

networks:
  media:
    external: true
```

## Usage with n8n

1. **Configure MCP Client Tool:**
   - **Endpoint URL**: `http://mcp-raddar:8000/mcp`
   - **Server Transport**: `streamable-http`

2. **Use MCP tools in your workflows:**
   ```json
   {
     "tool": "sonarr_search_series",
     "arguments": {
       "query": "Breaking Bad"
     }
   }
   ```

3. **Add a series:**
   ```json
   {
     "tool": "sonarr_add_series",
     "arguments": {
       "tvdb_id": 81189,
       "quality_profile_id": 1,
       "root_folder_path": "/tv"
     }
   }
   ```

## Common Workflows

### Get Configuration for Adding Content

```bash
# 1. Get quality profiles
curl -X POST http://localhost:8000/messages?session_id=SESSION_ID \
  -H "Content-Type: application/json" \
  -d '{"tool":"sonarr_get_quality_profiles"}'

# 2. Get root folders
curl -X POST http://localhost:8000/messages?session_id=SESSION_ID \
  -H "Content-Type: application/json" \
  -d '{"tool":"sonarr_get_root_folders"}'

# 3. Search for content
curl -X POST http://localhost:8000/messages?session_id=SESSION_ID \
  -H "Content-Type: application/json" \
  -d '{"tool":"sonarr_search_series","arguments":{"query":"The Wire"}}'

# 4. Add the series
curl -X POST http://localhost:8000/messages?session_id=SESSION_ID \
  -H "Content-Type: application/json" \
  -d '{"tool":"sonarr_add_series","arguments":{"tvdb_id":79126,"quality_profile_id":1,"root_folder_path":"/tv"}}'
```

### Monitor Downloads

```bash
# Get current download queue
curl -X POST http://localhost:8000/messages?session_id=SESSION_ID \
  -H "Content-Type: application/json" \
  -d '{"tool":"sonarr_get_queue","arguments":{"page":1,"page_size":20}}'
```

### Check Upcoming Content

```bash
# Get upcoming episodes (next 7 days)
curl -X POST http://localhost:8000/messages?session_id=SESSION_ID \
  -H "Content-Type: application/json" \
  -d '{"tool":"sonarr_get_calendar"}'

# Get upcoming movie releases (next 30 days)
curl -X POST http://localhost:8000/messages?session_id=SESSION_ID \
  -H "Content-Type: application/json" \
  -d '{"tool":"radarr_get_calendar"}'
```

## Endpoints

- **MCP Endpoint**: `POST /mcp` - Unified endpoint for all MCP communication
- **Protocol**: Streamable HTTP (MCP 2025-03-26+)
- **Session Management**: Handled via `MCP-Session-Id` header

## Health Check

```bash
# Check if server is running (via Docker healthcheck)
docker ps | grep mcp-raddar

# Or test MCP initialization
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'
```

## Logging

Logs are output to stdout/stderr. View with:

```bash
docker logs -f mcp-raddar
```

Set log level with `MCP_LOG_LEVEL`:
- `DEBUG` - Detailed debugging information
- `INFO` - General information (default)
- `WARNING` - Warning messages
- `ERROR` - Error messages only
- `CRITICAL` - Critical errors only

## Requirements

- Docker 20.10+
- Sonarr v3+ (API v3)
- Radarr v3+ (API v3)

## Architecture

Built with:
- Python 3.14+
- MCP Python SDK
- Starlette (ASGI framework)
- Uvicorn (ASGI server)
- uv (package manager)

## Support

- **Issues**: [GitHub Issues](https://github.com/YOUR_USERNAME/mcp-raddar/issues)
- **Documentation**: [Full Documentation](https://github.com/YOUR_USERNAME/mcp-raddar)
- **MCP Protocol**: [Model Context Protocol](https://modelcontextprotocol.io/)

## License

[Your License Here]

## Tags

`mcp` `sonarr` `radarr` `media-automation` `ai` `n8n` `model-context-protocol` `api` `integration` `streamable-http` `fastmcp` `python`
