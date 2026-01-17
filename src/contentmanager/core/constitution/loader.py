"""Backward compatibility wrapper for ConstitutionLoader.

New code should import from contentmanager.core.document directly.
"""

from contentmanager.core.document.loader import (
    DocumentLoader as ConstitutionLoader,
    ParsingStrategy,
    ChapterSectionStrategy,
    ArticleStrategy,
    NumberedListStrategy,
    PARSING_STRATEGIES,
)

__all__ = [
    "ConstitutionLoader",
    "ParsingStrategy",
    "ChapterSectionStrategy",
    "ArticleStrategy",
    "NumberedListStrategy",
    "PARSING_STRATEGIES",
]
