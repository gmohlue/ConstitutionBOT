"""Integration tests for API endpoints."""

import pytest
from httpx import AsyncClient


class TestAuthenticationFlow:
    """Tests for authentication endpoints."""

    async def test_login_page_accessible(self, client: AsyncClient):
        """Test that login page is accessible without auth."""
        response = await client.get("/login")
        assert response.status_code == 200
        assert "login" in response.text.lower()

    async def test_protected_routes_redirect_to_login(self, client: AsyncClient):
        """Test that protected routes redirect to login."""
        protected_routes = ["/", "/queue", "/generate", "/chat", "/settings"]
        for route in protected_routes:
            response = await client.get(route, follow_redirects=False)
            assert response.status_code == 303
            assert "/login" in response.headers.get("location", "")

    async def test_login_with_valid_credentials(self, client: AsyncClient):
        """Test login with valid credentials."""
        # Get CSRF token
        login_page = await client.get("/login")
        csrf_cookie = login_page.cookies.get("csrf_token")

        response = await client.post(
            "/login",
            data={
                "username": "admin",
                "password": "testpassword",
                "csrf_token": csrf_cookie,
                "next": "/",
            },
            follow_redirects=False,
        )

        assert response.status_code == 303
        assert response.headers.get("location") == "/"
        assert "session" in response.cookies

    async def test_login_with_invalid_credentials(self, client: AsyncClient):
        """Test login with invalid credentials."""
        login_page = await client.get("/login")
        csrf_cookie = login_page.cookies.get("csrf_token")

        response = await client.post(
            "/login",
            data={
                "username": "admin",
                "password": "wrongpassword",
                "csrf_token": csrf_cookie,
                "next": "/",
            },
            follow_redirects=False,
        )

        assert response.status_code == 303
        assert "error=Invalid" in response.headers.get("location", "")


class TestContentQueueAPI:
    """Tests for content queue API endpoints."""

    async def test_list_queue_requires_auth(self, client: AsyncClient):
        """Test that listing queue requires authentication."""
        response = await client.get("/api/queue")
        assert response.status_code == 401

    async def test_list_queue_empty(self, authenticated_client: AsyncClient):
        """Test listing an empty queue."""
        response = await authenticated_client.get("/api/queue")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []
        assert data["pending_count"] == 0


class TestHistoryAPI:
    """Tests for history API endpoints."""

    async def test_stats_requires_auth(self, client: AsyncClient):
        """Test that stats endpoint requires authentication."""
        response = await client.get("/api/history/stats")
        assert response.status_code == 401

    async def test_stats_returns_valid_data(self, authenticated_client: AsyncClient):
        """Test stats endpoint returns valid structure."""
        response = await authenticated_client.get("/api/history/stats")
        assert response.status_code == 200
        data = response.json()

        # Check all expected fields are present
        assert "pending_content" in data
        assert "approved_content" in data
        assert "total_posts" in data
        assert "document_loaded" in data
        assert "bot_enabled" in data

    async def test_list_history_empty(self, authenticated_client: AsyncClient):
        """Test listing empty history."""
        response = await authenticated_client.get("/api/history")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []


class TestDocumentsAPI:
    """Tests for documents API endpoints."""

    async def test_document_summary_requires_auth(self, client: AsyncClient):
        """Test that document summary requires authentication."""
        response = await client.get("/api/documents/summary")
        assert response.status_code == 401

    async def test_document_summary_empty(self, authenticated_client: AsyncClient):
        """Test getting summary when no document is loaded."""
        response = await authenticated_client.get("/api/documents/summary")
        assert response.status_code == 200
        data = response.json()
        assert data["is_loaded"] is False

    async def test_list_sections_requires_auth(self, client: AsyncClient):
        """Test that listing sections requires authentication."""
        response = await client.get("/api/documents/sections")
        assert response.status_code == 401

    async def test_list_sections_no_document(self, authenticated_client: AsyncClient):
        """Test listing sections when no document is loaded."""
        import pytest
        # When no document is loaded, the repository raises ValueError
        # This test documents the current behavior
        with pytest.raises(ValueError, match="No active document found"):
            await authenticated_client.get("/api/documents/sections")


