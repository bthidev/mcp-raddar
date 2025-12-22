"""MCP tools for Sonarr operations."""

import logging
from typing import Dict
from ..config import Config
from ..clients.sonarr import SonarrClient
from ..clients.base import ArrClientError

logger = logging.getLogger(__name__)


class SonarrTools:
    """MCP tools for Sonarr."""

    def __init__(self, config: Config):
        """Initialize Sonarr tools with configuration."""
        self.config = config
        self.clients: Dict[int, SonarrClient] = {}

        # Create clients for all configured instances
        for instance_id, instance_config in config.sonarr_instances.items():
            self.clients[instance_id] = SonarrClient(
                base_url=instance_config.url,
                api_key=instance_config.api_key,
                timeout=config.request_timeout,
                max_retries=config.request_max_retries,
                backoff_factor=config.request_backoff_factor,
            )

    def _get_client(self, instance_id: int | None = None) -> SonarrClient:
        """
        Get Sonarr client for the specified instance.

        Args:
            instance_id: Instance ID (default: first available instance)

        Returns:
            SonarrClient instance

        Raises:
            ValueError: If instance ID is invalid
        """
        # If no instance_id specified, use the first available
        if instance_id is None:
            instance_id = min(self.clients.keys())

        if instance_id not in self.clients:
            available = ", ".join(str(i) for i in sorted(self.clients.keys()))
            raise ValueError(
                f"Sonarr instance {instance_id} not found. "
                f"Available instances: {available}"
            )
        return self.clients[instance_id]

    async def search_series(self, query: str, instance_id: int | None = None) -> str:
        """
        Search for TV series by name or TVDB ID.

        Args:
            query: Search term or tvdb:ID
            instance_id: Sonarr instance ID (default: first available)

        Returns:
            JSON string with search results including image URLs
        """
        try:
            client = self._get_client(instance_id)
            results = client.search_series(query)

            # Format results for better readability
            formatted_results = []
            for series in results:
                formatted_series = {
                    "title": series.get("title"),
                    "year": series.get("year"),
                    "tvdbId": series.get("tvdbId"),
                    "overview": series.get("overview"),
                    "status": series.get("status"),
                    "network": series.get("network"),
                    "images": series.get("images", []),
                    "seasons": len(series.get("seasons", [])),
                }
                formatted_results.append(formatted_series)

            import json

            return json.dumps(formatted_results, indent=2)

        except ArrClientError as e:
            logger.error(f"Sonarr API error: {e}")
            return f"Error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in search_series: {e}")
            return f"Unexpected error: {str(e)}"

    async def list_series(self, instance_id: int | None = None) -> str:
        """
        List all series in the Sonarr library.

        Args:
            instance_id: Sonarr instance ID (default: first available)

        Returns:
            JSON string with all series
        """
        try:
            client = self._get_client(instance_id)
            series_list = client.list_series()

            # Format results
            formatted_results = []
            for series in series_list:
                stats = series.get("statistics", {})
                formatted_series = {
                    "title": series.get("title"),
                    "year": series.get("year"),
                    "tvdbId": series.get("tvdbId"),
                    "monitored": series.get("monitored"),
                    "path": series.get("path"),
                    "images": series.get("images", []),
                    "statistics": {
                        "episodeCount": stats.get("episodeCount", 0),
                        "episodeFileCount": stats.get("episodeFileCount", 0),
                        "percentOfEpisodes": stats.get("percentOfEpisodes", 0),
                        "sizeOnDisk": stats.get("sizeOnDisk", 0),
                    },
                }
                formatted_results.append(formatted_series)

            import json

            return json.dumps(formatted_results, indent=2)

        except ArrClientError as e:
            logger.error(f"Sonarr API error: {e}")
            return f"Error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in list_series: {e}")
            return f"Unexpected error: {str(e)}"

    async def get_history(
        self, instance_id: int | None = None, page: int = 1, page_size: int = 20
    ) -> str:
        """
        Get download and import history.

        Args:
            instance_id: Sonarr instance ID (default: first available)
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
                series_info = record.get("series", {})
                episode_info = record.get("episode", {})
                formatted_record = {
                    "eventType": record.get("eventType"),
                    "date": record.get("date"),
                    "series": series_info.get("title"),
                    "episode": f"S{episode_info.get('seasonNumber', 0):02d}E{episode_info.get('episodeNumber', 0):02d} - {episode_info.get('title', 'Unknown')}",
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
            logger.error(f"Sonarr API error: {e}")
            return f"Error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in get_history: {e}")
            return f"Unexpected error: {str(e)}"

    async def add_series(
        self,
        tvdb_id: int,
        quality_profile_id: int,
        root_folder_path: str,
        instance_id: int | None = None,
        monitor: str = "all",
        search_for_missing: bool = True,
    ) -> str:
        """
        Add a new TV series to Sonarr.

        Args:
            tvdb_id: TVDB ID of the series
            quality_profile_id: Quality profile ID
            root_folder_path: Root folder path
            instance_id: Sonarr instance ID (default: first available)
            monitor: Monitoring option (all, future, missing, existing, none)
            search_for_missing: Auto-search for missing episodes

        Returns:
            JSON string with added series details
        """
        try:
            client = self._get_client(instance_id)
            result = client.add_series(
                tvdb_id=tvdb_id,
                quality_profile_id=quality_profile_id,
                root_folder_path=root_folder_path,
                monitor=monitor,
                search_for_missing=search_for_missing,
            )

            # Format result
            formatted_result = {
                "success": True,
                "title": result.get("title"),
                "tvdbId": result.get("tvdbId"),
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
            logger.error(f"Sonarr API error: {e}")
            return f"Error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in add_series: {e}")
            return f"Unexpected error: {str(e)}"

    async def get_quality_profiles(self, instance_id: int | None = None) -> str:
        """
        Get available quality profiles.

        Args:
            instance_id: Sonarr instance ID (default: first available)

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
            logger.error(f"Sonarr API error: {e}")
            return f"Error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in get_quality_profiles: {e}")
            return f"Unexpected error: {str(e)}"

    async def get_root_folders(self, instance_id: int | None = None) -> str:
        """
        Get configured root folders.

        Args:
            instance_id: Sonarr instance ID (default: first available)

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
            logger.error(f"Sonarr API error: {e}")
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
            instance_id: Sonarr instance ID (default: first available)
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
                series_info = record.get("series", {})
                episode_info = record.get("episode", {})
                formatted_record = {
                    "title": record.get("title"),
                    "status": record.get("status"),
                    "size": record.get("size"),
                    "sizeleft": record.get("sizeleft"),
                    "timeleft": record.get("timeleft"),
                    "estimatedCompletionTime": record.get("estimatedCompletionTime"),
                    "protocol": record.get("protocol"),
                    "downloadClient": record.get("downloadClient"),
                    "series": series_info.get("title"),
                    "episode": f"S{episode_info.get('seasonNumber', 0):02d}E{episode_info.get('episodeNumber', 0):02d} - {episode_info.get('title', 'Unknown')}",
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
            logger.error(f"Sonarr API error: {e}")
            return f"Error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in get_queue: {e}")
            return f"Unexpected error: {str(e)}"

    async def get_calendar(
        self, instance_id: int | None = None, start_date: str | None = None, end_date: str | None = None
    ) -> str:
        """
        Get upcoming episodes from the calendar.

        Args:
            instance_id: Sonarr instance ID (default: first available)
            start_date: Start date in YYYY-MM-DD format (default: today)
            end_date: End date in YYYY-MM-DD format (default: today + 7 days)

        Returns:
            JSON string with upcoming episodes
        """
        try:
            client = self._get_client(instance_id)
            calendar = client.get_calendar(start_date=start_date, end_date=end_date)

            # Format results
            formatted_episodes = []
            for episode in calendar:
                series_info = episode.get("series", {})
                formatted_episode = {
                    "title": episode.get("title"),
                    "episodeNumber": episode.get("episodeNumber"),
                    "seasonNumber": episode.get("seasonNumber"),
                    "airDate": episode.get("airDate"),
                    "airDateUtc": episode.get("airDateUtc"),
                    "series": series_info.get("title"),
                    "hasFile": episode.get("hasFile"),
                    "monitored": episode.get("monitored"),
                }
                formatted_episodes.append(formatted_episode)

            import json
            return json.dumps(formatted_episodes, indent=2)

        except ArrClientError as e:
            logger.error(f"Sonarr API error: {e}")
            return f"Error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in get_calendar: {e}")
            return f"Unexpected error: {str(e)}"

    async def get_system_status(self, instance_id: int | None = None) -> str:
        """
        Get system status and information.

        Args:
            instance_id: Sonarr instance ID (default: first available)

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
            logger.error(f"Sonarr API error: {e}")
            return f"Error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in get_system_status: {e}")
            return f"Unexpected error: {str(e)}"
