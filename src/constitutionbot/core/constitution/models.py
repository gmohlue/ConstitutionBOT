"""Backward compatibility wrapper for Constitution models.

New code should import from constitutionbot.core.document.models directly.
"""

from constitutionbot.core.document.models import (
    Chapter,
    Section,
    Subsection,
    ParsedDocument as ParsedConstitution,
    CitationReference,
    DocumentContext,
)

__all__ = [
    "Chapter",
    "Section",
    "Subsection",
    "ParsedConstitution",
    "CitationReference",
    "DocumentContext",
]
