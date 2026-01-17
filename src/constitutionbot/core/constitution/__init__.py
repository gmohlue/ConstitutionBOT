"""Constitution module - backward compatibility wrapper.

This module re-exports from the new document module for backward compatibility.
New code should import from constitutionbot.core.document directly.
"""

from constitutionbot.core.document import (
    # Loader aliases
    DocumentLoader as ConstitutionLoader,
    # Retriever aliases
    DocumentRetriever as ConstitutionRetriever,
    # Models
    Chapter,
    Section,
    Subsection,
    ParsedDocument,
    CitationReference,
    DocumentContext,
)

__all__ = [
    # Backward compatibility aliases
    "ConstitutionLoader",
    "ConstitutionRetriever",
    # Models
    "Section",
    "Chapter",
    "Subsection",
    "ParsedDocument",
    "CitationReference",
    "DocumentContext",
]
