"""MCP tools for Radarr operations."""

import logging
from typing import Dict
from ..config import Config
from ..clients.radarr import RadarrClient
from ..clients.base import ArrClientError

logger = logging.getLogger(__name__)


class RadarrTools:
    """MCP tools for Radarr."""

    def __init__(self, config: Config):
        """Initialize Radarr tools with configuration."""
        self.config = config
        self.clients: Dict[int, RadarrClient] = {}

        # Create clients for all configured instances
        for instance_id, instance_config in config.radarr_instances.items():
            self.clients[instance_id] = RadarrClient(
                base_url=instance_config.url,
                api_key=instance_config.api_key,
                timeout=config.request_timeout,
                max_retries=config.request_max_retries,
                backoff_factor=config.request_backoff_factor,
            )

    def _get_client(self, instance_id: int | None = None) -> RadarrClient:
        """
        Get Radarr client for the specified instance.

        Args:
            instance_id: Instance ID (default: first available instance)

        Returns:
            RadarrClient instance

        Raises:
            ValueError: If instance ID is invalid
        """
        # If no instance_id specified, use the first available
        if instance_id is None:
            instance_id = min(self.clients.keys())

        if instance_id not in self.clients:
            available = ", ".join(str(i) for i in sorted(self.clients.keys()))
            raise ValueError(
                f"Radarr instance {instance_id} not found. "
                f"Available instances: {available}"
            )
        return self.clients[instance_id]

    async def search_movies(self, query: str, instance_id: int | None = None) -> str:
        """
        Search for movies by title, TMDB ID, or IMDB ID.

        Args:
            query: Search term, tmdb:ID, or imdb:ID
            instance_id: Radarr instance ID (default: first available)

        Returns:
            JSON string with search results including image URLs
        """
        try:
            client = self._get_client(instance_id)
            results = client.search_movies(query)

            # Format results for better readability
            formatted_results = []
            for movie in results:
                formatted_movie = {
                    "title": movie.get("title"),
                    "year": movie.get("year"),
                    "tmdbId": movie.get("tmdbId"),
                    "imdbId": movie.get("imdbId"),
                    "overview": movie.get("overview"),
                    "status": movie.get("status"),
                    "runtime": movie.get("runtime"),
                    "studio": movie.get("studio"),
                    "images": movie.get("images", []),
                }
                formatted_results.append(formatted_movie)

            import json

            return json.dumps(formatted_results, indent=2)

        except ArrClientError as e:
            logger.error(f"Radarr API error: {e}")
            return f"Error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in search_movies: {e}")
            return f"Unexpected error: {str(e)}"

    async def list_movies(self, instance_id: int | None = None) -> str:
        """
        List all movies in the Radarr library.

        Args:
            instance_id: Radarr instance ID (default: first available)

        Returns:
            JSON string with all movies
        """
        try:
            client = self._get_client(instance_id)
            movies_list = client.list_movies()

            # Format results
            formatted_results = []
            for movie in movies_list:
                formatted_movie = {
                    "title": movie.get("title"),
                    "year": movie.get("year"),
                    "tmdbId": movie.get("tmdbId"),
                    "imdbId": movie.get("imdbId"),
                    "monitored": movie.get("monitored"),
                    "hasFile": movie.get("hasFile"),
                    "path": movie.get("path"),
                    "images": movie.get("images", []),
                    "sizeOnDisk": movie.get("sizeOnDisk", 0),
                }
                formatted_results.append(formatted_movie)

            import json

            return json.dumps(formatted_results, indent=2)

        except ArrClientError as e:
            logger.error(f"Radarr API error: {e}")
            return f"Error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in list_movies: {e}")
            return f"Unexpected error: {str(e)}"

    async def get_history(
        self, instance_id: int | None = None, page: int = 1, page_size: int = 20
    ) -> str:
        """
        Get download and import history.

        Args:
            instance_id: Radarr instance ID (default: first available)
            page: Page number (default: 1)
            page_size: Results per page (default: 20)

        Returns:
            JSON string with history records
        """
        try:
            client = self._get_client(instance_id)
            history = client.get_history(page=page, page_size=page_size)

            # Format results
            records = history.get("records", [])
            formatted_records = []
            for record in records:
                movie_info = record.get("movie", {})
                formatted_record = {
                    "eventType": record.get("eventType"),
                    "date": record.get("date"),
                    "movie": movie_info.get("title"),
                    "quality": record.get("quality", {}).get("quality", {}).get("name"),
                    "sourceTitle": record.get("sourceTitle"),
                }
                formatted_records.append(formatted_record)

            result = {
                "records": formatted_records,
                "page": history.get("page", 1),
                "pageSize": history.get("pageSize", page_size),
                "totalRecords": history.get("totalRecords", 0),
            }

            import json

            return json.dumps(result, indent=2)

        except ArrClientError as e:
            logger.error(f"Radarr API error: {e}")
            return f"Error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in get_history: {e}")
            return f"Unexpected error: {str(e)}"

    async def add_movie(
        self,
        tmdb_id: int,
        quality_profile_id: int,
        root_folder_path: str,
        instance_id: int | None = None,
        monitor: bool = True,
        search_for_movie: bool = True,
    ) -> str:
        """
        Add a new movie to Radarr.

        Args:
            tmdb_id: TMDB ID of the movie
            quality_profile_id: Quality profile ID
            root_folder_path: Root folder path
            instance_id: Radarr instance ID (default: first available)
            monitor: Monitor the movie
            search_for_movie: Auto-search for the movie

        Returns:
            JSON string with added movie details
        """
        try:
            client = self._get_client(instance_id)
            result = client.add_movie(
                tmdb_id=tmdb_id,
                quality_profile_id=quality_profile_id,
                root_folder_path=root_folder_path,
                monitor=monitor,
                search_for_movie=search_for_movie,
            )

            # Format result
            formatted_result = {
                "success": True,
                "title": result.get("title"),
                "year": result.get("year"),
                "tmdbId": result.get("tmdbId"),
                "path": result.get("path"),
                "monitored": result.get("monitored"),
                "images": result.get("images", []),
            }

            import json

            return json.dumps(formatted_result, indent=2)

        except ValueError as e:
            logger.error(f"Validation error: {e}")
            return f"Validation error: {str(e)}"
        except ArrClientError as e:
            logger.error(f"Radarr API error: {e}")
            return f"Error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in add_movie: {e}")
            return f"Unexpected error: {str(e)}"

    async def get_quality_profiles(self, instance_id: int | None = None) -> str:
        """
        Get available quality profiles.

        Args:
            instance_id: Radarr instance ID (default: first available)

        Returns:
            JSON string with quality profiles
        """
        try:
            client = self._get_client(instance_id)
            profiles = client.get_quality_profiles()

            # Format results
            formatted_profiles = []
            for profile in profiles:
                cutoff = profile.get("cutoff")
                cutoff_name = cutoff.get("name") if isinstance(cutoff, dict) else cutoff
                formatted_profiles.append({
                    "id": profile.get("id"),
                    "name": profile.get("name"),
                    "upgradeAllowed": profile.get("upgradeAllowed"),
                    "cutoff": cutoff_name,
                })

            import json
            return json.dumps(formatted_profiles, indent=2)

        except ArrClientError as e:
            logger.error(f"Radarr API error: {e}")
            return f"Error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in get_quality_profiles: {e}")
            return f"Unexpected error: {str(e)}"

    async def get_root_folders(self, instance_id: int | None = None) -> str:
        """
        Get configured root folders.

        Args:
            instance_id: Radarr instance ID (default: first available)

        Returns:
            JSON string with root folders
        """
        try:
            client = self._get_client(instance_id)
            folders = client.get_root_folders()

            # Format results
            formatted_folders = []
            for folder in folders:
                formatted_folders.append({
                    "id": folder.get("id"),
                    "path": folder.get("path"),
                    "accessible": folder.get("accessible"),
                    "freeSpace": folder.get("freeSpace"),
                    "totalSpace": folder.get("totalSpace"),
                })

            import json
            return json.dumps(formatted_folders, indent=2)

        except ArrClientError as e:
            logger.error(f"Radarr API error: {e}")
            return f"Error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in get_root_folders: {e}")
            return f"Unexpected error: {str(e)}"

    async def get_queue(
        self, instance_id: int | None = None, page: int = 1, page_size: int = 20
    ) -> str:
        """
        Get the download queue.

        Args:
            instance_id: Radarr instance ID (default: first available)
            page: Page number (default: 1)
            page_size: Results per page (default: 20)

        Returns:
            JSON string with queue items
        """
        try:
            client = self._get_client(instance_id)
            queue = client.get_queue(page=page, page_size=page_size)

            # Format results
            records = queue.get("records", [])
            formatted_records = []
            for record in records:
                movie_info = record.get("movie", {})
                formatted_record = {
                    "title": record.get("title"),
                    "status": record.get("status"),
                    "size": record.get("size"),
                    "sizeleft": record.get("sizeleft"),
                    "timeleft": record.get("timeleft"),
                    "estimatedCompletionTime": record.get("estimatedCompletionTime"),
                    "protocol": record.get("protocol"),
                    "downloadClient": record.get("downloadClient"),
                    "movie": movie_info.get("title"),
                }
                formatted_records.append(formatted_record)

            result = {
                "records": formatted_records,
                "page": queue.get("page", 1),
                "pageSize": queue.get("pageSize", page_size),
                "totalRecords": queue.get("totalRecords", 0),
            }

            import json
            return json.dumps(result, indent=2)

        except ArrClientError as e:
            logger.error(f"Radarr API error: {e}")
            return f"Error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in get_queue: {e}")
            return f"Unexpected error: {str(e)}"

    async def get_calendar(
        self, instance_id: int | None = None, start_date: str | None = None, end_date: str | None = None
    ) -> str:
        """
        Get upcoming movie releases from the calendar.

        Args:
            instance_id: Radarr instance ID (default: first available)
            start_date: Start date in YYYY-MM-DD format (default: today)
            end_date: End date in YYYY-MM-DD format (default: today + 30 days)

        Returns:
            JSON string with upcoming movie releases
        """
        try:
            client = self._get_client(instance_id)
            calendar = client.get_calendar(start_date=start_date, end_date=end_date)

            # Format results
            formatted_movies = []
            for movie in calendar:
                formatted_movie = {
                    "title": movie.get("title"),
                    "year": movie.get("year"),
                    "physicalRelease": movie.get("physicalRelease"),
                    "digitalRelease": movie.get("digitalRelease"),
                    "inCinemas": movie.get("inCinemas"),
                    "tmdbId": movie.get("tmdbId"),
                    "hasFile": movie.get("hasFile"),
                    "monitored": movie.get("monitored"),
                }
                formatted_movies.append(formatted_movie)

            import json
            return json.dumps(formatted_movies, indent=2)

        except ArrClientError as e:
            logger.error(f"Radarr API error: {e}")
            return f"Error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in get_calendar: {e}")
            return f"Unexpected error: {str(e)}"

    async def get_system_status(self, instance_id: int | None = None) -> str:
        """
        Get system status and information.

        Args:
            instance_id: Radarr instance ID (default: first available)

        Returns:
            JSON string with system information
        """
        try:
            client = self._get_client(instance_id)
            status = client.get_system_status()

            # Format key information
            formatted_status = {
                "version": status.get("version"),
                "buildTime": status.get("buildTime"),
                "osName": status.get("osName"),
                "osVersion": status.get("osVersion"),
                "isLinux": status.get("isLinux"),
                "isOsx": status.get("isOsx"),
                "isWindows": status.get("isWindows"),
                "branch": status.get("branch"),
                "authentication": status.get("authentication"),
                "startupPath": status.get("startupPath"),
                "appData": status.get("appData"),
            }

            import json
            return json.dumps(formatted_status, indent=2)

        except ArrClientError as e:
            logger.error(f"Radarr API error: {e}")
            return f"Error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in get_system_status: {e}")
            return f"Unexpected error: {str(e)}"
