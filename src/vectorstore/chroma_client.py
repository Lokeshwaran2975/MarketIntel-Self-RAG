from typing import List, Dict, Optional, Any

from langchain_core.documents import Document

from src.vectorstore.collection_manage import (
    get_vector_store,
    load_all_documents,
)

from src.retriever.bm25 import bm25_retriever
from src.utils.logger import logger


class VectorRetriever:
    """
    Wrapper around ChromaDB retrieval.

    Responsibilities
    ----------------
    • Similarity Search
    • Maximum Marginal Relevance (MMR) Search
    • Metadata Filter Conversion

    Notes
    -----
    - This class only performs vector retrieval.
    - Retrieval fallback strategies are handled by HybridRetriever.
    - BM25 index is built once during application startup.
    """

    def __init__(self):

        self.vector_store = get_vector_store()

        # ---------------------------------------------------------
        # Build BM25 Index Once
        # ---------------------------------------------------------

        if not bm25_retriever.is_ready():

            logger.info("=" * 80)
            logger.info("Initializing BM25 Retriever")
            logger.info("=" * 80)

            docs = load_all_documents()

            logger.info(f"Loaded {len(docs)} documents from ChromaDB")

            bm25_retriever.build(docs)

            logger.info("BM25 Index Ready")
            logger.info("=" * 80)

    # ---------------------------------------------------------
    # Metadata Filter Builder
    # ---------------------------------------------------------

    def _build_filter(
        self,
        filters: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Convert metadata filters into ChromaDB format.
        """

        if not filters:
            return None

        clean_filters = {
            key: value
            for key, value in filters.items()
            if value is not None
        }

        if not clean_filters:
            return None

        if len(clean_filters) == 1:
            return clean_filters

        return {
            "$and": [
                {k: v}
                for k, v in clean_filters.items()
            ]
        }

    # ---------------------------------------------------------
    # Similarity Search
    # ---------------------------------------------------------

    def search(
        self,
        query: str,
        k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        Standard similarity search.
        """

        chroma_filter = self._build_filter(filters)

        logger.info("=" * 80)
        logger.info("VECTOR SIMILARITY SEARCH")
        logger.info("=" * 80)

        logger.info(f"Query      : {query}")

        if chroma_filter:
            logger.info(f"Filters    : {chroma_filter}")
        else:
            logger.info("Filters    : None")

        logger.info(f"Top K      : {k}")

        docs = self.vector_store.similarity_search(
            query=query,
            k=k,
            filter=chroma_filter
        )

        self._log_results(
            docs,
            search_type="Similarity"
        )

        return docs

    # ---------------------------------------------------------
    # MMR Search
    # ---------------------------------------------------------

    def mmr_search(
        self,
        query: str,
        k: int = 5,
        fetch_k: int = 20,
        lambda_mult: float = 0.5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        Maximum Marginal Relevance Search.
        """

        chroma_filter = self._build_filter(filters)

        logger.info("=" * 80)
        logger.info("MMR SEARCH")
        logger.info("=" * 80)

        logger.info(f"Query        : {query}")

        if chroma_filter:
            logger.info(f"Filters      : {chroma_filter}")
        else:
            logger.info("Filters      : None")

        logger.info(f"Fetch K      : {fetch_k}")
        logger.info(f"Return Top K : {k}")
        logger.info(f"Lambda       : {lambda_mult}")

        docs = self.vector_store.max_marginal_relevance_search(
            query=query,
            k=k,
            fetch_k=fetch_k,
            lambda_mult=lambda_mult,
            filter=chroma_filter
        )

        self._log_results(
            docs,
            search_type="MMR"
        )

        return docs

    # ---------------------------------------------------------
    # Retrieval Logger
    # ---------------------------------------------------------

    def _log_results(
        self,
        docs: List[Document],
        search_type: str
    ) -> None:
        """
        Log retrieval statistics and retrieved documents.
        """ 
        logger.info(f"{search_type} Search Retrieved {len(docs)} document(s)")

        if not docs:
            logger.warning("No documents retrieved.")
            logger.info("=" * 80)
            return

        companies = set()
        priorities = []
        chunk_sizes = []

        years = set()
        document_types = set()

        # ---------------------------------------------------------
        # Log Retrieved Documents
        # ---------------------------------------------------------

        for idx, doc in enumerate(docs, start=1):

            metadata = doc.metadata

            company = metadata.get("company")
            year = metadata.get(
                "document_year",
                metadata.get("year")
            )
            quarter = metadata.get("quarter")
            document_type = metadata.get("document_type")
            priority = metadata.get("priority")
            file_name = metadata.get("file_name")

            if company:
                companies.add(company)

            if year:
                years.add(year)

            if document_type:
                document_types.add(document_type)

            if isinstance(priority, (int, float)):
                priorities.append(priority)

            chunk_sizes.append(len(doc.page_content))

            logger.info(
                f"[{idx}] "
                f"Company={company} | "
                f"Year={year} | "
                f"Quarter={quarter} | "
                f"Type={document_type} | "
                f"Priority={priority} | "
                f"File={file_name}"
            )

        # ---------------------------------------------------------
        # Retrieval Statistics
        # ---------------------------------------------------------

        avg_chunk_size = (
            sum(chunk_sizes) / len(chunk_sizes)
            if chunk_sizes else 0
        )

        avg_priority = (
            sum(priorities) / len(priorities)
            if priorities else 0
        )

        logger.info("-" * 80)
        logger.info("Retrieval Summary")
        logger.info("-" * 80)

        logger.info(
            f"Documents Returned : {len(docs)}"
        )

        logger.info(
            f"Companies          : {sorted(companies)}"
        )

        logger.info(
            f"Years              : {sorted(years)}"
        )

        logger.info(
            f"Document Types     : {sorted(document_types)}"
        )

        logger.info(
            f"Average Chunk Size : {avg_chunk_size:.0f} characters"
        )

        logger.info(
            f"Average Priority   : {avg_priority:.2f}"
        )

        logger.info("=" * 80)


# ---------------------------------------------------------
# Singleton Retriever
# ---------------------------------------------------------

retriever = VectorRetriever()