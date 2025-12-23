"""Logging utilities for MCP server."""

import logging
import time
import json
from functools import wraps
from typing import Any, Callable, TypeVar, ParamSpec

logger = logging.getLogger(__name__)

P = ParamSpec('P')
R = TypeVar('R')


def log_tool_call(func: Callable[P, R]) -> Callable[P, R]:
    """Decorator to log MCP tool calls with parameters, responses, and timing.

    Logs at INFO level:
    - Tool name
    - All parameters
    - Execution time
    - Response data (or error)
    - Success/failure status
    """
    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        tool_name = func.__name__
        start_time = time.time()

        # Log input
        logger.info(f"MCP Tool Call: {tool_name}")
        logger.info(f"  Parameters: {kwargs}")

        try:
            # Execute tool
            result = await func(*args, **kwargs)

            # Log success
            execution_time = time.time() - start_time
            logger.info(f"  Status: SUCCESS")
            logger.info(f"  Execution Time: {execution_time:.3f}s")
            logger.info(f"  Response: {result}")

            return result

        except Exception as e:
            # Log failure
            execution_time = time.time() - start_time
            logger.error(f"  Status: FAILED")
            logger.error(f"  Execution Time: {execution_time:.3f}s")
            logger.error(f"  Error: {type(e).__name__}: {str(e)}")
            raise

    return wrapper


def log_http_call(method: str, url: str, params: dict = None, data: dict = None) -> None:
    """Log HTTP request details at INFO level."""
    logger.info(f"HTTP Request: {method} {url}")
    if params:
        logger.info(f"  Query Params: {params}")
    if data:
        logger.info(f"  Request Body: {data}")


def log_http_response(url: str, status_code: int, response_data: Any, duration: float) -> None:
    """Log HTTP response details at INFO level."""
    logger.info(f"HTTP Response: {url}")
    logger.info(f"  Status Code: {status_code}")
    logger.info(f"  Duration: {duration:.3f}s")
    logger.info(f"  Response Body: {response_data}")
