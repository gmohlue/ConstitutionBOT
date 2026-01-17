"""Export API endpoints for downloading data in CSV and JSON formats."""

import csv
import io
import json
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from contentmanager.dashboard.auth import require_auth
from contentmanager.database import get_session
from contentmanager.database.repositories.content_queue import ContentQueueRepository
from contentmanager.database.repositories.post_history import PostHistoryRepository
from contentmanager.database.repositories.conversation import (
    ConversationRepository,
    MessageRepository,
)

router = APIRouter(prefix="/api/export", tags=["Export"])


def _format_datetime(dt: datetime | None) -> str:
    """Format datetime for export."""
    if dt is None:
        return ""
    return dt.isoformat()


def _format_json_value(value) -> str:
    """Format JSON values for CSV export."""
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value)
    return str(value)


@router.get("/queue/csv")
async def export_queue_csv(
    status: str | None = Query(None, description="Filter by status"),
    _: str = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    """Export content queue to CSV format."""
    repo = ContentQueueRepository(session)
    items = await repo.get_all(status=status, limit=10000)

    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow([
        "id",
        "content_type",
        "raw_content",
        "formatted_content",
        "mode",
        "topic",
        "citations",
        "language",
        "status",
        "admin_notes",
        "scheduled_for",
        "auto_post",
        "created_at",
        "updated_at",
    ])

    # Write data rows
    for item in items:
        writer.writerow([
            item.id,
            item.content_type,
            item.raw_content,
            item.formatted_content,
            item.mode,
            item.topic or "",
            _format_json_value(item.citations),
            item.language,
            item.status,
            item.admin_notes or "",
            _format_datetime(item.scheduled_for),
            item.auto_post,
            _format_datetime(item.created_at),
            _format_datetime(item.updated_at),
        ])

    output.seek(0)
    filename = f"content_queue_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/queue/json")
async def export_queue_json(
    status: str | None = Query(None, description="Filter by status"),
    _: str = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    """Export content queue to JSON format."""
    repo = ContentQueueRepository(session)
    items = await repo.get_all(status=status, limit=10000)

    data = {
        "exported_at": datetime.now().isoformat(),
        "total_items": len(items),
        "items": [
            {
                "id": item.id,
                "content_type": item.content_type,
                "raw_content": item.raw_content,
                "formatted_content": item.formatted_content,
                "mode": item.mode,
                "topic": item.topic,
                "citations": item.citations,
                "language": item.language,
                "status": item.status,
                "admin_notes": item.admin_notes,
                "scheduled_for": _format_datetime(item.scheduled_for),
                "auto_post": item.auto_post,
                "created_at": _format_datetime(item.created_at),
                "updated_at": _format_datetime(item.updated_at),
            }
            for item in items
        ],
    }

    output = json.dumps(data, indent=2)
    filename = f"content_queue_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    return StreamingResponse(
        iter([output]),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/history/csv")
async def export_history_csv(
    content_type: str | None = Query(None, description="Filter by content type"),
    is_reply: bool | None = Query(None, description="Filter by reply status"),
    _: str = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    """Export post history to CSV format."""
    repo = PostHistoryRepository(session)
    items = await repo.get_all(
        content_type=content_type,
        is_reply=is_reply,
        limit=10000,
    )

    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow([
        "id",
        "tweet_id",
        "content",
        "content_type",
        "is_reply",
        "reply_to_id",
        "likes",
        "retweets",
        "replies",
        "impressions",
        "posted_at",
    ])

    # Write data rows
    for item in items:
        engagement = item.engagement or {}
        writer.writerow([
            item.id,
            item.tweet_id,
            item.content,
            item.content_type,
            item.is_reply,
            item.reply_to_id or "",
            engagement.get("likes", 0),
            engagement.get("retweets", 0),
            engagement.get("replies", 0),
            engagement.get("impressions", 0),
            _format_datetime(item.posted_at),
        ])

    output.seek(0)
    filename = f"post_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/history/json")
async def export_history_json(
    content_type: str | None = Query(None, description="Filter by content type"),
    is_reply: bool | None = Query(None, description="Filter by reply status"),
    _: str = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    """Export post history to JSON format."""
    repo = PostHistoryRepository(session)
    items = await repo.get_all(
        content_type=content_type,
        is_reply=is_reply,
        limit=10000,
    )

    data = {
        "exported_at": datetime.now().isoformat(),
        "total_items": len(items),
        "items": [
            {
                "id": item.id,
                "tweet_id": item.tweet_id,
                "content": item.content,
                "content_type": item.content_type,
                "is_reply": item.is_reply,
                "reply_to_id": item.reply_to_id,
                "engagement": item.engagement,
                "posted_at": _format_datetime(item.posted_at),
            }
            for item in items
        ],
    }

    output = json.dumps(data, indent=2)
    filename = f"post_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    return StreamingResponse(
        iter([output]),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/conversations/json")
async def export_conversations_json(
    status: str | None = Query(None, description="Filter by status"),
    include_messages: bool = Query(True, description="Include conversation messages"),
    _: str = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    """Export conversations to JSON format."""
    conv_repo = ConversationRepository(session)
    msg_repo = MessageRepository(session)

    conversations = await conv_repo.get_all(status=status, limit=1000)

    items = []
    for conv in conversations:
        conv_data = {
            "id": conv.id,
            "session_id": conv.session_id,
            "title": conv.title,
            "status": conv.status,
            "mode": conv.mode,
            "topic": conv.topic,
            "context_sections": conv.context_sections,
            "created_at": _format_datetime(conv.created_at),
            "updated_at": _format_datetime(conv.updated_at),
        }

        if include_messages:
            messages = await msg_repo.get_by_conversation(conv.id)
            conv_data["messages"] = [
                {
                    "id": msg.id,
                    "role": msg.role,
                    "message_type": msg.message_type,
                    "content": msg.content,
                    "structured_data": msg.structured_data,
                    "citations": msg.citations,
                    "created_at": _format_datetime(msg.created_at),
                }
                for msg in messages
            ]

        items.append(conv_data)

    data = {
        "exported_at": datetime.now().isoformat(),
        "total_conversations": len(items),
        "conversations": items,
    }

    output = json.dumps(data, indent=2)
    filename = f"conversations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    return StreamingResponse(
        iter([output]),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
