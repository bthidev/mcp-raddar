"""Main MCP server for Sonarr and Radarr integration."""

import logging
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import Response
import uvicorn

from .config import load_config, setup_logging
from .tools.sonarr_tools import SonarrTools
from .tools.radarr_tools import RadarrTools

logger = logging.getLogger(__name__)


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

    # Initialize MCP server
    server = Server(config.server_name)

    # Initialize tools
    sonarr_tools = SonarrTools(config) if config.sonarr_instances else None
    radarr_tools = RadarrTools(config) if config.radarr_instances else None

    # Helper function to add instance_id to schema if multiple instances
    def _add_instance_param(properties: dict, multiple_instances: bool, service: str):
        """Add instance_id parameter only if multiple instances exist."""
        if multiple_instances:
            properties["instance_id"] = {
                "type": "integer",
                "description": f"{service} instance ID (default: 1)",
                "default": 1,
            }

    # Register list tools handler
    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List all available MCP tools."""
        tools = []

        # Sonarr tools
        if sonarr_tools:
            multiple_sonarr = len(config.sonarr_instances) > 1

            # Search series tool
            search_props = {
                "query": {
                    "type": "string",
                    "description": "Search term or 'tvdb:12345' for TVDB ID",
                },
            }
            _add_instance_param(search_props, multiple_sonarr, "Sonarr")

            tools.append(
                Tool(
                    name="sonarr_search_series",
                    description="Search for TV series by name or TVDB ID. Returns title, year, overview, status, and image URLs.",
                    inputSchema={
                        "type": "object",
                        "properties": search_props,
                        "required": ["query"],
                    },
                )
            )

            # List series tool
            list_props = {}
            _add_instance_param(list_props, multiple_sonarr, "Sonarr")

            tools.append(
                Tool(
                    name="sonarr_list_series",
                    description="List all TV series in the Sonarr library with monitoring status and statistics.",
                    inputSchema={
                        "type": "object",
                        "properties": list_props,
                    },
                )
            )

            # Get history tool
            history_props = {
                "page": {
                    "type": "integer",
                    "description": "Page number (default: 1)",
                    "default": 1,
                },
                "page_size": {
                    "type": "integer",
                    "description": "Results per page (default: 20)",
                    "default": 20,
                },
            }
            _add_instance_param(history_props, multiple_sonarr, "Sonarr")

            tools.append(
                Tool(
                    name="sonarr_get_history",
                    description="Get download and import history from Sonarr with pagination.",
                    inputSchema={
                        "type": "object",
                        "properties": history_props,
                    },
                )
            )

            # Add series tool
            add_props = {
                "tvdb_id": {
                    "type": "integer",
                    "description": "TVDB ID of the series",
                },
                "quality_profile_id": {
                    "type": "integer",
                    "description": "Quality profile ID to use",
                },
                "root_folder_path": {
                    "type": "string",
                    "description": "Root folder path for the series",
                },
                "monitor": {
                    "type": "string",
                    "description": "Monitoring option: all, future, missing, existing, none (default: all)",
                    "default": "all",
                },
                "search_for_missing": {
                    "type": "boolean",
                    "description": "Auto-search for missing episodes (default: true)",
                    "default": True,
                },
            }
            _add_instance_param(add_props, multiple_sonarr, "Sonarr")

            tools.append(
                Tool(
                    name="sonarr_add_series",
                    description="Add a new TV series to Sonarr. Requires TVDB ID, quality profile ID, and root folder path.",
                    inputSchema={
                        "type": "object",
                        "properties": add_props,
                        "required": [
                            "tvdb_id",
                            "quality_profile_id",
                            "root_folder_path",
                        ],
                    },
                )
            )

        # Radarr tools
        if radarr_tools:
            multiple_radarr = len(config.radarr_instances) > 1

            # Search movies tool
            search_movies_props = {
                "query": {
                    "type": "string",
                    "description": "Search term, 'tmdb:12345' for TMDB ID, or 'imdb:tt1234567' for IMDB ID",
                },
            }
            _add_instance_param(search_movies_props, multiple_radarr, "Radarr")

            tools.append(
                Tool(
                    name="radarr_search_movies",
                    description="Search for movies by title, TMDB ID, or IMDB ID. Returns title, year, overview, and image URLs.",
                    inputSchema={
                        "type": "object",
                        "properties": search_movies_props,
                        "required": ["query"],
                    },
                )
            )

            # List movies tool
            list_movies_props = {}
            _add_instance_param(list_movies_props, multiple_radarr, "Radarr")

            tools.append(
                Tool(
                    name="radarr_list_movies",
                    description="List all movies in the Radarr library with monitoring status and file information.",
                    inputSchema={
                        "type": "object",
                        "properties": list_movies_props,
                    },
                )
            )

            # Get history tool
            history_movies_props = {
                "page": {
                    "type": "integer",
                    "description": "Page number (default: 1)",
                    "default": 1,
                },
                "page_size": {
                    "type": "integer",
                    "description": "Results per page (default: 20)",
                    "default": 20,
                },
            }
            _add_instance_param(history_movies_props, multiple_radarr, "Radarr")

            tools.append(
                Tool(
                    name="radarr_get_history",
                    description="Get download and import history from Radarr with pagination.",
                    inputSchema={
                        "type": "object",
                        "properties": history_movies_props,
                    },
                )
            )

            # Add movie tool
            add_movie_props = {
                "tmdb_id": {
                    "type": "integer",
                    "description": "TMDB ID of the movie",
                },
                "quality_profile_id": {
                    "type": "integer",
                    "description": "Quality profile ID to use",
                },
                "root_folder_path": {
                    "type": "string",
                    "description": "Root folder path for the movie",
                },
                "monitor": {
                    "type": "boolean",
                    "description": "Monitor the movie (default: true)",
                    "default": True,
                },
                "search_for_movie": {
                    "type": "boolean",
                    "description": "Auto-search for the movie (default: true)",
                    "default": True,
                },
            }
            _add_instance_param(add_movie_props, multiple_radarr, "Radarr")

            tools.append(
                Tool(
                    name="radarr_add_movie",
                    description="Add a new movie to Radarr. Requires TMDB ID, quality profile ID, and root folder path.",
                    inputSchema={
                        "type": "object",
                        "properties": add_movie_props,
                        "required": [
                            "tmdb_id",
                            "quality_profile_id",
                            "root_folder_path",
                        ],
                    },
                )
            )

        return tools

    # Register call tool handler
    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        """Handle tool calls."""
        try:
            logger.info(f"Calling tool: {name} with arguments: {arguments}")

            result = ""

            # Sonarr tools
            if name == "sonarr_search_series" and sonarr_tools:
                result = await sonarr_tools.search_series(
                    query=arguments["query"],
                    instance_id=arguments.get("instance_id"),
                )
            elif name == "sonarr_list_series" and sonarr_tools:
                result = await sonarr_tools.list_series(
                    instance_id=arguments.get("instance_id")
                )
            elif name == "sonarr_get_history" and sonarr_tools:
                result = await sonarr_tools.get_history(
                    instance_id=arguments.get("instance_id"),
                    page=arguments.get("page", 1),
                    page_size=arguments.get("page_size", 20),
                )
            elif name == "sonarr_add_series" and sonarr_tools:
                result = await sonarr_tools.add_series(
                    tvdb_id=arguments["tvdb_id"],
                    quality_profile_id=arguments["quality_profile_id"],
                    root_folder_path=arguments["root_folder_path"],
                    instance_id=arguments.get("instance_id"),
                    monitor=arguments.get("monitor", "all"),
                    search_for_missing=arguments.get("search_for_missing", True),
                )

            # Radarr tools
            elif name == "radarr_search_movies" and radarr_tools:
                result = await radarr_tools.search_movies(
                    query=arguments["query"],
                    instance_id=arguments.get("instance_id"),
                )
            elif name == "radarr_list_movies" and radarr_tools:
                result = await radarr_tools.list_movies(
                    instance_id=arguments.get("instance_id")
                )
            elif name == "radarr_get_history" and radarr_tools:
                result = await radarr_tools.get_history(
                    instance_id=arguments.get("instance_id"),
                    page=arguments.get("page", 1),
                    page_size=arguments.get("page_size", 20),
                )
            elif name == "radarr_add_movie" and radarr_tools:
                result = await radarr_tools.add_movie(
                    tmdb_id=arguments["tmdb_id"],
                    quality_profile_id=arguments["quality_profile_id"],
                    root_folder_path=arguments["root_folder_path"],
                    instance_id=arguments.get("instance_id"),
                    monitor=arguments.get("monitor", True),
                    search_for_movie=arguments.get("search_for_movie", True),
                )

            else:
                result = f"Unknown tool: {name}"

            return [TextContent(type="text", text=result)]

        except Exception as e:
            logger.error(f"Error calling tool {name}: {e}", exc_info=True)
            error_message = f"Error executing {name}: {str(e)}"
            return [TextContent(type="text", text=error_message)]

    # Create SSE transport
    sse = SseServerTransport("/messages")

    # Create Starlette app with SSE handlers
    async def handle_sse(request):
        async with sse.connect_sse(
            request.scope, request.receive, request._send
        ) as streams:
            await server.run(
                streams[0], streams[1], server.create_initialization_options()
            )
        return Response()

    app = Starlette(
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages", app=sse.handle_post_message),
        ]
    )

    # Run the server
    logger.info(
        f"MCP server ready. Listening on http://{config.mcp_hostname}:{config.mcp_port}"
    )
    uvicorn.run(app, host=config.mcp_hostname, port=config.mcp_port)


if __name__ == "__main__":
    main()
