"""Tests for configuration module."""

import pytest

from constitutionbot.config import Settings, get_settings


def test_settings_defaults():
    """Test that settings have sensible defaults."""
    settings = Settings()

    assert settings.dashboard_port == 8000
    assert settings.max_tweet_length == 280
    assert settings.bot_enabled is False
    assert "sqlite" in settings.database_url


def test_get_settings_cached():
    """Test that get_settings returns cached instance."""
    settings1 = get_settings()
    settings2 = get_settings()

    assert settings1 is settings2


def test_settings_paths_created(tmp_path):
    """Test that required directories are created."""
    settings = Settings(
        data_dir=tmp_path / "data",
    )

    assert settings.constitution_uploads_dir.exists()
    assert settings.constitution_processed_dir.exists()
    assert settings.database_dir.exists()
