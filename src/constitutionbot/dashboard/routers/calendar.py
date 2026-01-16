"""Calendar API endpoints for scheduling content."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from constitutionbot.dashboard.auth import require_auth
from constitutionbot.dashboard.schemas.requests import ScheduleContentRequest
from constitutionbot.dashboard.schemas.responses import (
    CalendarItemResponse,
    CalendarListResponse,
    ContentQueueResponse,
    MessageResponse,
)
from constitutionbot.database import get_session
from constitutionbot.database.repositories.content_queue import ContentQueueRepository

router = APIRouter(prefix="/api/calendar", tags=["Calendar"])


@router.get("", response_model=CalendarListResponse)
async def get_calendar_items(
    start: datetime = Query(..., description="Start date for calendar range"),
    end: datetime = Query(..., description="End date for calendar range"),
    _: str = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    """Get scheduled items within a date range."""
    repo = ContentQueueRepository(session)
    items = await repo.get_scheduled(start, end)

    return CalendarListResponse(
        items=[CalendarItemResponse.model_validate(item) for item in items],
        total=len(items),
    )


@router.post("/{item_id}/schedule", response_model=ContentQueueResponse)
async def schedule_item(
    item_id: int,
    request: ScheduleContentRequest,
    _: str = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    """Schedule an approved item for future posting."""
    repo = ContentQueueRepository(session)

    item = await repo.schedule_item(
        item_id,
        scheduled_for=request.scheduled_for,
        auto_post=request.auto_post,
    )

    if not item:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Item not found or not in approved status",
        )

    return ContentQueueResponse.model_validate(item)


@router.post("/{item_id}/unschedule", response_model=ContentQueueResponse)
async def unschedule_item(
    item_id: int,
    _: str = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    """Remove schedule from an item, returning it to approved status."""
    repo = ContentQueueRepository(session)

    item = await repo.unschedule_item(item_id)

    if not item:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Item not found or not in scheduled status",
        )

    return ContentQueueResponse.model_validate(item)
