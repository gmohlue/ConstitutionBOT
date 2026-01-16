"""API schemas for the dashboard."""

from constitutionbot.dashboard.schemas.requests import (
    ContentApproveRequest,
    ContentGenerateRequest,
    ContentUpdateRequest,
    LoginRequest,
    ReplyApproveRequest,
    ReplyRegenerateRequest,
    ReplyUpdateRequest,
    TopicSuggestRequest,
)
from constitutionbot.dashboard.schemas.responses import (
    ContentQueueResponse,
    ConstitutionSectionResponse,
    ConstitutionUploadResponse,
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
    # Responses
    "ContentQueueResponse",
    "ReplyQueueResponse",
    "ConstitutionSectionResponse",
    "ConstitutionUploadResponse",
    "TopicSuggestionResponse",
    "HistoryResponse",
    "StatsResponse",
]
