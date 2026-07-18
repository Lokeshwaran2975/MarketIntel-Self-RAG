"""
MarketIntel
Metadata Ranker
"""


class MetadataRanker:
    """
    Scores retrieved documents using metadata relevance.
    """

    COMPANY_WEIGHT = 30

    YEAR_WEIGHT = 20

    QUARTER_WEIGHT = 10

    DOCUMENT_WEIGHT = 10

    PRIORITY_WEIGHT = 0.10

    @classmethod
    def score(cls, filters, metadata):
        """
        Compute metadata relevance score.
        """

        score = 0.0

        if not filters:
            return score

        # -----------------------------------------------------
        # Company
        # -----------------------------------------------------

        if (
            filters.get("company")
            and metadata.get("company") == filters["company"]
        ):

            score += cls.COMPANY_WEIGHT

        # -----------------------------------------------------
        # Year
        # -----------------------------------------------------

        if (
            filters.get("year")
            and metadata.get("document_year") == filters["year"]
        ):

            score += cls.YEAR_WEIGHT

        # -----------------------------------------------------
        # Quarter
        # -----------------------------------------------------

        if (
            filters.get("quarter")
            and metadata.get("quarter") == filters["quarter"]
        ):

            score += cls.QUARTER_WEIGHT

        # -----------------------------------------------------
        # Document Type
        # -----------------------------------------------------

        if (
            filters.get("document_type")
            and metadata.get("document_type") == filters["document_type"]
        ):

            score += cls.DOCUMENT_WEIGHT

        # -----------------------------------------------------
        # Priority
        # -----------------------------------------------------

        priority = metadata.get("priority", 0)

        score += priority * cls.PRIORITY_WEIGHT

        return score