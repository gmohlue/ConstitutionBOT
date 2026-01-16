"""Constitution section retrieval and search functionality."""

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from constitutionbot.core.constitution.models import CitationReference
from constitutionbot.database.models import ConstitutionSection
from constitutionbot.database.repositories.constitution import ConstitutionRepository


class ConstitutionRetriever:
    """Retrieve and search Constitution sections from the database."""

    def __init__(self, session: AsyncSession):
        self.repo = ConstitutionRepository(session)

    async def get_section(self, section_num: int) -> Optional[ConstitutionSection]:
        """Get a specific section by number."""
        return await self.repo.get_by_section_num(section_num)

    async def get_sections_by_chapter(self, chapter_num: int) -> list[ConstitutionSection]:
        """Get all sections in a chapter."""
        return await self.repo.get_by_chapter(chapter_num)

    async def search(self, query: str, limit: int = 10) -> list[ConstitutionSection]:
        """Search sections by keyword."""
        return await self.repo.search(query, limit=limit)

    async def get_random_section(self) -> Optional[ConstitutionSection]:
        """Get a random section for content generation."""
        import random

        sections = await self.repo.get_all(limit=500)
        if not sections:
            return None
        return random.choice(sections)

    async def get_sections_by_keyword(
        self, keyword: str, limit: int = 10
    ) -> list[ConstitutionSection]:
        """Get sections that contain a specific keyword."""
        return await self.search(keyword, limit=limit)

    async def get_bill_of_rights_sections(self) -> list[ConstitutionSection]:
        """Get all sections from the Bill of Rights (Chapter 2)."""
        return await self.repo.get_by_chapter(2)

    async def get_sections_for_topic(
        self, topic: str, limit: int = 5
    ) -> list[ConstitutionSection]:
        """Get sections relevant to a given topic."""
        # Topic-to-keyword mapping
        topic_keywords = {
            "equality": ["equality", "discrimination", "equal"],
            "dignity": ["dignity", "human dignity"],
            "life": ["life", "death"],
            "freedom": ["freedom", "liberty", "free"],
            "privacy": ["privacy", "private"],
            "expression": ["expression", "speech", "press", "media"],
            "assembly": ["assembly", "demonstration", "protest"],
            "association": ["association", "political"],
            "vote": ["vote", "political", "election"],
            "labour": ["labour", "work", "union", "strike"],
            "property": ["property", "expropriation", "land"],
            "housing": ["housing", "shelter", "adequate"],
            "health": ["health", "medical", "care"],
            "education": ["education", "school", "basic"],
            "children": ["children", "child", "minor"],
            "environment": ["environment", "ecological", "sustainable"],
            "arrest": ["arrest", "detention", "accused"],
            "trial": ["trial", "fair", "court", "accused"],
            "access": ["access", "information", "courts"],
        }

        # Normalize topic
        topic_lower = topic.lower()

        # Find matching keywords
        keywords_to_search = []
        for key, values in topic_keywords.items():
            if key in topic_lower or any(v in topic_lower for v in values):
                keywords_to_search.extend(values)

        # If no mapping found, use the topic itself
        if not keywords_to_search:
            keywords_to_search = [topic_lower]

        # Search for each keyword and combine results
        seen_ids = set()
        results = []

        for keyword in keywords_to_search[:3]:  # Limit keywords to search
            sections = await self.search(keyword, limit=limit)
            for section in sections:
                if section.id not in seen_ids:
                    seen_ids.add(section.id)
                    results.append(section)
                    if len(results) >= limit:
                        break
            if len(results) >= limit:
                break

        return results[:limit]

    async def get_citation_context(
        self, section_num: int
    ) -> Optional[CitationReference]:
        """Get citation reference with full context for a section."""
        section = await self.get_section(section_num)
        if not section:
            return None

        # Get a short excerpt
        content = section.content
        excerpt = content[:200] + "..." if len(content) > 200 else content

        return CitationReference(
            section_num=section.section_num,
            section_title=section.section_title,
            chapter_num=section.chapter_num,
            chapter_title=section.chapter_title,
            excerpt=excerpt,
        )

    async def get_chapters_summary(self) -> list[dict]:
        """Get a summary of all chapters."""
        return await self.repo.get_chapters()

    async def has_constitution(self) -> bool:
        """Check if constitution has been loaded."""
        return await self.repo.has_content()

    async def get_section_context(
        self, section_num: int, include_adjacent: bool = True
    ) -> dict:
        """Get a section with its context (chapter info, adjacent sections)."""
        section = await self.get_section(section_num)
        if not section:
            return {}

        context = {
            "section": section,
            "chapter_num": section.chapter_num,
            "chapter_title": section.chapter_title,
        }

        if include_adjacent:
            # Get sections before and after
            prev_section = await self.repo.get_by_section_num(section_num - 1)
            next_section = await self.repo.get_by_section_num(section_num + 1)

            if prev_section and prev_section.chapter_num == section.chapter_num:
                context["previous_section"] = prev_section
            if next_section and next_section.chapter_num == section.chapter_num:
                context["next_section"] = next_section

        return context

    async def format_section_for_prompt(self, section: ConstitutionSection) -> str:
        """Format a section for inclusion in an AI prompt."""
        lines = [
            f"## Section {section.section_num}: {section.section_title or 'Untitled'}",
            f"Chapter {section.chapter_num}: {section.chapter_title}",
            "",
            section.content,
        ]

        if section.subsections:
            lines.append("")
            for sub in section.subsections:
                lines.append(f"({sub['letter']}) {sub['content']}")

        return "\n".join(lines)

    async def format_multiple_sections(
        self, sections: list[ConstitutionSection]
    ) -> str:
        """Format multiple sections for inclusion in an AI prompt."""
        formatted = []
        for section in sections:
            formatted.append(await self.format_section_for_prompt(section))
        return "\n\n---\n\n".join(formatted)
