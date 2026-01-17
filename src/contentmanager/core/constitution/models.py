"""Backward compatibility wrapper for Constitution models.

New code should import from contentmanager.core.document.models directly.
"""

from contentmanager.core.document.models import (
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
