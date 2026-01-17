"""Post history API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from constitutionbot.dashboard.auth import require_auth
from constitutionbot.dashboard.schemas.responses import (
    AnalyticsDashboardResponse,
    EngagementAnalyticsResponse,
    HistoryListResponse,
    HistoryResponse,
    StatsResponse,
    TopPostResponse,
)
from constitutionbot.database import get_session
from constitutionbot.database.models import ContentStatus
from constitutionbot.database.repositories.constitution import ConstitutionRepository
from constitutionbot.database.repositories.content_queue import ContentQueueRepository
from constitutionbot.database.repositories.post_history import PostHistoryRepository
from constitutionbot.database.repositories.reply_queue import ReplyQueueRepository

router = APIRouter(prefix="/api/history", tags=["Post History"])


@router.get("", response_model=HistoryListResponse)
async def list_history(
    content_type: str | None = None,
    is_reply: bool | None = None,
    limit: int = 50,
    offset: int = 0,
    _: str = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    """List post history."""
    repo = PostHistoryRepository(session)

    items = await repo.get_all(
        content_type=content_type,
        is_reply=is_reply,
        limit=limit,
        offset=offset,
    )
    total = await repo.count(content_type=content_type, is_reply=is_reply)

    return HistoryListResponse(
        items=[HistoryResponse.model_validate(item) for item in items],
        total=total,
    )


@router.get("/recent", response_model=HistoryListResponse)
async def get_recent(
    limit: int = 10,
    _: str = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    """Get most recent posts."""
    repo = PostHistoryRepository(session)
    items = await repo.get_recent(limit=limit)
    total = await repo.count()

    return HistoryListResponse(
        items=[HistoryResponse.model_validate(item) for item in items],
        total=total,
    )


@router.get("/stats", response_model=StatsResponse)
async def get_stats(
    _: str = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    """Get dashboard statistics."""
    from constitutionbot.config import get_settings

    settings = get_settings()

    # Queue stats
    content_repo = ContentQueueRepository(session)
    pending_content = await content_repo.count(status=ContentStatus.PENDING.value)
    approved_content = await content_repo.count(status=ContentStatus.APPROVED.value)

    reply_repo = ReplyQueueRepository(session)
    pending_replies = await reply_repo.count(status=ContentStatus.PENDING.value)

    # History stats
    history_repo = PostHistoryRepository(session)
    history_stats = await history_repo.get_stats()

    # Constitution stats
    const_repo = ConstitutionRepository(session)
    constitution_loaded = await const_repo.has_content()
    total_sections = await const_repo.count() if constitution_loaded else 0

    return StatsResponse(
        pending_content=pending_content,
        approved_content=approved_content,
        pending_replies=pending_replies,
        total_posts=history_stats["total_posts"],
        tweets_posted=history_stats["tweets"],
        threads_posted=history_stats["threads"],
        replies_posted=history_stats["replies"],
        constitution_loaded=constitution_loaded,
        total_sections=total_sections,
        bot_enabled=settings.bot_enabled,
        auto_generate_enabled=settings.auto_generate_enabled,
    )


@router.get("/{post_id}", response_model=HistoryResponse)
async def get_post(
    post_id: int,
    _: str = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    """Get a specific post from history."""
    repo = PostHistoryRepository(session)
    post = await repo.get_by_id(post_id)

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    return HistoryResponse.model_validate(post)


@router.get("/analytics/engagement", response_model=EngagementAnalyticsResponse)
async def get_engagement_analytics(
    days: int = 30,
    _: str = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    """Get engagement analytics for the specified period."""
    repo = PostHistoryRepository(session)
    analytics = await repo.get_engagement_analytics(days=days)
    return EngagementAnalyticsResponse(**analytics)


@router.get("/analytics/top-posts", response_model=list[TopPostResponse])
async def get_top_posts(
    limit: int = 10,
    metric: str = "likes",
    _: str = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    """Get top performing posts by engagement metric."""
    if metric not in ["likes", "retweets", "replies", "impressions"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid metric. Choose from: likes, retweets, replies, impressions",
        )

    repo = PostHistoryRepository(session)
    posts = await repo.get_top_posts(limit=limit, metric=metric)

    return [
        TopPostResponse(
            id=post.id,
            tweet_id=post.tweet_id,
            content=post.content,
            content_type=post.content_type,
            posted_at=post.posted_at,
            likes=post.engagement.get("likes", 0) if post.engagement else 0,
            retweets=post.engagement.get("retweets", 0) if post.engagement else 0,
            replies=post.engagement.get("replies", 0) if post.engagement else 0,
            impressions=post.engagement.get("impressions", 0) if post.engagement else 0,
        )
        for post in posts
    ]


@router.get("/analytics/dashboard", response_model=AnalyticsDashboardResponse)
async def get_analytics_dashboard(
    days: int = 30,
    _: str = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    """Get full analytics dashboard data."""
    repo = PostHistoryRepository(session)

    analytics = await repo.get_engagement_analytics(days=days)
    top_posts = await repo.get_top_posts(limit=5, metric="likes")

    return AnalyticsDashboardResponse(
        analytics=EngagementAnalyticsResponse(**analytics),
        top_posts=[
            TopPostResponse(
                id=post.id,
                tweet_id=post.tweet_id,
                content=post.content,
                content_type=post.content_type,
                posted_at=post.posted_at,
                likes=post.engagement.get("likes", 0) if post.engagement else 0,
                retweets=post.engagement.get("retweets", 0) if post.engagement else 0,
                replies=post.engagement.get("replies", 0) if post.engagement else 0,
                impressions=post.engagement.get("impressions", 0) if post.engagement else 0,
            )
            for post in top_posts
        ],
    )
