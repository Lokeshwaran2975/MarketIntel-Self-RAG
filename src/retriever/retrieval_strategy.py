"""
MarketIntel
Retrieval Strategy

Generates progressively relaxed metadata filters for retrieval.
"""

from copy import deepcopy
from typing import Dict, List, Optional


class RetrievalStrategy:
    """
    Search order:

    1. Full metadata
    2. Company + Year
    3. Company
    4. Document Type
    5. Year
    6. No filters
    """

    @staticmethod
    def _clean(filters: Dict) -> Dict:
        """Remove empty values."""

        return {
            k: v
            for k, v in filters.items()
            if v not in (None, "", [], {})
        }

    @classmethod
    def build(cls, filters: Optional[Dict]) -> List[Optional[Dict]]:

        if not filters:
            return [None]

        filters = cls._clean(filters)

        strategies = []

        # -------------------------
        # Full Filter
        # -------------------------

        strategies.append(deepcopy(filters))

        # -------------------------
        # Company + Year
        # -------------------------

        if (
            "company" in filters
            and "year" in filters
        ):

            reduced = {
                "company": filters["company"],
                "year": filters["year"]
            }

            if reduced not in strategies:
                strategies.append(reduced)

        # -------------------------
        # Company
        # -------------------------

        if "company" in filters:

            reduced = {
                "company": filters["company"]
            }

            if reduced not in strategies:
                strategies.append(reduced)

        # -------------------------
        # Document Type
        # -------------------------

        if "document_type" in filters:

            reduced = {
                "document_type": filters["document_type"]
            }

            if reduced not in strategies:
                strategies.append(reduced)

        # -------------------------
        # Year
        # -------------------------

        if "year" in filters:

            reduced = {
                "year": filters["year"]
            }

            if reduced not in strategies:
                strategies.append(reduced)

        # -------------------------
        # Global Search
        # -------------------------

        strategies.append(None)

        return strategies