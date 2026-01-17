"""Request and response schemas for the chat API."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# Request schemas


class ConversationCreateRequest(BaseModel):
    """Request to create a new conversation."""

    mode: Optional[str] = Field(
        default=None,
        description="Initial mode for the conversation",
    )
    initial_topic: Optional[str] = Field(
        default=None,
        description="Initial topic to discuss",
    )
    initial_message: Optional[str] = Field(
        default=None,
        description="Initial message to start the conversation",
    )


class ChatMessageRequest(BaseModel):
    """Request to send a message in a conversation."""

    content: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="The message content",
    )
    message_type: str = Field(
        default="text",
        pattern="^(text|action)$",
        description="Type of message",
    )
    action: Optional[str] = Field(
        default=None,
        pattern="^(generate|refine|suggest_topics|explain)$",
        description="Explicit action to perform",
    )
    parameters: Optional[dict] = Field(
        default=None,
        description="Parameters for the action",
    )


class FinalizeContentRequest(BaseModel):
    """Request to finalize content and add to queue."""

    message_id: int = Field(
        ...,
        description="ID of the message containing the content",
    )
    edits: Optional[str] = Field(
        default=None,
        description="Optional final edits to the content",
    )
    content_type: Optional[str] = Field(
        default=None,
        pattern="^(tweet|thread|script)$",
        description="Override content type if needed",
    )


class ConversationUpdateRequest(BaseModel):
    """Request to update a conversation."""

    title: Optional[str] = Field(
        default=None,
        max_length=255,
        description="New title for the conversation",
    )
    status: Optional[str] = Field(
        default=None,
        pattern="^(active|completed|archived)$",
        description="New status for the conversation",
    )


# Response schemas


class CitationResponse(BaseModel):
    """Citation reference in a response."""

    section_num: Optional[int] = None
    section_title: Optional[str] = None
    chapter_num: Optional[int] = None
    chapter_title: Optional[str] = None


class ChatMessageResponse(BaseModel):
    """Response representing a chat message."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    conversation_id: int
    role: str
    message_type: str
    content: str
    structured_data: Optional[dict] = None
    citations: Optional[list[CitationResponse]] = None
    created_at: datetime


class ConversationResponse(BaseModel):
    """Response representing a conversation."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: str
    title: Optional[str] = None
    status: str
    mode: Optional[str] = None
    topic: Optional[str] = None
    context_sections: Optional[dict] = None
    created_at: datetime
    updated_at: datetime
    messages: list[ChatMessageResponse] = []
    message_count: int = 0


class ConversationListResponse(BaseModel):
    """Response for listing conversations."""

    conversations: list[ConversationResponse]
    total: int


class TopicSuggestionItem(BaseModel):
    """A single topic suggestion."""

    title: str
    sections: list[int]
    angle: str
    reason: str


class TopicSuggestionsResponse(BaseModel):
    """Response containing topic suggestions."""

    suggestions: list[TopicSuggestionItem]


class FinalizeContentResponse(BaseModel):
    """Response after finalizing content."""

    success: bool
    queue_id: Optional[int] = None
    message: str
