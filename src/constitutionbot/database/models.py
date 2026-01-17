"""SQLAlchemy database models."""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import JSON, Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all models."""

    pass


class ContentStatus(str, Enum):
    """Status for content queue items."""

    PENDING = "pending"
    APPROVED = "approved"
    SCHEDULED = "scheduled"
    REJECTED = "rejected"
    POSTED = "posted"


class ContentType(str, Enum):
    """Types of content that can be generated."""

    TWEET = "tweet"
    THREAD = "thread"
    SCRIPT = "script"


class ContentMode(str, Enum):
    """Modes for content generation."""

    BOT_PROPOSED = "bot_proposed"
    USER_PROVIDED = "user_provided"
    HISTORICAL = "historical"


class SALanguage(str, Enum):
    """South Africa's 11 official languages."""

    ENGLISH = "en"
    AFRIKAANS = "af"
    ISIZULU = "zu"
    ISIXHOSA = "xh"
    SEPEDI = "nso"  # Northern Sotho
    SETSWANA = "tn"
    SESOTHO = "st"  # Southern Sotho
    XITSONGA = "ts"
    SISWATI = "ss"
    TSHIVENDA = "ve"
    ISINDEBELE = "nr"

    @classmethod
    def get_display_name(cls, code: str) -> str:
        """Get the display name for a language code."""
        names = {
            "en": "English",
            "af": "Afrikaans",
            "zu": "isiZulu",
            "xh": "isiXhosa",
            "nso": "Sepedi (Northern Sotho)",
            "tn": "Setswana",
            "st": "Sesotho (Southern Sotho)",
            "ts": "Xitsonga",
            "ss": "siSwati",
            "ve": "Tshivenda",
            "nr": "isiNdebele",
        }
        return names.get(code, code)


class ContentQueue(Base):
    """Content queue - posts waiting for approval."""

    __tablename__ = "content_queue"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    content_type: Mapped[str] = mapped_column(String(50), default=ContentType.TWEET.value)
    raw_content: Mapped[str] = mapped_column(Text, nullable=False)
    formatted_content: Mapped[str] = mapped_column(Text, nullable=False)
    mode: Mapped[str] = mapped_column(String(50), default=ContentMode.BOT_PROPOSED.value)
    topic: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    citations: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    language: Mapped[str] = mapped_column(String(10), default=SALanguage.ENGLISH.value)
    status: Mapped[str] = mapped_column(String(50), default=ContentStatus.PENDING.value, index=True)
    admin_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    scheduled_for: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    auto_post: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<ContentQueue(id={self.id}, status={self.status}, topic={self.topic[:30] if self.topic else None})>"


class ReplyQueue(Base):
    """Reply queue - replies to @mentions waiting for approval."""

    __tablename__ = "reply_queue"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mention_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    mention_text: Mapped[str] = mapped_column(Text, nullable=False)
    mention_author: Mapped[str] = mapped_column(String(100), nullable=False)
    mention_author_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    draft_reply: Mapped[str] = mapped_column(Text, nullable=False)
    final_reply: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default=ContentStatus.PENDING.value, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<ReplyQueue(id={self.id}, status={self.status}, author={self.mention_author})>"


class PostHistory(Base):
    """Post history - what's been posted to Twitter."""

    __tablename__ = "post_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tweet_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_type: Mapped[str] = mapped_column(String(50), default=ContentType.TWEET.value)
    is_reply: Mapped[bool] = mapped_column(default=False)
    reply_to_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    engagement: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    posted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<PostHistory(id={self.id}, tweet_id={self.tweet_id})>"


class ConstitutionSection(Base):
    """Parsed Constitution sections."""

    __tablename__ = "constitution_sections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chapter_num: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    chapter_title: Mapped[str] = mapped_column(String(500), nullable=False)
    section_num: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    section_title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    subsections: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    keywords: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    def __repr__(self) -> str:
        return f"<ConstitutionSection(chapter={self.chapter_num}, section={self.section_num})>"


class BotSettings(Base):
    """Bot configuration settings stored in database."""

    __tablename__ = "bot_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<BotSettings(key={self.key})>"
