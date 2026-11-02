"""Application logging configuration tests."""

import logging

import pytest

from paperless_mcp.logging_config import configure_logging


class TestConfigureLogging:
    @pytest.mark.parametrize(
        ("level", "expected_level"),
        [
            ("debug", logging.DEBUG),
            ("INFO", logging.INFO),
            ("warning", logging.WARNING),
        ],
    )
    def test_sets_root_logger_level(self, level: str, expected_level: int) -> None:
        """Set the root logger level for supported values, case-insensitively."""
        root_logger = logging.getLogger()
        previous_level = root_logger.level
        try:
            configure_logging(level)
            assert root_logger.level == expected_level
        finally:
            root_logger.setLevel(previous_level)

    def test_rejects_unsupported_level(self) -> None:
        """Raise an explicit error for invalid logging levels."""
        with pytest.raises(ValueError, match="Unsupported log level"):
            configure_logging("TRACE")
