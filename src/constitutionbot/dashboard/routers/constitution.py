"""Constitution management API endpoints."""

import shutil
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from constitutionbot.config import get_settings
from constitutionbot.core.constitution.loader import ConstitutionLoader
from constitutionbot.dashboard.auth import require_auth
from constitutionbot.dashboard.schemas.responses import (
    ChapterSummary,
    ConstitutionSectionResponse,
    ConstitutionSummaryResponse,
    ConstitutionUploadResponse,
    MessageResponse,
)
from constitutionbot.database import get_session
from constitutionbot.database.repositories.constitution import ConstitutionRepository

router = APIRouter(prefix="/api/constitution", tags=["Constitution"])


@router.post("/upload", response_model=ConstitutionUploadResponse)
async def upload_constitution(
    file: UploadFile = File(...),
    _: str = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    """Upload and parse a Constitution document (PDF or TXT)."""
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
    upload_path = settings.constitution_uploads_dir / file.filename
    try:
        with open(upload_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}",
        )

    # Parse the constitution
    loader = ConstitutionLoader()
    try:
        constitution = loader.parse_file(upload_path)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to parse constitution: {str(e)}",
        )

    # Save processed JSON
    loader.save_processed(constitution)

    # Clear existing sections and add new ones
    repo = ConstitutionRepository(session)
    await repo.clear_all()

    records = loader.to_database_records(constitution)
    await repo.bulk_create(records)

    return ConstitutionUploadResponse(
        success=True,
        message="Constitution uploaded and parsed successfully",
        chapters_count=len(constitution.chapters),
        sections_count=len(constitution.all_sections),
    )


@router.get("/summary", response_model=ConstitutionSummaryResponse)
async def get_summary(
    _: str = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    """Get a summary of the loaded Constitution."""
    repo = ConstitutionRepository(session)

    is_loaded = await repo.has_content()
    if not is_loaded:
        return ConstitutionSummaryResponse(is_loaded=False)

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

    return ConstitutionSummaryResponse(
        is_loaded=True,
        total_sections=total,
        chapters=chapter_summaries,
    )


@router.get("/sections", response_model=list[ConstitutionSectionResponse])
async def list_sections(
    chapter_num: int | None = None,
    limit: int = 100,
    offset: int = 0,
    _: str = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    """List constitution sections."""
    repo = ConstitutionRepository(session)

    if chapter_num:
        sections = await repo.get_by_chapter(chapter_num)
    else:
        sections = await repo.get_all(limit=limit, offset=offset)

    return [ConstitutionSectionResponse.model_validate(s) for s in sections]


@router.get("/sections/{section_num}", response_model=ConstitutionSectionResponse)
async def get_section(
    section_num: int,
    _: str = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    """Get a specific section by number."""
    repo = ConstitutionRepository(session)
    section = await repo.get_by_section_num(section_num)

    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Section {section_num} not found",
        )

    return ConstitutionSectionResponse.model_validate(section)


@router.get("/search", response_model=list[ConstitutionSectionResponse])
async def search_sections(
    q: str,
    limit: int = 20,
    _: str = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    """Search constitution sections."""
    repo = ConstitutionRepository(session)
    sections = await repo.search(q, limit=limit)
    return [ConstitutionSectionResponse.model_validate(s) for s in sections]


@router.delete("", response_model=MessageResponse)
async def clear_constitution(
    _: str = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    """Clear all constitution data (for re-upload)."""
    repo = ConstitutionRepository(session)
    deleted = await repo.clear_all()

    return MessageResponse(
        success=True,
        message=f"Cleared {deleted} constitution sections",
    )
