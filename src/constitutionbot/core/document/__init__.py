"""Document processing module - supports any document type."""

from constitutionbot.core.document.loader import (
    DocumentLoader,
    ParsingStrategy,
    ChapterSectionStrategy,
    ArticleStrategy,
    NumberedListStrategy,
    PARSING_STRATEGIES,
    # Backward compatibility
    ConstitutionLoader,
)
from constitutionbot.core.document.models import (
    Chapter,
    CitationReference,
    DocumentContext,
    ParsedDocument,
    Section,
    Subsection,
)
from constitutionbot.core.document.retriever import (
    DocumentRetriever,
    # Backward compatibility
    ConstitutionRetriever,
)

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
    # Backward compatibility
    "ConstitutionLoader",
    "ConstitutionRetriever",
]
