"""Repository for Post History operations."""

from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from constitutionbot.database.models import PostHistory


class PostHistoryRepository:
    """Repository for managing post history."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        tweet_id: str,
        content: str,
        content_type: str = "tweet",
        is_reply: bool = False,
        reply_to_id: Optional[str] = None,
        engagement: Optional[dict] = None,
    ) -> PostHistory:
        """Create a new post history record."""
        post = PostHistory(
            tweet_id=tweet_id,
            content=content,
            content_type=content_type,
            is_reply=is_reply,
            reply_to_id=reply_to_id,
            engagement=engagement,
        )
        self.session.add(post)
        await self.session.flush()
        await self.session.refresh(post)
        return post

    async def get_by_id(self, post_id: int) -> Optional[PostHistory]:
        """Get a post history record by ID."""
        result = await self.session.execute(
            select(PostHistory).where(PostHistory.id == post_id)
        )
        return result.scalar_one_or_none()

    async def get_by_tweet_id(self, tweet_id: str) -> Optional[PostHistory]:
        """Get a post history record by Twitter tweet ID."""
        result = await self.session.execute(
            select(PostHistory).where(PostHistory.tweet_id == tweet_id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        content_type: Optional[str] = None,
        is_reply: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[PostHistory]:
        """Get all post history records."""
        query = select(PostHistory).order_by(PostHistory.posted_at.desc())

        if content_type:
            query = query.where(PostHistory.content_type == content_type)
        if is_reply is not None:
            query = query.where(PostHistory.is_reply == is_reply)

        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_recent(self, limit: int = 10) -> list[PostHistory]:
        """Get most recent posts."""
        return await self.get_all(limit=limit)

    async def update_engagement(
        self, tweet_id: str, engagement: dict
    ) -> Optional[PostHistory]:
        """Update engagement metrics for a post."""
        post = await self.get_by_tweet_id(tweet_id)
        if not post:
            return None

        post.engagement = engagement
        await self.session.flush()
        await self.session.refresh(post)
        return post

    async def count(
        self,
        content_type: Optional[str] = None,
        is_reply: Optional[bool] = None,
        since: Optional[datetime] = None,
    ) -> int:
        """Count post history records."""
        from sqlalchemy import func

        query = select(func.count(PostHistory.id))
        if content_type:
            query = query.where(PostHistory.content_type == content_type)
        if is_reply is not None:
            query = query.where(PostHistory.is_reply == is_reply)
        if since:
            query = query.where(PostHistory.posted_at >= since)

        result = await self.session.execute(query)
        return result.scalar() or 0

    async def get_stats(self) -> dict:
        """Get statistics about posted content."""
        total = await self.count()
        tweets = await self.count(content_type="tweet", is_reply=False)
        threads = await self.count(content_type="thread", is_reply=False)
        replies = await self.count(is_reply=True)

        return {
            "total_posts": total,
            "tweets": tweets,
            "threads": threads,
            "replies": replies,
        }
