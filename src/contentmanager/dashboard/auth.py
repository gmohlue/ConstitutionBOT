"""Authentication for the admin dashboard."""

import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Cookie, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from contentmanager.config import get_settings
from contentmanager.database import get_session
from contentmanager.database.repositories.session import SessionRepository


class AuthManager:
    """Session-based authentication for the dashboard using database storage."""

    def __init__(self):
        self.settings = get_settings()
        self._session_duration = timedelta(hours=24)

    def verify_credentials(self, username: str, password: str) -> bool:
        """Verify username and password against configured credentials."""
        return (
            username == self.settings.dashboard_username
            and password == self.settings.dashboard_password.get_secret_value()
        )

    async def create_session(
        self,
        db_session: AsyncSession,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> str:
        """Create a new session and return the session token."""
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + self._session_duration

        repo = SessionRepository(db_session)
        await repo.create(
            token=token,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        # Cleanup expired sessions periodically
        await repo.delete_expired()
        await db_session.commit()

        return token

    async def verify_session(self, db_session: AsyncSession, token: Optional[str]) -> bool:
        """Verify if a session token is valid."""
        if not token:
            return False

        repo = SessionRepository(db_session)
        is_valid = await repo.is_valid(token)
        await db_session.commit()
        return is_valid

    async def destroy_session(self, db_session: AsyncSession, token: str) -> None:
        """Destroy a session."""
        repo = SessionRepository(db_session)
        await repo.delete_by_token(token)
        await db_session.commit()


# Global auth manager instance
_auth_manager: Optional[AuthManager] = None


def get_auth_manager() -> AuthManager:
    """Get the auth manager singleton."""
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AuthManager()
    return _auth_manager


async def get_current_session(
    session_token: Optional[str] = Cookie(default=None, alias="session"),
) -> Optional[str]:
    """Get the current session token from cookies."""
    return session_token


async def require_auth(
    request: Request,
    session_token: Optional[str] = Depends(get_current_session),
    db_session: AsyncSession = Depends(get_session),
) -> str:
    """Dependency that requires authentication.

    For API endpoints, raises HTTPException.
    For page routes, redirects to login.
    """
    auth = get_auth_manager()

    if not await auth.verify_session(db_session, session_token):
        # Check if this is an API request or page request
        if request.url.path.startswith("/api/"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
            )
        else:
            # Redirect to login page
            raise HTTPException(
                status_code=status.HTTP_303_SEE_OTHER,
                headers={"Location": f"/login?next={request.url.path}"},
            )

    return session_token


async def optional_auth(
    session_token: Optional[str] = Depends(get_current_session),
    db_session: AsyncSession = Depends(get_session),
) -> bool:
    """Dependency that checks auth but doesn't require it."""
    auth = get_auth_manager()
    return await auth.verify_session(db_session, session_token)


async def login_user(
    response: Response,
    username: str,
    password: str,
    db_session: AsyncSession,
    request: Optional[Request] = None,
) -> bool:
    """Attempt to log in a user.

    Args:
        response: The response object to set cookies on
        username: The username
        password: The password
        db_session: Database session for storing the session
        request: Optional request to extract user agent and IP

    Returns:
        True if login successful, False otherwise
    """
    auth = get_auth_manager()

    if not auth.verify_credentials(username, password):
        return False

    user_agent = None
    ip_address = None
    if request:
        user_agent = request.headers.get("user-agent")
        ip_address = request.client.host if request.client else None

    token = await auth.create_session(
        db_session,
        user_agent=user_agent,
        ip_address=ip_address,
    )
    settings = get_settings()
    response.set_cookie(
        key="session",
        value=token,
        path="/",
        httponly=True,
        secure=settings.dashboard_secure_cookies,
        samesite="lax",
        max_age=86400,  # 24 hours
    )

    return True


async def logout_user(
    response: Response,
    db_session: AsyncSession,
    session_token: Optional[str] = None,
) -> None:
    """Log out the current user."""
    auth = get_auth_manager()

    if session_token:
        await auth.destroy_session(db_session, session_token)

    response.delete_cookie(key="session")
