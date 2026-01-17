"""API routers for the dashboard."""

from contentmanager.dashboard.routers.calendar import router as calendar_router
from contentmanager.dashboard.routers.chat import router as chat_router
from contentmanager.dashboard.routers.documents import router as documents_router
from contentmanager.dashboard.routers.content_queue import router as content_queue_router
from contentmanager.dashboard.routers.export import router as export_router
from contentmanager.dashboard.routers.history import router as history_router
from contentmanager.dashboard.routers.reply_queue import router as reply_queue_router
from contentmanager.dashboard.routers.settings import router as settings_router
from contentmanager.dashboard.routers.suggestions import router as suggestions_router

__all__ = [
    "calendar_router",
    "chat_router",
    "content_queue_router",
    "export_router",
    "reply_queue_router",
    "documents_router",
    "suggestions_router",
    "history_router",
    "settings_router",
]
