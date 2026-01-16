"""Mode 3: Historical event analysis for content generation."""

from dataclasses import dataclass
from datetime import date
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from constitutionbot.core.content.generator import ContentGenerator, GeneratedContent


@dataclass
class HistoricalEvent:
    """A significant historical event related to South African democracy."""

    date: date
    name: str
    description: str
    related_sections: list[int]
    significance: str


class HistoricalMode:
    """Mode 3: Historical event analysis and content generation.

    This mode creates content that connects historical events to
    constitutional provisions, helping citizens understand the
    Constitution in its historical context.

    Workflow:
    1. Select or specify a historical event/date
    2. Identify relevant constitutional provisions
    3. Generate content connecting history to Constitution
    4. Content goes to queue for admin review
    """

    # Key dates in South African constitutional history
    SIGNIFICANT_DATES = [
        HistoricalEvent(
            date=date(1996, 12, 10),
            name="Constitution Signed",
            description="President Mandela signed the final Constitution into law",
            related_sections=[1, 2, 7],
            significance="The foundation of our democratic order",
        ),
        HistoricalEvent(
            date=date(1994, 4, 27),
            name="Freedom Day",
            description="First democratic elections in South Africa",
            related_sections=[1, 19],
            significance="Birth of our democracy and the right to vote",
        ),
        HistoricalEvent(
            date=date(1960, 3, 21),
            name="Human Rights Day (Sharpeville)",
            description="Sharpeville massacre - a turning point in the struggle",
            related_sections=[9, 10, 11, 12],
            significance="Why we enshrine the rights to equality, dignity, life, and freedom",
        ),
        HistoricalEvent(
            date=date(1955, 6, 26),
            name="Freedom Charter Adopted",
            description="The Freedom Charter was adopted at Kliptown",
            related_sections=[1, 7, 9, 26, 29],
            significance="Many Charter principles became constitutional rights",
        ),
        HistoricalEvent(
            date=date(1990, 2, 11),
            name="Mandela Released",
            description="Nelson Mandela released from Victor Verster Prison",
            related_sections=[12, 35],
            significance="The beginning of the transition to democracy",
        ),
        HistoricalEvent(
            date=date(1976, 6, 16),
            name="Youth Day (Soweto Uprising)",
            description="Student uprising against Bantu education",
            related_sections=[29, 30, 31],
            significance="The struggle for educational and language rights",
        ),
        HistoricalEvent(
            date=date(1996, 5, 8),
            name="Constitution Adopted",
            description="Constitutional Assembly adopted the final Constitution",
            related_sections=[1, 2, 3],
            significance="The culmination of constitutional negotiations",
        ),
        HistoricalEvent(
            date=date(1997, 2, 4),
            name="Constitution Comes into Force",
            description="The Constitution of 1996 came into full effect",
            related_sections=[1, 2, 7, 8],
            significance="The supreme law of our land took effect",
        ),
    ]

    def __init__(self, session: AsyncSession):
        self.session = session
        self.generator = ContentGenerator(session)

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
        event = self._find_event_for_date(target_date)
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

    def _find_event_for_date(self, target_date: date) -> Optional[HistoricalEvent]:
        """Find a significant event for a given date (ignoring year)."""
        for event in self.SIGNIFICANT_DATES:
            if event.date.month == target_date.month and event.date.day == target_date.day:
                return event
        return None

    def get_upcoming_events(self, days: int = 30) -> list[HistoricalEvent]:
        """Get significant events in the next N days.

        Args:
            days: Number of days to look ahead

        Returns:
            List of upcoming HistoricalEvents
        """
        from datetime import timedelta

        today = date.today()
        upcoming = []

        for event in self.SIGNIFICANT_DATES:
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

    def get_event_by_name(self, name: str) -> Optional[HistoricalEvent]:
        """Find an event by its name.

        Args:
            name: Name or partial name of the event

        Returns:
            HistoricalEvent if found, None otherwise
        """
        name_lower = name.lower()
        for event in self.SIGNIFICANT_DATES:
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
        event = self._find_event_for_date(today)

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

    def get_all_events(self) -> list[HistoricalEvent]:
        """Get all significant dates."""
        return self.SIGNIFICANT_DATES.copy()
