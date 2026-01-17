"""Content suggestion and generation API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from contentmanager.core.modes.bot_proposed import BotProposedMode
from contentmanager.core.modes.historical import HistoricalMode
from contentmanager.core.modes.user_provided import UserProvidedMode
from contentmanager.core.safety.filters import ContentFilter
from contentmanager.core.content.question_generator import QuestionGenerator
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


# ========================================================================
# INTERACTIVE QUESTION ENDPOINTS
# ========================================================================


class QuestionRequest(BaseModel):
    """Request for pre-generation questions."""
    topic: str
    content_type: str = "tweet"
    max_questions: int = 4


class QuestionOption(BaseModel):
    """An option for a question."""
    label: str
    value: str


class QuestionResponse(BaseModel):
    """A question to ask the user."""
    question: str
    category: str
    options: list[QuestionOption]
    allows_custom: bool = True
    help_text: str | None = None


class QuestionsResponse(BaseModel):
    """Response containing questions."""
    questions: list[QuestionResponse]
    topic: str
    content_type: str


@router.post("/questions", response_model=QuestionsResponse)
async def get_pre_generation_questions(
    request: QuestionRequest,
    _: str = Depends(require_auth),
):
    """Get questions to ask before generating content.

    These questions help tailor the generated content to the user's needs.
    """
    generator = QuestionGenerator()
    questions = generator.get_pre_generation_questions(
        topic=request.topic,
        content_type=request.content_type,
        max_questions=request.max_questions,
    )

    return QuestionsResponse(
        questions=[
            QuestionResponse(
                question=q.question,
                category=q.category.value,
                options=[
                    QuestionOption(label=opt, value=opt.lower().replace(" ", "_"))
                    for opt in q.options
                ],
                allows_custom=q.allows_custom,
                help_text=q.help_text,
            )
            for q in questions
        ],
        topic=request.topic,
        content_type=request.content_type,
    )


class EnhancementRequest(BaseModel):
    """Request for enhancement suggestions."""
    content: str
    content_type: str
    topic: str
    max_suggestions: int = 4


class EnhancementResponse(BaseModel):
    """An enhancement suggestion."""
    suggestion: str
    action: str
    category: str
    prompt_modifier: str


class EnhancementsResponse(BaseModel):
    """Response containing enhancement suggestions."""
    suggestions: list[EnhancementResponse]
    topic: str
    content_type: str


@router.post("/enhancements", response_model=EnhancementsResponse)
async def get_enhancement_suggestions(
    request: EnhancementRequest,
    _: str = Depends(require_auth),
):
    """Get suggestions for enhancing generated content.

    Returns actionable suggestions for improving the content.
    """
    generator = QuestionGenerator()
    suggestions = generator.get_enhancement_suggestions(
        content=request.content,
        content_type=request.content_type,
        topic=request.topic,
        max_suggestions=request.max_suggestions,
    )

    return EnhancementsResponse(
        suggestions=[
            EnhancementResponse(
                suggestion=s.suggestion,
                action=s.action,
                category=s.category,
                prompt_modifier=s.prompt_modifier,
            )
            for s in suggestions
        ],
        topic=request.topic,
        content_type=request.content_type,
    )


class EnhancedGenerateRequest(BaseModel):
    """Request to generate content with question answers."""
    topic: str
    content_type: str = "tweet"
    answers: dict[str, str] = {}  # category -> answer
    section_nums: list[int] | None = None
    num_tweets: int = 5
    duration: str = "2-3 minutes"
    language: str = "en"


@router.post("/topic-enhanced", response_model=GeneratedContentResponse)
async def generate_enhanced_content(
    request: EnhancedGenerateRequest,
    add_to_queue: bool = True,
    _: str = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    """Generate content using answers to clarifying questions.

    This endpoint takes the user's answers to pre-generation questions
    and uses them to create more tailored content.
    """
    # Check if document is loaded
    doc_repo = DocumentSectionRepository(session)
    if not await doc_repo.has_content():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document not loaded. Please upload a document first.",
        )

    # Build enhanced parameters from answers
    question_gen = QuestionGenerator()
    enhanced_params = question_gen.build_enhanced_prompt(
        base_topic=request.topic,
        answers=request.answers,
        content_type=request.content_type,
    )

    # Build an enhanced topic that includes the user's preferences
    enhanced_topic = request.topic
    if enhanced_params.get("enhancement_instructions"):
        enhanced_topic = f"{request.topic}\n\nAdditional guidance:\n{enhanced_params['enhancement_instructions']}"

    # Generate using UserProvidedMode
    mode = UserProvidedMode(session)

    if request.content_type == "thread":
        content = await mode.generate_thread(
            topic=enhanced_topic,
            num_tweets=request.num_tweets,
            section_nums=request.section_nums,
        )
    elif request.content_type == "script":
        content = await mode.generate_script(
            topic=enhanced_topic,
            duration=request.duration,
            section_nums=request.section_nums,
        )
    else:
        content = await mode.generate_tweet(
            topic=enhanced_topic,
            section_nums=request.section_nums,
        )

    queue_id = None
    if add_to_queue:
        queue_repo = ContentQueueRepository(session)
        item = await queue_repo.create(
            raw_content=content.raw_content,
            formatted_content=content.formatted_content,
            content_type=content.content_type,
            mode=content.mode,
            topic=request.topic,  # Store original topic, not enhanced
            citations=content.citations,
            language=request.language,
        )
        queue_id = item.id

    return GeneratedContentResponse(
        content_type=content.content_type,
        raw_content=content.raw_content,
        formatted_content=content.formatted_content,
        topic=request.topic,
        citations=content.citations,
        validation_errors=content.validation.errors if content.validation else [],
        validation_warnings=content.validation.warnings if content.validation else [],
        queue_id=queue_id,
    )


# ========================================================================
# REPLY TO EXTERNAL TWEET ENDPOINTS
# ========================================================================


class ExternalTweetReplyRequest(BaseModel):
    """Request for generating a reply to an external tweet."""
    tweet_text: str
    author: str = "unknown"
    stance: str  # 'agree', 'disagree', or 'neutral'
    tone: str = "respectful but firm"
    focus: str | None = None


class ExternalTweetReplyResponse(BaseModel):
    """Response containing the generated reply."""
    reply: str
    stance: str
    author: str
    original_tweet: str
    citations: list[dict]
    validation_errors: list[str]
    validation_warnings: list[str]


@router.post("/reply-to-tweet", response_model=ExternalTweetReplyResponse)
async def generate_reply_to_tweet(
    request: ExternalTweetReplyRequest,
    _: str = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    """Generate a reply to an external tweet based on constitutional principles.

    This allows users to craft responses to tweets they agree or disagree with,
    using the Constitution as a basis for their argument.

    Stances:
    - agree: Reinforce the tweet's position using constitutional principles
    - disagree: Respectfully challenge the position using constitutional principles
    - neutral: Present relevant constitutional principles without taking sides
    """
    # Validate stance
    valid_stances = ["agree", "disagree", "neutral"]
    if request.stance.lower() not in valid_stances:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid stance. Must be one of: {', '.join(valid_stances)}",
        )

    # Check if document is loaded
    doc_repo = DocumentSectionRepository(session)
    if not await doc_repo.has_content():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document not loaded. Please upload a document first.",
        )

    mode = UserProvidedMode(session)
    content = await mode.generate_external_tweet_reply(
        tweet_text=request.tweet_text,
        author=request.author,
        stance=request.stance.lower(),
        tone=request.tone,
        focus=request.focus,
    )

    return ExternalTweetReplyResponse(
        reply=content.formatted_content,
        stance=request.stance.lower(),
        author=request.author,
        original_tweet=request.tweet_text,
        citations=[
            {"section_num": c.section_num, "title": c.title}
            for c in content.citations
        ],
        validation_errors=content.validation.errors if content.validation else [],
        validation_warnings=content.validation.warnings if content.validation else [],
    )
