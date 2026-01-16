"""FastAPI application for the admin dashboard."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from constitutionbot.config import get_settings
from constitutionbot.dashboard.auth import (
    get_current_session,
    login_user,
    logout_user,
    optional_auth,
    require_auth,
)
from constitutionbot.dashboard.routers import (
    calendar_router,
    constitution_router,
    content_queue_router,
    history_router,
    reply_queue_router,
    settings_router,
    suggestions_router,
)
from constitutionbot.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    await init_db()
    yield


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="ConstitutionBOT Admin Dashboard",
        description="Admin dashboard for the ConstitutionBOT civic education assistant",
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
    app.include_router(content_queue_router)
    app.include_router(reply_queue_router)
    app.include_router(constitution_router)
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
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "next": next, "error": error},
        )

    @app.post("/login")
    async def login_submit(
        request: Request,
        username: str = Form(...),
        password: str = Form(...),
        next: str = Form("/"),
    ):
        """Handle login form submission."""
        response = RedirectResponse(url=next, status_code=303)

        if login_user(response, username, password):
            return response

        # Login failed
        return RedirectResponse(
            url=f"/login?error=Invalid+credentials&next={next}",
            status_code=303,
        )

    @app.get("/logout")
    async def logout(
        session_token: str = Depends(get_current_session),
    ):
        """Log out the user."""
        response = RedirectResponse(url="/login", status_code=303)
        logout_user(response, session_token)
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

    @app.get("/constitution", response_class=HTMLResponse)
    async def constitution_page(
        request: Request,
        _: str = Depends(require_auth),
    ):
        """Constitution management page."""
        return templates.TemplateResponse(
            "constitution.html",
            {"request": request, "active_page": "constitution"},
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
