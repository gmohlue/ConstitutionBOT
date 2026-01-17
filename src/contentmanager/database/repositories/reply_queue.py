"""Repository for Reply Queue operations."""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from contentmanager.database.models import ContentStatus, ReplyQueue


class ReplyQueueRepository:
    """Repository for managing reply queue items."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        mention_id: str,
        mention_text: str,
        mention_author: str,
        draft_reply: str,
        mention_author_id: Optional[str] = None,
    ) -> ReplyQueue:
        """Create a new reply queue item."""
        item = ReplyQueue(
            mention_id=mention_id,
            mention_text=mention_text,
            mention_author=mention_author,
            mention_author_id=mention_author_id,
            draft_reply=draft_reply,
            status=ContentStatus.PENDING.value,
        )
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def get_by_id(self, item_id: int) -> Optional[ReplyQueue]:
        """Get a reply queue item by ID."""
        result = await self.session.execute(
            select(ReplyQueue).where(ReplyQueue.id == item_id)
        )
        return result.scalar_one_or_none()

    async def get_by_mention_id(self, mention_id: str) -> Optional[ReplyQueue]:
        """Get a reply queue item by Twitter mention ID."""
        result = await self.session.execute(
            select(ReplyQueue).where(ReplyQueue.mention_id == mention_id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ReplyQueue]:
        """Get all reply queue items, optionally filtered by status."""
        query = select(ReplyQueue).order_by(ReplyQueue.created_at.desc())

        if status:
            query = query.where(ReplyQueue.status == status)

        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_pending(self, limit: int = 50) -> list[ReplyQueue]:
        """Get pending reply queue items."""
        return await self.get_all(status=ContentStatus.PENDING.value, limit=limit)

    async def get_approved(self, limit: int = 50) -> list[ReplyQueue]:
        """Get approved reply queue items ready for posting."""
        return await self.get_all(status=ContentStatus.APPROVED.value, limit=limit)

    async def update(
        self,
        item_id: int,
        draft_reply: Optional[str] = None,
        final_reply: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Optional[ReplyQueue]:
        """Update a reply queue item."""
        item = await self.get_by_id(item_id)
        if not item:
            return None

        if draft_reply is not None:
            item.draft_reply = draft_reply
        if final_reply is not None:
            item.final_reply = final_reply
        if status is not None:
            item.status = status

        item.updated_at = datetime.now(timezone.utc)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def approve(
        self, item_id: int, final_reply: Optional[str] = None
    ) -> Optional[ReplyQueue]:
        """Approve a reply queue item for posting."""
        return await self.update(
            item_id,
            final_reply=final_reply,
            status=ContentStatus.APPROVED.value,
        )

    async def reject(self, item_id: int) -> Optional[ReplyQueue]:
        """Reject a reply queue item."""
        return await self.update(item_id, status=ContentStatus.REJECTED.value)

    async def mark_posted(self, item_id: int) -> Optional[ReplyQueue]:
        """Mark a reply queue item as posted."""
        return await self.update(item_id, status=ContentStatus.POSTED.value)

    async def delete(self, item_id: int) -> bool:
        """Delete a reply queue item."""
        item = await self.get_by_id(item_id)
        if not item:
            return False

        await self.session.delete(item)
        await self.session.flush()
        return True

    async def mention_exists(self, mention_id: str) -> bool:
        """Check if a mention has already been processed."""
        item = await self.get_by_mention_id(mention_id)
        return item is not None

    async def count(self, status: Optional[str] = None) -> int:
        """Count reply queue items, optionally by status."""
        from sqlalchemy import func

        query = select(func.count(ReplyQueue.id))
        if status:
            query = query.where(ReplyQueue.status == status)

        result = await self.session.execute(query)
        return result.scalar() or 0