class TestSettingsAPI:
    """Tests for settings API endpoints."""

    async def test_get_settings_requires_auth(self, client: AsyncClient):
        """Test that getting settings requires authentication."""
        response = await client.get("/api/settings")
        assert response.status_code == 401

    async def test_get_settings(self, authenticated_client: AsyncClient):
        """Test getting settings."""
        response = await authenticated_client.get("/api/settings")
        assert response.status_code == 200
        data = response.json()
        # Check for expected settings fields
        assert "bot_enabled" in data
        assert "auto_generate_enabled" in data

    async def test_get_llm_config(self, authenticated_client: AsyncClient):
        """Test getting LLM configuration."""
        response = await authenticated_client.get("/api/settings/llm")
        assert response.status_code == 200
        data = response.json()
        assert "provider" in data

    async def test_get_credentials_status(self, authenticated_client: AsyncClient):
        """Test getting credentials status."""
        response = await authenticated_client.get("/api/settings/credentials")
        assert response.status_code == 200
        data = response.json()
        # Should have masked credential info
        assert "anthropic_api_key" in data


class TestExportAPI:
    """Tests for export API endpoints."""

    async def test_export_queue_csv_requires_auth(self, client: AsyncClient):
        """Test that exporting queue requires authentication."""
        response = await client.get("/api/export/queue/csv")
        assert response.status_code == 401

    async def test_export_queue_csv(self, authenticated_client: AsyncClient):
        """Test exporting queue to CSV."""
        response = await authenticated_client.get("/api/export/queue/csv")
        assert response.status_code == 200
        assert "text/csv" in response.headers.get("content-type", "")
        assert "attachment" in response.headers.get("content-disposition", "")

    async def test_export_queue_json(self, authenticated_client: AsyncClient):
        """Test exporting queue to JSON."""
        response = await authenticated_client.get("/api/export/queue/json")
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type", "")
        data = response.json()
        assert "exported_at" in data
        assert "items" in data

    async def test_export_history_csv(self, authenticated_client: AsyncClient):
        """Test exporting history to CSV."""
        response = await authenticated_client.get("/api/export/history/csv")
        assert response.status_code == 200
        assert "text/csv" in response.headers.get("content-type", "")

    async def test_export_history_json(self, authenticated_client: AsyncClient):
        """Test exporting history to JSON."""
        response = await authenticated_client.get("/api/export/history/json")
        assert response.status_code == 200
        data = response.json()
        assert "exported_at" in data
        assert "items" in data

    async def test_export_conversations_json(self, authenticated_client: AsyncClient):
        """Test exporting conversations to JSON."""
        response = await authenticated_client.get("/api/export/conversations/json")
        assert response.status_code == 200
        data = response.json()
        assert "exported_at" in data
        assert "conversations" in data


class TestChatAPI:
    """Tests for chat API endpoints."""

    async def test_list_conversations_requires_auth(self, client: AsyncClient):
        """Test that listing conversations requires authentication."""
        response = await client.get("/api/chat/conversations")
        assert response.status_code == 401

    async def test_list_conversations_empty(self, authenticated_client: AsyncClient):
        """Test listing empty conversations."""
        response = await authenticated_client.get("/api/chat/conversations")
        assert response.status_code == 200
        data = response.json()
        assert "conversations" in data
        assert data["total"] == 0


class TestCalendarAPI:
    """Tests for calendar API endpoints."""

    async def test_get_calendar_requires_auth(self, client: AsyncClient):
        """Test that getting calendar requires authentication."""
        response = await client.get(
            "/api/calendar",
            params={"start": "2024-01-01T00:00:00", "end": "2024-01-31T23:59:59"}
        )
        assert response.status_code == 401

    async def test_get_calendar_empty(self, authenticated_client: AsyncClient):
        """Test getting empty calendar with valid date range."""
        response = await authenticated_client.get(
            "/api/calendar",
            params={"start": "2024-01-01T00:00:00", "end": "2024-01-31T23:59:59"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert data["total"] == 0

    async def test_get_calendar_missing_params(self, authenticated_client: AsyncClient):
        """Test calendar endpoint requires date parameters."""
        response = await authenticated_client.get("/api/calendar")
        assert response.status_code == 422  # Validation error
