"""Tests for CSRF protection module."""

import time

import pytest

from contentmanager.dashboard.csrf import (
    CSRF_TOKEN_MAX_AGE,
    generate_csrf_token,
    verify_csrf_token,
)


def test_generate_csrf_token_format():
    """Test that generated CSRF token has correct format."""
    token = generate_csrf_token()

    # Token should have 3 parts: timestamp:random:signature
    parts = token.split(":")
    assert len(parts) == 3

    # First part should be a valid timestamp
    timestamp = int(parts[0])
    assert timestamp > 0
    assert timestamp <= int(time.time()) + 1


def test_verify_csrf_token_valid():
    """Test that valid tokens pass verification."""
    token = generate_csrf_token()
    assert verify_csrf_token(token) is True


def test_verify_csrf_token_invalid_format():
    """Test that tokens with invalid format fail verification."""
    assert verify_csrf_token("") is False
    assert verify_csrf_token(None) is False
    assert verify_csrf_token("invalid") is False
    assert verify_csrf_token("only:two:parts:extra") is False
    assert verify_csrf_token("not:valid") is False


def test_verify_csrf_token_tampered_signature():
    """Test that tokens with tampered signatures fail verification."""
    token = generate_csrf_token()
    parts = token.split(":")

    # Tamper with the signature
    tampered_token = f"{parts[0]}:{parts[1]}:tampered_signature"
    assert verify_csrf_token(tampered_token) is False


def test_verify_csrf_token_tampered_data():
    """Test that tokens with tampered data fail verification."""
    token = generate_csrf_token()
    parts = token.split(":")

    # Tamper with the timestamp
    tampered_token = f"9999999999:{parts[1]}:{parts[2]}"
    assert verify_csrf_token(tampered_token) is False


def test_csrf_tokens_are_unique():
    """Test that each generated token is unique."""
    tokens = [generate_csrf_token() for _ in range(10)]
    assert len(set(tokens)) == 10
