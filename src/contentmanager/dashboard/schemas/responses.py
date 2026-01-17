"""Response schemas for the dashboard API."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class ContentQueueResponse(BaseModel):
    """Content queue item response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    content_type: str
    raw_content: str
    formatted_content: str
    mode: str
    topic: Optional[str]
    citations: Optional[list[dict]]
    language: str = "en"
    status: str
    admin_notes: Optional[str]
    scheduled_for: Optional[datetime] = None
    auto_post: bool = False
    created_at: datetime
    updated_at: datetime


class ContentQueueListResponse(BaseModel):
    """List of content queue items."""

    items: list[ContentQueueResponse]
    total: int
    pending_count: int
    approved_count: int


class CalendarItemResponse(BaseModel):
    """Calendar item response for scheduled content."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    content_type: str
    topic: Optional[str]
    formatted_content: str
    scheduled_for: datetime
    auto_post: bool
    status: str


class CalendarListResponse(BaseModel):
    """List of calendar items."""

    items: list[CalendarItemResponse]
    total: int


class ReplyQueueResponse(BaseModel):
    """Reply queue item response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    mention_id: str
    mention_text: str
    mention_author: str
    mention_author_id: Optional[str]
    draft_reply: str
    final_reply: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime


class ReplyQueueListResponse(BaseModel):
    """List of reply queue items."""

    items: list[ReplyQueueResponse]
    total: int
    pending_count: int


class DocumentSectionResponse(BaseModel):
    """Document section response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    chapter_num: int
    chapter_title: str
    section_num: Optional[int]
    section_title: Optional[str]
    content: str
    subsections: Optional[list[dict]]
    keywords: Optional[list[str]]


class DocumentUploadResponse(BaseModel):
    """Response after uploading a document."""

    success: bool
    message: str
    chapters_count: int = 0
    sections_count: int = 0


class ChapterSummary(BaseModel):
    """Summary of a chapter."""

    chapter_num: int
    chapter_title: str
    sections_count: int = 0


class DocumentSummaryResponse(BaseModel):
    """Summary of loaded document."""

    is_loaded: bool
    total_sections: int = 0
    chapters: list[ChapterSummary] = Field(default_factory=list)


class TopicSuggestionResponse(BaseModel):
    """Topic suggestion response."""

    topic: str
    section_nums: list[int]
    angle: str
    reason: str


class GeneratedContentResponse(BaseModel):
    """Generated content response."""

    content_type: str
    raw_content: str
    formatted_content: str
    topic: Optional[str]
    citations: Optional[list[dict]]
    validation_errors: list[str] = Field(default_factory=list)
    validation_warnings: list[str] = Field(default_factory=list)
    queue_id: Optional[int] = None  # ID if added to queue


class HistoryResponse(BaseModel):
    """Post history item response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    tweet_id: str
    content: str
    content_type: str
    is_reply: bool
    reply_to_id: Optional[str]
    engagement: Optional[dict]
    posted_at: datetime


class HistoryListResponse(BaseModel):
    """List of post history items."""

    items: list[HistoryResponse]
    total: int


class StatsResponse(BaseModel):
    """Dashboard statistics response."""

    # Queue stats
    pending_content: int
    approved_content: int
    pending_replies: int

    # History stats
    total_posts: int
    tweets_posted: int
    threads_posted: int
    replies_posted: int

    # Document stats
    document_loaded: bool
    total_sections: int

    # Bot status
    bot_enabled: bool
    auto_generate_enabled: bool


class ValidationResponse(BaseModel):
    """Content validation response."""

    is_valid: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)


class MessageResponse(BaseModel):
    """Simple message response."""

    success: bool
    message: str
    data: Optional[Any] = None


class SimilarContentItem(BaseModel):
    """Similar content item for duplicate detection."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    topic: Optional[str]
    formatted_content: str
    similarity_score: float
    status: str
    created_at: datetime


class DuplicateCheckResponse(BaseModel):
    """Duplicate check response."""

    has_duplicates: bool
    similar_items: list[SimilarContentItem] = Field(default_factory=list)
    message: str


class SafetyCheckResponse(BaseModel):
    """Content safety check response."""

    level: str  # safe, caution, review_required, blocked
    is_safe: bool
    needs_review: bool
    is_blocked: bool
    concerns: list[str] = Field(default_factory=list)
    blocked_reason: Optional[str] = None


class EngagementAnalyticsResponse(BaseModel):
    """Engagement analytics response."""

    period_days: int
    posts_count: int
    total_likes: int
    total_retweets: int
    total_replies: int
    total_quotes: int
    total_impressions: int
    avg_likes: float
    avg_retweets: float
    avg_replies: float
    engagement_rate: float


class TopPostResponse(BaseModel):
    """Top performing post response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    tweet_id: str
    content: str
    content_type: str
    posted_at: datetime
    likes: int = 0
    retweets: int = 0
    replies: int = 0
    impressions: int = 0


class AnalyticsDashboardResponse(BaseModel):
    """Full analytics dashboard response."""

    analytics: EngagementAnalyticsResponse
    top_posts: list[TopPostResponse] = Field(default_factory=list)
