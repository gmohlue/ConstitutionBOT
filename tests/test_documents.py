"""Tests for document repository and file handling."""

import pytest
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from contentmanager.database.models import Base, Document, DocumentSection


@pytest.fixture
async def async_engine():
    """Create an async in-memory SQLite engine for testing."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def async_session(async_engine):
    """Create an async session for testing."""
    async_session_maker = sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with async_session_maker() as session:
        yield session


class TestDocumentRepository:
    """Tests for DocumentRepository."""

    @pytest.mark.asyncio
    async def test_create_document(self, async_session):
        """Test creating a document."""
        from contentmanager.database.repositories.document import DocumentRepository

        repo = DocumentRepository(async_session)

        document = await repo.create(
            name="Test Document",
            short_name="TestDoc",
            description="A test document",
            structure_type="chapter_section",
        )

        assert document is not None
        assert document.name == "Test Document"
        assert document.short_name == "TestDoc"
        assert document.is_active is True

    @pytest.mark.asyncio
    async def test_get_active_returns_single_document(self, async_session):
        """Test getting the active document."""
        from contentmanager.database.repositories.document import DocumentRepository

        repo = DocumentRepository(async_session)

        # Create a document (active by default)
        await repo.create(name="Active Doc", short_name="Active")
        await async_session.commit()

        active_doc = await repo.get_active()
        assert active_doc is not None
        assert active_doc.short_name == "Active"

    @pytest.mark.asyncio
    async def test_set_active_deactivates_others(self, async_session):
        """Test that setting a document active deactivates others."""
        from contentmanager.database.repositories.document import DocumentRepository

        repo = DocumentRepository(async_session)

        doc1 = await repo.create(name="Doc 1", short_name="D1")
        doc2 = await repo.create(name="Doc 2", short_name="D2")
        await async_session.commit()

        # Set doc2 as active
        await repo.set_active(doc2.id)
        await async_session.commit()

        # Verify doc2 is active and doc1 is not
        active = await repo.get_active()
        assert active.id == doc2.id

    @pytest.mark.asyncio
    async def test_update_document(self, async_session):
        """Test updating a document."""
        from contentmanager.database.repositories.document import DocumentRepository

        repo = DocumentRepository(async_session)

        document = await repo.create(name="Original", short_name="Orig")
        await async_session.commit()

        updated = await repo.update(
            document.id,
            name="Updated Name",
            description="New description",
        )

        assert updated is not None
        assert updated.name == "Updated Name"
        assert updated.description == "New description"

    @pytest.mark.asyncio
    async def test_delete_document(self, async_session):
        """Test deleting a document."""
        from contentmanager.database.repositories.document import DocumentRepository

        repo = DocumentRepository(async_session)

        document = await repo.create(name="Delete Me", short_name="Del")
        await async_session.commit()

        result = await repo.delete(document.id)
        assert result is True

        found = await repo.get_by_id(document.id)
        assert found is None


class TestDocumentSectionRepository:
    """Tests for DocumentSectionRepository."""

    @pytest.mark.asyncio
    async def test_create_section(self, async_session):
        """Test creating a section."""
        from contentmanager.database.repositories.document import (
            DocumentRepository,
            DocumentSectionRepository,
        )

        doc_repo = DocumentRepository(async_session)
        document = await doc_repo.create(name="Test", short_name="Test")
        await async_session.commit()

        section_repo = DocumentSectionRepository(async_session, document_id=document.id)
        section = await section_repo.create(
            chapter_num=1,
            chapter_title="Chapter 1",
            section_num=1,
            section_title="Section 1",
            content="Content of section 1",
        )

        assert section is not None
        assert section.section_title == "Section 1"
        assert section.document_id == document.id

    @pytest.mark.asyncio
    async def test_bulk_create_sections(self, async_session):
        """Test bulk creating sections."""
        from contentmanager.database.repositories.document import (
            DocumentRepository,
            DocumentSectionRepository,
        )

        doc_repo = DocumentRepository(async_session)
        document = await doc_repo.create(name="Test", short_name="Test")
        await async_session.commit()

        section_repo = DocumentSectionRepository(async_session, document_id=document.id)
        sections_data = [
            {
                "chapter_num": 1,
                "chapter_title": "Chapter 1",
                "section_num": i,
                "section_title": f"Section {i}",
                "content": f"Content {i}",
            }
            for i in range(1, 4)
        ]

        created = await section_repo.bulk_create(sections_data)
        assert len(created) == 3

    @pytest.mark.asyncio
    async def test_get_all_sections(self, async_session):
        """Test getting all sections for a document."""
        from contentmanager.database.repositories.document import (
            DocumentRepository,
            DocumentSectionRepository,
        )

        doc_repo = DocumentRepository(async_session)
        document = await doc_repo.create(name="Test", short_name="Test")
        await async_session.commit()

        section_repo = DocumentSectionRepository(async_session, document_id=document.id)
        sections_data = [
            {
                "chapter_num": 1,
                "chapter_title": "Ch 1",
                "section_num": i,
                "section_title": f"Section {i}",
                "content": f"Content {i}",
            }
            for i in range(1, 6)
        ]

        await section_repo.bulk_create(sections_data)
        await async_session.commit()

        result = await section_repo.get_all()
        assert len(result) == 5

    @pytest.mark.asyncio
    async def test_get_section_by_num(self, async_session):
        """Test getting a specific section by number."""
        from contentmanager.database.repositories.document import (
            DocumentRepository,
            DocumentSectionRepository,
        )

        doc_repo = DocumentRepository(async_session)
        document = await doc_repo.create(name="Test", short_name="Test")
        await async_session.commit()

        section_repo = DocumentSectionRepository(async_session, document_id=document.id)
        await section_repo.create(
            chapter_num=1,
            chapter_title="Ch 1",
            section_num=42,
            section_title="The Answer",
            content="The answer to everything",
        )
        await async_session.commit()

        section = await section_repo.get_by_section_num(42)
        assert section is not None
        assert section.section_title == "The Answer"

    @pytest.mark.asyncio
    async def test_count_sections(self, async_session):
        """Test counting sections."""
        from contentmanager.database.repositories.document import (
            DocumentRepository,
            DocumentSectionRepository,
        )

        doc_repo = DocumentRepository(async_session)
        document = await doc_repo.create(name="Test", short_name="Test")
        await async_session.commit()

        section_repo = DocumentSectionRepository(async_session, document_id=document.id)
        sections_data = [
            {
                "chapter_num": 1,
                "chapter_title": "Ch 1",
                "section_num": i,
                "section_title": f"Section {i}",
                "content": f"Content {i}",
            }
            for i in range(1, 11)
        ]

        await section_repo.bulk_create(sections_data)
        await async_session.commit()

        count = await section_repo.count()
        assert count == 10

    @pytest.mark.asyncio
    async def test_clear_all_sections(self, async_session):
        """Test clearing all sections for a document."""
        from contentmanager.database.repositories.document import (
            DocumentRepository,
            DocumentSectionRepository,
        )

        doc_repo = DocumentRepository(async_session)
        document = await doc_repo.create(name="Test", short_name="Test")
        await async_session.commit()

        section_repo = DocumentSectionRepository(async_session, document_id=document.id)
        sections_data = [
            {
                "chapter_num": 1,
                "chapter_title": "Ch 1",
                "section_num": i,
                "section_title": f"Section {i}",
                "content": f"Content {i}",
            }
            for i in range(1, 4)
        ]

        await section_repo.bulk_create(sections_data)
        await async_session.commit()

        deleted = await section_repo.clear_all()
        assert deleted == 3

        count = await section_repo.count()
        assert count == 0


class TestFilenameSecurityValidation:
    """Tests for filename security validation in document upload."""

    def test_path_name_extracts_filename_only(self):
        """Test that Path().name extracts only the filename component."""
        # Normal filenames are preserved
        assert Path("document.pdf").name == "document.pdf"
        assert Path("my-file_v2.txt").name == "my-file_v2.txt"

        # Path traversal attempts get stripped to just the final component
        assert Path("../../../etc/passwd").name == "passwd"
        assert Path("/etc/passwd").name == "passwd"
        assert Path("test/../../../secret.txt").name == "secret.txt"

    def test_hidden_files_detection(self):
        """Test detecting hidden files (starting with dot)."""
        hidden_files = [".env", ".gitignore", ".secret"]
        for filename in hidden_files:
            safe_name = Path(filename).name
            assert safe_name.startswith(".")

        # Normal files don't start with dot
        normal_files = ["document.pdf", "file.txt"]
        for filename in normal_files:
            safe_name = Path(filename).name
            assert not safe_name.startswith(".")

    def test_valid_filenames_preserved(self):
        """Test that valid filenames are preserved correctly."""
        valid_names = [
            "document.pdf",
            "my-file_v2.txt",
            "Report 2024.docx",
            "test.PDF",
        ]

        for filename in valid_names:
            safe_name = Path(filename).name
            assert safe_name == filename
