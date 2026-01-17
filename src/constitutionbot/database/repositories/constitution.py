"""Backward compatibility wrapper for ConstitutionRepository.

New code should import from constitutionbot.database.repositories.document directly.
"""

from constitutionbot.database.repositories.document import (
    DocumentRepository,
    DocumentSectionRepository as ConstitutionRepository,
)

__all__ = [
    "ConstitutionRepository",
    "DocumentRepository",
]
