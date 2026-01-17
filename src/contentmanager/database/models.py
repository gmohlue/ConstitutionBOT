"""SQLAlchemy database models."""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import JSON, Boolean, DateTime, Integer, String, Text, UniqueConstraint, func
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


class ConversationStatus(str, Enum):
    """Status for chat conversations."""

    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class MessageRole(str, Enum):
    """Role of a message sender in a conversation."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageType(str, Enum):
    """Type of message content."""

    TEXT = "text"
    TOPIC_SUGGESTION = "topic_suggestion"
    GENERATED_CONTENT = "generated_content"
    ACTION = "action"


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


class DocumentStructureType(str, Enum):
    """Types of document structures for parsing."""

    CHAPTER_SECTION = "chapter_section"  # e.g., Constitution (Chapter X, Section Y)
    ARTICLE = "article"  # e.g., Legal documents (Article 1, 2, 3)
    NUMBERED_LIST = "numbered_list"  # e.g., Policies (1., 2., 3.)
    HEADING_BASED = "heading_based"  # Parse by headings
    CUSTOM = "custom"  # Custom regex patterns


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


class Document(Base):
    """Document metadata - supports multiple source documents."""

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    short_name: Mapped[str] = mapped_column(String(100), nullable=False)  # For prompts
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    structure_type: Mapped[str] = mapped_column(
        String(50), default=DocumentStructureType.CHAPTER_SECTION.value
    )
    section_label: Mapped[str] = mapped_column(String(50), default="Section")  # "Section", "Article", etc.
    section_count: Mapped[int] = mapped_column(Integer, default=0)
    chapter_count: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    # Document-specific configuration (topic vocabulary, keywords, etc.)
    config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # Custom prompt templates (if different from defaults)
    custom_prompts: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # Historical events specific to this document
    historical_events: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    # Default hashtags for this document
    default_hashtags: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<Document(id={self.id}, name={self.short_name})>"


class DocumentSection(Base):
    """Parsed document sections - supports any document type."""

    __tablename__ = "document_sections"
    __table_args__ = (
        UniqueConstraint("document_id", "section_num", name="uq_document_section"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    chapter_num: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    chapter_title: Mapped[str] = mapped_column(String(500), nullable=False)
    section_num: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    section_title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    subsections: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    keywords: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    def __repr__(self) -> str:
        return f"<DocumentSection(doc={self.document_id}, chapter={self.chapter_num}, section={self.section_num})>"



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


class Conversation(Base):
    """Chat conversation for interactive Q&A and content generation."""

    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), default=ConversationStatus.ACTIVE.value, index=True
    )
    mode: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    topic: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    context_sections: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<Conversation(id={self.id}, status={self.status}, title={self.title[:30] if self.title else None})>"


class ConversationMessage(Base):
    """Individual message in a chat conversation."""

    __tablename__ = "conversation_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    message_type: Mapped[str] = mapped_column(
        String(50), default=MessageType.TEXT.value
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    structured_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    citations: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<ConversationMessage(id={self.id}, role={self.role}, conversation_id={self.conversation_id})>"


class Session(Base):
    """User session for dashboard authentication."""

    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    token: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)

    def __repr__(self) -> str:
        return f"<Session(id={self.id}, expires_at={self.expires_at})>"
