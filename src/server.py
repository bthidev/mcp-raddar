"""Main MCP server for Sonarr and Radarr integration."""

import logging
import contextlib
from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.routing import Mount
import uvicorn

from .config import load_config, setup_logging
from .tools.sonarr_tools import SonarrTools
from .tools.radarr_tools import RadarrTools

logger = logging.getLogger(__name__)


def _register_sonarr_tools(mcp: FastMCP, sonarr_tools: SonarrTools):
    """Register all Sonarr tools with FastMCP."""

    @mcp.tool()
    async def sonarr_search_series(query: str, instance_id: int = 1) -> str:
        """Search for TV series by name or TVDB ID. Returns title, year, overview, status, and image URLs.

        Args:
            query: Search term or 'tvdb:12345' for TVDB ID
            instance_id: Sonarr instance ID (default: 1)
        """
        return await sonarr_tools.search_series(query, instance_id)

    @mcp.tool()
    async def sonarr_list_series(instance_id: int = 1) -> str:
        """List all TV series in the Sonarr library with monitoring status and statistics.

        Args:
            instance_id: Sonarr instance ID (default: 1)
        """
        return await sonarr_tools.list_series(instance_id)

    @mcp.tool()
    async def sonarr_get_history(instance_id: int = 1, page: int = 1, page_size: int = 20) -> str:
        """Get download and import history from Sonarr with pagination.

        Args:
            instance_id: Sonarr instance ID (default: 1)
            page: Page number (default: 1)
            page_size: Results per page (default: 20)
        """
        return await sonarr_tools.get_history(instance_id, page, page_size)

    @mcp.tool()
    async def sonarr_add_series(
        tvdb_id: int,
        quality_profile_id: int,
        root_folder_path: str,
        instance_id: int = 1,
        monitor: str = "all",
        search_for_missing: bool = True
    ) -> str:
        """Add a new TV series to Sonarr. Requires TVDB ID, quality profile ID, and root folder path.

        Args:
            tvdb_id: TVDB ID of the series
            quality_profile_id: Quality profile ID to use
            root_folder_path: Root folder path for the series
            instance_id: Sonarr instance ID (default: 1)
            monitor: Monitoring option: all, future, missing, existing, none (default: all)
            search_for_missing: Auto-search for missing episodes (default: true)
        """
        return await sonarr_tools.add_series(
            tvdb_id, quality_profile_id, root_folder_path,
            instance_id, monitor, search_for_missing
        )

    @mcp.tool()
    async def sonarr_get_quality_profiles(instance_id: int = 1) -> str:
        """Get available quality profiles from Sonarr. Use this to find quality profile IDs for adding series.

        Args:
            instance_id: Sonarr instance ID (default: 1)
        """
        return await sonarr_tools.get_quality_profiles(instance_id)

    @mcp.tool()
    async def sonarr_get_root_folders(instance_id: int = 1) -> str:
        """Get configured root folders from Sonarr. Use this to find root folder paths for adding series.

        Args:
            instance_id: Sonarr instance ID (default: 1)
        """
        return await sonarr_tools.get_root_folders(instance_id)

    @mcp.tool()
    async def sonarr_get_queue(instance_id: int = 1, page: int = 1, page_size: int = 20) -> str:
        """Get the current download queue from Sonarr with pagination.

        Args:
            instance_id: Sonarr instance ID (default: 1)
            page: Page number (default: 1)
            page_size: Results per page (default: 20)
        """
        return await sonarr_tools.get_queue(instance_id, page, page_size)

    @mcp.tool()
    async def sonarr_get_calendar(instance_id: int = 1, start_date: str = None, end_date: str = None) -> str:
        """Get upcoming episodes from Sonarr calendar.

        Args:
            instance_id: Sonarr instance ID (default: 1)
            start_date: Start date in YYYY-MM-DD format (default: today)
            end_date: End date in YYYY-MM-DD format (default: today + 7 days)
        """
        return await sonarr_tools.get_calendar(instance_id, start_date, end_date)

    @mcp.tool()
    async def sonarr_get_system_status(instance_id: int = 1) -> str:
        """Get Sonarr system status and information.

        Args:
            instance_id: Sonarr instance ID (default: 1)
        """
        return await sonarr_tools.get_system_status(instance_id)


