"""Radarr API client."""

import logging
from typing import Any, Dict, List, Optional
from .base import BaseArrClient

logger = logging.getLogger(__name__)


class RadarrClient(BaseArrClient):
    """Client for interacting with Radarr API v3."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: int = 30,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
    ):
        """Initialize Radarr client."""
        super().__init__(base_url, api_key, timeout, max_retries, backoff_factor)

    def _transform_images(self, item: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Transform relative image URLs to absolute URLs.

        Args:
            item: Movie data from API

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

    def search_movies(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for movies by title, TMDB ID, or IMDB ID.

        Args:
            query: Search term, "tmdb:12345", or "imdb:tt1234567"

        Returns:
            List of movies matching the search query

        Example response includes:
            - title
            - year
            - tmdbId
            - imdbId
            - overview
            - images (with absolute URLs)
            - status
            - runtime
        """
        logger.info(f"Searching for movies: {query}")

        results = self.get("/api/v3/movie/lookup", params={"term": query})

        if not isinstance(results, list):
            results = [results] if results else []

        # Transform images to absolute URLs
        for movie in results:
            movie["images"] = self._transform_images(movie)

        return results

    def list_movies(self) -> List[Dict[str, Any]]:
        """
        List all movies in the Radarr library.

        Returns:
            List of all movies with full details

        Example response includes:
            - title
            - tmdbId
            - imdbId
            - monitored
            - path
            - images (with absolute URLs)
            - hasFile
            - sizeOnDisk
            - statistics
        """
        logger.info("Fetching all movies")

        movies_list = self.get("/api/v3/movie")

        if not isinstance(movies_list, list):
            movies_list = []

        # Transform images to absolute URLs
        for movie in movies_list:
            movie["images"] = self._transform_images(movie)

        return movies_list

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
                - movie (title, tmdbId)
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

    def add_movie(
        self,
        tmdb_id: int,
        quality_profile_id: int,
        root_folder_path: str,
        monitor: bool = True,
        search_for_movie: bool = True,
        tags: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """
        Add a new movie to Radarr.

        Args:
            tmdb_id: TMDB ID of the movie
            quality_profile_id: Quality profile ID to use
            root_folder_path: Root folder path where movie will be stored
            monitor: Whether to monitor the movie
            search_for_movie: Whether to automatically search for the movie
            tags: Optional list of tag IDs

        Returns:
            Added movie data

        Raises:
            ArrAPIError: If movie already exists or other API error occurs
        """
        logger.info(f"Adding movie: tmdb_id={tmdb_id}")

        # First, lookup the movie to get full details
        lookup_results = self.search_movies(f"tmdb:{tmdb_id}")

        if not lookup_results:
            raise ValueError(f"Movie with TMDB ID {tmdb_id} not found")

        movie_data = lookup_results[0]

        # Prepare the payload for adding
        payload = {
            "tmdbId": tmdb_id,
            "title": movie_data.get("title"),
            "qualityProfileId": quality_profile_id,
            "titleSlug": movie_data.get("titleSlug"),
            "images": movie_data.get("images", []),
            "year": movie_data.get("year"),
            "rootFolderPath": root_folder_path,
            "monitored": monitor,
            "addOptions": {
                "searchForMovie": search_for_movie,
            },
        }

        if tags:
            payload["tags"] = tags

        result = self.post("/api/v3/movie", json_data=payload)

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
