"""Document management API endpoints."""

import shutil
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from contentmanager.config import get_settings
from contentmanager.core.document.loader import DocumentLoader
from contentmanager.dashboard.auth import require_auth
from contentmanager.dashboard.schemas.responses import (
    ChapterSummary,
    DocumentSectionResponse,
    DocumentSummaryResponse,
    DocumentUploadResponse,
    MessageResponse,
)
from contentmanager.database import get_session
from contentmanager.database.repositories.document import DocumentRepository, DocumentSectionRepository

router = APIRouter(prefix="/api/documents", tags=["Documents"])


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    _: str = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    """Upload and parse a document (PDF or TXT)."""
    settings = get_settings()

    # Validate file type
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided",
        )

    suffix = Path(file.filename).suffix.lower()
    if suffix not in (".pdf", ".txt", ".text"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF and TXT files are supported",
        )

    # Save uploaded file
    upload_path = settings.document_uploads_dir / file.filename
    try:
        with open(upload_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}",
        )

    # Parse the document
    loader = DocumentLoader()
    # Derive name from filename (remove extension)
    doc_name = Path(file.filename).stem.replace("_", " ").replace("-", " ").title()
    short_name = doc_name[:50] if len(doc_name) > 50 else doc_name
    try:
        document = loader.parse_file(upload_path, name=doc_name, short_name=short_name)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to parse document: {str(e)}",
        )

    # Save processed JSON
    loader.save_processed(document)

    # Create or get document record in database
    doc_repo = DocumentRepository(session)
    existing_doc = await doc_repo.get_by_short_name(short_name)
    if existing_doc:
        db_doc = existing_doc
    else:
        db_doc = await doc_repo.create(
            name=doc_name,
            short_name=short_name,
            description=document.description,
        )
    # Always set the uploaded document as active
    await doc_repo.set_active(db_doc.id)

    # Clear existing sections and add new ones
    repo = DocumentSectionRepository(session, document_id=db_doc.id)
    await repo.clear_all(document_id=db_doc.id)

    records = loader.to_database_records(document, document_id=db_doc.id)
    await repo.bulk_create(records, document_id=db_doc.id)

    return DocumentUploadResponse(
        success=True,
        message="Document uploaded and parsed successfully",
        chapters_count=len(document.chapters),
        sections_count=len(document.all_sections),
    )


@router.get("/summary", response_model=DocumentSummaryResponse)
async def get_summary(
    _: str = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    """Get a summary of the loaded document."""
    repo = DocumentSectionRepository(session)

    is_loaded = await repo.has_content()
    if not is_loaded:
        return DocumentSummaryResponse(is_loaded=False)

    total = await repo.count()
    chapters = await repo.get_chapters()

    chapter_summaries = []
    for chapter in chapters:
        chapter_sections = await repo.get_by_chapter(chapter["chapter_num"])
        chapter_summaries.append(
            ChapterSummary(
                chapter_num=chapter["chapter_num"],
                chapter_title=chapter["chapter_title"],
                sections_count=len(chapter_sections),
            )
        )

    return DocumentSummaryResponse(
        is_loaded=True,
        total_sections=total,
        chapters=chapter_summaries,
    )


@router.get("/sections", response_model=list[DocumentSectionResponse])
async def list_sections(
    chapter_num: int | None = None,
    limit: int = 100,
    offset: int = 0,
    _: str = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    """List document sections."""
    repo = DocumentSectionRepository(session)

    if chapter_num:
        sections = await repo.get_by_chapter(chapter_num)
    else:
        sections = await repo.get_all(limit=limit, offset=offset)

    return [DocumentSectionResponse.model_validate(s) for s in sections]


@router.get("/sections/{section_num}", response_model=DocumentSectionResponse)
async def get_section(
    section_num: int,
    _: str = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    """Get a specific section by number."""
    repo = DocumentSectionRepository(session)
    section = await repo.get_by_section_num(section_num)

    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Section {section_num} not found",
        )

    return DocumentSectionResponse.model_validate(section)


@router.get("/search", response_model=list[DocumentSectionResponse])
async def search_sections(
    q: str,
    limit: int = 20,
    _: str = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    """Search document sections."""
    repo = DocumentSectionRepository(session)
    sections = await repo.search(q, limit=limit)
    return [DocumentSectionResponse.model_validate(s) for s in sections]


@router.delete("", response_model=MessageResponse)
async def clear_document(
    _: str = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    """Clear all document data (for re-upload)."""
    repo = DocumentSectionRepository(session)
    deleted = await repo.clear_all()

    return MessageResponse(
        success=True,
        message=f"Cleared {deleted} document sections",
    )
