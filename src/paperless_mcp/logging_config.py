"""Standard-library logging configuration."""

import logging

LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"


def configure_logging(level: str) -> None:
    """Configure application logging to stderr at the requested level."""
    numeric_level = logging.getLevelName(level.upper())
    if not isinstance(numeric_level, int):
        raise ValueError(f"Unsupported log level: {level}")

    logging.basicConfig(level=numeric_level, format=LOG_FORMAT)
    logging.getLogger().setLevel(numeric_level)
