"""Configuration module for MCP Raddar server."""

import os
import logging
from typing import Dict
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


class InstanceConfig(BaseModel):
    """Configuration for a single Sonarr/Radarr instance."""

    url: str
    api_key: str

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate and normalize URL."""
        if not v:
            raise ValueError("URL cannot be empty")
        # Remove trailing slash
        return v.rstrip("/")

    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """Validate API key."""
        if not v or len(v) < 10:
            raise ValueError("API key must be at least 10 characters")
        return v


class Config(BaseModel):
    """Main configuration class for MCP Raddar."""

    server_name: str = Field(default="mcp-raddar")
    log_level: str = Field(default="INFO")
    sonarr_instances: Dict[int, InstanceConfig] = Field(default_factory=dict)
    radarr_instances: Dict[int, InstanceConfig] = Field(default_factory=dict)
    request_timeout: int = Field(default=30, ge=1, le=300)
    request_max_retries: int = Field(default=3, ge=0, le=10)
    request_backoff_factor: float = Field(default=0.5, ge=0.1, le=5.0)
    mcp_port: int = Field(default=8000, ge=1, le=65535)
    mcp_hostname: str = Field(default="0.0.0.0")

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"Log level must be one of: {', '.join(valid_levels)}")
        return v_upper


def discover_instances(service_type: str) -> Dict[int, InstanceConfig]:
    """
    Discover instances by scanning environment variables.

    Looks for variables in the format:
    - {SERVICE_TYPE}_URL_1, {SERVICE_TYPE}_API_KEY_1
    - {SERVICE_TYPE}_URL_2, {SERVICE_TYPE}_API_KEY_2
    - etc.

    Args:
        service_type: Either 'SONARR' or 'RADARR'

    Returns:
        Dictionary mapping instance ID to InstanceConfig

    Raises:
        ValueError: If URL is found without matching API key or vice versa
    """
    instances: Dict[int, InstanceConfig] = {}
    prefix = service_type.upper()

    # Scan for numbered instances (1-100 should be more than enough)
    for i in range(1, 101):
        url_key = f"{prefix}_URL_{i}"
        api_key_key = f"{prefix}_API_KEY_{i}"

        url = os.getenv(url_key)
        api_key = os.getenv(api_key_key)

        # If both are found, create instance
        if url and api_key:
            try:
                instances[i] = InstanceConfig(url=url, api_key=api_key)
                logger.info(f"Discovered {service_type.lower()} instance {i}: {url}")
            except Exception as e:
                logger.error(
                    f"Failed to configure {service_type.lower()} instance {i}: {e}"
                )
                raise ValueError(
                    f"Invalid configuration for {service_type.lower()} instance {i}: {e}"
                )
        # If only one is found, that's an error
        elif url or api_key:
            missing = api_key_key if url else url_key
            raise ValueError(
                f"Found {url_key if url else api_key_key} but {missing} is missing. "
                f"Both URL and API key must be provided for {service_type.lower()} instance {i}."
            )
        # If neither found, we've reached the end of instances
        elif i > 1:
            # Stop scanning if we haven't found any instance for this number
            break

    return instances


def load_config() -> Config:
    """
    Load configuration from environment variables.

    Returns:
        Configured Config object

    Raises:
        ValueError: If configuration is invalid or no instances are found
    """
    logger.info("Loading configuration from environment variables...")

    # Discover instances
    sonarr_instances = discover_instances("SONARR")
    radarr_instances = discover_instances("RADARR")

    # Require at least one instance
    if not sonarr_instances and not radarr_instances:
        raise ValueError(
            "No Sonarr or Radarr instances configured. "
            "Please set at least one SONARR_URL_1/SONARR_API_KEY_1 "
            "or RADARR_URL_1/RADARR_API_KEY_1 pair."
        )

    # Build config
    config = Config(
        server_name=os.getenv("MCP_SERVER_NAME", "mcp-raddar"),
        log_level=os.getenv("MCP_LOG_LEVEL", "INFO"),
        sonarr_instances=sonarr_instances,
        radarr_instances=radarr_instances,
        request_timeout=int(os.getenv("REQUEST_TIMEOUT", "30")),
        request_max_retries=int(os.getenv("REQUEST_MAX_RETRIES", "3")),
        request_backoff_factor=float(os.getenv("REQUEST_BACKOFF_FACTOR", "0.5")),
        mcp_port=int(os.getenv("MCP_PORT", "8000")),
        mcp_hostname=os.getenv("MCP_HOSTNAME", "0.0.0.0"),
    )

    logger.info(
        f"Configuration loaded: {len(sonarr_instances)} Sonarr instance(s), "
        f"{len(radarr_instances)} Radarr instance(s)"
    )

    return config


# Configure logging
def setup_logging(config: Config) -> None:
    """Set up logging configuration."""
    logging.basicConfig(
        level=getattr(logging, config.log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
