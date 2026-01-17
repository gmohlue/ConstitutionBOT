"""Encryption utilities for secure credential storage."""

import base64
import hashlib
import os
from functools import lru_cache

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


# Salt for key derivation - this could be stored per-installation
# but a static salt is acceptable when combined with a strong secret key
_SALT = b"contentmanager_credential_salt_v1"


def _derive_key(secret_key: str) -> bytes:
    """Derive a Fernet-compatible key from a secret key using PBKDF2."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=_SALT,
        iterations=480000,  # OWASP recommended minimum
    )
    key = kdf.derive(secret_key.encode())
    return base64.urlsafe_b64encode(key)


@lru_cache(maxsize=1)
def _get_fernet(secret_key: str) -> Fernet:
    """Get a Fernet instance with the derived key (cached)."""
    key = _derive_key(secret_key)
    return Fernet(key)


def encrypt_value(value: str, secret_key: str) -> str:
    """Encrypt a string value using Fernet symmetric encryption.

    Args:
        value: The plaintext value to encrypt
        secret_key: The secret key to derive the encryption key from

    Returns:
        The encrypted value as a base64-encoded string
    """
    if not value:
        return ""
    fernet = _get_fernet(secret_key)
    encrypted = fernet.encrypt(value.encode())
    return encrypted.decode()


def decrypt_value(encrypted_value: str, secret_key: str) -> str:
    """Decrypt an encrypted value using Fernet symmetric encryption.

    Args:
        encrypted_value: The encrypted value (base64-encoded)
        secret_key: The secret key to derive the decryption key from

    Returns:
        The decrypted plaintext value

    Raises:
        ValueError: If decryption fails (wrong key or tampered data)
    """
    if not encrypted_value:
        return ""
    try:
        fernet = _get_fernet(secret_key)
        decrypted = fernet.decrypt(encrypted_value.encode())
        return decrypted.decode()
    except InvalidToken:
        raise ValueError("Failed to decrypt: invalid token or wrong key")


def is_encrypted(value: str) -> bool:
    """Check if a value appears to be Fernet-encrypted.

    This is a heuristic check - Fernet tokens start with 'gAAAAA'.
    """
    if not value:
        return False
    return value.startswith("gAAAAA")


def migrate_base64_to_encrypted(
    base64_value: str, secret_key: str
) -> tuple[str, bool]:
    """Migrate a base64-encoded value to proper encryption.

    Args:
        base64_value: The base64-encoded value (old format)
        secret_key: The secret key for encryption

    Returns:
        Tuple of (encrypted_value, was_migrated)
    """
    if not base64_value:
        return "", False

    # Check if already encrypted
    if is_encrypted(base64_value):
        return base64_value, False

    # Try to decode as base64
    try:
        decoded = base64.b64decode(base64_value.encode()).decode()
        # Re-encrypt with proper encryption
        encrypted = encrypt_value(decoded, secret_key)
        return encrypted, True
    except Exception:
        # Not valid base64, encrypt as-is
        encrypted = encrypt_value(base64_value, secret_key)
        return encrypted, True
