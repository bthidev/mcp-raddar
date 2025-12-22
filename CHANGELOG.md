# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **10 New MCP Tools** for enhanced data extraction (5 Sonarr + 5 Radarr)
  - `sonarr_get_quality_profiles` - Get available quality profiles
  - `sonarr_get_root_folders` - Get configured root folders
  - `sonarr_get_queue` - Monitor current downloads with pagination
  - `sonarr_get_calendar` - Get upcoming episodes (customizable date range)
  - `sonarr_get_system_status` - Get system information and health
  - `radarr_get_quality_profiles` - Get available quality profiles
  - `radarr_get_root_folders` - Get configured root folders
  - `radarr_get_queue` - Monitor current downloads with pagination
  - `radarr_get_calendar` - Get upcoming movie releases (customizable date range)
  - `radarr_get_system_status` - Get system information and health
- Docker Hub README with comprehensive documentation
- GitHub Actions workflow for automatic Docker Hub description updates
- Automatic CHANGELOG.md generation on version releases
- Documentation files:
  - `DOCKER_HUB_README.md` - Docker Hub repository description
  - `NEW_TOOLS.md` - Detailed documentation of new tools
  - `INSTANCE_ID_CHANGES.md` - Documentation of instance_id parameter improvements

### Changed
- **Breaking**: Fixed SSE endpoint handlers to use raw ASGI signatures
  - Changed from `async def handle_sse(request)` to `async def handle_sse(scope, receive, send)`
  - Added `Response()` return to SSE handler to prevent TypeError
  - Changed `/messages` endpoint from `Route` to `Mount` for proper ASGI app handling
- **Improved**: Instance ID parameter is now automatically hidden when only one instance is configured
  - Tools only show `instance_id` parameter when multiple instances exist
  - Single-instance setups get cleaner, simpler tool schemas
  - `_get_client()` methods now accept `None` and automatically select first available instance
- **Enhanced**: Docker build workflow now supports multiple platforms (linux/amd64, linux/arm64)
- **Enhanced**: Docker tagging strategy includes:
  - Semantic versioning tags (e.g., `1.0.0`)
  - Major.minor tags (e.g., `1.0`)
  - `latest` tag for default branch

### Fixed
- SSE endpoint returning `None` instead of proper response (TypeError: 'NoneType' object is not callable)
- `/messages` endpoint 307 redirect issue by using `Mount` instead of `Route`
- Instance ID parameter handling - now properly passes `None` when not provided

### Technical
- Added client methods to `SonarrClient` and `RadarrClient`:
  - `get_queue()` - Fetch download queue with pagination
  - `get_calendar()` - Fetch upcoming releases with date filtering
  - `get_system_status()` - Fetch system information
- Added wrapper methods to `SonarrTools` and `RadarrTools` for all new endpoints
- Updated server tool registration with dynamic schema generation
- Added tool call handlers for all 10 new tools
- Enhanced GitHub Actions pipeline with:
  - Docker Hub description sync using `peter-evans/dockerhub-description@v4`
  - Automatic changelog generation from git history
  - Multi-platform Docker builds

## [Initial Release]

### Added
- MCP server for Sonarr and Radarr integration
- HTTP/SSE transport for n8n and web client compatibility
- **8 Initial MCP Tools**:
  - `sonarr_search_series` - Search for TV series by name or TVDB ID
  - `sonarr_list_series` - List all series in library
  - `sonarr_get_history` - Get download/import history
  - `sonarr_add_series` - Add new series to library
  - `radarr_search_movies` - Search for movies by title, TMDB or IMDB ID
  - `radarr_list_movies` - List all movies in library
  - `radarr_get_history` - Get download/import history
  - `radarr_add_movie` - Add new movie to library
- Multi-instance support for Sonarr and Radarr
- Image URL transformation (relative to absolute URLs)
- Retry logic with exponential backoff
- Pydantic-based configuration validation
- Docker containerization with uv package manager
- Environment variable based configuration
- Comprehensive error handling and logging

### Features
- Built with Python 3.14+ and uv package manager
- Starlette web framework with Uvicorn ASGI server
- MCP SDK integration for tool registration and handling
- Configurable request timeouts and retry behavior
- Support for numbered instance configuration (e.g., SONARR_URL_1, SONARR_URL_2)
- Fail-fast configuration validation

[Unreleased]: https://github.com/YOUR_USERNAME/mcp-raddar/compare/v1.0.0...HEAD
[Initial Release]: https://github.com/YOUR_USERNAME/mcp-raddar/releases/tag/v1.0.0
