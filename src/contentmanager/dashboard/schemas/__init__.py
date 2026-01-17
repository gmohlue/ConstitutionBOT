"""API schemas for the dashboard."""

from contentmanager.dashboard.schemas.chat import (
    ChatMessageRequest,
    ChatMessageResponse,
    ConversationCreateRequest,
    ConversationListResponse,
    ConversationResponse,
    ConversationUpdateRequest,
    FinalizeContentRequest,
    FinalizeContentResponse,
    TopicSuggestionItem,
    TopicSuggestionsResponse,
)
from contentmanager.dashboard.schemas.requests import (
    ContentApproveRequest,
    ContentGenerateRequest,
    ContentUpdateRequest,
    LoginRequest,
    ReplyApproveRequest,
    ReplyRegenerateRequest,
    ReplyUpdateRequest,
    TopicSuggestRequest,
)
from contentmanager.dashboard.schemas.responses import (
    ContentQueueResponse,
    DocumentSectionResponse,
    DocumentUploadResponse,
    HistoryResponse,
    ReplyQueueResponse,
    StatsResponse,
    TopicSuggestionResponse,
)

__all__ = [
    # Requests
    "LoginRequest",
    "ContentUpdateRequest",
    "ContentApproveRequest",
    "ContentGenerateRequest",
    "ReplyUpdateRequest",
    "ReplyApproveRequest",
    "ReplyRegenerateRequest",
    "TopicSuggestRequest",
    # Chat requests
    "ConversationCreateRequest",
    "ChatMessageRequest",
    "FinalizeContentRequest",
    "ConversationUpdateRequest",
    # Responses
    "ContentQueueResponse",
    "ReplyQueueResponse",
    "DocumentSectionResponse",
    "DocumentUploadResponse",
    "TopicSuggestionResponse",
    "HistoryResponse",
    "StatsResponse",
    # Chat responses
    "ConversationResponse",
    "ConversationListResponse",
    "ChatMessageResponse",
    "TopicSuggestionsResponse",
    "TopicSuggestionItem",
    "FinalizeContentResponse",
]
