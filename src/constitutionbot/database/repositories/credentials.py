"""Repository for API credentials management."""

import base64
import hashlib
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from constitutionbot.database.models import BotSettings


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
        status = {}
        for key in self.CREDENTIAL_KEYS:
            value = await self.get_credential(key)
            status[key] = {
                "configured": bool(value),
                "masked_value": self._mask(value) if value else None,
            }
        return status

    async def get_all_credentials(self) -> dict:
        """Get all credential values (for internal use only)."""
        credentials = {}
        for key in self.CREDENTIAL_KEYS:
            credentials[key] = await self.get_credential(key)
        return credentials
