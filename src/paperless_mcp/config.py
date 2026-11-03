"""Environment-based server configuration."""

import logging
import os
from dataclasses import dataclass
from urllib.parse import urlparse

VALID_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}


@dataclass(frozen=True)
class Settings:
    """Runtime configuration for the Paperless MCP server."""

    base_url: str
    api_key: str
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> "Settings":
        """Load and validate settings from the process environment.

        Returns:
            Settings: A validated configuration object for the server.

        Raises:
            ValueError: If a required environment variable is missing or invalid.
        """
        base_url = os.environ.get("PAPERLESS_BASE_URL", "").strip().rstrip("/")
        api_key = os.environ.get("PAPERLESS_API_KEY", "").strip()
        log_level = os.environ.get("PAPERLESS_LOG_LEVEL", "INFO").strip().upper()
        if not base_url:
            raise ValueError("PAPERLESS_BASE_URL must be set")
        if not api_key:
            raise ValueError("PAPERLESS_API_KEY must be set")
        if log_level not in VALID_LOG_LEVELS or not isinstance(
            logging.getLevelName(log_level), int
        ):
            raise ValueError(
                "PAPERLESS_LOG_LEVEL must be one of "
                f"{', '.join(sorted(VALID_LOG_LEVELS))}"
            )

        parsed_url = urlparse(base_url)
        if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
            raise ValueError("PAPERLESS_BASE_URL must be an absolute HTTP(S) URL")
        return cls(base_url=base_url, api_key=api_key, log_level=log_level)
