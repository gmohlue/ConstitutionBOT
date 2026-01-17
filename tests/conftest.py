"""Shared pytest fixtures for tests."""

import os
import tempfile
from typing import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# IMPORTANT: Set environment variables BEFORE importing any contentmanager modules
# that might trigger settings initialization
os.environ["DASHBOARD_USERNAME"] = "admin"
os.environ["DASHBOARD_PASSWORD"] = "testpassword"
os.environ["DASHBOARD_SECRET_KEY"] = "test-secret-key-for-tests"
os.environ["LLM_PROVIDER"] = "anthropic"
os.environ["ANTHROPIC_API_KEY"] = "test-key"

# Clear settings cache if it exists
from contentmanager.config import get_settings
get_settings.cache_clear()

from contentmanager.database.models import Base
from contentmanager.dashboard.app import create_app
from contentmanager.database import get_session
from contentmanager.dashboard.auth import _auth_manager

# Clear auth manager singleton to ensure it picks up new settings
import contentmanager.dashboard.auth as auth_module
auth_module._auth_manager = None


@pytest.fixture
async def test_db_path():
    """Create a temporary database file."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    yield db_path
    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
async def test_engine(test_db_path):
    """Create a test database engine."""
    engine = create_async_engine(
        f"sqlite+aiosqlite:///{test_db_path}",
        echo=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async_session = sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with async_session() as session:
        yield session


@pytest.fixture
async def app(test_engine):
    """Create a test FastAPI application with test database."""
    app = create_app()

    # Override the database session dependency
    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        async_session = sessionmaker(
            test_engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        async with async_session() as session:
            yield session
            await session.commit()

    app.dependency_overrides[get_session] = override_get_session
    yield app
    app.dependency_overrides.clear()


@pytest.fixture
async def client(app) -> AsyncGenerator[AsyncClient, None]:
    """Create a test HTTP client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
async def authenticated_client(app, test_engine) -> AsyncGenerator[AsyncClient, None]:
    """Create an authenticated test HTTP client by bypassing auth dependency."""
    from contentmanager.dashboard.auth import require_auth

    # Override auth to always return a valid token
    async def override_require_auth():
        return "test-session-token"

    app.dependency_overrides[require_auth] = override_require_auth

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    # Clean up override
    if require_auth in app.dependency_overrides:
        del app.dependency_overrides[require_auth]
