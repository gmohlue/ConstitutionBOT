"""API routers for the dashboard."""

from constitutionbot.dashboard.routers.calendar import router as calendar_router
from constitutionbot.dashboard.routers.chat import router as chat_router
from constitutionbot.dashboard.routers.constitution import router as constitution_router
from constitutionbot.dashboard.routers.content_queue import router as content_queue_router
from constitutionbot.dashboard.routers.history import router as history_router
from constitutionbot.dashboard.routers.reply_queue import router as reply_queue_router
from constitutionbot.dashboard.routers.settings import router as settings_router
from constitutionbot.dashboard.routers.suggestions import router as suggestions_router

__all__ = [
    "calendar_router",
    "chat_router",
    "content_queue_router",
    "reply_queue_router",
    "constitution_router",
    "suggestions_router",
    "history_router",
    "settings_router",
]
