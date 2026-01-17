"""Backward compatibility wrapper for ConstitutionRetriever.

New code should import from contentmanager.core.document directly.
"""

from contentmanager.core.document.retriever import DocumentRetriever as ConstitutionRetriever

__all__ = [
    "ConstitutionRetriever",
]
