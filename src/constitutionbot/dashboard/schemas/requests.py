"""Request schemas for the dashboard API."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Login request."""

    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class ContentUpdateRequest(BaseModel):
    """Update content queue item."""

    formatted_content: Optional[str] = Field(default=None)
    admin_notes: Optional[str] = Field(default=None)


class ContentApproveRequest(BaseModel):
    """Approve content for posting."""

    admin_notes: Optional[str] = Field(default=None)


class ContentGenerateRequest(BaseModel):
    """Generate new content."""

    topic: str = Field(..., min_length=1, description="Topic for content generation")
    content_type: str = Field(default="tweet", pattern="^(tweet|thread)$")
    num_tweets: int = Field(default=5, ge=2, le=10, description="Number of tweets for threads")
    section_nums: Optional[list[int]] = Field(
        default=None, description="Specific section numbers to reference"
    )
    mode: str = Field(
        default="user_provided",
        pattern="^(bot_proposed|user_provided|historical)$",
    )


class ReplyUpdateRequest(BaseModel):
    """Update reply queue item."""

    draft_reply: Optional[str] = Field(default=None)
    final_reply: Optional[str] = Field(default=None)


class ReplyApproveRequest(BaseModel):
    """Approve reply for posting."""

    final_reply: Optional[str] = Field(default=None, description="Final edited reply")


class ReplyRegenerateRequest(BaseModel):
    """Request to regenerate a reply."""

    pass


class TopicSuggestRequest(BaseModel):
    """Request for topic suggestion."""

    content_type: str = Field(default="tweet", pattern="^(tweet|thread)$")
    generate_content: bool = Field(
        default=True, description="Whether to generate content immediately"
    )


class ExplainSectionRequest(BaseModel):
    """Request to explain a specific section."""

    section_num: int = Field(..., ge=1, le=243)
    content_type: str = Field(default="tweet", pattern="^(tweet|thread)$")


class HistoricalContentRequest(BaseModel):
    """Request for historical event content."""

    event: str = Field(..., min_length=1, description="Historical event description")
    content_type: str = Field(default="tweet", pattern="^(tweet|thread)$")


class SettingsUpdateRequest(BaseModel):
    """Update bot settings."""

    bot_enabled: Optional[bool] = Field(default=None)
    mention_check_interval: Optional[int] = Field(default=None, ge=30, le=3600)
    auto_generate_enabled: Optional[bool] = Field(default=None)
    auto_generate_interval: Optional[int] = Field(default=None, ge=300, le=86400)


class ScheduleContentRequest(BaseModel):
    """Schedule content for future posting."""

    scheduled_for: datetime = Field(..., description="Date and time to post the content")
    auto_post: bool = Field(default=False, description="Whether to automatically post at scheduled time")
