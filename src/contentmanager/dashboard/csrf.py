"""CSRF protection for forms."""

import hashlib
import hmac
import secrets
import time
from typing import Optional

from fastapi import HTTPException, Request, Response, status

from contentmanager.config import get_settings

# Token validity period (1 hour)
CSRF_TOKEN_MAX_AGE = 3600


def generate_csrf_token() -> str:
    """Generate a new CSRF token with timestamp."""
    settings = get_settings()
    timestamp = str(int(time.time()))
    random_part = secrets.token_hex(16)
    data = f"{timestamp}:{random_part}"

    # Sign the token
    secret = settings.dashboard_secret_key.get_secret_value()
    signature = hmac.new(
        secret.encode(),
        data.encode(),
        hashlib.sha256,
    ).hexdigest()

    return f"{data}:{signature}"


def verify_csrf_token(token: Optional[str]) -> bool:
    """Verify a CSRF token is valid and not expired."""
    if not token:
        return False

    try:
        parts = token.split(":")
        if len(parts) != 3:
            return False

        timestamp_str, random_part, provided_signature = parts

        # Check timestamp
        timestamp = int(timestamp_str)
        if time.time() - timestamp > CSRF_TOKEN_MAX_AGE:
            return False

        # Verify signature
        settings = get_settings()
        secret = settings.dashboard_secret_key.get_secret_value()
        data = f"{timestamp_str}:{random_part}"
        expected_signature = hmac.new(
            secret.encode(),
            data.encode(),
            hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(provided_signature, expected_signature)

    except (ValueError, AttributeError):
        return False


def set_csrf_cookie(response: Response, token: str) -> None:
    """Set CSRF token in a cookie."""
    settings = get_settings()
    response.set_cookie(
        key="csrf_token",
        value=token,
        path="/",
        httponly=False,  # JavaScript needs to read this for API calls
        secure=settings.dashboard_secure_cookies,
        samesite="strict",
        max_age=CSRF_TOKEN_MAX_AGE,
    )


def get_csrf_from_cookie(request: Request) -> Optional[str]:
    """Get CSRF token from cookie."""
    return request.cookies.get("csrf_token")


def validate_csrf(cookie_token: Optional[str], form_token: Optional[str]) -> None:
    """Validate CSRF tokens match and are valid.

    Raises HTTPException if validation fails.
    """
    if not cookie_token or not form_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token missing",
        )

    if not hmac.compare_digest(cookie_token, form_token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token mismatch",
        )

    if not verify_csrf_token(form_token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token invalid or expired",
        )
