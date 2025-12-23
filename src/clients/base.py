"""Base HTTP client for Sonarr/Radarr API communication."""

import logging
import time
from typing import Any, Dict, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ..logging_utils import log_http_call, log_http_response

logger = logging.getLogger(__name__)


class ArrClientError(Exception):
    """Base exception for Arr client errors."""

    pass


class ArrConfigurationError(ArrClientError):
    """Configuration-related errors."""

    pass


class ArrNetworkError(ArrClientError):
    """Network-related errors."""

    pass


class ArrAPIError(ArrClientError):
    """API-related errors."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class BaseArrClient:
    """Base client for Sonarr/Radarr API communication with retry logic."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: int = 30,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
    ):
        """
        Initialize the base client.

        Args:
            base_url: Base URL of the Sonarr/Radarr instance
            api_key: API key for authentication
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
            backoff_factor: Backoff factor for retry delays
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.session = self._create_session(max_retries, backoff_factor)

    def _create_session(
        self, max_retries: int, backoff_factor: float
    ) -> requests.Session:
        """
        Create a requests session with retry logic.

        Args:
            max_retries: Maximum number of retries
            backoff_factor: Backoff factor for retry delays

        Returns:
            Configured requests session
        """
        session = requests.Session()

        # Configure retry strategy
        # Retry on network errors and 5xx server errors, but not on 4xx client errors
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE", "OPTIONS"],
            raise_on_status=False,  # We'll handle status codes manually
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Set default headers
        session.headers.update(
            {
                "X-Api-Key": self.api_key,
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

        return session

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Make an HTTP request to the API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (will be appended to base_url)
            params: Query parameters
            json_data: JSON body data

        Returns:
            Response data (parsed JSON)

        Raises:
            ArrNetworkError: If network error occurs
            ArrAPIError: If API returns an error response
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        # Log HTTP request at INFO level
        log_http_call(method, url, params=params, data=json_data)

        # Track request timing
        start_time = time.time()

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                timeout=self.timeout,
            )

            # Handle different status codes
            if response.status_code == 401:
                raise ArrAPIError(
                    "Authentication failed. Please check your API key.",
                    status_code=401,
                )
            elif response.status_code == 404:
                raise ArrAPIError(
                    f"Resource not found: {endpoint}",
                    status_code=404,
                )
            elif response.status_code == 400:
                error_msg = "Bad request"
                try:
                    error_data = response.json()
                    if isinstance(error_data, list) and error_data:
                        error_msg = error_data[0].get("errorMessage", error_msg)
                    elif isinstance(error_data, dict):
                        error_msg = error_data.get("message", error_msg)
                except Exception:
                    pass
                raise ArrAPIError(error_msg, status_code=400)
            elif response.status_code >= 500:
                raise ArrAPIError(
                    f"Server error: {response.status_code} - {response.text[:100]}",
                    status_code=response.status_code,
                )
            elif not response.ok:
                raise ArrAPIError(
                    f"API request failed: {response.status_code} - {response.text[:100]}",
                    status_code=response.status_code,
                )

            # Parse JSON response
            response_data = response.json() if response.text else None

            # Calculate duration and log HTTP response at INFO level
            duration = time.time() - start_time
            log_http_response(url, response.status_code, response_data, duration)

            return response_data

        except requests.exceptions.Timeout as e:
            logger.error(f"Request timeout: {url}")
            raise ArrNetworkError(f"Request timeout: {url}") from e
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {url}")
            raise ArrNetworkError(f"Failed to connect to {self.base_url}") from e
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise ArrNetworkError(f"Request failed: {str(e)}") from e

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Make a GET request."""
        return self._make_request("GET", endpoint, params=params)

    def post(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make a POST request."""
        return self._make_request("POST", endpoint, params=params, json_data=json_data)

    def put(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make a PUT request."""
        return self._make_request("PUT", endpoint, params=params, json_data=json_data)

    def delete(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Make a DELETE request."""
        return self._make_request("DELETE", endpoint, params=params)
