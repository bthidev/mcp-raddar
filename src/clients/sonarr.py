"""Sonarr API client."""

import logging
from typing import Any, Dict, List, Optional
from .base import BaseArrClient

logger = logging.getLogger(__name__)


class SonarrClient(BaseArrClient):
    """Client for interacting with Sonarr API v3."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: int = 30,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
    ):
        """Initialize Sonarr client."""
        super().__init__(base_url, api_key, timeout, max_retries, backoff_factor)

    def _transform_images(self, item: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Transform relative image URLs to absolute URLs.

        Args:
            item: Series data from API

        Returns:
            List of image dictionaries with absolute URLs
        """
        images = item.get("images", [])
        transformed = []

        for img in images:
            cover_type = img.get("coverType", "unknown")
            url = img.get("url", "")

            # Convert relative URLs to absolute
            if url.startswith("/"):
                absolute_url = f"{self.base_url}{url}"
            else:
                absolute_url = url

            transformed.append({"type": cover_type, "url": absolute_url})

        return transformed

    def search_series(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for TV series by name or TVDB ID.

        Args:
            query: Search term or "tvdb:12345"

        Returns:
            List of series matching the search query

        Example response includes:
            - title
            - year
            - tvdbId
            - overview
            - images (with absolute URLs)
            - status
            - seasons
        """
        logger.info(f"Searching for series: {query}")

        results = self.get("/api/v3/series/lookup", params={"term": query})

        if not isinstance(results, list):
            results = [results] if results else []

        # Transform images to absolute URLs
        for series in results:
            series["images"] = self._transform_images(series)

        return results

    def list_series(self) -> List[Dict[str, Any]]:
        """
        List all series in the Sonarr library.

        Returns:
            List of all series with full details

        Example response includes:
            - title
            - tvdbId
            - monitored
            - seasonFolder
            - path
            - images (with absolute URLs)
            - statistics (episodeCount, sizeOnDisk, etc.)
        """
        logger.info("Fetching all series")

        series_list = self.get("/api/v3/series")

        if not isinstance(series_list, list):
            series_list = []

        # Transform images to absolute URLs
        for series in series_list:
            series["images"] = self._transform_images(series)

        return series_list

    def get_history(self, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """
        Get download and import history.

        Args:
            page: Page number (1-indexed)
            page_size: Number of results per page

        Returns:
            Dictionary with 'records' (list) and pagination info

        Example response includes:
            - records: List of history events
                - eventType (grabbed, downloadFolderImported, etc.)
                - date
                - series (title, tvdbId)
                - episode (title, episodeNumber, seasonNumber)
                - quality
                - sourceTitle
            - page
            - pageSize
            - totalRecords
        """
        logger.info(f"Fetching history: page={page}, page_size={page_size}")

        history = self.get(
            "/api/v3/history",
            params={
                "page": page,
                "pageSize": page_size,
                "sortKey": "date",
                "sortDirection": "descending",
            },
        )

        return (
            history
            if history
            else {"records": [], "page": 1, "pageSize": page_size, "totalRecords": 0}
        )

    def add_series(
        self,
        tvdb_id: int,
        quality_profile_id: int,
        root_folder_path: str,
        monitor: str = "all",
        search_for_missing: bool = True,
        season_folder: bool = True,
        tags: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """
        Add a new TV series to Sonarr.

        Args:
            tvdb_id: TVDB ID of the series
            quality_profile_id: Quality profile ID to use
            root_folder_path: Root folder path where series will be stored
            monitor: Monitoring option ("all", "future", "missing", "existing", "none")
            search_for_missing: Whether to automatically search for missing episodes
            season_folder: Whether to use season folders
            tags: Optional list of tag IDs

        Returns:
            Added series data

        Raises:
            ArrAPIError: If series already exists or other API error occurs
        """
        logger.info(f"Adding series: tvdb_id={tvdb_id}")

        # First, lookup the series to get full details
        lookup_results = self.search_series(f"tvdb:{tvdb_id}")

        if not lookup_results:
            raise ValueError(f"Series with TVDB ID {tvdb_id} not found")

        series_data = lookup_results[0]

        # Prepare the payload for adding
        payload = {
            "tvdbId": tvdb_id,
            "title": series_data.get("title"),
            "qualityProfileId": quality_profile_id,
            "titleSlug": series_data.get("titleSlug"),
            "images": series_data.get("images", []),
            "seasons": series_data.get("seasons", []),
            "rootFolderPath": root_folder_path,
            "monitored": True,
            "seasonFolder": season_folder,
            "addOptions": {
                "monitor": monitor,
                "searchForMissingEpisodes": search_for_missing,
            },
        }

        if tags:
            payload["tags"] = tags

        result = self.post("/api/v3/series", json_data=payload)

        # Transform images in response
        if result and "images" in result:
            result["images"] = self._transform_images(result)

        return result

    def get_quality_profiles(self) -> List[Dict[str, Any]]:
        """
        Get available quality profiles.

        Returns:
            List of quality profiles with id and name
        """
        return self.get("/api/v3/qualityprofile")

    def get_root_folders(self) -> List[Dict[str, Any]]:
        """
        Get configured root folders.

        Returns:
            List of root folders with path and freeSpace
        """
        return self.get("/api/v3/rootfolder")
