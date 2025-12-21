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

    def _get_client(self, instance_id: int = 1) -> SonarrClient:
        """
        Get Sonarr client for the specified instance.

        Args:
            instance_id: Instance ID (default: 1)

        Returns:
            SonarrClient instance

        Raises:
            ValueError: If instance ID is invalid
        """
        if instance_id not in self.clients:
            available = ", ".join(str(i) for i in sorted(self.clients.keys()))
            raise ValueError(
                f"Sonarr instance {instance_id} not found. "
                f"Available instances: {available}"
            )
        return self.clients[instance_id]

    async def search_series(self, query: str, instance_id: int = 1) -> str:
        """
        Search for TV series by name or TVDB ID.

        Args:
            query: Search term or tvdb:ID
            instance_id: Sonarr instance ID (default: 1)

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

    async def list_series(self, instance_id: int = 1) -> str:
        """
        List all series in the Sonarr library.

        Args:
            instance_id: Sonarr instance ID (default: 1)

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
        self, instance_id: int = 1, page: int = 1, page_size: int = 20
    ) -> str:
        """
        Get download and import history.

        Args:
            instance_id: Sonarr instance ID (default: 1)
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
        instance_id: int = 1,
        monitor: str = "all",
        search_for_missing: bool = True,
    ) -> str:
        """
        Add a new TV series to Sonarr.

        Args:
            tvdb_id: TVDB ID of the series
            quality_profile_id: Quality profile ID
            root_folder_path: Root folder path
            instance_id: Sonarr instance ID (default: 1)
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
