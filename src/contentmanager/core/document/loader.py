"""Document loader and parser with configurable parsing strategies."""

import json
import re
from pathlib import Path
from typing import Optional

import fitz  # PyMuPDF

from contentmanager.config import get_settings
from contentmanager.core.document.models import (
    Chapter,
    ParsedDocument,
    Section,
    Subsection,
)


class ParsingStrategy:
    """Base class for document parsing strategies."""

    # Default patterns (can be overridden)
    CHAPTER_PATTERN = re.compile(
        r"^CHAPTER\s+(\d+)\s*[-–—:]?\s*(.+?)$",
        re.MULTILINE | re.IGNORECASE
    )
    SECTION_PATTERN = re.compile(
        r"^(\d+)\.\s+(.+?)$",
        re.MULTILINE
    )
    SUBSECTION_PATTERN = re.compile(
        r"^\s*\(([a-z])\)\s*(.+?)$",
        re.MULTILINE
    )

    # Default keywords for extraction
    DEFAULT_KEYWORDS = [
        "rights", "freedom", "equality", "justice", "law", "legal",
        "policy", "procedure", "requirement", "obligation", "duty",
        "authority", "power", "responsibility", "compliance", "regulation",
    ]

    def __init__(
        self,
        chapter_pattern: Optional[re.Pattern] = None,
        section_pattern: Optional[re.Pattern] = None,
        subsection_pattern: Optional[re.Pattern] = None,
        keywords: Optional[list[str]] = None,
    ):
        if chapter_pattern:
            self.CHAPTER_PATTERN = chapter_pattern
        if section_pattern:
            self.SECTION_PATTERN = section_pattern
        if subsection_pattern:
            self.SUBSECTION_PATTERN = subsection_pattern
        self.keywords = keywords or self.DEFAULT_KEYWORDS


class ChapterSectionStrategy(ParsingStrategy):
    """Strategy for documents with Chapter X / Section Y structure."""
    pass


class ArticleStrategy(ParsingStrategy):
    """Strategy for documents with Article-based structure."""

    CHAPTER_PATTERN = re.compile(
        r"^(?:PART|TITLE)\s+(\d+|[IVXLC]+)\s*[-–—:]?\s*(.+?)$",
        re.MULTILINE | re.IGNORECASE
    )
    SECTION_PATTERN = re.compile(
        r"^(?:Article|Art\.?)\s+(\d+)\s*[-–—:]?\s*(.+?)$",
        re.MULTILINE | re.IGNORECASE
    )


class NumberedListStrategy(ParsingStrategy):
    """Strategy for simple numbered documents."""

    CHAPTER_PATTERN = re.compile(
        r"^(?:Part|Section)\s+(\d+)\s*[-–—:]?\s*(.+?)$",
        re.MULTILINE | re.IGNORECASE
    )
    SECTION_PATTERN = re.compile(
        r"^(\d+)\.\s+(.+?)$",
        re.MULTILINE
    )


# Strategy registry
PARSING_STRATEGIES = {
    "chapter_section": ChapterSectionStrategy,
    "article": ArticleStrategy,
    "numbered_list": NumberedListStrategy,
    "custom": ParsingStrategy,
}


