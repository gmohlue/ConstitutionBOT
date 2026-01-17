"""Repository for Document and DocumentSection management."""

from typing import Optional

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from contentmanager.database.models import Document, DocumentSection


class DocumentRepository:
    """Repository for managing documents."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        name: str,
        short_name: str,
        description: Optional[str] = None,
        structure_type: str = "chapter_section",
        section_label: str = "Section",
        config: Optional[dict] = None,
        custom_prompts: Optional[dict] = None,
        historical_events: Optional[list] = None,
        default_hashtags: Optional[list] = None,
    ) -> Document:
        """Create a new document."""
        doc = Document(
            name=name,
            short_name=short_name,
            description=description,
            structure_type=structure_type,
            section_label=section_label,
            config=config,
            custom_prompts=custom_prompts,
            historical_events=historical_events,
            default_hashtags=default_hashtags,
        )
        self.session.add(doc)
        await self.session.flush()
        await self.session.refresh(doc)
        return doc

    async def get_by_id(self, document_id: int) -> Optional[Document]:
        """Get a document by ID."""
        result = await self.session.execute(
            select(Document).where(Document.id == document_id)
        )
        return result.scalar_one_or_none()

    async def get_by_short_name(self, short_name: str) -> Optional[Document]:
        """Get a document by short name."""
        result = await self.session.execute(
            select(Document).where(Document.short_name == short_name)
        )
        return result.scalar_one_or_none()

    async def get_active(self) -> Optional[Document]:
        """Get the currently active document."""
        result = await self.session.execute(
            select(Document).where(Document.is_active == True).limit(1)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> list[Document]:
        """Get all documents."""
        result = await self.session.execute(
            select(Document).order_by(Document.created_at.desc())
        )
        return list(result.scalars().all())

    async def set_active(self, document_id: int) -> bool:
        """Set a document as active (deactivates others)."""
        # Deactivate all
        all_docs = await self.get_all()
        for doc in all_docs:
            doc.is_active = False

        # Activate the specified one
        doc = await self.get_by_id(document_id)
        if doc:
            doc.is_active = True
            await self.session.flush()
            return True
        return False

    async def update(
        self,
        document_id: int,
        **kwargs,
    ) -> Optional[Document]:
        """Update a document."""
        doc = await self.get_by_id(document_id)
        if not doc:
            return None

        for key, value in kwargs.items():
            if hasattr(doc, key):
                setattr(doc, key, value)

        await self.session.flush()
        await self.session.refresh(doc)
        return doc

    async def delete(self, document_id: int) -> bool:
        """Delete a document and its sections."""
        # Delete sections first
        await self.session.execute(
            delete(DocumentSection).where(DocumentSection.document_id == document_id)
        )
        # Delete document
        result = await self.session.execute(
            delete(Document).where(Document.id == document_id)
        )
        await self.session.flush()
        return result.rowcount > 0


class DocumentSectionRepository:
    """Repository for managing document sections."""

    def __init__(self, session: AsyncSession, document_id: Optional[int] = None):
        self.session = session
        self._document_id = document_id

    async def _get_document_id(self) -> int:
        """Get the document ID to use for queries."""
        if self._document_id:
            return self._document_id
        # Get active document
        doc_repo = DocumentRepository(self.session)
        doc = await doc_repo.get_active()
        if doc:
            return doc.id
        raise ValueError("No active document found")

    async def create(
        self,
        chapter_num: int,
        chapter_title: str,
        content: str,
        document_id: Optional[int] = None,
        section_num: Optional[int] = None,
        section_title: Optional[str] = None,
        subsections: Optional[dict] = None,
        keywords: Optional[list] = None,
    ) -> DocumentSection:
        """Create a new document section."""
        doc_id = document_id or await self._get_document_id()
        section = DocumentSection(
            document_id=doc_id,
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

    async def bulk_create(
        self, sections: list[dict], document_id: Optional[int] = None
    ) -> list[DocumentSection]:
        """Bulk create document sections."""
        doc_id = document_id or await self._get_document_id()
        created = []
        for section_data in sections:
            section_data["document_id"] = doc_id
            section = await self.create(**section_data)
            created.append(section)
        return created

    async def get_by_id(self, section_id: int) -> Optional[DocumentSection]:
        """Get a section by ID."""
        result = await self.session.execute(
            select(DocumentSection).where(DocumentSection.id == section_id)
        )
        return result.scalar_one_or_none()

    async def get_by_section_num(
        self, section_num: int, document_id: Optional[int] = None
    ) -> Optional[DocumentSection]:
        """Get a section by its section number."""
        doc_id = document_id or await self._get_document_id()
        result = await self.session.execute(
            select(DocumentSection).where(
                DocumentSection.document_id == doc_id,
                DocumentSection.section_num == section_num,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_chapter(
        self, chapter_num: int, document_id: Optional[int] = None
    ) -> list[DocumentSection]:
        """Get all sections in a chapter."""
        doc_id = document_id or await self._get_document_id()
        result = await self.session.execute(
            select(DocumentSection)
            .where(
                DocumentSection.document_id == doc_id,
                DocumentSection.chapter_num == chapter_num,
            )
            .order_by(DocumentSection.section_num)
        )
        return list(result.scalars().all())

    async def get_all(
        self,
        document_id: Optional[int] = None,
        limit: int = 500,
        offset: int = 0,
    ) -> list[DocumentSection]:
        """Get all document sections."""
        doc_id = document_id or await self._get_document_id()
        result = await self.session.execute(
            select(DocumentSection)
            .where(DocumentSection.document_id == doc_id)
            .order_by(DocumentSection.chapter_num, DocumentSection.section_num)
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def get_chapters(self, document_id: Optional[int] = None) -> list[dict]:
        """Get list of unique chapters."""
        doc_id = document_id or await self._get_document_id()
        result = await self.session.execute(
            select(
                DocumentSection.chapter_num,
                DocumentSection.chapter_title,
            )
            .where(DocumentSection.document_id == doc_id)
            .distinct()
            .order_by(DocumentSection.chapter_num)
        )
        return [
            {"chapter_num": row[0], "chapter_title": row[1]}
            for row in result.all()
        ]

    async def search(
        self,
        query: str,
        document_id: Optional[int] = None,
        limit: int = 20,
    ) -> list[DocumentSection]:
        """Search sections by content or title."""
        doc_id = document_id or await self._get_document_id()
        search_pattern = f"%{query}%"
        result = await self.session.execute(
            select(DocumentSection)
            .where(
                DocumentSection.document_id == doc_id,
                (
                    DocumentSection.content.ilike(search_pattern)
                    | DocumentSection.section_title.ilike(search_pattern)
                    | DocumentSection.chapter_title.ilike(search_pattern)
                ),
            )
            .order_by(DocumentSection.chapter_num, DocumentSection.section_num)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def clear_all(self, document_id: Optional[int] = None) -> int:
        """Delete all sections for a document. Returns count deleted."""
        try:
            doc_id = document_id or await self._get_document_id()
        except ValueError:
            return 0
        result = await self.session.execute(
            delete(DocumentSection).where(DocumentSection.document_id == doc_id)
        )
        await self.session.flush()
        return result.rowcount

    async def count(self, document_id: Optional[int] = None) -> int:
        """Count total document sections."""
        try:
            doc_id = document_id or await self._get_document_id()
        except ValueError:
            return 0
        result = await self.session.execute(
            select(func.count(DocumentSection.id)).where(
                DocumentSection.document_id == doc_id
            )
        )
        return result.scalar() or 0

    async def has_content(self, document_id: Optional[int] = None) -> bool:
        """Check if document has been uploaded."""
        try:
            count = await self.count(document_id)
            return count > 0
        except ValueError:
            return False
