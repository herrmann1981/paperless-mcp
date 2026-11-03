"""Standard-library logging configuration."""

import logging

LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"


def configure_logging(level: str) -> None:
    """Configure application logging to stderr at the requested level.

    Args:
        level: Logging level name, such as INFO or DEBUG.

    Raises:
        ValueError: If the supplied log level is not a valid standard Python level.
    """
    numeric_level = logging.getLevelName(level.upper())
    if not isinstance(numeric_level, int):
        raise ValueError(f"Unsupported log level: {level}")

    logging.basicConfig(level=numeric_level, format=LOG_FORMAT)
    logging.getLogger().setLevel(numeric_level)
