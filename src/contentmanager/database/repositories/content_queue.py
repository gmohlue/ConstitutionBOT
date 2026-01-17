"""Repository for Content Queue operations."""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from contentmanager.database.models import ContentQueue, ContentStatus


class ContentQueueRepository:
    """Repository for managing content queue items."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        raw_content: str,
        formatted_content: str,
        content_type: str = "tweet",
        mode: str = "bot_proposed",
        topic: Optional[str] = None,
        citations: Optional[dict] = None,
        language: str = "en",
    ) -> ContentQueue:
        """Create a new content queue item."""
        item = ContentQueue(
            raw_content=raw_content,
            formatted_content=formatted_content,
            content_type=content_type,
            mode=mode,
            topic=topic,
            citations=citations,
            language=language,
            status=ContentStatus.PENDING.value,
        )
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def get_by_id(self, item_id: int) -> Optional[ContentQueue]:
        """Get a content queue item by ID."""
        result = await self.session.execute(
            select(ContentQueue).where(ContentQueue.id == item_id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ContentQueue]:
        """Get all content queue items, optionally filtered by status."""
        query = select(ContentQueue).order_by(ContentQueue.created_at.desc())

        if status:
            query = query.where(ContentQueue.status == status)

        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_pending(self, limit: int = 50) -> list[ContentQueue]:
        """Get pending content queue items."""
        return await self.get_all(status=ContentStatus.PENDING.value, limit=limit)

    async def get_approved(self, limit: int = 50) -> list[ContentQueue]:
        """Get approved content queue items ready for posting."""
        return await self.get_all(status=ContentStatus.APPROVED.value, limit=limit)

    async def update(
        self,
        item_id: int,
        formatted_content: Optional[str] = None,
        admin_notes: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Optional[ContentQueue]:
        """Update a content queue item."""
        item = await self.get_by_id(item_id)
        if not item:
            return None

        if formatted_content is not None:
            item.formatted_content = formatted_content
        if admin_notes is not None:
            item.admin_notes = admin_notes
        if status is not None:
            item.status = status

        item.updated_at = datetime.now(timezone.utc)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def approve(self, item_id: int, admin_notes: Optional[str] = None) -> Optional[ContentQueue]:
        """Approve a content queue item for posting."""
        return await self.update(item_id, status=ContentStatus.APPROVED.value, admin_notes=admin_notes)

    async def reject(self, item_id: int, admin_notes: Optional[str] = None) -> Optional[ContentQueue]:
        """Reject a content queue item."""
        return await self.update(item_id, status=ContentStatus.REJECTED.value, admin_notes=admin_notes)

    async def mark_posted(self, item_id: int) -> Optional[ContentQueue]:
        """Mark a content queue item as posted."""
        return await self.update(item_id, status=ContentStatus.POSTED.value)

    async def delete(self, item_id: int) -> bool:
        """Delete a content queue item."""
        item = await self.get_by_id(item_id)
        if not item:
            return False

        await self.session.delete(item)
        await self.session.flush()
        return True

    async def count(self, status: Optional[str] = None) -> int:
        """Count content queue items, optionally by status."""
        from sqlalchemy import func

        query = select(func.count(ContentQueue.id))
        if status:
            query = query.where(ContentQueue.status == status)

        result = await self.session.execute(query)
        return result.scalar() or 0

    async def get_scheduled(
        self, start_date: datetime, end_date: datetime
    ) -> list[ContentQueue]:
        """Get items scheduled within a date range."""
        query = (
            select(ContentQueue)
            .where(ContentQueue.status == ContentStatus.SCHEDULED.value)
            .where(ContentQueue.scheduled_for >= start_date)
            .where(ContentQueue.scheduled_for <= end_date)
            .order_by(ContentQueue.scheduled_for)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def schedule_item(
        self, item_id: int, scheduled_for: datetime, auto_post: bool = False
    ) -> Optional[ContentQueue]:
        """Schedule an approved item for future posting."""
        item = await self.get_by_id(item_id)
        if not item:
            return None

        # Only approved items can be scheduled
        if item.status != ContentStatus.APPROVED.value:
            return None

        item.scheduled_for = scheduled_for
        item.auto_post = auto_post
        item.status = ContentStatus.SCHEDULED.value
        item.updated_at = datetime.now(timezone.utc)

        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def unschedule_item(self, item_id: int) -> Optional[ContentQueue]:
        """Remove schedule from an item, returning it to approved status."""
        item = await self.get_by_id(item_id)
        if not item:
            return None

        # Only scheduled items can be unscheduled
        if item.status != ContentStatus.SCHEDULED.value:
            return None

        item.scheduled_for = None
        item.auto_post = False
        item.status = ContentStatus.APPROVED.value
        item.updated_at = datetime.now(timezone.utc)

        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def get_due_for_posting(self) -> list[ContentQueue]:
        """Get items that are due for auto-posting (scheduled_for <= now and auto_post=True)."""
        now = datetime.now(timezone.utc)
        query = (
            select(ContentQueue)
            .where(ContentQueue.status == ContentStatus.SCHEDULED.value)
            .where(ContentQueue.scheduled_for <= now)
            .where(ContentQueue.auto_post == True)
            .order_by(ContentQueue.scheduled_for)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def find_similar(
        self,
        content: str,
        threshold: float = 0.6,
        limit: int = 5,
    ) -> list[tuple[ContentQueue, float]]:
        """Find content items similar to the given content.

        Uses word overlap (Jaccard similarity) to find similar content.

        Args:
            content: The content to compare against
            threshold: Minimum similarity score (0-1) to include
            limit: Maximum number of results

        Returns:
            List of (item, similarity_score) tuples, sorted by similarity
        """
        # Get all recent content (not rejected)
        query = (
            select(ContentQueue)
            .where(ContentQueue.status != ContentStatus.REJECTED.value)
            .order_by(ContentQueue.created_at.desc())
            .limit(200)  # Check last 200 items
        )
        result = await self.session.execute(query)
        items = list(result.scalars().all())

        # Calculate similarity for each item
        similar = []
        content_words = set(content.lower().split())

        for item in items:
            item_words = set(item.formatted_content.lower().split())

            # Jaccard similarity
            if not content_words or not item_words:
                continue

            intersection = len(content_words & item_words)
            union = len(content_words | item_words)
            similarity = intersection / union if union > 0 else 0

            if similarity >= threshold:
                similar.append((item, similarity))

        # Sort by similarity (highest first) and limit
        similar.sort(key=lambda x: x[1], reverse=True)
        return similar[:limit]

    async def check_duplicate_topic(
        self,
        topic: str,
        days_back: int = 30,
    ) -> list[ContentQueue]:
        """Check if a topic has been recently covered.

        Args:
            topic: The topic to check
            days_back: Number of days to look back

        Returns:
            List of items with similar topics
        """
        from datetime import timedelta

        cutoff = datetime.now(timezone.utc) - timedelta(days=days_back)
        topic_lower = topic.lower()

        # Get recent items
        query = (
            select(ContentQueue)
            .where(ContentQueue.created_at >= cutoff)
            .where(ContentQueue.status != ContentStatus.REJECTED.value)
            .where(ContentQueue.topic.isnot(None))
            .order_by(ContentQueue.created_at.desc())
        )
        result = await self.session.execute(query)
        items = list(result.scalars().all())

        # Find items with similar topics (simple substring matching)
        similar = []
        topic_words = set(topic_lower.split())

        for item in items:
            if not item.topic:
                continue

            item_topic_lower = item.topic.lower()
            item_words = set(item_topic_lower.split())

            # Check for significant word overlap
            overlap = len(topic_words & item_words)
            if overlap >= min(2, len(topic_words)):  # At least 2 words in common
                similar.append(item)

        return similar
