"""Backward compatibility wrapper for ConstitutionRepository.

New code should import from contentmanager.database.repositories.document directly.
"""

from contentmanager.database.repositories.document import (
    DocumentRepository,
    DocumentSectionRepository as ConstitutionRepository,
)

__all__ = [
    "ConstitutionRepository",
    "DocumentRepository",
]
