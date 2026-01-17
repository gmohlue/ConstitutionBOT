"""Repository for Conversation and Message operations."""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from contentmanager.database.models import (
    Conversation,
    ConversationMessage,
    ConversationStatus,
    MessageRole,
    MessageType,
)


class ConversationRepository:
    """Repository for managing chat conversations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        session_id: str,
        title: Optional[str] = None,
        mode: Optional[str] = None,
        topic: Optional[str] = None,
        context_sections: Optional[dict] = None,
    ) -> Conversation:
        """Create a new conversation."""
        conversation = Conversation(
            session_id=session_id,
            title=title,
            status=ConversationStatus.ACTIVE.value,
            mode=mode,
            topic=topic,
            context_sections=context_sections,
        )
        self.session.add(conversation)
        await self.session.flush()
        await self.session.refresh(conversation)
        return conversation

    async def get_by_id(self, conversation_id: int) -> Optional[Conversation]:
        """Get a conversation by ID."""
        result = await self.session.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        return result.scalar_one_or_none()

    async def get_by_session(
        self,
        session_id: str,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Conversation]:
        """Get conversations for a session, optionally filtered by status."""
        query = (
            select(Conversation)
            .where(Conversation.session_id == session_id)
            .order_by(Conversation.updated_at.desc())
        )

        if status:
            query = query.where(Conversation.status == status)

        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_active_by_session(self, session_id: str) -> list[Conversation]:
        """Get active conversations for a session."""
        return await self.get_by_session(
            session_id=session_id,
            status=ConversationStatus.ACTIVE.value,
        )

    async def update(
        self,
        conversation_id: int,
        title: Optional[str] = None,
        status: Optional[str] = None,
        mode: Optional[str] = None,
        topic: Optional[str] = None,
        context_sections: Optional[dict] = None,
    ) -> Optional[Conversation]:
        """Update a conversation."""
        conversation = await self.get_by_id(conversation_id)
        if not conversation:
            return None

        if title is not None:
            conversation.title = title
        if status is not None:
            conversation.status = status
        if mode is not None:
            conversation.mode = mode
        if topic is not None:
            conversation.topic = topic
        if context_sections is not None:
            conversation.context_sections = context_sections

        conversation.updated_at = datetime.now(timezone.utc)
        await self.session.flush()
        await self.session.refresh(conversation)
        return conversation

    async def archive(self, conversation_id: int) -> Optional[Conversation]:
        """Archive a conversation."""
        return await self.update(
            conversation_id,
            status=ConversationStatus.ARCHIVED.value,
        )

    async def complete(self, conversation_id: int) -> Optional[Conversation]:
        """Mark a conversation as completed."""
        return await self.update(
            conversation_id,
            status=ConversationStatus.COMPLETED.value,
        )

    async def delete(self, conversation_id: int) -> bool:
        """Delete a conversation and all its messages."""
        conversation = await self.get_by_id(conversation_id)
        if not conversation:
            return False

        # Bulk delete all messages in a single query
        await self.session.execute(
            delete(ConversationMessage).where(
                ConversationMessage.conversation_id == conversation_id
            )
        )

        await self.session.delete(conversation)
        await self.session.flush()
        return True


class MessageRepository:
    """Repository for managing conversation messages."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        conversation_id: int,
        role: str,
        content: str,
        message_type: str = MessageType.TEXT.value,
        structured_data: Optional[dict] = None,
        citations: Optional[list] = None,
    ) -> ConversationMessage:
        """Create a new message in a conversation."""
        message = ConversationMessage(
            conversation_id=conversation_id,
            role=role,
            message_type=message_type,
            content=content,
            structured_data=structured_data,
            citations=citations,
        )
        self.session.add(message)
        await self.session.flush()
        await self.session.refresh(message)
        return message

    async def get_by_id(self, message_id: int) -> Optional[ConversationMessage]:
        """Get a message by ID."""
        result = await self.session.execute(
            select(ConversationMessage).where(ConversationMessage.id == message_id)
        )
        return result.scalar_one_or_none()

    async def get_by_conversation(
        self,
        conversation_id: int,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> list[ConversationMessage]:
        """Get all messages for a conversation in chronological order."""
        query = (
            select(ConversationMessage)
            .where(ConversationMessage.conversation_id == conversation_id)
            .order_by(ConversationMessage.created_at.asc())
            .offset(offset)
        )

        if limit:
            query = query.limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_last_n_messages(
        self,
        conversation_id: int,
        n: int = 10,
    ) -> list[ConversationMessage]:
        """Get the last N messages for a conversation."""
        query = (
            select(ConversationMessage)
            .where(ConversationMessage.conversation_id == conversation_id)
            .order_by(ConversationMessage.created_at.desc())
            .limit(n)
        )
        result = await self.session.execute(query)
        messages = list(result.scalars().all())
        # Return in chronological order
        return list(reversed(messages))

    async def count_by_conversation(self, conversation_id: int) -> int:
        """Count messages in a conversation."""
        from sqlalchemy import func

        query = select(func.count(ConversationMessage.id)).where(
            ConversationMessage.conversation_id == conversation_id
        )
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def get_generated_content_messages(
        self,
        conversation_id: int,
    ) -> list[ConversationMessage]:
        """Get all generated content messages from a conversation."""
        query = (
            select(ConversationMessage)
            .where(ConversationMessage.conversation_id == conversation_id)
            .where(ConversationMessage.message_type == MessageType.GENERATED_CONTENT.value)
            .order_by(ConversationMessage.created_at.desc())
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
