"""Bot settings API endpoints."""

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from constitutionbot.config import get_settings
from constitutionbot.dashboard.auth import require_auth
from constitutionbot.dashboard.schemas.requests import SettingsUpdateRequest
from constitutionbot.dashboard.schemas.responses import MessageResponse
from constitutionbot.database import get_session

router = APIRouter(prefix="/api/settings", tags=["Settings"])


class SettingsResponse(BaseModel):
    """Current settings response."""

    # Bot settings
    bot_enabled: bool
    mention_check_interval: int
    auto_generate_enabled: bool
    auto_generate_interval: int

    # Content settings
    max_tweet_length: int
    max_thread_tweets: int
    default_hashtags: list[str]

    # Twitter connection status
    twitter_configured: bool


@router.get("", response_model=SettingsResponse)
async def get_current_settings(
    _: str = Depends(require_auth),
):
    """Get current bot settings."""
    settings = get_settings()

    # Check if Twitter is configured
    twitter_configured = bool(
        settings.twitter_api_key.get_secret_value()
        and settings.twitter_access_token.get_secret_value()
    )

    return SettingsResponse(
        bot_enabled=settings.bot_enabled,
        mention_check_interval=settings.mention_check_interval,
        auto_generate_enabled=settings.auto_generate_enabled,
        auto_generate_interval=settings.auto_generate_interval,
        max_tweet_length=settings.max_tweet_length,
        max_thread_tweets=settings.max_thread_tweets,
        default_hashtags=settings.default_hashtags,
        twitter_configured=twitter_configured,
    )


@router.patch("", response_model=MessageResponse)
async def update_settings(
    request: SettingsUpdateRequest,
    _: str = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    """Update bot settings.

    Note: Some settings require a restart to take effect.
    """
    from constitutionbot.database.models import BotSettings

    # For now, we'll store runtime settings in the database
    # These can be read by the bot process

    updates: dict[str, Any] = {}

    if request.bot_enabled is not None:
        updates["bot_enabled"] = str(request.bot_enabled).lower()
    if request.mention_check_interval is not None:
        updates["mention_check_interval"] = str(request.mention_check_interval)
    if request.auto_generate_enabled is not None:
        updates["auto_generate_enabled"] = str(request.auto_generate_enabled).lower()
    if request.auto_generate_interval is not None:
        updates["auto_generate_interval"] = str(request.auto_generate_interval)

    if updates:
        from sqlalchemy import select

        for key, value in updates.items():
            # Upsert pattern
            result = await session.execute(
                select(BotSettings).where(BotSettings.key == key)
            )
            existing = result.scalar_one_or_none()

            if existing:
                existing.value = value
            else:
                session.add(BotSettings(key=key, value=value))

        await session.flush()

    return MessageResponse(
        success=True,
        message=f"Updated {len(updates)} settings. Some changes may require restart.",
        data=updates,
    )


@router.get("/twitter-status")
async def get_twitter_status(
    _: str = Depends(require_auth),
):
    """Check Twitter API connection status."""
    settings = get_settings()

    # Check if credentials are configured
    has_api_key = bool(settings.twitter_api_key.get_secret_value())
    has_api_secret = bool(settings.twitter_api_secret.get_secret_value())
    has_access_token = bool(settings.twitter_access_token.get_secret_value())
    has_access_secret = bool(settings.twitter_access_secret.get_secret_value())
    has_bearer = bool(settings.twitter_bearer_token.get_secret_value())

    configured = all([has_api_key, has_api_secret, has_access_token, has_access_secret])

    # Try to verify credentials if configured
    verified = False
    error = None

    if configured:
        try:
            from constitutionbot.twitter.client import TwitterClient

            client = TwitterClient()
            verified = client.verify_credentials()
        except Exception as e:
            error = str(e)

    return {
        "configured": configured,
        "verified": verified,
        "error": error,
        "credentials": {
            "api_key": has_api_key,
            "api_secret": has_api_secret,
            "access_token": has_access_token,
            "access_secret": has_access_secret,
            "bearer_token": has_bearer,
        },
    }


@router.get("/rate-limits")
async def get_rate_limits(
    _: str = Depends(require_auth),
):
    """Get current Twitter API rate limit status."""
    settings = get_settings()

    # Check if configured
    configured = bool(
        settings.twitter_api_key.get_secret_value()
        and settings.twitter_access_token.get_secret_value()
    )

    if not configured:
        return {
            "configured": False,
            "error": "Twitter API not configured",
            "endpoints": {},
            "app_limit": {"tweets_per_day": 50, "tweets_per_month": 1500},
        }

    try:
        from constitutionbot.twitter.client import TwitterClient

        client = TwitterClient()
        limits = client.get_rate_limits()
        limits["configured"] = True
        return limits
    except Exception as e:
        return {
            "configured": True,
            "error": str(e),
            "endpoints": {},
            "app_limit": {"tweets_per_day": 50, "tweets_per_month": 1500},
        }
