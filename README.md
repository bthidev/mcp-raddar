# MCP Raddar

A Model Context Protocol (MCP) server for integrating with Sonarr and Radarr APIs. This server allows you to search, list, and manage TV series and movies through a unified MCP interface, perfect for use with n8n workflows or other MCP clients.

## Features

- **Multi-instance Support**: Connect to multiple Sonarr and Radarr instances
- **Complete API Coverage**: Search, list, history, and add operations
- **Image URL Support**: Returns absolute image URLs for posters, banners, and fanart
- **Docker Ready**: Easy deployment with Docker Compose
- **n8n Compatible**: Works seamlessly with n8n MCP integration
- **Type-safe**: Built with Pydantic for robust configuration and validation
- **Retry Logic**: Automatic retry with exponential backoff for failed requests

## Available Tools

**18 MCP Tools** for comprehensive media management (9 Sonarr + 9 Radarr)

### Sonarr Tools (9)

1. **sonarr_search_series** - Search for TV series by name or TVDB ID
2. **sonarr_list_series** - List all series in your library
3. **sonarr_get_history** - Get download and import history
4. **sonarr_add_series** - Add a new TV series
5. **sonarr_get_quality_profiles** - Get available quality profiles
6. **sonarr_get_root_folders** - Get configured root folders
7. **sonarr_get_queue** - Monitor current downloads
8. **sonarr_get_calendar** - Get upcoming episodes
9. **sonarr_get_system_status** - Get system information

### Radarr Tools (9)

1. **radarr_search_movies** - Search for movies by title, TMDB ID, or IMDB ID
2. **radarr_list_movies** - List all movies in your library
3. **radarr_get_history** - Get download and import history
4. **radarr_add_movie** - Add a new movie
5. **radarr_get_quality_profiles** - Get available quality profiles
6. **radarr_get_root_folders** - Get configured root folders
7. **radarr_get_queue** - Monitor current downloads
8. **radarr_get_calendar** - Get upcoming movie releases
9. **radarr_get_system_status** - Get system information

> 📖 For detailed tool documentation and examples, see [NEW_TOOLS.md](NEW_TOOLS.md)

## Prerequisites

