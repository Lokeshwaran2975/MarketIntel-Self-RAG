import re
from typing import Dict, Optional

from rank_bm25 import BM25Okapi

from src.utils.logger import logger


class BM25Retriever:
    """
    BM25 Retriever for lexical search.

    Features
    --------
    - Fast lexical retrieval
    - Metadata-aware filtering
    - Duplicate removal
    """

    def __init__(self):
        self.documents = []
        self.bm25 = None

    # ---------------------------------------------------------
    # Tokenizer
    # ---------------------------------------------------------

    @staticmethod
    def tokenize(text: str):

        return re.findall(
            r"[a-zA-Z0-9]+",
            text.lower()
        )

    # ---------------------------------------------------------
    # Build Index
    # ---------------------------------------------------------

    def build(self, documents):

        if not documents:
            logger.warning("No documents found for BM25 indexing.")
            return

        self.documents = documents

        tokenized_docs = [
            self.tokenize(doc.page_content)
            for doc in documents
        ]

        self.bm25 = BM25Okapi(tokenized_docs)

        logger.info(
            f"✅ BM25 Index Built ({len(documents)} documents)"
        )

    # ---------------------------------------------------------
    # Clear Index
    # ---------------------------------------------------------

    def clear(self):

        self.documents = []
        self.bm25 = None

    # ---------------------------------------------------------
    # Ready?
    # ---------------------------------------------------------

    def is_ready(self):

        return self.bm25 is not None

    # ---------------------------------------------------------
    # Metadata Matching
    # ---------------------------------------------------------

    def _match_metadata(
        self,
        doc,
        filters: Optional[Dict]
    ) -> bool:

        if not filters:
            return True

        for key, value in filters.items():

            if doc.metadata.get(key) != value:
                return False

        return True

    # ---------------------------------------------------------
    # Search
    # ---------------------------------------------------------

    def search(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict] = None
    ):

        if not self.is_ready():
            logger.warning("BM25 index has not been built.")
            return []

        tokens = self.tokenize(query)

        if not tokens:
            return []

        # -----------------------------------------------------
        # Retrieve a larger candidate pool
        # -----------------------------------------------------

        candidates = self.bm25.get_top_n(
            tokens,
            self.documents,
            n=min(100, len(self.documents))
        )

        # -----------------------------------------------------
        # Apply metadata filters
        # -----------------------------------------------------

        filtered = [
            doc
            for doc in candidates
            if self._match_metadata(doc, filters)
        ]

        # -----------------------------------------------------
        # If metadata filters are too strict,
        # fallback to lexical results.
        # -----------------------------------------------------

        if not filtered and filters:

            logger.warning(
                "BM25 metadata filtering returned 0 documents."
            )

            logger.warning(
                "Retrying BM25 without metadata filters..."
            )

            filtered = candidates

        # -----------------------------------------------------
        # Remove duplicates
        # -----------------------------------------------------

        unique = []
        seen = set()

        for doc in filtered:

            key = (
                doc.metadata.get("source", ""),
                doc.metadata.get("page", -1),
                hash(doc.page_content)
            )

            if key in seen:
                continue

            seen.add(key)
            unique.append(doc)

        logger.info(
            f"BM25 Final Results : {len(unique[:top_k])}"
        )

        return unique[:top_k]


bm25_retriever = BM25Retriever()