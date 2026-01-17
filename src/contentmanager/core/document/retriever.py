"""Document section retrieval and search functionality."""

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from contentmanager.core.document.models import CitationReference
from contentmanager.database.models import Document, DocumentSection
from contentmanager.database.repositories.document import (
    DocumentRepository,
    DocumentSectionRepository,
)


class DocumentRetriever:
    """Retrieve and search document sections from the database."""

    def __init__(self, session: AsyncSession, document_id: Optional[int] = None):
        self.session = session
        self._document_id = document_id
        self._document: Optional[Document] = None
        self.doc_repo = DocumentRepository(session)
        self.section_repo = DocumentSectionRepository(session, document_id)

    async def get_document(self) -> Optional[Document]:
        """Get the current document."""
        if self._document:
            return self._document

        if self._document_id:
            self._document = await self.doc_repo.get_by_id(self._document_id)
        else:
            self._document = await self.doc_repo.get_active()

        return self._document

    async def get_section_label(self) -> str:
        """Get the section label for the current document."""
        doc = await self.get_document()
        return doc.section_label if doc else "Section"

    async def get_section(self, section_num: int) -> Optional[DocumentSection]:
        """Get a specific section by number."""
        return await self.section_repo.get_by_section_num(section_num)

    async def get_sections_by_chapter(self, chapter_num: int) -> list[DocumentSection]:
        """Get all sections in a chapter."""
        return await self.section_repo.get_by_chapter(chapter_num)

    async def search(self, query: str, limit: int = 10) -> list[DocumentSection]:
        """Search sections by keyword."""
        return await self.section_repo.search(query, limit=limit)

    async def get_random_section(self) -> Optional[DocumentSection]:
        """Get a random section for content generation."""
        import secrets

        sections = await self.section_repo.get_all(limit=500)
        if not sections:
            return None
        return secrets.choice(sections)

    async def get_sections_by_keyword(
        self, keyword: str, limit: int = 10
    ) -> list[DocumentSection]:
        """Get sections that contain a specific keyword."""
        return await self.search(keyword, limit=limit)

    async def get_featured_sections(self, chapter_num: int = 2) -> list[DocumentSection]:
        """Get featured sections (e.g., Bill of Rights for Constitution).

        This method is document-aware and will check the document config
        for a 'featured_chapter' setting.
        """
        doc = await self.get_document()
        if doc and doc.config:
            featured_chapter = doc.config.get("featured_chapter", chapter_num)
            return await self.section_repo.get_by_chapter(featured_chapter)
        return await self.section_repo.get_by_chapter(chapter_num)

    async def get_sections_for_topic(
        self, topic: str, limit: int = 5
    ) -> list[DocumentSection]:
        """Get sections relevant to a given topic."""
        doc = await self.get_document()

        # Check for document-specific topic mappings
        topic_keywords = {}
        if doc and doc.config:
            topic_keywords = doc.config.get("topic_keywords", {})

        # Default topic mappings if none specified
        if not topic_keywords:
            topic_keywords = self._default_topic_keywords()

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

        for keyword in keywords_to_search[:3]:
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

    def _default_topic_keywords(self) -> dict:
        """Default topic-to-keyword mappings."""
        return {
            "policy": ["policy", "procedure", "guideline"],
            "rights": ["rights", "entitlement", "privilege"],
            "responsibilities": ["responsibility", "duty", "obligation"],
            "compliance": ["compliance", "requirement", "regulation"],
            "authority": ["authority", "power", "governance"],
            "process": ["process", "procedure", "workflow"],
        }

    async def get_citation_context(
        self, section_num: int
    ) -> Optional[CitationReference]:
        """Get citation reference with full context for a section."""
        section = await self.get_section(section_num)
        if not section:
            return None

        section_label = await self.get_section_label()

        # Get a short excerpt
        content = section.content
        excerpt = content[:200] + "..." if len(content) > 200 else content

        return CitationReference(
            section_num=section.section_num,
            section_title=section.section_title,
            chapter_num=section.chapter_num,
            chapter_title=section.chapter_title,
            excerpt=excerpt,
            section_label=section_label,
        )

    async def get_chapters_summary(self) -> list[dict]:
        """Get a summary of all chapters."""
        return await self.section_repo.get_chapters()

    async def has_document(self) -> bool:
        """Check if document has been loaded."""
        return await self.section_repo.has_content()

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
            prev_section = await self.section_repo.get_by_section_num(section_num - 1)
            next_section = await self.section_repo.get_by_section_num(section_num + 1)

            if prev_section and prev_section.chapter_num == section.chapter_num:
                context["previous_section"] = prev_section
            if next_section and next_section.chapter_num == section.chapter_num:
                context["next_section"] = next_section

        return context

    async def format_section_for_prompt(self, section: DocumentSection) -> str:
        """Format a section for inclusion in an AI prompt."""
        section_label = await self.get_section_label()
        lines = [
            f"## {section_label} {section.section_num}: {section.section_title or 'Untitled'}",
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
        self, sections: list[DocumentSection]
    ) -> str:
        """Format multiple sections for inclusion in an AI prompt."""
        formatted = []
        for section in sections:
            formatted.append(await self.format_section_for_prompt(section))
        return "\n\n---\n\n".join(formatted)
