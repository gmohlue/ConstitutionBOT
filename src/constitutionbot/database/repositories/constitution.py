"""Repository for Constitution sections."""

from typing import Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from constitutionbot.database.models import ConstitutionSection


class ConstitutionRepository:
    """Repository for managing constitution sections."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        chapter_num: int,
        chapter_title: str,
        content: str,
        section_num: Optional[int] = None,
        section_title: Optional[str] = None,
        subsections: Optional[dict] = None,
        keywords: Optional[list] = None,
    ) -> ConstitutionSection:
        """Create a new constitution section."""
        section = ConstitutionSection(
            chapter_num=chapter_num,
            chapter_title=chapter_title,
            section_num=section_num,
            section_title=section_title,
            content=content,
            subsections=subsections,
            keywords=keywords,
        )
        self.session.add(section)
        await self.session.flush()
        await self.session.refresh(section)
        return section

    async def bulk_create(self, sections: list[dict]) -> list[ConstitutionSection]:
        """Bulk create constitution sections."""
        created = []
        for section_data in sections:
            section = await self.create(**section_data)
            created.append(section)
        return created

    async def get_by_id(self, section_id: int) -> Optional[ConstitutionSection]:
        """Get a section by ID."""
        result = await self.session.execute(
            select(ConstitutionSection).where(ConstitutionSection.id == section_id)
        )
        return result.scalar_one_or_none()

    async def get_by_section_num(self, section_num: int) -> Optional[ConstitutionSection]:
        """Get a section by its section number."""
        result = await self.session.execute(
            select(ConstitutionSection).where(ConstitutionSection.section_num == section_num)
        )
        return result.scalar_one_or_none()

    async def get_by_chapter(self, chapter_num: int) -> list[ConstitutionSection]:
        """Get all sections in a chapter."""
        result = await self.session.execute(
            select(ConstitutionSection)
            .where(ConstitutionSection.chapter_num == chapter_num)
            .order_by(ConstitutionSection.section_num)
        )
        return list(result.scalars().all())

    async def get_all(
        self,
        limit: int = 500,
        offset: int = 0,
    ) -> list[ConstitutionSection]:
        """Get all constitution sections."""
        result = await self.session.execute(
            select(ConstitutionSection)
            .order_by(ConstitutionSection.chapter_num, ConstitutionSection.section_num)
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def get_chapters(self) -> list[dict]:
        """Get list of unique chapters."""
        result = await self.session.execute(
            select(
                ConstitutionSection.chapter_num,
                ConstitutionSection.chapter_title,
            ).distinct()
            .order_by(ConstitutionSection.chapter_num)
        )
        return [
            {"chapter_num": row[0], "chapter_title": row[1]}
            for row in result.all()
        ]

    async def search(
        self,
        query: str,
        limit: int = 20,
    ) -> list[ConstitutionSection]:
        """Search sections by content or title."""
        search_pattern = f"%{query}%"
        result = await self.session.execute(
            select(ConstitutionSection)
            .where(
                ConstitutionSection.content.ilike(search_pattern)
                | ConstitutionSection.section_title.ilike(search_pattern)
                | ConstitutionSection.chapter_title.ilike(search_pattern)
            )
            .order_by(ConstitutionSection.chapter_num, ConstitutionSection.section_num)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def clear_all(self) -> int:
        """Delete all constitution sections. Returns count deleted."""
        result = await self.session.execute(delete(ConstitutionSection))
        await self.session.flush()
        return result.rowcount

    async def count(self) -> int:
        """Count total constitution sections."""
        from sqlalchemy import func

        result = await self.session.execute(
            select(func.count(ConstitutionSection.id))
        )
        return result.scalar() or 0

    async def has_content(self) -> bool:
        """Check if constitution has been uploaded."""
        count = await self.count()
        return count > 0
