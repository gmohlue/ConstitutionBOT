"""Content suggestion and generation API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from contentmanager.core.modes.bot_proposed import BotProposedMode
from contentmanager.core.modes.historical import HistoricalMode
from contentmanager.core.modes.user_provided import UserProvidedMode
from contentmanager.core.safety.filters import ContentFilter
from contentmanager.dashboard.auth import require_auth
from contentmanager.dashboard.schemas.requests import (
    ContentGenerateRequest,
    ExplainSectionRequest,
    HistoricalContentRequest,
    TopicSuggestRequest,
)
from contentmanager.dashboard.schemas.responses import (
    GeneratedContentResponse,
    SafetyCheckResponse,
    TopicSuggestionResponse,
)
from contentmanager.database import get_session
from contentmanager.database.repositories.document import DocumentSectionRepository
from contentmanager.database.repositories.content_queue import ContentQueueRepository

router = APIRouter(prefix="/api/generate", tags=["Content Generation"])


@router.post("/suggest", response_model=TopicSuggestionResponse)
async def suggest_topic(
    request: TopicSuggestRequest | None = None,
    _: str = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    """Get a topic suggestion from the bot."""
    # Check if document is loaded
    doc_repo = DocumentSectionRepository(session)
    if not await doc_repo.has_content():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document not loaded. Please upload a document first.",
        )

    mode = BotProposedMode(session)
    suggestion = await mode.suggest_only()

    return TopicSuggestionResponse(
        topic=suggestion.topic,
        section_nums=suggestion.section_nums,
        angle=suggestion.angle,
        reason=suggestion.reason,
    )


@router.post("/topic", response_model=GeneratedContentResponse)
async def generate_content(
    request: ContentGenerateRequest,
    add_to_queue: bool = True,
    _: str = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    """Generate content for a topic."""
    # Check if document is loaded
    doc_repo = DocumentSectionRepository(session)
    if not await doc_repo.has_content():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document not loaded. Please upload a document first.",
        )

    # Select mode
    if request.mode == "bot_proposed":
        mode = BotProposedMode(session)
        result = await mode.suggest_and_generate(
            content_type=request.content_type,
            num_tweets=request.num_tweets,
        )
        content = result.content
    elif request.mode == "historical":
        mode = HistoricalMode(session)
        content = await mode.generate_for_custom_event(
            event_description=request.topic,
            content_type=request.content_type,
        )
    else:  # user_provided
        mode = UserProvidedMode(session)
        if request.content_type == "thread":
            content = await mode.generate_thread(
                topic=request.topic,
                num_tweets=request.num_tweets,
                section_nums=request.section_nums,
            )
        elif request.content_type == "script":
            content = await mode.generate_script(
                topic=request.topic,
                duration=request.duration,
                section_nums=request.section_nums,
            )
        else:
            content = await mode.generate_tweet(
                topic=request.topic,
                section_nums=request.section_nums,
            )

    queue_id = None
    if add_to_queue:
        # Add to content queue
        queue_repo = ContentQueueRepository(session)
        item = await queue_repo.create(
            raw_content=content.raw_content,
            formatted_content=content.formatted_content,
            content_type=content.content_type,
            mode=content.mode,
            topic=content.topic,
            citations=content.citations,
            language=request.language,
        )
        queue_id = item.id

    return GeneratedContentResponse(
        content_type=content.content_type,
        raw_content=content.raw_content,
        formatted_content=content.formatted_content,
        topic=content.topic,
        citations=content.citations,
        validation_errors=content.validation.errors if content.validation else [],
        validation_warnings=content.validation.warnings if content.validation else [],
        queue_id=queue_id,
    )


@router.post("/explain", response_model=GeneratedContentResponse)
async def explain_section(
    request: ExplainSectionRequest,
    add_to_queue: bool = True,
    _: str = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    """Generate an explanation for a specific section."""
    # Check if document is loaded
    doc_repo = DocumentSectionRepository(session)
    if not await doc_repo.has_content():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document not loaded. Please upload a document first.",
        )

    # Verify section exists
    section = await doc_repo.get_by_section_num(request.section_num)
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Section {request.section_num} not found",
        )

    mode = UserProvidedMode(session)
    content = await mode.explain_section(
        section_num=request.section_num,
        content_type=request.content_type,
    )

    queue_id = None
    if add_to_queue:
        queue_repo = ContentQueueRepository(session)
        item = await queue_repo.create(
            raw_content=content.raw_content,
            formatted_content=content.formatted_content,
            content_type=content.content_type,
            mode=content.mode,
            topic=content.topic,
            citations=content.citations,
        )
        queue_id = item.id

    return GeneratedContentResponse(
        content_type=content.content_type,
        raw_content=content.raw_content,
        formatted_content=content.formatted_content,
        topic=content.topic,
        citations=content.citations,
        validation_errors=content.validation.errors if content.validation else [],
        validation_warnings=content.validation.warnings if content.validation else [],
        queue_id=queue_id,
    )


@router.post("/historical", response_model=GeneratedContentResponse)
async def generate_historical_content(
    request: HistoricalContentRequest,
    add_to_queue: bool = True,
    _: str = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    """Generate content about a historical event."""
    # Check if document is loaded
    doc_repo = DocumentSectionRepository(session)
    if not await doc_repo.has_content():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document not loaded. Please upload a document first.",
        )

    mode = HistoricalMode(session)
    content = await mode.generate_for_custom_event(
        event_description=request.event,
        content_type=request.content_type,
    )

    queue_id = None
    if add_to_queue:
        queue_repo = ContentQueueRepository(session)
        item = await queue_repo.create(
            raw_content=content.raw_content,
            formatted_content=content.formatted_content,
            content_type=content.content_type,
            mode="historical",
            topic=content.topic,
            citations=content.citations,
        )
        queue_id = item.id

    return GeneratedContentResponse(
        content_type=content.content_type,
        raw_content=content.raw_content,
        formatted_content=content.formatted_content,
        topic=content.topic,
        citations=content.citations,
        validation_errors=content.validation.errors if content.validation else [],
        validation_warnings=content.validation.warnings if content.validation else [],
        queue_id=queue_id,
    )


@router.post("/auto", response_model=GeneratedContentResponse)
async def auto_generate(
    content_type: str = "tweet",
    _: str = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    """Auto-generate content (bot suggests topic and generates)."""
    # Check if document is loaded
    doc_repo = DocumentSectionRepository(session)
    if not await doc_repo.has_content():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document not loaded. Please upload a document first.",
        )

    mode = BotProposedMode(session)
    result = await mode.suggest_and_generate(content_type=content_type)
    content = result.content

    # Add to queue
    queue_repo = ContentQueueRepository(session)
    item = await queue_repo.create(
        raw_content=content.raw_content,
        formatted_content=content.formatted_content,
        content_type=content.content_type,
        mode="bot_proposed",
        topic=content.topic,
        citations=content.citations,
    )

    return GeneratedContentResponse(
        content_type=content.content_type,
        raw_content=content.raw_content,
        formatted_content=content.formatted_content,
        topic=content.topic,
        citations=content.citations,
        validation_errors=content.validation.errors if content.validation else [],
        validation_warnings=content.validation.warnings if content.validation else [],
        queue_id=item.id,
    )


class SafetyCheckRequest(BaseModel):
    """Request body for safety check."""

    content: str


@router.post("/safety-check", response_model=SafetyCheckResponse)
async def check_content_safety(
    request: SafetyCheckRequest,
    _: str = Depends(require_auth),
):
    """Check content for safety issues including profanity and sensitive topics.

    Returns safety level and any concerns found.
    """
    content_filter = ContentFilter()
    result = content_filter.filter(request.content)

    return SafetyCheckResponse(
        level=result.level.value,
        is_safe=result.is_safe,
        needs_review=result.needs_review,
        is_blocked=result.is_blocked,
        concerns=result.concerns,
        blocked_reason=result.blocked_reason,
    )
