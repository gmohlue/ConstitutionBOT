"""Chat API endpoints for interactive conversations."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from contentmanager.core.chat.service import ChatService
from contentmanager.dashboard.auth import get_current_session, require_auth
from contentmanager.dashboard.schemas.chat import (
    ChatMessageRequest,
    ChatMessageResponse,
    ConversationCreateRequest,
    ConversationListResponse,
    ConversationResponse,
    ConversationUpdateRequest,
    FinalizeContentRequest,
    FinalizeContentResponse,
)
from contentmanager.database import get_session
from contentmanager.database.models import (
    ContentStatus,
    MessageRole,
    MessageType,
)
from contentmanager.database.repositories.content_queue import ContentQueueRepository
from contentmanager.database.repositories.conversation import (
    ConversationRepository,
    MessageRepository,
)

router = APIRouter(prefix="/api/chat", tags=["Chat"])


def _message_to_response(message) -> ChatMessageResponse:
    """Convert a database message to a response schema."""
    return ChatMessageResponse(
        id=message.id,
        conversation_id=message.conversation_id,
        role=message.role,
        message_type=message.message_type,
        content=message.content,
        structured_data=message.structured_data,
        citations=message.citations,
        created_at=message.created_at,
    )


def _conversation_to_response(
    conversation, messages=None, message_count: int = 0
) -> ConversationResponse:
    """Convert a database conversation to a response schema."""
    return ConversationResponse(
        id=conversation.id,
        session_id=conversation.session_id,
        title=conversation.title,
        status=conversation.status,
        mode=conversation.mode,
        topic=conversation.topic,
        context_sections=conversation.context_sections,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        messages=[_message_to_response(m) for m in (messages or [])],
        message_count=message_count,
    )


@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    request: ConversationCreateRequest,
    session_token: str = Depends(require_auth),
    db_session: AsyncSession = Depends(get_session),
):
    """Create a new chat conversation."""
    conv_repo = ConversationRepository(db_session)
    msg_repo = MessageRepository(db_session)

    # Create the conversation
    conversation = await conv_repo.create(
        session_id=session_token,
        title=request.initial_topic or "New Conversation",
        mode=request.mode,
        topic=request.initial_topic,
    )

    messages = []

    # If there's an initial message, process it
    if request.initial_message:
        # Save user message
        user_message = await msg_repo.create(
            conversation_id=conversation.id,
            role=MessageRole.USER.value,
            content=request.initial_message,
        )
        messages.append(user_message)

        # Generate response
        chat_service = ChatService(db_session)
        response = await chat_service.process_message(
            conversation_id=conversation.id,
            user_message=request.initial_message,
        )

        # Save assistant response
        assistant_message = await msg_repo.create(
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT.value,
            content=response.content,
            message_type=response.message_type,
            structured_data=response.structured_data,
            citations=response.citations,
        )
        messages.append(assistant_message)

        # Update conversation title if topic was extracted
        if response.structured_data and response.structured_data.get("topic"):
            await conv_repo.update(
                conversation.id,
                title=response.structured_data["topic"][:100],
                topic=response.structured_data["topic"],
            )

    await db_session.commit()

    return _conversation_to_response(conversation, messages, len(messages))


@router.get("/conversations", response_model=ConversationListResponse)
async def list_conversations(
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
    session_token: str = Depends(require_auth),
    db_session: AsyncSession = Depends(get_session),
):
    """List conversations for the current session."""
    conv_repo = ConversationRepository(db_session)
    msg_repo = MessageRepository(db_session)

    conversations = await conv_repo.get_by_session(
        session_id=session_token,
        status=status,
        limit=limit,
        offset=offset,
    )

    # Get message counts for each conversation
    response_items = []
    for conv in conversations:
        count = await msg_repo.count_by_conversation(conv.id)
        response_items.append(_conversation_to_response(conv, message_count=count))

    return ConversationListResponse(
        conversations=response_items,
        total=len(conversations),
    )


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    _: str = Depends(require_auth),
    db_session: AsyncSession = Depends(get_session),
):
    """Get a conversation with all its messages."""
    conv_repo = ConversationRepository(db_session)
    msg_repo = MessageRepository(db_session)

    conversation = await conv_repo.get_by_id(conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    messages = await msg_repo.get_by_conversation(conversation_id)

    return _conversation_to_response(conversation, messages, len(messages))


@router.patch("/conversations/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: int,
    request: ConversationUpdateRequest,
    _: str = Depends(require_auth),
    db_session: AsyncSession = Depends(get_session),
):
    """Update a conversation's title or status."""
    conv_repo = ConversationRepository(db_session)
    msg_repo = MessageRepository(db_session)

    conversation = await conv_repo.update(
        conversation_id,
        title=request.title,
        status=request.status,
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    await db_session.commit()

    count = await msg_repo.count_by_conversation(conversation_id)
    return _conversation_to_response(conversation, message_count=count)


@router.delete("/conversations/{conversation_id}")
async def archive_conversation(
    conversation_id: int,
    _: str = Depends(require_auth),
    db_session: AsyncSession = Depends(get_session),
):
    """Archive (soft delete) a conversation."""
    conv_repo = ConversationRepository(db_session)

    conversation = await conv_repo.archive(conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    await db_session.commit()

    return {"success": True, "message": "Conversation archived"}


@router.post(
    "/conversations/{conversation_id}/messages", response_model=ChatMessageResponse
)
async def send_message(
    conversation_id: int,
    request: ChatMessageRequest,
    _: str = Depends(require_auth),
    db_session: AsyncSession = Depends(get_session),
):
    """Send a message in a conversation and get a response."""
    conv_repo = ConversationRepository(db_session)
    msg_repo = MessageRepository(db_session)

    # Verify conversation exists
    conversation = await conv_repo.get_by_id(conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    # Save user message
    user_message = await msg_repo.create(
        conversation_id=conversation_id,
        role=MessageRole.USER.value,
        content=request.content,
        message_type=request.message_type,
    )

    # Process with chat service
    chat_service = ChatService(db_session)
    response = await chat_service.process_message(
        conversation_id=conversation_id,
        user_message=request.content,
        action=request.action,
        parameters=request.parameters,
    )

    # Save assistant response
    assistant_message = await msg_repo.create(
        conversation_id=conversation_id,
        role=MessageRole.ASSISTANT.value,
        content=response.content,
        message_type=response.message_type,
        structured_data=response.structured_data,
        citations=response.citations,
    )

    # Update conversation topic/title if we extracted one
    if response.structured_data:
        topic = response.structured_data.get("topic")
        if topic and not conversation.topic:
            await conv_repo.update(
                conversation_id,
                title=topic[:100],
                topic=topic,
            )

    await db_session.commit()

    return _message_to_response(assistant_message)


@router.post(
    "/conversations/{conversation_id}/finalize", response_model=FinalizeContentResponse
)
async def finalize_content(
    conversation_id: int,
    request: FinalizeContentRequest,
    _: str = Depends(require_auth),
    db_session: AsyncSession = Depends(get_session),
):
    """Finalize generated content and add it to the content queue."""
    conv_repo = ConversationRepository(db_session)
    msg_repo = MessageRepository(db_session)

    # Verify conversation exists
    conversation = await conv_repo.get_by_id(conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    # Get the message with generated content
    message = await msg_repo.get_by_id(request.message_id)
    if not message or message.conversation_id != conversation_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found in this conversation",
        )

    if message.message_type != MessageType.GENERATED_CONTENT.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This message does not contain generated content",
        )

    if not message.structured_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message has no structured data",
        )

    # Extract content from message
    formatted_content = request.edits or message.structured_data.get(
        "formatted_content", ""
    )
    raw_content = message.structured_data.get("raw_content", formatted_content)
    content_type = request.content_type or message.structured_data.get(
        "content_type", "tweet"
    )
    topic = message.structured_data.get("topic", conversation.topic)

    # Add to content queue
    queue_repo = ContentQueueRepository(db_session)
    queue_item = await queue_repo.create(
        raw_content=raw_content,
        formatted_content=formatted_content,
        content_type=content_type,
        mode="user_provided",
        topic=topic,
        citations=message.citations,
        language="en",
    )

    # Add a message noting the finalization
    await msg_repo.create(
        conversation_id=conversation_id,
        role=MessageRole.ASSISTANT.value,
        content=f"Content added to queue (ID: {queue_item.id}). You can review and approve it in the Content Queue page.",
        message_type=MessageType.ACTION.value,
        structured_data={
            "action": "finalized",
            "queue_id": queue_item.id,
            "content_type": content_type,
        },
    )

    await db_session.commit()

    return FinalizeContentResponse(
        success=True,
        queue_id=queue_item.id,
        message=f"Content added to queue (ID: {queue_item.id})",
    )


@router.get("/conversations/{conversation_id}/generated-content")
async def list_generated_content(
    conversation_id: int,
    _: str = Depends(require_auth),
    db_session: AsyncSession = Depends(get_session),
):
    """List all generated content in a conversation."""
    conv_repo = ConversationRepository(db_session)
    msg_repo = MessageRepository(db_session)

    # Verify conversation exists
    conversation = await conv_repo.get_by_id(conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    messages = await msg_repo.get_generated_content_messages(conversation_id)

    return {
        "conversation_id": conversation_id,
        "generated_content": [_message_to_response(m) for m in messages],
        "count": len(messages),
    }
