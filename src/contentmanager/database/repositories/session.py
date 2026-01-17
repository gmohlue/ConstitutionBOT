"""Repository for Session management."""

from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from contentmanager.database.models import Session


class SessionRepository:
    """Repository for managing user sessions."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        token: str,
        expires_at: datetime,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> Session:
        """Create a new session."""
        db_session = Session(
            token=token,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        self.session.add(db_session)
        await self.session.flush()
        await self.session.refresh(db_session)
        return db_session

    async def get_by_token(self, token: str) -> Optional[Session]:
        """Get a session by its token."""
        result = await self.session.execute(
            select(Session).where(Session.token == token)
        )
        return result.scalar_one_or_none()

    async def delete_by_token(self, token: str) -> bool:
        """Delete a session by its token."""
        result = await self.session.execute(
            delete(Session).where(Session.token == token)
        )
        await self.session.flush()
        return result.rowcount > 0

    async def delete_expired(self) -> int:
        """Delete all expired sessions. Returns count of deleted sessions."""
        now = datetime.utcnow()
        result = await self.session.execute(
            delete(Session).where(Session.expires_at < now)
        )
        await self.session.flush()
        return result.rowcount

    async def is_valid(self, token: str) -> bool:
        """Check if a session token is valid and not expired."""
        session = await self.get_by_token(token)
        if not session:
            return False
        if datetime.utcnow() > session.expires_at.replace(tzinfo=None):
            await self.delete_by_token(token)
            return False
        return True
