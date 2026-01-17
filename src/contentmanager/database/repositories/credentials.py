"""Repository for API credentials management."""

import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from contentmanager.core.encryption import (
    decrypt_value,
    encrypt_value,
    is_encrypted,
    migrate_base64_to_encrypted,
)
from contentmanager.database.models import BotSettings

logger = logging.getLogger(__name__)


class CredentialsRepository:
    """Repository for managing API credentials securely.

    Credentials are encrypted using Fernet symmetric encryption with
    a key derived from DASHBOARD_SECRET_KEY using PBKDF2.
    """

    # Credential keys
    ANTHROPIC_API_KEY = "anthropic_api_key"
    TWITTER_API_KEY = "twitter_api_key"
    TWITTER_API_SECRET = "twitter_api_secret"
    TWITTER_ACCESS_TOKEN = "twitter_access_token"
    TWITTER_ACCESS_SECRET = "twitter_access_secret"
    TWITTER_BEARER_TOKEN = "twitter_bearer_token"
    OPENAI_API_KEY = "openai_api_key"

    CREDENTIAL_KEYS = [
        ANTHROPIC_API_KEY,
        TWITTER_API_KEY,
        TWITTER_API_SECRET,
        TWITTER_ACCESS_TOKEN,
        TWITTER_ACCESS_SECRET,
        TWITTER_BEARER_TOKEN,
        OPENAI_API_KEY,
    ]

    def __init__(self, session: AsyncSession, secret_key: Optional[str] = None):
        self.session = session
        # Get secret key from config if not provided
        if secret_key is None:
            from contentmanager.config import get_settings
            settings = get_settings()
            self._secret_key = settings.dashboard_secret_key
        else:
            self._secret_key = secret_key

    def _encrypt(self, value: str) -> str:
        """Encrypt a value for secure storage."""
        return encrypt_value(value, self._secret_key)

    def _decrypt(self, encrypted_value: str) -> str:
        """Decrypt an encrypted value."""
        try:
            return decrypt_value(encrypted_value, self._secret_key)
        except ValueError:
            # Try legacy base64 decoding for backwards compatibility
            import base64
            try:
                return base64.b64decode(encrypted_value.encode()).decode()
            except Exception:
                return encrypted_value  # Return as-is if decryption fails

    async def _migrate_if_needed(self, setting: BotSettings) -> bool:
        """Migrate a credential from base64 to proper encryption if needed."""
        if not setting.value or is_encrypted(setting.value):
            return False

        encrypted, was_migrated = migrate_base64_to_encrypted(
            setting.value, self._secret_key
        )
        if was_migrated:
            setting.value = encrypted
            await self.session.flush()
            logger.info(f"Migrated credential {setting.key} to encrypted format")
        return was_migrated

    def _mask(self, value: str) -> str:
        """Mask a credential for display (show first 4 and last 4 chars)."""
        if not value or len(value) < 12:
            return "*" * len(value) if value else ""
        return value[:4] + "*" * (len(value) - 8) + value[-4:]

    async def get_credential(self, key: str) -> Optional[str]:
        """Get a credential value (decrypted)."""
        result = await self.session.execute(
            select(BotSettings).where(BotSettings.key == key)
        )
        setting = result.scalar_one_or_none()
        if setting:
            # Auto-migrate if using old format
            await self._migrate_if_needed(setting)
            return self._decrypt(setting.value)
        return None

    async def set_credential(self, key: str, value: str) -> bool:
        """Set a credential value (encrypted for storage)."""
        if key not in self.CREDENTIAL_KEYS:
            return False

        encrypted_value = self._encrypt(value)

        result = await self.session.execute(
            select(BotSettings).where(BotSettings.key == key)
        )
        existing = result.scalar_one_or_none()

        if existing:
            existing.value = encrypted_value
        else:
            self.session.add(BotSettings(key=key, value=encrypted_value))

        await self.session.flush()
        return True

    async def delete_credential(self, key: str) -> bool:
        """Delete a credential."""
        result = await self.session.execute(
            select(BotSettings).where(BotSettings.key == key)
        )
        existing = result.scalar_one_or_none()
        if existing:
            await self.session.delete(existing)
            await self.session.flush()
            return True
        return False

    async def get_credentials_status(self) -> dict:
        """Get status of all credentials (masked values, not actual)."""
        # Fetch all credentials in a single query to avoid N+1
        result = await self.session.execute(
            select(BotSettings).where(BotSettings.key.in_(self.CREDENTIAL_KEYS))
        )
        all_settings = list(result.scalars().all())

        # Migrate any old format credentials and build settings dict
        settings = {}
        for s in all_settings:
            await self._migrate_if_needed(s)
            settings[s.key] = self._decrypt(s.value)

        status = {}
        for key in self.CREDENTIAL_KEYS:
            value = settings.get(key)
            status[key] = {
                "configured": bool(value),
                "masked_value": self._mask(value) if value else None,
            }
        return status

    async def get_all_credentials(self) -> dict:
        """Get all credential values (for internal use only)."""
        # Fetch all credentials in a single query to avoid N+1
        result = await self.session.execute(
            select(BotSettings).where(BotSettings.key.in_(self.CREDENTIAL_KEYS))
        )
        all_settings = list(result.scalars().all())

        # Migrate any old format credentials and build settings dict
        settings = {}
        for s in all_settings:
            await self._migrate_if_needed(s)
            settings[s.key] = self._decrypt(s.value)

        # Ensure all keys are present (even if None)
        return {key: settings.get(key) for key in self.CREDENTIAL_KEYS}

    async def migrate_all_credentials(self) -> int:
        """Migrate all credentials from base64 to encrypted format.

        Returns:
            Number of credentials migrated
        """
        result = await self.session.execute(
            select(BotSettings).where(BotSettings.key.in_(self.CREDENTIAL_KEYS))
        )
        migrated_count = 0
        for setting in result.scalars().all():
            if await self._migrate_if_needed(setting):
                migrated_count += 1
        return migrated_count
