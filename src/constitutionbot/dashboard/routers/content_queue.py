"""Content Queue API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from constitutionbot.dashboard.auth import require_auth
from constitutionbot.dashboard.schemas.requests import (
    ContentApproveRequest,
    ContentUpdateRequest,
)
from constitutionbot.dashboard.schemas.responses import (
    ContentQueueListResponse,
    ContentQueueResponse,
    MessageResponse,
)
from constitutionbot.database import get_session
from constitutionbot.database.models import ContentStatus
from constitutionbot.database.repositories.content_queue import ContentQueueRepository

router = APIRouter(prefix="/api/queue", tags=["Content Queue"])


@router.get("", response_model=ContentQueueListResponse)
async def list_queue(
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
    _: str = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    """List content queue items."""
    repo = ContentQueueRepository(session)

    items = await repo.get_all(status=status, limit=limit, offset=offset)
    total = await repo.count(status=status)
    pending_count = await repo.count(status=ContentStatus.PENDING.value)
    approved_count = await repo.count(status=ContentStatus.APPROVED.value)

    return ContentQueueListResponse(
        items=[ContentQueueResponse.model_validate(item) for item in items],
        total=total,
        pending_count=pending_count,
        approved_count=approved_count,
    )


@router.get("/pending", response_model=ContentQueueListResponse)
async def list_pending(
    limit: int = 50,
    _: str = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    """List pending content queue items."""
    repo = ContentQueueRepository(session)

    items = await repo.get_pending(limit=limit)
    total = await repo.count(status=ContentStatus.PENDING.value)

    return ContentQueueListResponse(
        items=[ContentQueueResponse.model_validate(item) for item in items],
        total=total,
        pending_count=total,
        approved_count=await repo.count(status=ContentStatus.APPROVED.value),
    )


@router.get("/{item_id}", response_model=ContentQueueResponse)
async def get_item(
    item_id: int,
    _: str = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    """Get a single content queue item."""
    repo = ContentQueueRepository(session)
    item = await repo.get_by_id(item_id)

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content queue item not found",
        )

    return ContentQueueResponse.model_validate(item)


@router.patch("/{item_id}", response_model=ContentQueueResponse)
async def update_item(
    item_id: int,
    request: ContentUpdateRequest,
    _: str = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    """Update a content queue item."""
    repo = ContentQueueRepository(session)

    item = await repo.update(
        item_id,
        formatted_content=request.formatted_content,
        admin_notes=request.admin_notes,
    )

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content queue item not found",
        )

    return ContentQueueResponse.model_validate(item)


@router.post("/{item_id}/approve", response_model=ContentQueueResponse)
async def approve_item(
    item_id: int,
    request: ContentApproveRequest | None = None,
    _: str = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    """Approve a content queue item for posting."""
    repo = ContentQueueRepository(session)

    notes = request.admin_notes if request else None
    item = await repo.approve(item_id, admin_notes=notes)

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content queue item not found",
        )

    return ContentQueueResponse.model_validate(item)


@router.post("/{item_id}/reject", response_model=ContentQueueResponse)
async def reject_item(
    item_id: int,
    request: ContentApproveRequest | None = None,
    _: str = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    """Reject a content queue item."""
    repo = ContentQueueRepository(session)

    notes = request.admin_notes if request else None
    item = await repo.reject(item_id, admin_notes=notes)

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content queue item not found",
        )

    return ContentQueueResponse.model_validate(item)


@router.delete("/{item_id}", response_model=MessageResponse)
async def delete_item(
    item_id: int,
    _: str = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    """Delete a content queue item."""
    repo = ContentQueueRepository(session)

    success = await repo.delete(item_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content queue item not found",
        )

    return MessageResponse(success=True, message="Item deleted successfully")
