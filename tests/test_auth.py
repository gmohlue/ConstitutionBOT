"""Tests for authentication module."""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from contentmanager.dashboard.auth import AuthManager


class TestAuthManager:
    """Tests for AuthManager class."""

    def test_verify_credentials_valid(self):
        """Test that valid credentials pass verification."""
        with patch("contentmanager.dashboard.auth.get_settings") as mock_settings:
            mock_settings.return_value.dashboard_username = "testuser"
            mock_settings.return_value.dashboard_password.get_secret_value.return_value = "testpass"

            auth = AuthManager()
            assert auth.verify_credentials("testuser", "testpass") is True

    def test_verify_credentials_invalid_username(self):
        """Test that invalid username fails verification."""
        with patch("contentmanager.dashboard.auth.get_settings") as mock_settings:
            mock_settings.return_value.dashboard_username = "testuser"
            mock_settings.return_value.dashboard_password.get_secret_value.return_value = "testpass"

            auth = AuthManager()
            assert auth.verify_credentials("wronguser", "testpass") is False

    def test_verify_credentials_invalid_password(self):
        """Test that invalid password fails verification."""
        with patch("contentmanager.dashboard.auth.get_settings") as mock_settings:
            mock_settings.return_value.dashboard_username = "testuser"
            mock_settings.return_value.dashboard_password.get_secret_value.return_value = "testpass"

            auth = AuthManager()
            assert auth.verify_credentials("testuser", "wrongpass") is False

    def test_verify_credentials_both_invalid(self):
        """Test that both invalid username and password fails verification."""
        with patch("contentmanager.dashboard.auth.get_settings") as mock_settings:
            mock_settings.return_value.dashboard_username = "testuser"
            mock_settings.return_value.dashboard_password.get_secret_value.return_value = "testpass"

            auth = AuthManager()
            assert auth.verify_credentials("wronguser", "wrongpass") is False

    @pytest.mark.asyncio
    async def test_create_session_returns_token(self):
        """Test that create_session returns a valid token."""
        with patch("contentmanager.dashboard.auth.get_settings") as mock_settings:
            mock_settings.return_value.dashboard_username = "testuser"
            mock_settings.return_value.dashboard_password.get_secret_value.return_value = "testpass"

            auth = AuthManager()

            # Mock the database session and repository
            mock_db_session = AsyncMock()
            mock_repo = MagicMock()
            mock_repo.create = AsyncMock()
            mock_repo.delete_expired = AsyncMock()

            with patch("contentmanager.dashboard.auth.SessionRepository", return_value=mock_repo):
                token = await auth.create_session(mock_db_session)

                assert token is not None
                assert len(token) > 20  # Token should be reasonably long
                mock_repo.create.assert_called_once()
                mock_repo.delete_expired.assert_called_once()

    @pytest.mark.asyncio
    async def test_verify_session_valid(self):
        """Test that valid session returns True."""
        with patch("contentmanager.dashboard.auth.get_settings") as mock_settings:
            auth = AuthManager()

            mock_db_session = AsyncMock()
            mock_repo = MagicMock()
            mock_repo.is_valid = AsyncMock(return_value=True)

            with patch("contentmanager.dashboard.auth.SessionRepository", return_value=mock_repo):
                result = await auth.verify_session(mock_db_session, "valid_token")
                assert result is True

    @pytest.mark.asyncio
    async def test_verify_session_invalid(self):
        """Test that invalid session returns False."""
        with patch("contentmanager.dashboard.auth.get_settings") as mock_settings:
            auth = AuthManager()

            mock_db_session = AsyncMock()
            mock_repo = MagicMock()
            mock_repo.is_valid = AsyncMock(return_value=False)

            with patch("contentmanager.dashboard.auth.SessionRepository", return_value=mock_repo):
                result = await auth.verify_session(mock_db_session, "invalid_token")
                assert result is False

    @pytest.mark.asyncio
    async def test_verify_session_none_token(self):
        """Test that None token returns False."""
        with patch("contentmanager.dashboard.auth.get_settings") as mock_settings:
            auth = AuthManager()

            mock_db_session = AsyncMock()
            result = await auth.verify_session(mock_db_session, None)
            assert result is False

    @pytest.mark.asyncio
    async def test_destroy_session(self):
        """Test that destroy_session calls repository delete."""
        with patch("contentmanager.dashboard.auth.get_settings") as mock_settings:
            auth = AuthManager()

            mock_db_session = AsyncMock()
            mock_repo = MagicMock()
            mock_repo.delete_by_token = AsyncMock()

            with patch("contentmanager.dashboard.auth.SessionRepository", return_value=mock_repo):
                await auth.destroy_session(mock_db_session, "some_token")
                mock_repo.delete_by_token.assert_called_once_with("some_token")