- Python 3.14+
- [uv](https://docs.astral.sh/uv/) package manager
- Docker and Docker Compose (for containerized deployment)
- Sonarr and/or Radarr instances with API access

## Installation

### Local Development

1. Clone the repository:
```bash
git clone <your-repo-url>
cd mcp-raddar
```

2. Install dependencies with uv:
```bash
uv sync
```

3. Copy the example environment file:
```bash
cp .env.example .env
```

4. Edit `.env` and configure your Sonarr/Radarr instances:
```bash
# Sonarr Instance 1
SONARR_URL_1=http://localhost:8989
SONARR_API_KEY_1=your_sonarr_api_key

# Radarr Instance 1
RADARR_URL_1=http://localhost:7878
RADARR_API_KEY_1=your_radarr_api_key
```

5. Run the server:
```bash
uv run python -m src.server
```

### Docker Deployment

1. Copy and configure environment variables:
```bash
cp .env.example .env
# Edit .env with your Sonarr/Radarr URLs and API keys
```

2. Build and start with Docker Compose:
```bash
docker-compose up -d
```

3. View logs:
```bash
docker-compose logs -f mcp-raddar
```

## Configuration

### Environment Variables

The server is configured through environment variables. All variables are defined in `.env.example`.

#### Server Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `MCP_SERVER_NAME` | Server name | `mcp-raddar` |
| `MCP_LOG_LEVEL` | Log level (DEBUG, INFO, WARNING, ERROR) | `INFO` |

#### Sonarr Configuration

For each Sonarr instance, configure:
- `SONARR_URL_{N}` - Base URL (e.g., `http://sonarr:8989`)
- `SONARR_API_KEY_{N}` - API key from Sonarr settings

Where `{N}` is 1, 2, 3, etc. for multiple instances.

**Example**:
```bash
SONARR_URL_1=http://sonarr:8989
SONARR_API_KEY_1=abc123def456
SONARR_URL_2=http://sonarr-4k:8989
SONARR_API_KEY_2=ghi789jkl012
```

#### Radarr Configuration

For each Radarr instance, configure:
- `RADARR_URL_{N}` - Base URL (e.g., `http://radarr:7878`)
- `RADARR_API_KEY_{N}` - API key from Radarr settings

Where `{N}` is 1, 2, 3, etc. for multiple instances.

**Example**:
```bash
RADARR_URL_1=http://radarr:7878
RADARR_API_KEY_1=mno345pqr678
```

#### Request Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `REQUEST_TIMEOUT` | Request timeout in seconds | `30` |
| `REQUEST_MAX_RETRIES` | Maximum retry attempts | `3` |
| `REQUEST_BACKOFF_FACTOR` | Exponential backoff factor | `0.5` |

### Finding Your API Keys

**Sonarr**: Settings → General → Security → API Key
**Radarr**: Settings → General → Security → API Key

## Usage Examples

### Searching for a Series

```json
{
  "tool": "sonarr_search_series",
  "arguments": {
    "query": "Breaking Bad",
    "instance_id": 1
  }
}
```

**Response includes:**
- Title, year, TVDB ID
- Overview and status
- Network information
- **Image URLs** (poster, banner)
- Season count

### Searching for a Movie

```json
{
  "tool": "radarr_search_movies",
  "arguments": {
    "query": "The Matrix",
    "instance_id": 1
  }
}
```

**Response includes:**
- Title, year, TMDB ID, IMDB ID
- Overview and status
- Runtime and studio
- **Image URLs** (poster, fanart)

### Adding a Series

```json
{
  "tool": "sonarr_add_series",
  "arguments": {
    "tvdb_id": 81189,
    "quality_profile_id": 1,
    "root_folder_path": "/tv",
    "monitor": "all",
    "search_for_missing": true,
    "instance_id": 1
  }
}
```

### Adding a Movie

```json
{
  "tool": "radarr_add_movie",
  "arguments": {
    "tmdb_id": 603,
    "quality_profile_id": 1,
    "root_folder_path": "/movies",
    "monitor": true,
    "search_for_movie": true,
    "instance_id": 1
  }
}
```

### Getting History

```json
{
  "tool": "sonarr_get_history",
  "arguments": {
    "page": 1,
    "page_size": 20,
    "instance_id": 1
  }
}
```

## n8n Integration

### Option 1: Using mcp-remote (Recommended)

1. Install mcp-remote:
```bash
npm install -g @modelcontextprotocol/mcp-remote
```

2. Start the MCP server in STDIO mode (default)

3. Use mcp-remote to bridge to SSE:
```bash
mcp-remote --stdio "uv run python -m src.server" --port 8000
```

4. Configure n8n to connect to `http://localhost:8000`

### Option 2: Direct SSE Mode

1. Modify `docker-compose.yml` to expose port 8000

2. Set environment variables:
```bash
MCP_PORT=8000
MCP_HOSTNAME=0.0.0.0
```

3. Configure n8n to connect to your MCP server URL

## Troubleshooting

### Connection Errors

**Problem**: `Failed to connect to Sonarr/Radarr`

**Solutions**:
- Verify URLs are correct and accessible
- Check that instances are running
- Ensure network connectivity (especially in Docker)
- Verify firewall rules

### Authentication Errors

**Problem**: `Authentication failed. Please check your API key.`

**Solutions**:
- Verify API keys are correct
- Check API keys haven't been regenerated
- Ensure no extra spaces in `.env` file

### No Instances Configured

**Problem**: `No Sonarr or Radarr instances configured`

**Solutions**:
- Verify `.env` file exists and is loaded
- Check environment variable format: `SONARR_URL_1`, not `SONARR_URL1`
- Ensure both URL and API key are set for each instance

### Docker Network Issues

**Problem**: Cannot connect to Sonarr/Radarr from Docker container

**Solutions**:
- Use service names instead of `localhost` in URLs
- Ensure all containers are on the same network
- Check `docker-compose.yml` network configuration
- Try using container IP addresses

## Development

### Project Structure

```
mcp-raddar/
├── src/
│   ├── server.py           # Main MCP server
│   ├── config.py           # Configuration management
│   ├── clients/
│   │   ├── base.py         # Base HTTP client
│   │   ├── sonarr.py       # Sonarr API client
│   │   └── radarr.py       # Radarr API client
│   └── tools/
│       ├── sonarr_tools.py # Sonarr MCP tools
│       └── radarr_tools.py # Radarr MCP tools
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
└── README.md
```

### Running Tests

```bash
# Install dev dependencies
uv sync --all-extras

# Run tests (when implemented)
uv run pytest
```

### Code Quality

```bash
# Format code
uv run black src/

# Type checking
uv run mypy src/

# Linting
uv run ruff check src/
```

## Architecture

### Image URL Transformation

The server automatically transforms relative image URLs from Sonarr/Radarr APIs to absolute URLs:

```python
# API returns: "/api/v3/mediacover/123/poster.jpg"
# Server returns: "http://sonarr:8989/api/v3/mediacover/123/poster.jpg"
```

### Retry Logic

Implements exponential backoff for:
- Network errors (connection timeout, DNS failure)
- Server errors (5xx status codes)
- Rate limiting (429 status code)

Does not retry:
- Client errors (4xx except 429)
- Authentication failures (401)

### Error Handling

- **Configuration errors**: Fail fast on startup
- **Network errors**: Retry with backoff, then return error
- **API errors**: Return detailed error messages to client
- **Validation errors**: Check inputs before making requests

## GitHub Actions

This project uses GitHub Actions for continuous integration and deployment:

### PR Checks Workflow

Automatically runs on pull requests and pushes to main/master:
- **Code formatting** - Validates formatting with black
- **Linting** - Checks code quality with ruff
- **Type checking** - Verifies type annotations with mypy
- **Docker build** - Ensures Docker image builds successfully

### Docker Hub Publishing

Automatically builds and publishes Docker images when version tags are pushed:

**Trigger**: Push tags matching `v*.*.*` (e.g., `v1.0.0`, `v1.2.3`)

**Features**:
- Multi-platform builds (linux/amd64, linux/arm64)
- Automatic tagging with semantic versioning
- GitHub Actions cache for faster builds
- **Automatic Docker Hub description updates** from `DOCKER_HUB_README.md`
- **Automatic CHANGELOG.md generation** from git commit history
- Commits changelog back to repository

**Required GitHub Secrets**:
1. `DOCKERHUB_USERNAME` - Your Docker Hub username
2. `DOCKERHUB_TOKEN` - Docker Hub access token (create at [Docker Hub Security Settings](https://hub.docker.com/settings/security))

**Published to**: `${DOCKERHUB_USERNAME}/mcp-raddar`

**What Gets Created**:
- Docker images with tags: `1.0.0`, `1.0`, `latest`
- Updated Docker Hub repository description
- CHANGELOG.md entry with all commits since previous release

**Example release**:
```bash
# Create a version tag
git tag v1.0.0
git push origin v1.0.0

# Wait 5-10 minutes for pipeline to complete
# Then pull the auto-generated changelog
git pull origin master
```

**Setup Guide**: See [CICD_SETUP.md](CICD_SETUP.md) for detailed setup instructions.

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues, questions, or feature requests, please open an issue on GitHub.

## Acknowledgments

- [Sonarr](https://sonarr.tv/) - Smart PVR for newsgroup and bittorrent users
- [Radarr](https://radarr.video/) - Movie collection manager
- [Model Context Protocol](https://modelcontextprotocol.io/) - Open protocol for LLM integrations
- [uv](https://docs.astral.sh/uv/) - Fast Python package manager
