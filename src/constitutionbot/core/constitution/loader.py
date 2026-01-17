"""Backward compatibility wrapper for ConstitutionLoader.

New code should import from constitutionbot.core.document directly.
"""

from constitutionbot.core.document.loader import (
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