class DocumentLoader:
    """Load and parse documents from PDF or TXT files."""

    def __init__(self, strategy: Optional[ParsingStrategy] = None):
        self.settings = get_settings()
        self.strategy = strategy or ChapterSectionStrategy()

    @classmethod
    def with_strategy(cls, strategy_name: str, **kwargs) -> "DocumentLoader":
        """Create a loader with a specific parsing strategy."""
        strategy_class = PARSING_STRATEGIES.get(strategy_name, ChapterSectionStrategy)
        strategy = strategy_class(**kwargs)
        return cls(strategy=strategy)

    @classmethod
    def with_custom_patterns(
        cls,
        chapter_pattern: str,
        section_pattern: str,
        subsection_pattern: Optional[str] = None,
        keywords: Optional[list[str]] = None,
    ) -> "DocumentLoader":
        """Create a loader with custom regex patterns."""
        strategy = ParsingStrategy(
            chapter_pattern=re.compile(chapter_pattern, re.MULTILINE | re.IGNORECASE),
            section_pattern=re.compile(section_pattern, re.MULTILINE),
            subsection_pattern=re.compile(subsection_pattern, re.MULTILINE) if subsection_pattern else None,
            keywords=keywords,
        )
        return cls(strategy=strategy)

    def load_from_pdf(self, file_path: Path) -> str:
        """Extract text from a PDF file."""
        doc = fitz.open(file_path)
        text_parts = []

        for page in doc:
            text = page.get_text("text")
            text_parts.append(text)

        doc.close()
        return "\n".join(text_parts)

    def load_from_txt(self, file_path: Path) -> str:
        """Load text from a TXT file."""
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def load_file(self, file_path: Path) -> str:
        """Load a file based on its extension."""
        suffix = file_path.suffix.lower()
        if suffix == ".pdf":
            return self.load_from_pdf(file_path)
        elif suffix in (".txt", ".text"):
            return self.load_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {suffix}")

    def parse_text(
        self,
        text: str,
        name: str,
        short_name: str,
        description: Optional[str] = None,
        section_label: str = "Section",
    ) -> ParsedDocument:
        """Parse document text into structured format."""
        document = ParsedDocument(
            name=name,
            short_name=short_name,
            description=description,
            section_label=section_label,
        )

        # Extract preamble (text before first chapter)
        first_chapter = self.strategy.CHAPTER_PATTERN.search(text)
        if first_chapter:
            preamble_text = text[:first_chapter.start()].strip()
            if preamble_text:
                document.preamble = self._clean_text(preamble_text)

        # Find all chapters
        chapter_matches = list(self.strategy.CHAPTER_PATTERN.finditer(text))

        if not chapter_matches:
            # No chapters found - treat entire document as one chapter
            sections = self._parse_sections(text, 1)
            if sections:
                chapter = Chapter(
                    chapter_num=1,
                    title=name,
                    sections=sections,
                )
                document.chapters.append(chapter)
        else:
            for i, match in enumerate(chapter_matches):
                chapter_num = self._parse_chapter_num(match.group(1))
                chapter_title = self._clean_text(match.group(2))

                # Get chapter content (text until next chapter or end)
                start_pos = match.end()
                end_pos = chapter_matches[i + 1].start() if i + 1 < len(chapter_matches) else len(text)
                chapter_text = text[start_pos:end_pos]

                # Parse sections within chapter
                sections = self._parse_sections(chapter_text, chapter_num)

                chapter = Chapter(
                    chapter_num=chapter_num,
                    title=chapter_title,
                    sections=sections,
                )
                document.chapters.append(chapter)

        return document

    def _parse_chapter_num(self, num_str: str) -> int:
        """Parse chapter number from string (handles Roman numerals)."""
        num_str = num_str.strip()
        if num_str.isdigit():
            return int(num_str)
        # Try Roman numerals
        roman_map = {
            'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100
        }
        try:
            result = 0
            prev = 0
            for char in reversed(num_str.upper()):
                val = roman_map.get(char, 0)
                if val < prev:
                    result -= val
                else:
                    result += val
                prev = val
            return result if result > 0 else 1
        except (KeyError, ValueError):
            return 1

    def _parse_sections(self, chapter_text: str, chapter_num: int) -> list[Section]:
        """Parse sections from chapter text."""
        sections = []
        section_matches = list(self.strategy.SECTION_PATTERN.finditer(chapter_text))

        for i, match in enumerate(section_matches):
            section_num = int(match.group(1))
            section_title = self._clean_text(match.group(2))

            # Get section content (text until next section or end)
            start_pos = match.end()
            end_pos = section_matches[i + 1].start() if i + 1 < len(section_matches) else len(chapter_text)
            section_text = chapter_text[start_pos:end_pos].strip()

            # Parse subsections
            subsections, main_content = self._parse_subsections(section_text)

            # Extract keywords from content
            keywords = self._extract_keywords(section_title, main_content)

            section = Section(
                section_num=section_num,
                title=section_title,
                content=main_content,
                subsections=subsections,
                keywords=keywords,
            )
            sections.append(section)

        return sections

    def _parse_subsections(self, text: str) -> tuple[list[Subsection], str]:
        """Parse subsections and return remaining main content."""
        subsections = []
        main_content_parts = []

        lines = text.split("\n")
        current_subsection = None

        for line in lines:
            subsection_match = self.strategy.SUBSECTION_PATTERN.match(line)
            if subsection_match:
                if current_subsection:
                    subsections.append(current_subsection)
                current_subsection = Subsection(
                    letter=subsection_match.group(1),
                    content=self._clean_text(subsection_match.group(2)),
                )
            elif current_subsection:
                # Continuation of subsection
                current_subsection.content += " " + self._clean_text(line)
            else:
                # Main content before subsections
                main_content_parts.append(line)

        if current_subsection:
            subsections.append(current_subsection)

        main_content = self._clean_text("\n".join(main_content_parts))
        return subsections, main_content

    def _extract_keywords(self, title: str, content: str) -> list[str]:
        """Extract keywords from section title and content."""
        text = f"{title} {content}".lower()

        found_keywords = []
        for keyword in self.strategy.keywords:
            if keyword in text:
                found_keywords.append(keyword)

        return found_keywords[:10]  # Limit to 10 keywords

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        text = re.sub(r"\s+", " ", text)
        text = text.strip()
        return text

    def parse_file(
        self,
        file_path: Path,
        name: str,
        short_name: str,
        description: Optional[str] = None,
        section_label: str = "Section",
    ) -> ParsedDocument:
        """Load and parse a document file."""
        text = self.load_file(file_path)
        return self.parse_text(
            text=text,
            name=name,
            short_name=short_name,
            description=description,
            section_label=section_label,
        )

    def save_processed(
        self,
        document: ParsedDocument,
        output_path: Optional[Path] = None,
    ) -> Path:
        """Save processed document to JSON file."""
        if output_path is None:
            safe_name = document.short_name.lower().replace(" ", "_")
            output_path = self.settings.document_processed_dir / f"{safe_name}.json"

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(document.model_dump(), f, indent=2, ensure_ascii=False)

        return output_path

    def load_processed(self, path: Path) -> Optional[ParsedDocument]:
        """Load a previously processed document from JSON."""
        if not path.exists():
            return None

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return ParsedDocument.model_validate(data)

    def to_database_records(self, document: ParsedDocument, document_id: int) -> list[dict]:
        """Convert parsed document to database record format."""
        records = []

        for chapter in document.chapters:
            for section in chapter.sections:
                record = {
                    "document_id": document_id,
                    "chapter_num": chapter.chapter_num,
                    "chapter_title": chapter.title,
                    "section_num": section.section_num,
                    "section_title": section.title,
                    "content": section.full_text,
                    "subsections": [s.model_dump() for s in section.subsections],
                    "keywords": section.keywords,
                }
                records.append(record)

        return records


# Backward compatibility alias
ConstitutionLoader = DocumentLoader
