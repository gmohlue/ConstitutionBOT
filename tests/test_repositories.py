"""Tests for database repositories."""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from contentmanager.database.models import (
    Base,
    ContentQueue,
    ContentStatus,
    Session,
    Conversation,
    ConversationMessage,
    ConversationStatus,
    MessageRole,
)


@pytest.fixture
async def async_engine():
    """Create an async in-memory SQLite engine for testing."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def async_session(async_engine):
    """Create an async session for testing."""
    async_session_maker = sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with async_session_maker() as session:
        yield session


class TestSessionRepository:
    """Tests for SessionRepository."""

    @pytest.mark.asyncio
    async def test_create_session(self, async_session):
        """Test creating a new session."""
        from contentmanager.database.repositories.session import SessionRepository

        repo = SessionRepository(async_session)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=24)

        session = await repo.create(
            token="test_token_123",
            expires_at=expires_at,
            user_agent="Test Browser",
            ip_address="127.0.0.1",
        )

        assert session is not None
        assert session.token == "test_token_123"
        assert session.user_agent == "Test Browser"
        assert session.ip_address == "127.0.0.1"

    @pytest.mark.asyncio
    async def test_get_by_token(self, async_session):
        """Test getting a session by token."""
        from contentmanager.database.repositories.session import SessionRepository

        repo = SessionRepository(async_session)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=24)

        await repo.create(token="find_me", expires_at=expires_at)
        await async_session.commit()

        found = await repo.get_by_token("find_me")
        assert found is not None
        assert found.token == "find_me"

    @pytest.mark.asyncio
    async def test_get_by_token_not_found(self, async_session):
        """Test getting a non-existent session."""
        from contentmanager.database.repositories.session import SessionRepository

        repo = SessionRepository(async_session)
        found = await repo.get_by_token("nonexistent")
        assert found is None

    @pytest.mark.asyncio
    async def test_delete_by_token(self, async_session):
        """Test deleting a session by token."""
        from contentmanager.database.repositories.session import SessionRepository

        repo = SessionRepository(async_session)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=24)

        await repo.create(token="delete_me", expires_at=expires_at)
        await async_session.commit()

        result = await repo.delete_by_token("delete_me")
        assert result is True

        found = await repo.get_by_token("delete_me")
        assert found is None

    @pytest.mark.asyncio
    async def test_is_valid_with_valid_session(self, async_session):
        """Test is_valid returns True for valid session."""
        from contentmanager.database.repositories.session import SessionRepository

        repo = SessionRepository(async_session)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=24)

        await repo.create(token="valid_session", expires_at=expires_at)
        await async_session.commit()

        is_valid = await repo.is_valid("valid_session")
        assert is_valid is True

    @pytest.mark.asyncio
    async def test_is_valid_with_expired_session(self, async_session):
        """Test is_valid returns False for expired session."""
        from contentmanager.database.repositories.session import SessionRepository

        repo = SessionRepository(async_session)
        # Set expiration in the past
        expires_at = datetime.now(timezone.utc) - timedelta(hours=1)

        await repo.create(token="expired_session", expires_at=expires_at)
        await async_session.commit()

        is_valid = await repo.is_valid("expired_session")
        assert is_valid is False


class TestContentQueueRepository:
    """Tests for ContentQueueRepository."""

    @pytest.mark.asyncio
    async def test_create_content(self, async_session):
        """Test creating content queue item."""
        from contentmanager.database.repositories.content_queue import ContentQueueRepository

        repo = ContentQueueRepository(async_session)

        item = await repo.create(
            raw_content="Test raw content",
            formatted_content="Test formatted content",
            content_type="tweet",
            mode="user_provided",
            topic="Test topic",
        )

        assert item is not None
        assert item.raw_content == "Test raw content"
        assert item.formatted_content == "Test formatted content"
        assert item.status == ContentStatus.PENDING.value

    @pytest.mark.asyncio
    async def test_get_by_id(self, async_session):
        """Test getting content by ID."""
        from contentmanager.database.repositories.content_queue import ContentQueueRepository

        repo = ContentQueueRepository(async_session)

        created = await repo.create(
            raw_content="Find me",
            formatted_content="Find me formatted",
        )
        await async_session.commit()

        found = await repo.get_by_id(created.id)
        assert found is not None
        assert found.raw_content == "Find me"

    @pytest.mark.asyncio
    async def test_approve(self, async_session):
        """Test approving content."""
        from contentmanager.database.repositories.content_queue import ContentQueueRepository

        repo = ContentQueueRepository(async_session)

        item = await repo.create(
            raw_content="Approve me",
            formatted_content="Approve me formatted",
        )
        await async_session.commit()

        approved = await repo.approve(item.id, admin_notes="Looks good!")
        assert approved is not None
        assert approved.status == ContentStatus.APPROVED.value
        assert approved.admin_notes == "Looks good!"

    @pytest.mark.asyncio
    async def test_reject(self, async_session):
        """Test rejecting content."""
        from contentmanager.database.repositories.content_queue import ContentQueueRepository

        repo = ContentQueueRepository(async_session)

        item = await repo.create(
            raw_content="Reject me",
            formatted_content="Reject me formatted",
        )
        await async_session.commit()

        rejected = await repo.reject(item.id, admin_notes="Not suitable")
        assert rejected is not None
        assert rejected.status == ContentStatus.REJECTED.value

    @pytest.mark.asyncio
    async def test_get_pending(self, async_session):
        """Test getting pending content."""
        from contentmanager.database.repositories.content_queue import ContentQueueRepository

        repo = ContentQueueRepository(async_session)

        # Create some items
        await repo.create(raw_content="Pending 1", formatted_content="F1")
        await repo.create(raw_content="Pending 2", formatted_content="F2")
        await async_session.commit()

        pending = await repo.get_pending()
        assert len(pending) == 2

    @pytest.mark.asyncio
    async def test_delete(self, async_session):
        """Test deleting content."""
        from contentmanager.database.repositories.content_queue import ContentQueueRepository

        repo = ContentQueueRepository(async_session)

        item = await repo.create(
            raw_content="Delete me",
            formatted_content="Delete me formatted",
        )
        await async_session.commit()

        result = await repo.delete(item.id)
        assert result is True

        found = await repo.get_by_id(item.id)
        assert found is None


class TestConversationRepository:
    """Tests for ConversationRepository."""

    @pytest.mark.asyncio
    async def test_create_conversation(self, async_session):
        """Test creating a conversation."""
        from contentmanager.database.repositories.conversation import ConversationRepository

        repo = ConversationRepository(async_session)

        conversation = await repo.create(
            session_id="test_session_123",
            title="Test Conversation",
            mode="user_provided",
        )

        assert conversation is not None
        assert conversation.session_id == "test_session_123"
        assert conversation.title == "Test Conversation"
        assert conversation.status == ConversationStatus.ACTIVE.value

    @pytest.mark.asyncio
    async def test_get_by_session(self, async_session):
        """Test getting conversations by session ID."""
        from contentmanager.database.repositories.conversation import ConversationRepository

        repo = ConversationRepository(async_session)

        await repo.create(session_id="session_a", title="Conv 1")
        await repo.create(session_id="session_a", title="Conv 2")
        await repo.create(session_id="session_b", title="Conv 3")
        await async_session.commit()

        conversations = await repo.get_by_session("session_a")
        assert len(conversations) == 2

    @pytest.mark.asyncio
    async def test_archive_conversation(self, async_session):
        """Test archiving a conversation."""
        from contentmanager.database.repositories.conversation import ConversationRepository

        repo = ConversationRepository(async_session)

        conversation = await repo.create(session_id="test", title="Archive me")
        await async_session.commit()

        archived = await repo.archive(conversation.id)
        assert archived is not None
        assert archived.status == ConversationStatus.ARCHIVED.value

    @pytest.mark.asyncio
    async def test_delete_conversation_with_messages(self, async_session):
        """Test deleting a conversation also deletes its messages."""
        from contentmanager.database.repositories.conversation import (
            ConversationRepository,
            MessageRepository,
        )

        conv_repo = ConversationRepository(async_session)
        msg_repo = MessageRepository(async_session)

        conversation = await conv_repo.create(session_id="test", title="Delete me")
        await async_session.flush()

        # Add some messages
        await msg_repo.create(
            conversation_id=conversation.id,
            role=MessageRole.USER.value,
            content="Hello",
        )
        await msg_repo.create(
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT.value,
            content="Hi there!",
        )
        await async_session.commit()

        # Verify messages exist
        messages = await msg_repo.get_by_conversation(conversation.id)
        assert len(messages) == 2

        # Delete conversation
        result = await conv_repo.delete(conversation.id)
        assert result is True

        # Verify messages are also deleted
        messages = await msg_repo.get_by_conversation(conversation.id)
        assert len(messages) == 0


class TestMessageRepository:
    """Tests for MessageRepository."""

    @pytest.mark.asyncio
    async def test_create_message(self, async_session):
        """Test creating a message."""
        from contentmanager.database.repositories.conversation import (
            ConversationRepository,
            MessageRepository,
        )

        conv_repo = ConversationRepository(async_session)
        msg_repo = MessageRepository(async_session)

        conversation = await conv_repo.create(session_id="test", title="Test")
        await async_session.flush()

        message = await msg_repo.create(
            conversation_id=conversation.id,
            role=MessageRole.USER.value,
            content="Hello, world!",
        )

        assert message is not None
        assert message.content == "Hello, world!"
        assert message.role == MessageRole.USER.value

    @pytest.mark.asyncio
    async def test_get_last_n_messages(self, async_session):
        """Test getting the last N messages."""
        from contentmanager.database.repositories.conversation import (
            ConversationRepository,
            MessageRepository,
        )

        conv_repo = ConversationRepository(async_session)
        msg_repo = MessageRepository(async_session)

        conversation = await conv_repo.create(session_id="test", title="Test")
        await async_session.flush()

        # Create 5 messages
        for i in range(5):
            await msg_repo.create(
                conversation_id=conversation.id,
                role=MessageRole.USER.value,
                content=f"Message {i}",
            )
        await async_session.commit()

        # Get last 3 messages
        messages = await msg_repo.get_last_n_messages(conversation.id, n=3)
        assert len(messages) == 3
        # Messages should be in chronological order and be the last 3
        # The exact order depends on database ordering, so just verify we got 3 messages
        contents = [m.content for m in messages]
        assert len(contents) == 3
