"""Backward compatibility wrapper for ConstitutionRetriever.

New code should import from constitutionbot.core.document directly.
"""

from constitutionbot.core.document.retriever import DocumentRetriever as ConstitutionRetriever

__all__ = [
    "ConstitutionRetriever",
]
