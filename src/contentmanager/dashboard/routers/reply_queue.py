"""Reply Queue API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from contentmanager.dashboard.auth import require_auth
from contentmanager.dashboard.schemas.requests import (
    ReplyApproveRequest,
    ReplyUpdateRequest,
)
from contentmanager.dashboard.schemas.responses import (
    GeneratedContentResponse,
    MessageResponse,
    ReplyQueueListResponse,
    ReplyQueueResponse,
)
from contentmanager.database import get_session
from contentmanager.database.models import ContentStatus
from contentmanager.database.repositories.reply_queue import ReplyQueueRepository

router = APIRouter(prefix="/api/replies", tags=["Reply Queue"])


@router.get("", response_model=ReplyQueueListResponse)
async def list_replies(
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
    _: str = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    """List reply queue items."""
    repo = ReplyQueueRepository(session)

    items = await repo.get_all(status=status, limit=limit, offset=offset)
    total = await repo.count(status=status)
    pending_count = await repo.count(status=ContentStatus.PENDING.value)

    return ReplyQueueListResponse(
        items=[ReplyQueueResponse.model_validate(item) for item in items],
        total=total,
        pending_count=pending_count,
    )


@router.get("/pending", response_model=ReplyQueueListResponse)
async def list_pending_replies(
    limit: int = 50,
    _: str = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    """List pending reply queue items."""
    repo = ReplyQueueRepository(session)

    items = await repo.get_pending(limit=limit)
    total = await repo.count(status=ContentStatus.PENDING.value)

    return ReplyQueueListResponse(
        items=[ReplyQueueResponse.model_validate(item) for item in items],
        total=total,
        pending_count=total,
    )


@router.get("/{item_id}", response_model=ReplyQueueResponse)
async def get_reply(
    item_id: int,
    _: str = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    """Get a single reply queue item."""
    repo = ReplyQueueRepository(session)
    item = await repo.get_by_id(item_id)

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reply queue item not found",
        )

    return ReplyQueueResponse.model_validate(item)


@router.patch("/{item_id}", response_model=ReplyQueueResponse)
async def update_reply(
    item_id: int,
    request: ReplyUpdateRequest,
    _: str = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    """Update a reply queue item."""
    repo = ReplyQueueRepository(session)

    item = await repo.update(
        item_id,
        draft_reply=request.draft_reply,
        final_reply=request.final_reply,
    )

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reply queue item not found",
        )

    return ReplyQueueResponse.model_validate(item)


@router.post("/{item_id}/approve", response_model=ReplyQueueResponse)
async def approve_reply(
    item_id: int,
    request: ReplyApproveRequest | None = None,
    _: str = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    """Approve a reply for posting."""
    repo = ReplyQueueRepository(session)

    final_reply = request.final_reply if request else None
    item = await repo.approve(item_id, final_reply=final_reply)

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reply queue item not found",
        )

    return ReplyQueueResponse.model_validate(item)


@router.post("/{item_id}/reject", response_model=ReplyQueueResponse)
async def reject_reply(
    item_id: int,
    _: str = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    """Reject a reply."""
    repo = ReplyQueueRepository(session)

    item = await repo.reject(item_id)

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reply queue item not found",
        )

    return ReplyQueueResponse.model_validate(item)


@router.post("/{item_id}/regenerate", response_model=GeneratedContentResponse)
async def regenerate_reply(
    item_id: int,
    _: str = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    """Regenerate the draft reply for an item."""
    from contentmanager.core.modes.user_provided import UserProvidedMode

    repo = ReplyQueueRepository(session)
    item = await repo.get_by_id(item_id)

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reply queue item not found",
        )

    # Regenerate reply
    mode = UserProvidedMode(session)
    content = await mode.regenerate_reply(
        mention_text=item.mention_text,
        mention_author=item.mention_author,
        previous_reply=item.draft_reply,
    )

    # Update the draft
    await repo.update(item_id, draft_reply=content.formatted_content)

    return GeneratedContentResponse(
        content_type=content.content_type,
        raw_content=content.raw_content,
        formatted_content=content.formatted_content,
        topic=content.topic,
        citations=content.citations,
        validation_errors=content.validation.errors if content.validation else [],
        validation_warnings=content.validation.warnings if content.validation else [],
    )


@router.delete("/{item_id}", response_model=MessageResponse)
async def delete_reply(
    item_id: int,
    _: str = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    """Delete a reply queue item."""
    repo = ReplyQueueRepository(session)

    success = await repo.delete(item_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reply queue item not found",
        )

    return MessageResponse(success=True, message="Reply deleted successfully")
