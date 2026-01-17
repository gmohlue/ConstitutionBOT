"""Tests for the encryption module."""

import base64
import pytest

from contentmanager.core.encryption import (
    decrypt_value,
    encrypt_value,
    is_encrypted,
    migrate_base64_to_encrypted,
)


class TestEncryption:
    """Tests for encryption/decryption functions."""

    def test_encrypt_and_decrypt_roundtrip(self):
        """Test that encrypting and decrypting returns the original value."""
        secret_key = "test-secret-key-12345"
        original = "my-api-key-value-12345"

        encrypted = encrypt_value(original, secret_key)
        decrypted = decrypt_value(encrypted, secret_key)

        assert decrypted == original

    def test_encrypt_produces_different_output_each_time(self):
        """Test that encryption produces different ciphertext each time."""
        secret_key = "test-secret-key"
        value = "my-secret-value"

        encrypted1 = encrypt_value(value, secret_key)
        encrypted2 = encrypt_value(value, secret_key)

        # Fernet uses random IV, so each encryption is different
        assert encrypted1 != encrypted2
        # But both decrypt to the same value
        assert decrypt_value(encrypted1, secret_key) == value
        assert decrypt_value(encrypted2, secret_key) == value

    def test_decrypt_with_wrong_key_raises_error(self):
        """Test that decryption with wrong key raises ValueError."""
        correct_key = "correct-key"
        wrong_key = "wrong-key"
        value = "my-secret-value"

        encrypted = encrypt_value(value, correct_key)

        with pytest.raises(ValueError, match="Failed to decrypt"):
            decrypt_value(encrypted, wrong_key)

    def test_encrypt_empty_string(self):
        """Test encrypting empty string returns empty string."""
        result = encrypt_value("", "secret-key")
        assert result == ""

    def test_decrypt_empty_string(self):
        """Test decrypting empty string returns empty string."""
        result = decrypt_value("", "secret-key")
        assert result == ""

    def test_encrypt_special_characters(self):
        """Test encrypting values with special characters."""
        secret_key = "test-key"
        special_value = "key-with-special-chars!@#$%^&*()[]{}|;:',.<>?`~"

        encrypted = encrypt_value(special_value, secret_key)
        decrypted = decrypt_value(encrypted, secret_key)

        assert decrypted == special_value

    def test_encrypt_unicode(self):
        """Test encrypting unicode values."""
        secret_key = "test-key"
        unicode_value = "key-with-émojis-🔐-and-中文"

        encrypted = encrypt_value(unicode_value, secret_key)
        decrypted = decrypt_value(encrypted, secret_key)

        assert decrypted == unicode_value


class TestIsEncrypted:
    """Tests for the is_encrypted function."""

    def test_is_encrypted_true_for_fernet_token(self):
        """Test that Fernet-encrypted values are detected."""
        secret_key = "test-key"
        encrypted = encrypt_value("test-value", secret_key)

        assert is_encrypted(encrypted) is True

    def test_is_encrypted_false_for_base64(self):
        """Test that base64-encoded values are not detected as encrypted."""
        base64_value = base64.b64encode(b"test-value").decode()

        assert is_encrypted(base64_value) is False

    def test_is_encrypted_false_for_plain_text(self):
        """Test that plain text is not detected as encrypted."""
        assert is_encrypted("plain-text-value") is False

    def test_is_encrypted_false_for_empty(self):
        """Test that empty string is not detected as encrypted."""
        assert is_encrypted("") is False

    def test_is_encrypted_false_for_none(self):
        """Test that None is not detected as encrypted."""
        assert is_encrypted(None) is False


class TestMigration:
    """Tests for migrating base64 to encrypted format."""

    def test_migrate_base64_value(self):
        """Test migrating a base64-encoded value."""
        secret_key = "test-key"
        original = "my-api-key"
        base64_value = base64.b64encode(original.encode()).decode()

        encrypted, was_migrated = migrate_base64_to_encrypted(base64_value, secret_key)

        assert was_migrated is True
        assert is_encrypted(encrypted) is True
        assert decrypt_value(encrypted, secret_key) == original

    def test_migrate_already_encrypted_value(self):
        """Test that already encrypted values are not migrated."""
        secret_key = "test-key"
        original = "my-api-key"
        encrypted_value = encrypt_value(original, secret_key)

        result, was_migrated = migrate_base64_to_encrypted(encrypted_value, secret_key)

        assert was_migrated is False
        assert result == encrypted_value

    def test_migrate_empty_value(self):
        """Test migrating empty value."""
        result, was_migrated = migrate_base64_to_encrypted("", "secret-key")

        assert was_migrated is False
        assert result == ""

    def test_migrate_non_base64_value(self):
        """Test migrating a value that isn't valid base64."""
        secret_key = "test-key"
        plain_value = "not-base64-!!!invalid"

        encrypted, was_migrated = migrate_base64_to_encrypted(plain_value, secret_key)

        assert was_migrated is True
        assert is_encrypted(encrypted) is True
        # The original value should be encrypted as-is
        assert decrypt_value(encrypted, secret_key) == plain_value
