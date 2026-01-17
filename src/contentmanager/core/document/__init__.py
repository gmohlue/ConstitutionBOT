"""Document processing module - supports any document type."""

from contentmanager.core.document.loader import (
    ArticleStrategy,
    ChapterSectionStrategy,
    DocumentLoader,
    NumberedListStrategy,
    PARSING_STRATEGIES,
    ParsingStrategy,
)
from contentmanager.core.document.models import (
    Chapter,
    CitationReference,
    DocumentContext,
    ParsedDocument,
    Section,
    Subsection,
)
from contentmanager.core.document.retriever import DocumentRetriever

__all__ = [
    # Models
    "Chapter",
    "CitationReference",
    "DocumentContext",
    "ParsedDocument",
    "Section",
    "Subsection",
    # Loader
    "DocumentLoader",
    "ParsingStrategy",
    "ChapterSectionStrategy",
    "ArticleStrategy",
    "NumberedListStrategy",
    "PARSING_STRATEGIES",
    # Retriever
    "DocumentRetriever",
]
