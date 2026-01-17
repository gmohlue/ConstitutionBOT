"""FastAPI application for the admin dashboard."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from contentmanager.config import get_settings
from contentmanager.dashboard.auth import (
    get_current_session,
    login_user,
    logout_user,
    optional_auth,
    require_auth,
)
from contentmanager.dashboard.csrf import (
    generate_csrf_token,
    get_csrf_from_cookie,
    set_csrf_cookie,
    validate_csrf,
)
from contentmanager.dashboard.routers import (
    calendar_router,
    chat_router,
    documents_router,
    content_queue_router,
    export_router,
    history_router,
    reply_queue_router,
    settings_router,
    suggestions_router,
)
from contentmanager.database import get_session, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    await init_db()
    yield


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="Content Manager Dashboard",
        description="Admin dashboard for Content Manager - AI-powered content generation",
        version="0.1.0",
        lifespan=lifespan,
    )

    # Get paths for templates and static files
    dashboard_dir = Path(__file__).parent
    templates_dir = dashboard_dir / "templates"
    static_dir = dashboard_dir / "static"

    # Mount static files
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=static_dir), name="static")

    # Set up Jinja2 templates
    templates = Jinja2Templates(directory=templates_dir)

    # Include API routers
    app.include_router(calendar_router)
    app.include_router(chat_router)
    app.include_router(content_queue_router)
    app.include_router(export_router)
    app.include_router(reply_queue_router)
    app.include_router(documents_router)
    app.include_router(suggestions_router)
    app.include_router(history_router)
    app.include_router(settings_router)

    # Page routes (HTML)
    @app.get("/", response_class=HTMLResponse)
    async def dashboard(
        request: Request,
        is_authenticated: bool = Depends(optional_auth),
    ):
        """Main dashboard page."""
        if not is_authenticated:
            return RedirectResponse(url="/login", status_code=303)

        return templates.TemplateResponse(
            "dashboard.html",
            {"request": request, "active_page": "dashboard"},
        )

    @app.get("/login", response_class=HTMLResponse)
    async def login_page(
        request: Request,
        next: str = "/",
        error: str = None,
    ):
        """Login page."""
        csrf_token = generate_csrf_token()
        response = templates.TemplateResponse(
            "login.html",
            {"request": request, "next": next, "error": error, "csrf_token": csrf_token},
        )
        set_csrf_cookie(response, csrf_token)
        return response

    @app.post("/login")
    async def login_submit(
        request: Request,
        username: str = Form(...),
        password: str = Form(...),
        csrf_token: str = Form(...),
        next: str = Form("/"),
        db_session: AsyncSession = Depends(get_session),
    ):
        """Handle login form submission."""
        # Verify CSRF token
        cookie_token = get_csrf_from_cookie(request)
        validate_csrf(cookie_token, csrf_token)

        response = RedirectResponse(url=next, status_code=303)

        if await login_user(response, username, password, db_session, request):
            return response

        # Login failed
        return RedirectResponse(
            url=f"/login?error=Invalid+credentials&next={next}",
            status_code=303,
        )

    @app.get("/logout")
    async def logout(
        session_token: str = Depends(get_current_session),
        db_session: AsyncSession = Depends(get_session),
    ):
        """Log out the user."""
        response = RedirectResponse(url="/login", status_code=303)
        await logout_user(response, db_session, session_token)
        return response

    @app.get("/queue", response_class=HTMLResponse)
    async def queue_page(
        request: Request,
        _: str = Depends(require_auth),
    ):
        """Content queue page."""
        return templates.TemplateResponse(
            "queue.html",
            {"request": request, "active_page": "queue"},
        )

    @app.get("/replies", response_class=HTMLResponse)
    async def replies_page(
        request: Request,
        _: str = Depends(require_auth),
    ):
        """Reply queue page."""
        return templates.TemplateResponse(
            "replies.html",
            {"request": request, "active_page": "replies"},
        )

    @app.get("/documents", response_class=HTMLResponse)
    async def documents_page(
        request: Request,
        _: str = Depends(require_auth),
    ):
        """Document management page."""
        return templates.TemplateResponse(
            "documents.html",
            {"request": request, "active_page": "documents"},
        )

    @app.get("/generate", response_class=HTMLResponse)
    async def generate_page(
        request: Request,
        _: str = Depends(require_auth),
    ):
        """Content generation page."""
        return templates.TemplateResponse(
            "generate.html",
            {"request": request, "active_page": "generate"},
        )

    @app.get("/chat", response_class=HTMLResponse)
    async def chat_page(
        request: Request,
        _: str = Depends(require_auth),
    ):
        """Interactive chat page."""
        return templates.TemplateResponse(
            "chat.html",
            {"request": request, "active_page": "chat"},
        )

    @app.get("/calendar", response_class=HTMLResponse)
    async def calendar_page(
        request: Request,
        _: str = Depends(require_auth),
    ):
        """Content calendar page."""
        return templates.TemplateResponse(
            "calendar.html",
            {"request": request, "active_page": "calendar"},
        )

    @app.get("/history", response_class=HTMLResponse)
    async def history_page(
        request: Request,
        _: str = Depends(require_auth),
    ):
        """Post history page."""
        return templates.TemplateResponse(
            "history.html",
            {"request": request, "active_page": "history"},
        )

    @app.get("/analytics", response_class=HTMLResponse)
    async def analytics_page(
        request: Request,
        _: str = Depends(require_auth),
    ):
        """Analytics dashboard page."""
        return templates.TemplateResponse(
            "analytics.html",
            {"request": request, "active_page": "analytics"},
        )

    @app.get("/settings", response_class=HTMLResponse)
    async def settings_page(
        request: Request,
        _: str = Depends(require_auth),
    ):
        """Settings page."""
        return templates.TemplateResponse(
            "settings.html",
            {"request": request, "active_page": "settings"},
        )

    return app


# Create app instance for uvicorn
app = create_app()
