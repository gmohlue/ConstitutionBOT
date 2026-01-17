"""Repository for API credentials management."""

import base64
import hashlib
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from contentmanager.database.models import BotSettings


class CredentialsRepository:
    """Repository for managing API credentials securely."""

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

    def __init__(self, session: AsyncSession):
        self.session = session

    def _encode(self, value: str) -> str:
        """Simple encoding for storage (not encryption, but obfuscation)."""
        # In production, use proper encryption with a secret key
        return base64.b64encode(value.encode()).decode()

    def _decode(self, encoded: str) -> str:
        """Decode stored value."""
        try:
            return base64.b64decode(encoded.encode()).decode()
        except Exception:
            return encoded  # Return as-is if not encoded

    def _mask(self, value: str) -> str:
        """Mask a credential for display (show first 4 and last 4 chars)."""
        if not value or len(value) < 12:
            return "*" * len(value) if value else ""
        return value[:4] + "*" * (len(value) - 8) + value[-4:]

    async def get_credential(self, key: str) -> Optional[str]:
        """Get a credential value (decoded)."""
        result = await self.session.execute(
            select(BotSettings).where(BotSettings.key == key)
        )
        setting = result.scalar_one_or_none()
        if setting:
            return self._decode(setting.value)
        return None

    async def set_credential(self, key: str, value: str) -> bool:
        """Set a credential value (encoded for storage)."""
        if key not in self.CREDENTIAL_KEYS:
            return False

        encoded_value = self._encode(value)

        result = await self.session.execute(
            select(BotSettings).where(BotSettings.key == key)
        )
        existing = result.scalar_one_or_none()

        if existing:
            existing.value = encoded_value
        else:
            self.session.add(BotSettings(key=key, value=encoded_value))

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
        settings = {s.key: self._decode(s.value) for s in result.scalars().all()}

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
        settings = {s.key: self._decode(s.value) for s in result.scalars().all()}

        # Ensure all keys are present (even if None)
        return {key: settings.get(key) for key in self.CREDENTIAL_KEYS}
