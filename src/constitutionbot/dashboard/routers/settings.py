"""Bot settings API endpoints."""

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from constitutionbot.config import get_settings
from constitutionbot.dashboard.auth import require_auth
from constitutionbot.dashboard.schemas.requests import SettingsUpdateRequest
from constitutionbot.dashboard.schemas.responses import MessageResponse
from constitutionbot.database import get_session
from constitutionbot.database.repositories.credentials import CredentialsRepository

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


# ============================================================================
# Credentials Management Endpoints
# ============================================================================


class CredentialStatusResponse(BaseModel):
    """Response for credential status."""

    configured: bool
    masked_value: Optional[str] = None


class CredentialsStatusResponse(BaseModel):
    """Response for all credentials status."""

    twitter_api_key: CredentialStatusResponse
    twitter_api_secret: CredentialStatusResponse
    twitter_access_token: CredentialStatusResponse
    twitter_access_secret: CredentialStatusResponse
    twitter_bearer_token: CredentialStatusResponse
    openai_api_key: CredentialStatusResponse


class SetCredentialRequest(BaseModel):
    """Request to set a credential."""

    key: str
    value: str


class SetCredentialsRequest(BaseModel):
    """Request to set multiple credentials at once."""

    twitter_api_key: Optional[str] = None
    twitter_api_secret: Optional[str] = None
    twitter_access_token: Optional[str] = None
    twitter_access_secret: Optional[str] = None
    twitter_bearer_token: Optional[str] = None
    openai_api_key: Optional[str] = None


@router.get("/credentials", response_model=CredentialsStatusResponse)
async def get_credentials_status(
    _: str = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    """Get status of all API credentials (masked values, not actual secrets)."""
    repo = CredentialsRepository(session)
    status = await repo.get_credentials_status()

    return CredentialsStatusResponse(
        twitter_api_key=CredentialStatusResponse(**status[repo.TWITTER_API_KEY]),
        twitter_api_secret=CredentialStatusResponse(**status[repo.TWITTER_API_SECRET]),
        twitter_access_token=CredentialStatusResponse(**status[repo.TWITTER_ACCESS_TOKEN]),
        twitter_access_secret=CredentialStatusResponse(**status[repo.TWITTER_ACCESS_SECRET]),
        twitter_bearer_token=CredentialStatusResponse(**status[repo.TWITTER_BEARER_TOKEN]),
        openai_api_key=CredentialStatusResponse(**status[repo.OPENAI_API_KEY]),
    )


@router.post("/credentials", response_model=MessageResponse)
async def set_credentials(
    request: SetCredentialsRequest,
    _: str = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    """Set multiple API credentials at once.

    Only non-null values will be updated.
    """
    repo = CredentialsRepository(session)
    updated = []

    # Map request fields to credential keys
    credential_map = {
        "twitter_api_key": repo.TWITTER_API_KEY,
        "twitter_api_secret": repo.TWITTER_API_SECRET,
        "twitter_access_token": repo.TWITTER_ACCESS_TOKEN,
        "twitter_access_secret": repo.TWITTER_ACCESS_SECRET,
        "twitter_bearer_token": repo.TWITTER_BEARER_TOKEN,
        "openai_api_key": repo.OPENAI_API_KEY,
    }

    for field, key in credential_map.items():
        value = getattr(request, field)
        if value is not None and value.strip():
            await repo.set_credential(key, value.strip())
            updated.append(field)

    await session.commit()

    if not updated:
        return MessageResponse(
            success=False,
            message="No credentials provided to update",
        )

    return MessageResponse(
        success=True,
        message=f"Updated {len(updated)} credential(s): {', '.join(updated)}",
        data={"updated": updated},
    )


@router.put("/credentials/{key}", response_model=MessageResponse)
async def set_single_credential(
    key: str,
    request: SetCredentialRequest,
    _: str = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    """Set a single API credential."""
    repo = CredentialsRepository(session)

    if key not in repo.CREDENTIAL_KEYS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid credential key. Valid keys: {', '.join(repo.CREDENTIAL_KEYS)}",
        )

    if not request.value.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Credential value cannot be empty",
        )

    await repo.set_credential(key, request.value.strip())
    await session.commit()

    return MessageResponse(
        success=True,
        message=f"Credential '{key}' updated successfully",
    )


@router.delete("/credentials/{key}", response_model=MessageResponse)
async def delete_credential(
    key: str,
    _: str = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    """Delete a single API credential."""
    repo = CredentialsRepository(session)

    if key not in repo.CREDENTIAL_KEYS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid credential key. Valid keys: {', '.join(repo.CREDENTIAL_KEYS)}",
        )

    deleted = await repo.delete_credential(key)
    await session.commit()

    if not deleted:
        return MessageResponse(
            success=False,
            message=f"Credential '{key}' not found",
        )

    return MessageResponse(
        success=True,
        message=f"Credential '{key}' deleted successfully",
    )


@router.post("/credentials/test", response_model=MessageResponse)
async def test_credentials(
    _: str = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    """Test if the stored credentials work with Twitter API."""
    repo = CredentialsRepository(session)
    creds = await repo.get_all_credentials()

    # Check if all required Twitter credentials are present
    required = [
        repo.TWITTER_API_KEY,
        repo.TWITTER_API_SECRET,
        repo.TWITTER_ACCESS_TOKEN,
        repo.TWITTER_ACCESS_SECRET,
    ]

    missing = [k for k in required if not creds.get(k)]
    if missing:
        return MessageResponse(
            success=False,
            message=f"Missing required credentials: {', '.join(missing)}",
            data={"missing": missing},
        )

    # Try to verify with Twitter
    try:
        import tweepy

        auth = tweepy.OAuth1UserHandler(
            creds[repo.TWITTER_API_KEY],
            creds[repo.TWITTER_API_SECRET],
            creds[repo.TWITTER_ACCESS_TOKEN],
            creds[repo.TWITTER_ACCESS_SECRET],
        )
        api = tweepy.API(auth)
        user = api.verify_credentials()

        return MessageResponse(
            success=True,
            message=f"Successfully connected as @{user.screen_name}",
            data={
                "screen_name": user.screen_name,
                "user_id": str(user.id),
                "followers_count": user.followers_count,
            },
        )
    except tweepy.errors.Unauthorized:
        return MessageResponse(
            success=False,
            message="Invalid credentials. Please check your API keys and tokens.",
        )
    except Exception as e:
        return MessageResponse(
            success=False,
            message=f"Error testing credentials: {str(e)}",
        )
