import os
import sys
import logging
import requests
from typing import Callable, TypeVar, Any, Union
from functools import wraps
from pydantic import ValidationError
from pathlib import Path

# Type variable for generic function signatures
F = TypeVar("F", bound=Callable[..., Any])


# Utility: get base_dir and resolve_path
def find_project_root(start_path: str) -> str:
    """Finds the project root, accommodating both development and bundled app structures."""
    if getattr(sys, "frozen", False):
        return str(Path(sys.executable).parent)

    current = Path(start_path).resolve()
    for parent in current.parents:
        if (parent / "pyproject.toml").is_file():
            return str(parent)
    return str(Path.cwd())


base_dir = find_project_root(__file__)


def resolve_path(path: str) -> str:
    """Resolves relative paths to absolute paths relative to the project root."""
    p = Path(path)
    return str(p) if p.is_absolute() else str(Path(base_dir) / p)


# Terminal colors
class Colors:
    # Simplified to fewer colors for maintainability.
    GREEN = "\033[92m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    END = "\033[0m"


# Pretty logging with more emojis and life!
class PrettyFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        msg = record.getMessage()
        # Improved logic for color application.
        if record.levelname == "INFO":
            if any(
                s in msg for s in ["✅", "✓", "Successfully", "🎉", "🏆", "completed"]
            ):
                return f"{Colors.GREEN}{msg}{Colors.END}"
            if any(s in msg for s in ["❌", "✗", "Failed", "Error"]):
                return f"{Colors.RED}{msg}{Colors.END}"
            return f"{Colors.BLUE}{msg}{Colors.END}"
        if record.levelname == "ERROR":
            return f"{Colors.RED}{Colors.BOLD}{msg}{Colors.END}"
        if record.levelname == "WARNING":
            return f"{Colors.RED}{msg}{Colors.END}"  # Changed to red for warnings for better visibility
        return msg


# Configure logger
logger = logging.getLogger(__name__)
log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
log_level = getattr(logging, log_level_str, logging.INFO)
logger.setLevel(log_level)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(PrettyFormatter())
logger.addHandler(handler)
logger.propagate = False


class IQServerError(Exception):
    """Custom exception for IQ Server related errors."""

    pass


class ErrorHandler:
    """Centralized error handling with different strategies."""

    @staticmethod
    def handle_config_error(func: F) -> F:
        """Handles configuration-related errors."""

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except (ValidationError, FileNotFoundError, Exception) as e:
                # Consolidated error handling for config errors
                error_msg = (
                    "Configuration validation failed"
                    if isinstance(e, ValidationError)
                    else "Configuration file not found"
                    if isinstance(e, FileNotFoundError)
                    else "Unexpected configuration error"
                )
                logger.error(f"{error_msg}: {e}")
                sys.exit(1)

        return wrapper  # type: ignore[return-value]

    @staticmethod
    def handle_api_error(func: F) -> F:
        """Handles API-related errors with retry logic."""

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Union[Any, None]:
            try:
                return func(*args, **kwargs)
            except requests.exceptions.ConnectionError:
                logger.error("Failed to connect to IQ Server. Check URL and network.")
            except requests.exceptions.Timeout:
                logger.warning("Request timeout. Server may be slow.")
            except requests.exceptions.HTTPError as e:
                if e.response:
                    status_code = e.response.status_code
                    if status_code == 401:
                        logger.error("Authentication failed. Check credentials.")
                    elif status_code == 403:
                        logger.error("Access forbidden. Check permissions.")
                    elif status_code == 404:
                        logger.warning(f"Resource not found: {e}")
                    else:
                        logger.error(f"HTTP error {status_code}: {e}")
                else:
                    logger.error(f"HTTP error: {e}")
            except Exception as e:
                logger.error(f"Unexpected API error: {e}")
            return None  # Always return None on API error

        return wrapper  # type: ignore[return-value]

    @staticmethod
    def handle_file_error(func: F) -> F:
        """Handles file operation errors."""

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Union[Any, bool]:
            try:
                return func(*args, **kwargs)
            except (PermissionError, OSError, Exception) as e:
                # Consolidated error handling for file errors
                error_msg = (
                    "Permission denied"
                    if isinstance(e, PermissionError)
                    else "File system error"
                    if isinstance(e, OSError)
                    else "Unexpected file error"
                )
                logger.error(f"{error_msg}: {e}")
                return False

        return wrapper  # type: ignore[return-value]
