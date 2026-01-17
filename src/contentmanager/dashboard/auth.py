"""Authentication for the admin dashboard."""

import secrets
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Cookie, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse

from contentmanager.config import get_settings


class AuthManager:
    """Simple session-based authentication for the dashboard."""

    def __init__(self):
        self.settings = get_settings()
        self._sessions: dict[str, datetime] = {}
        self._session_duration = timedelta(hours=24)

    def verify_credentials(self, username: str, password: str) -> bool:
        """Verify username and password against configured credentials."""
        return (
            username == self.settings.dashboard_username
            and password == self.settings.dashboard_password.get_secret_value()
        )

    def create_session(self) -> str:
        """Create a new session and return the session token."""
        token = secrets.token_urlsafe(32)
        self._sessions[token] = datetime.utcnow()
        self._cleanup_expired_sessions()
        return token

    def verify_session(self, token: Optional[str]) -> bool:
        """Verify if a session token is valid."""
        if not token or token not in self._sessions:
            return False

        created_at = self._sessions[token]
        if datetime.utcnow() - created_at > self._session_duration:
            del self._sessions[token]
            return False

        return True

    def destroy_session(self, token: str) -> None:
        """Destroy a session."""
        if token in self._sessions:
            del self._sessions[token]

    def _cleanup_expired_sessions(self) -> None:
        """Remove expired sessions."""
        now = datetime.utcnow()
        expired = [
            token
            for token, created_at in self._sessions.items()
            if now - created_at > self._session_duration
        ]
        for token in expired:
            del self._sessions[token]


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
) -> str:
    """Dependency that requires authentication.

    For API endpoints, raises HTTPException.
    For page routes, redirects to login.
    """
    auth = get_auth_manager()

    if not auth.verify_session(session_token):
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
) -> bool:
    """Dependency that checks auth but doesn't require it."""
    auth = get_auth_manager()
    return auth.verify_session(session_token)


def login_user(response: Response, username: str, password: str) -> bool:
    """Attempt to log in a user.

    Args:
        response: The response object to set cookies on
        username: The username
        password: The password

    Returns:
        True if login successful, False otherwise
    """
    auth = get_auth_manager()

    if not auth.verify_credentials(username, password):
        return False

    token = auth.create_session()
    response.set_cookie(
        key="session",
        value=token,
        path="/",
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=86400,  # 24 hours
    )

    return True


def logout_user(response: Response, session_token: Optional[str] = None) -> None:
    """Log out the current user."""
    auth = get_auth_manager()

    if session_token:
        auth.destroy_session(session_token)

    response.delete_cookie(key="session")
