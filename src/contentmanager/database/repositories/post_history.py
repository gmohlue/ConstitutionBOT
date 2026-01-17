"""Repository for Post History operations."""

from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from contentmanager.database.models import PostHistory


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

    async def get_engagement_analytics(self, days: int = 30) -> dict:
        """Get aggregated engagement analytics for the specified period."""
        from datetime import timedelta

        from sqlalchemy import func

        since = datetime.utcnow() - timedelta(days=days)

        # Get posts with engagement data
        query = select(PostHistory).where(
            PostHistory.posted_at >= since,
            PostHistory.engagement.isnot(None),
        )
        result = await self.session.execute(query)
        posts = list(result.scalars().all())

        # Aggregate engagement metrics
        total_likes = 0
        total_retweets = 0
        total_replies = 0
        total_impressions = 0
        total_quotes = 0

        for post in posts:
            if post.engagement:
                total_likes += post.engagement.get("likes", 0) or 0
                total_retweets += post.engagement.get("retweets", 0) or 0
                total_replies += post.engagement.get("replies", 0) or 0
                total_impressions += post.engagement.get("impressions", 0) or 0
                total_quotes += post.engagement.get("quotes", 0) or 0

        posts_with_engagement = len(posts)
        avg_likes = round(total_likes / posts_with_engagement, 1) if posts_with_engagement else 0
        avg_retweets = round(total_retweets / posts_with_engagement, 1) if posts_with_engagement else 0
        avg_replies = round(total_replies / posts_with_engagement, 1) if posts_with_engagement else 0

        # Calculate engagement rate (engagements / impressions * 100)
        total_engagements = total_likes + total_retweets + total_replies + total_quotes
        engagement_rate = round((total_engagements / total_impressions * 100), 2) if total_impressions else 0

        return {
            "period_days": days,
            "posts_count": posts_with_engagement,
            "total_likes": total_likes,
            "total_retweets": total_retweets,
            "total_replies": total_replies,
            "total_quotes": total_quotes,
            "total_impressions": total_impressions,
            "avg_likes": avg_likes,
            "avg_retweets": avg_retweets,
            "avg_replies": avg_replies,
            "engagement_rate": engagement_rate,
        }

    async def get_top_posts(self, limit: int = 10, metric: str = "likes") -> list[PostHistory]:
        """Get top performing posts by a specific metric."""
        # Get all posts with engagement
        query = select(PostHistory).where(PostHistory.engagement.isnot(None))
        result = await self.session.execute(query)
        posts = list(result.scalars().all())

        # Sort by the specified metric
        def get_metric(post):
            if not post.engagement:
                return 0
            return post.engagement.get(metric, 0) or 0

        posts.sort(key=get_metric, reverse=True)
        return posts[:limit]

    async def get_posts_needing_engagement_update(
        self, hours_since_post: int = 1, hours_since_update: int = 6
    ) -> list[PostHistory]:
        """Get posts that need engagement metrics updated.

        Returns posts that are at least hours_since_post old and haven't been
        updated in hours_since_update hours.
        """
        from datetime import timedelta

        now = datetime.utcnow()
        min_age = now - timedelta(hours=hours_since_post)

        query = select(PostHistory).where(PostHistory.posted_at <= min_age)
        result = await self.session.execute(query)
        return list(result.scalars().all())
