"""
MarketIntel
Production Hybrid Retriever

Pipeline
--------
1. Query Processing
2. Retrieval Strategy
3. Vector Search (MMR)
4. BM25 Search
5. Reciprocal Rank Fusion
6. Duplicate Removal
7. CrossEncoder Re-ranking
8. Metadata Ranking
"""

from collections import defaultdict
from typing import Dict, List, Optional, Any

from langchain_core.documents import Document

from src.vectorstore.chroma_client import retriever
from src.retriever.bm25 import bm25_retriever
from src.reranker.cross_encoder import reranker

from src.retriever.retrieval_strategy import RetrievalStrategy
from src.retriever.duplicate_handler import DuplicateHandler
from src.retriever.metadata_ranker import MetadataRanker

from src.retriever.config import (
    VECTOR_TOP_K,
    VECTOR_FETCH_K,
    BM25_TOP_K,
    RRF_K,
    FINAL_TOP_K,
    RERANK_TOP_K,
    MMR_LAMBDA,
)

from src.utils.logger import logger


class HybridRetriever:
    """
    Production Hybrid Retriever
    """

    def __init__(self):

        self.vector_k = VECTOR_TOP_K

        self.fetch_k = VECTOR_FETCH_K

        self.bm25_k = BM25_TOP_K

        self.final_k = FINAL_TOP_K

        self.strategy = RetrievalStrategy()

        self.metadata_ranker = MetadataRanker()

    # ---------------------------------------------------------
    # Reciprocal Rank Fusion
    # ---------------------------------------------------------

    def reciprocal_rank_fusion(
        self,
        vector_docs: List[Document],
        bm25_docs: List[Document],
        top_k: int = 20
    ) -> List[Document]:

        scores = defaultdict(float)

        documents = {}

        # -----------------------------
        # Vector Results
        # -----------------------------

        for rank, doc in enumerate(vector_docs, start=1):

            key = (

                doc.metadata.get("file_name"),

                doc.metadata.get("page"),

                hash(doc.page_content)

            )

            documents[key] = doc

            scores[key] += 1 / (RRF_K + rank)

        # -----------------------------
        # BM25 Results
        # -----------------------------

        for rank, doc in enumerate(bm25_docs, start=1):

            key = (

                doc.metadata.get("file_name"),

                doc.metadata.get("page"),

                hash(doc.page_content)

            )

            documents[key] = doc

            scores[key] += 1 / (RRF_K + rank)

        ranked = sorted(

            scores.items(),

            key=lambda x: x[1],

            reverse=True

        )

        return [

            documents[key]

            for key, _ in ranked[:top_k]

        ]

    # ---------------------------------------------------------
    # Vector Search
    # ---------------------------------------------------------

    def vector_search(

        self,

        query: str,

        filters: Optional[Dict[str, Any]]

    ) -> List[Document]:

        logger.info(f"Vector Search : {filters}")

        return retriever.mmr_search(

            query=query,

            k=self.vector_k,

            fetch_k=self.fetch_k,

            lambda_mult=MMR_LAMBDA,

            filters=filters

        )

    # ---------------------------------------------------------
    # BM25 Search
    # ---------------------------------------------------------

    def bm25_search(

        self,

        query: str,

        filters: Optional[Dict[str, Any]]

    ) -> List[Document]:

        logger.info(f"BM25 Search : {filters}")

        return bm25_retriever.search(

            query=query,

            top_k=self.bm25_k,

            filters=filters

        )

    # ---------------------------------------------------------
    # Hybrid Retrieval
    # ---------------------------------------------------------

    def retrieve(

        self,

        question: str,

        query: str,

        filters: Optional[Dict[str, Any]] = None,

        top_k: Optional[int] = None

    ) -> List[Document]:

        if top_k is None:

            top_k = self.final_k

        logger.info("=" * 80)

        logger.info("HYBRID RETRIEVAL")

        logger.info("=" * 80)

        logger.info(f"Question : {question}")

        logger.info(f"Query    : {query}")

        logger.info(f"Filters  : {filters}")

        strategies = self.strategy.build(filters)

        logger.info(

            f"Generated {len(strategies)} retrieval strategies."

        )

        all_documents = []

        # ---------------------------------------------------------
        # Try each strategy
        # ---------------------------------------------------------

        for idx, strategy in enumerate(

            strategies,

            start=1

        ):

            logger.info("-" * 80)

            logger.info(f"Strategy {idx}")

            logger.info(f"{strategy}")

            logger.info("-" * 80)

            vector_docs = self.vector_search(

                query=query,

                filters=strategy

            )

            bm25_docs = self.bm25_search(

                query=query,

                filters=strategy

            )

            merged_docs = self.reciprocal_rank_fusion(

                vector_docs,

                bm25_docs,

                top_k=20

            )

            logger.info(

                f"After RRF : {len(merged_docs)}"

            )

            merged_docs = DuplicateHandler.remove(

                merged_docs

            )

            logger.info(

                f"After Dedup : {len(merged_docs)}"

            )

            if not merged_docs:

                continue

            reranked_docs = reranker.rerank(

                question=question,

                docs=merged_docs,

                top_k=RERANK_TOP_K

            )

            logger.info(

                f"CrossEncoder : {len(reranked_docs)}"

            )

            all_documents.extend(

                reranked_docs

            )

            if len(all_documents) >= 20:

                logger.info(

                    "Enough documents collected."

                )

                break

                        # ---------------------------------------------------------
        # No Documents Retrieved
        # ---------------------------------------------------------

        if not all_documents:

            logger.warning("No relevant documents retrieved.")

            return []

        logger.info("=" * 80)
        logger.info(
            f"Collected {len(all_documents)} reranked documents."
        )
        logger.info("=" * 80)

        # ---------------------------------------------------------
        # Final Deduplication
        # ---------------------------------------------------------

        all_documents = DuplicateHandler.remove(
            all_documents
        )

        logger.info(
            f"Unique Documents : {len(all_documents)}"
        )

        # ---------------------------------------------------------
        # Metadata Ranking
        # ---------------------------------------------------------

        scored_documents = []

        for doc in all_documents:

            semantic_score = float(

                doc.metadata.get(

                    "semantic_score",

                    0.0

                )

            )

            metadata_score = float(

                self.metadata_ranker.score(

                    filters=filters,

                    metadata=doc.metadata

                )

            )

            # -------------------------------------------------
            # Final Score
            # -------------------------------------------------

            #
            # Semantic score has higher importance
            #
            # 70% Semantic
            # 30% Metadata
            #

            final_score = (

                (semantic_score * 0.7)

                +

                (metadata_score * 0.3)

            )

            doc.metadata["semantic_score"] = semantic_score

            doc.metadata["metadata_score"] = metadata_score

            doc.metadata["final_score"] = final_score

            scored_documents.append(doc)

        # ---------------------------------------------------------
        # Final Ranking
        # ---------------------------------------------------------

        scored_documents.sort(

            key=lambda doc: doc.metadata.get(

                "final_score",

                0.0

            ),

            reverse=True

        )

        final_documents = scored_documents[:top_k]

        logger.info("")
        logger.info("=" * 80)
        logger.info("FINAL DOCUMENT RANKING")
        logger.info("=" * 80)

        for idx, doc in enumerate(

            final_documents,

            start=1

        ):

            metadata = doc.metadata

            logger.info(

                f"[{idx}] "

                f"Company={metadata.get('company')} | "

                f"Year={metadata.get('document_year', metadata.get('year'))} | "

                f"Quarter={metadata.get('quarter')} | "

                f"Type={metadata.get('document_type')} | "

                f"Section={metadata.get('section')} | "

                f"Semantic={metadata.get('semantic_score', 0):.3f} | "

                f"Metadata={metadata.get('metadata_score', 0):.3f} | "

                f"Final={metadata.get('final_score', 0):.3f}"

            )

        logger.info("=" * 80)

        logger.info(

            f"Returning {len(final_documents)} document(s)"

        )

        logger.info("=" * 80)

        return final_documents


# ---------------------------------------------------------
# Singleton
# ---------------------------------------------------------

hybrid_retriever = HybridRetriever()