"""Mode 3: Historical event analysis for content generation."""

from dataclasses import dataclass
from datetime import date
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from constitutionbot.core.content.generator import ContentGenerator, GeneratedContent
from constitutionbot.database.repositories.document import DocumentRepository


@dataclass
class HistoricalEvent:
    """A significant historical event related to a document's history."""

    date: date
    name: str
    description: str
    related_sections: list[int]
    significance: str

    @classmethod
    def from_dict(cls, data: dict) -> "HistoricalEvent":
        """Create HistoricalEvent from dictionary."""
        event_date = data.get("date")
        if isinstance(event_date, str):
            event_date = date.fromisoformat(event_date)
        elif isinstance(event_date, dict):
            event_date = date(event_date["year"], event_date["month"], event_date["day"])

        return cls(
            date=event_date,
            name=data.get("name", ""),
            description=data.get("description", ""),
            related_sections=data.get("related_sections", []),
            significance=data.get("significance", ""),
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "date": self.date.isoformat(),
            "name": self.name,
            "description": self.description,
            "related_sections": self.related_sections,
            "significance": self.significance,
        }


# Default events for SA Constitution (for backward compatibility)
DEFAULT_SA_CONSTITUTION_EVENTS = [
    {
        "date": "1996-12-10",
        "name": "Constitution Signed",
        "description": "President Mandela signed the final Constitution into law",
        "related_sections": [1, 2, 7],
        "significance": "The foundation of our democratic order",
    },
    {
        "date": "1994-04-27",
        "name": "Freedom Day",
        "description": "First democratic elections in South Africa",
        "related_sections": [1, 19],
        "significance": "Birth of our democracy and the right to vote",
    },
    {
        "date": "1960-03-21",
        "name": "Human Rights Day (Sharpeville)",
        "description": "Sharpeville massacre - a turning point in the struggle",
        "related_sections": [9, 10, 11, 12],
        "significance": "Why we enshrine the rights to equality, dignity, life, and freedom",
    },
    {
        "date": "1955-06-26",
        "name": "Freedom Charter Adopted",
        "description": "The Freedom Charter was adopted at Kliptown",
        "related_sections": [1, 7, 9, 26, 29],
        "significance": "Many Charter principles became constitutional rights",
    },
    {
        "date": "1990-02-11",
        "name": "Mandela Released",
        "description": "Nelson Mandela released from Victor Verster Prison",
        "related_sections": [12, 35],
        "significance": "The beginning of the transition to democracy",
    },
    {
        "date": "1976-06-16",
        "name": "Youth Day (Soweto Uprising)",
        "description": "Student uprising against Bantu education",
        "related_sections": [29, 30, 31],
        "significance": "The struggle for educational and language rights",
    },
    {
        "date": "1996-05-08",
        "name": "Constitution Adopted",
        "description": "Constitutional Assembly adopted the final Constitution",
        "related_sections": [1, 2, 3],
        "significance": "The culmination of constitutional negotiations",
    },
    {
        "date": "1997-02-04",
        "name": "Constitution Comes into Force",
        "description": "The Constitution of 1996 came into full effect",
        "related_sections": [1, 2, 7, 8],
        "significance": "The supreme law of our land took effect",
    },
]