def _register_radarr_tools(mcp: FastMCP, radarr_tools: RadarrTools):
    """Register all Radarr tools with FastMCP."""

    @mcp.tool()
    async def radarr_search_movies(query: str, instance_id: int = 1) -> str:
        """Search for movies by title, TMDB ID, or IMDB ID. Returns title, year, overview, and image URLs.

        Args:
            query: Search term, 'tmdb:12345' for TMDB ID, or 'imdb:tt1234567' for IMDB ID
            instance_id: Radarr instance ID (default: 1)
        """
        return await radarr_tools.search_movies(query, instance_id)

    @mcp.tool()
    async def radarr_list_movies(instance_id: int = 1) -> str:
        """List all movies in the Radarr library with monitoring status and file information.

        Args:
            instance_id: Radarr instance ID (default: 1)
        """
        return await radarr_tools.list_movies(instance_id)

    @mcp.tool()
    async def radarr_get_history(instance_id: int = 1, page: int = 1, page_size: int = 20) -> str:
        """Get download and import history from Radarr with pagination.

        Args:
            instance_id: Radarr instance ID (default: 1)
            page: Page number (default: 1)
            page_size: Results per page (default: 20)
        """
        return await radarr_tools.get_history(instance_id, page, page_size)

    @mcp.tool()
    async def radarr_add_movie(
        tmdb_id: int,
        quality_profile_id: int,
        root_folder_path: str,
        instance_id: int = 1,
        monitor: bool = True,
        search_for_movie: bool = True
    ) -> str:
        """Add a new movie to Radarr. Requires TMDB ID, quality profile ID, and root folder path.

        Args:
            tmdb_id: TMDB ID of the movie
            quality_profile_id: Quality profile ID to use
            root_folder_path: Root folder path for the movie
            instance_id: Radarr instance ID (default: 1)
            monitor: Monitor the movie (default: true)
            search_for_movie: Auto-search for the movie (default: true)
        """
        return await radarr_tools.add_movie(
            tmdb_id, quality_profile_id, root_folder_path,
            instance_id, monitor, search_for_movie
        )

    @mcp.tool()
    async def radarr_get_quality_profiles(instance_id: int = 1) -> str:
        """Get available quality profiles from Radarr. Use this to find quality profile IDs for adding movies.

        Args:
            instance_id: Radarr instance ID (default: 1)
        """
        return await radarr_tools.get_quality_profiles(instance_id)

    @mcp.tool()
    async def radarr_get_root_folders(instance_id: int = 1) -> str:
        """Get configured root folders from Radarr. Use this to find root folder paths for adding movies.

        Args:
            instance_id: Radarr instance ID (default: 1)
        """
        return await radarr_tools.get_root_folders(instance_id)

    @mcp.tool()
    async def radarr_get_queue(instance_id: int = 1, page: int = 1, page_size: int = 20) -> str:
        """Get the current download queue from Radarr with pagination.

        Args:
            instance_id: Radarr instance ID (default: 1)
            page: Page number (default: 1)
            page_size: Results per page (default: 20)
        """
        return await radarr_tools.get_queue(instance_id, page, page_size)

    @mcp.tool()
    async def radarr_get_calendar(instance_id: int = 1, start_date: str = None, end_date: str = None) -> str:
        """Get upcoming movie releases from Radarr calendar.

        Args:
            instance_id: Radarr instance ID (default: 1)
            start_date: Start date in YYYY-MM-DD format (default: today)
            end_date: End date in YYYY-MM-DD format (default: today + 30 days)
        """
        return await radarr_tools.get_calendar(instance_id, start_date, end_date)

    @mcp.tool()
    async def radarr_get_system_status(instance_id: int = 1) -> str:
        """Get Radarr system status and information.

        Args:
            instance_id: Radarr instance ID (default: 1)
        """
        return await radarr_tools.get_system_status(instance_id)


def main():
    """Main entry point for the MCP server."""
    # Load configuration
    try:
        config = load_config()
        setup_logging(config)
        logger.info(f"Starting {config.server_name}...")
    except Exception as e:
        print(f"Failed to load configuration: {e}")
        return

    # Initialize FastMCP server with Streamable HTTP support
    mcp = FastMCP(
        config.server_name,
        json_response=True,    # Return JSON instead of SSE for simple requests
        stateless_http=True    # Enable stateless mode for scalability
    )

    # Initialize tools
    sonarr_tools = SonarrTools(config) if config.sonarr_instances else None
    radarr_tools = RadarrTools(config) if config.radarr_instances else None

    # Register tools with FastMCP
    if sonarr_tools:
        _register_sonarr_tools(mcp, sonarr_tools)
        logger.info(f"Registered {len(config.sonarr_instances)} Sonarr instance(s) with 9 tools each")

    if radarr_tools:
        _register_radarr_tools(mcp, radarr_tools)
        logger.info(f"Registered {len(config.radarr_instances)} Radarr instance(s) with 9 tools each")

    # Get the ASGI app from FastMCP (it handles the /mcp path internally)
    app = mcp.streamable_http_app()

    # Run the server
    logger.info(
        f"MCP server ready. Listening on http://{config.mcp_hostname}:{config.mcp_port}/mcp"
    )
    uvicorn.run(app, host=config.mcp_hostname, port=config.mcp_port)


if __name__ == "__main__":
    main()
