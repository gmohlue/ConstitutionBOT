"""Constitution document loader and parser."""

import json
import re
from pathlib import Path
from typing import Optional

import fitz  # PyMuPDF

from constitutionbot.config import get_settings
from constitutionbot.core.constitution.models import (
    Chapter,
    ParsedConstitution,
    Section,
    Subsection,
)


class ConstitutionLoader:
    """Load and parse Constitution documents from PDF or TXT files."""

    # Regex patterns for parsing the SA Constitution
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

    def __init__(self):
        self.settings = get_settings()

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

    def parse_text(self, text: str) -> ParsedConstitution:
        """Parse Constitution text into structured format."""
        constitution = ParsedConstitution()

        # Extract preamble (text before first chapter)
        first_chapter = self.CHAPTER_PATTERN.search(text)
        if first_chapter:
            preamble_text = text[:first_chapter.start()].strip()
            if preamble_text:
                constitution.preamble = self._clean_text(preamble_text)

        # Find all chapters
        chapter_matches = list(self.CHAPTER_PATTERN.finditer(text))

        for i, match in enumerate(chapter_matches):
            chapter_num = int(match.group(1))
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
            constitution.chapters.append(chapter)

        return constitution

    def _parse_sections(self, chapter_text: str, chapter_num: int) -> list[Section]:
        """Parse sections from chapter text."""
        sections = []
        section_matches = list(self.SECTION_PATTERN.finditer(chapter_text))

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
            subsection_match = self.SUBSECTION_PATTERN.match(line)
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
        # Combine title and content
        text = f"{title} {content}".lower()

        # Common constitutional keywords to look for
        keyword_patterns = [
            "rights", "freedom", "equality", "dignity", "justice",
            "democracy", "vote", "citizen", "parliament", "court",
            "president", "minister", "province", "municipal", "property",
            "education", "health", "housing", "water", "environment",
            "children", "language", "culture", "religion", "expression",
            "assembly", "association", "labour", "trade", "union",
            "arrest", "detention", "trial", "legal", "access",
            "information", "privacy", "administrative", "enforcement",
        ]

        found_keywords = []
        for keyword in keyword_patterns:
            if keyword in text:
                found_keywords.append(keyword)

        return found_keywords[:10]  # Limit to 10 keywords

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        # Remove multiple spaces
        text = re.sub(r"\s+", " ", text)
        # Remove leading/trailing whitespace
        text = text.strip()
        return text

    def parse_file(self, file_path: Path) -> ParsedConstitution:
        """Load and parse a Constitution file."""
        text = self.load_file(file_path)
        return self.parse_text(text)

    def save_processed(
        self,
        constitution: ParsedConstitution,
        output_path: Optional[Path] = None,
    ) -> Path:
        """Save processed Constitution to JSON file."""
        if output_path is None:
            output_path = self.settings.constitution_processed_dir / "constitution.json"

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(constitution.model_dump(), f, indent=2, ensure_ascii=False)

        return output_path

    def load_processed(self, path: Optional[Path] = None) -> Optional[ParsedConstitution]:
        """Load a previously processed Constitution from JSON."""
        if path is None:
            path = self.settings.constitution_processed_dir / "constitution.json"

        if not path.exists():
            return None

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return ParsedConstitution.model_validate(data)

    def to_database_records(self, constitution: ParsedConstitution) -> list[dict]:
        """Convert parsed Constitution to database record format."""
        records = []

        for chapter in constitution.chapters:
            for section in chapter.sections:
                record = {
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
