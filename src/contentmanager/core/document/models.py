"""Pydantic models for document data structures."""

from typing import Optional

from pydantic import BaseModel, Field


class Subsection(BaseModel):
    """A subsection within a section."""

    letter: str = Field(description="Subsection identifier (a, b, c, etc.)")
    content: str = Field(description="Text content of the subsection")


class Section(BaseModel):
    """A section of a document."""

    section_num: int = Field(description="Section number")
    title: Optional[str] = Field(default=None, description="Section title/heading")
    content: str = Field(description="Main text content of the section")
    subsections: list[Subsection] = Field(default_factory=list, description="List of subsections")
    keywords: list[str] = Field(default_factory=list, description="Keywords for search")

    @property
    def full_text(self) -> str:
        """Get the full text including subsections."""
        text = self.content
        for sub in self.subsections:
            text += f"\n({sub.letter}) {sub.content}"
        return text

    def get_citation(self, label: str = "Section") -> str:
        """Get citation reference for this section."""
        return f"{label} {self.section_num}"


class Chapter(BaseModel):
    """A chapter of a document."""

    chapter_num: int = Field(description="Chapter number")
    title: str = Field(description="Chapter title")
    sections: list[Section] = Field(default_factory=list, description="Sections in this chapter")
    preamble: Optional[str] = Field(default=None, description="Chapter preamble text if any")

    @property
    def section_range(self) -> tuple[int, int]:
        """Get the range of section numbers in this chapter."""
        if not self.sections:
            return (0, 0)
        nums = [s.section_num for s in self.sections]
        return (min(nums), max(nums))


class ParsedDocument(BaseModel):
    """A fully parsed document."""

    name: str = Field(description="Document name")
    short_name: str = Field(description="Short name for prompts")
    description: Optional[str] = Field(default=None, description="Document description")
    preamble: Optional[str] = Field(default=None, description="Document preamble")
    chapters: list[Chapter] = Field(default_factory=list, description="List of chapters")
    section_label: str = Field(default="Section", description="Label for sections (Section, Article, etc.)")

    @property
    def all_sections(self) -> list[Section]:
        """Get all sections from all chapters."""
        sections = []
        for chapter in self.chapters:
            sections.extend(chapter.sections)
        return sections

    @property
    def section_count(self) -> int:
        """Get total number of sections."""
        return len(self.all_sections)

    @property
    def chapter_count(self) -> int:
        """Get total number of chapters."""
        return len(self.chapters)

    @property
    def section_range(self) -> tuple[int, int]:
        """Get the valid section number range."""
        sections = self.all_sections
        if not sections:
            return (0, 0)
        nums = [s.section_num for s in sections]
        return (min(nums), max(nums))

    def get_section(self, section_num: int) -> Optional[Section]:
        """Get a specific section by number."""
        for chapter in self.chapters:
            for section in chapter.sections:
                if section.section_num == section_num:
                    return section
        return None

    def get_chapter(self, chapter_num: int) -> Optional[Chapter]:
        """Get a specific chapter by number."""
        for chapter in self.chapters:
            if chapter.chapter_num == chapter_num:
                return chapter
        return None


class CitationReference(BaseModel):
    """A reference to a specific part of a document."""

    section_num: int
    section_title: Optional[str] = None
    chapter_num: Optional[int] = None
    chapter_title: Optional[str] = None
    excerpt: Optional[str] = None
    section_label: str = "Section"  # "Section", "Article", etc.

    @property
    def display(self) -> str:
        """Get display string for this citation."""
        parts = [f"{self.section_label} {self.section_num}"]
        if self.section_title:
            parts.append(f"({self.section_title})")
        return " ".join(parts)


class DocumentContext(BaseModel):
    """Context object for document-aware prompt generation."""

    document_name: str
    document_short_name: str
    section_label: str = "Section"
    description: Optional[str] = None
    default_hashtags: list[str] = Field(default_factory=list)

    @classmethod
    def from_document(cls, doc: "ParsedDocument") -> "DocumentContext":
        """Create context from a parsed document."""
        return cls(
            document_name=doc.name,
            document_short_name=doc.short_name,
            section_label=doc.section_label,
            description=doc.description,
        )