class HistoricalMode:
    """Mode 3: Historical event analysis and content generation.

    This mode creates content that connects historical events to
    document provisions, helping users understand the document
    in its historical context.

    Workflow:
    1. Select or specify a historical event/date
    2. Identify relevant document provisions
    3. Generate content connecting history to document
    4. Content goes to queue for admin review
    """

    def __init__(self, session: AsyncSession, document_id: Optional[int] = None):
        self.session = session
        self.document_id = document_id
        self.generator = ContentGenerator(session, document_id=document_id)
        self._events: Optional[list[HistoricalEvent]] = None
        self._events_loaded = False

    async def _get_events(self) -> list[HistoricalEvent]:
        """Get historical events from document or defaults."""
        if self._events_loaded:
            return self._events or []

        doc_repo = DocumentRepository(self.session)

        if self.document_id:
            doc = await doc_repo.get_by_id(self.document_id)
        else:
            doc = await doc_repo.get_active()

        if doc and doc.historical_events:
            self._events = [
                HistoricalEvent.from_dict(e) for e in doc.historical_events
            ]
        else:
            # Fall back to default SA Constitution events
            self._events = [
                HistoricalEvent.from_dict(e) for e in DEFAULT_SA_CONSTITUTION_EVENTS
            ]

        self._events_loaded = True
        return self._events

    async def generate_for_date(
        self,
        target_date: date,
        content_type: str = "tweet",
    ) -> Optional[GeneratedContent]:
        """Generate content for a specific date if significant.

        Args:
            target_date: The date to check
            content_type: "tweet" or "thread"

        Returns:
            GeneratedContent if date is significant, None otherwise
        """
        event = await self._find_event_for_date(target_date)
        if not event:
            return None

        return await self.generate_for_event(event, content_type)

    async def generate_for_event(
        self,
        event: HistoricalEvent,
        content_type: str = "tweet",
    ) -> GeneratedContent:
        """Generate content for a historical event.

        Args:
            event: The HistoricalEvent to create content about
            content_type: "tweet" or "thread"

        Returns:
            GeneratedContent about the event
        """
        event_description = (
            f"{event.name} ({event.date.strftime('%d %B %Y')}): "
            f"{event.description}. {event.significance}"
        )

        return await self.generator.generate_historical(
            event=event_description,
            content_type=content_type,
        )

    async def generate_for_custom_event(
        self,
        event_description: str,
        content_type: str = "tweet",
    ) -> GeneratedContent:
        """Generate content for a custom historical event.

        Args:
            event_description: Description of the event
            content_type: "tweet" or "thread"

        Returns:
            GeneratedContent about the event
        """
        return await self.generator.generate_historical(
            event=event_description,
            content_type=content_type,
        )

    async def _find_event_for_date(self, target_date: date) -> Optional[HistoricalEvent]:
        """Find a significant event for a given date (ignoring year)."""
        events = await self._get_events()
        for event in events:
            if event.date.month == target_date.month and event.date.day == target_date.day:
                return event
        return None

    async def get_upcoming_events(self, days: int = 30) -> list[HistoricalEvent]:
        """Get significant events in the next N days.

        Args:
            days: Number of days to look ahead

        Returns:
            List of upcoming HistoricalEvents
        """
        today = date.today()
        upcoming = []
        events = await self._get_events()

        for event in events:
            # Create this year's occurrence of the event
            this_year_date = event.date.replace(year=today.year)

            # If it's already passed this year, check next year
            if this_year_date < today:
                this_year_date = this_year_date.replace(year=today.year + 1)

            # Check if within range
            days_until = (this_year_date - today).days
            if 0 <= days_until <= days:
                upcoming.append(event)

        # Sort by upcoming date
        upcoming.sort(key=lambda e: (
            e.date.replace(year=today.year)
            if e.date.replace(year=today.year) >= today
            else e.date.replace(year=today.year + 1)
        ))

        return upcoming

    async def get_event_by_name(self, name: str) -> Optional[HistoricalEvent]:
        """Find an event by its name.

        Args:
            name: Name or partial name of the event

        Returns:
            HistoricalEvent if found, None otherwise
        """
        events = await self._get_events()
        name_lower = name.lower()
        for event in events:
            if name_lower in event.name.lower():
                return event
        return None

    async def generate_anniversary_content(
        self,
        content_type: str = "thread",
    ) -> Optional[GeneratedContent]:
        """Generate content for today if it's a significant anniversary.

        Args:
            content_type: "tweet" or "thread"

        Returns:
            GeneratedContent if today is significant, None otherwise
        """
        today = date.today()
        event = await self._find_event_for_date(today)

        if not event:
            return None

        # Calculate years since event
        years = today.year - event.date.year

        # Create anniversary-specific description
        anniversary_description = (
            f"Today marks {years} years since {event.name} "
            f"({event.date.strftime('%d %B %Y')}). "
            f"{event.description}. "
            f"This moment reminds us: {event.significance}"
        )

        return await self.generator.generate_historical(
            event=anniversary_description,
            content_type=content_type,
        )

    async def get_all_events(self) -> list[HistoricalEvent]:
        """Get all significant dates."""
        events = await self._get_events()
        return events.copy()
