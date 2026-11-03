"""Configuration tests."""

import pytest

from paperless_mcp.config import Settings


class TestSettings:
    def test_loads_settings_from_environment(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Normalize environment settings and preserve the configured log level."""
        monkeypatch.setenv("PAPERLESS_BASE_URL", "https://paperless.example.com/")
        monkeypatch.setenv("PAPERLESS_API_KEY", "secret-token")
        monkeypatch.setenv("PAPERLESS_LOG_LEVEL", "debug")

        settings = Settings.from_env()

        assert settings.base_url == "https://paperless.example.com"
        assert settings.api_key == "secret-token"
        assert settings.log_level == "DEBUG"

    def test_log_level_defaults_to_info(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Default logging configuration to INFO when unset."""
        monkeypatch.setenv("PAPERLESS_BASE_URL", "http://localhost:8000")
        monkeypatch.setenv("PAPERLESS_API_KEY", "secret-token")
        monkeypatch.delenv("PAPERLESS_LOG_LEVEL", raising=False)

        assert Settings.from_env().log_level == "INFO"

    @pytest.mark.parametrize(
        ("base_url", "api_key", "message"),
        [
            ("", "token", "PAPERLESS_BASE_URL"),
            ("http://localhost:8000", "", "PAPERLESS_API_KEY"),
            ("not-a-url", "token", "absolute HTTP"),
            ("ftp://paperless.example.com", "token", "absolute HTTP"),
            ("http:///missing-host", "token", "absolute HTTP"),
            ("http://localhost:8000", "token", "PAPERLESS_LOG_LEVEL"),
        ],
    )
    def test_rejects_invalid_settings(
        self,
        monkeypatch: pytest.MonkeyPatch,
        base_url: str,
        api_key: str,
        message: str,
    ) -> None:
        """Reject missing credentials, malformed URLs, and unknown log levels."""
        monkeypatch.setenv("PAPERLESS_BASE_URL", base_url)
        monkeypatch.setenv("PAPERLESS_API_KEY", api_key)
        if message == "PAPERLESS_LOG_LEVEL":
            monkeypatch.setenv("PAPERLESS_LOG_LEVEL", "TRACE")

        with pytest.raises(ValueError, match=message):
            Settings.from_env()
