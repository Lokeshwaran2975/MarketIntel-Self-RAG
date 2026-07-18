"""
MarketIntel
Cross Encoder Reranker

Computes semantic relevance between the user query and
retrieved document chunks using a CrossEncoder model.
"""

from typing import List

from langchain_core.documents import Document
from sentence_transformers import CrossEncoder

from src.utils.logger import logger


class CrossEncoderReranker:
    """
    CrossEncoder-based semantic reranker.
    """

    MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    def __init__(self):

        logger.info("Loading CrossEncoder model...")

        self.model = CrossEncoder(self.MODEL_NAME)

        logger.info("CrossEncoder loaded successfully.")

    # ---------------------------------------------------------
    # Normalize scores
    # ---------------------------------------------------------

    @staticmethod
    def _normalize(scores):

        if len(scores) == 0:
            return []

        minimum = min(scores)
        maximum = max(scores)

        if maximum == minimum:
            return [1.0] * len(scores)

        return [

            (score - minimum) / (maximum - minimum)

            for score in scores

        ]

    # ---------------------------------------------------------
    # Re-rank Documents
    # ---------------------------------------------------------

    def rerank(
        self,
        question: str,
        docs: List[Document],
        top_k: int = 5
    ) -> List[Document]:

        if not docs:

            logger.warning(
                "CrossEncoder received an empty document list."
            )

            return []

        pairs = [

            (
                question,
                doc.page_content
            )

            for doc in docs

        ]

        raw_scores = self.model.predict(
            pairs,
            batch_size=16,
            show_progress_bar=False
        )

        normalized_scores = self._normalize(raw_scores)

        ranked = sorted(

            zip(raw_scores, normalized_scores, docs),

            key=lambda x: x[0],

            reverse=True

        )

        reranked_docs = []

        logger.info("=" * 80)
        logger.info("CrossEncoder Ranking")
        logger.info("=" * 80)

        for rank, (raw_score, normalized_score, doc) in enumerate(

            ranked,

            start=1

        ):

            doc.metadata["semantic_score_raw"] = float(raw_score)

            doc.metadata["semantic_score"] = float(normalized_score)

            reranked_docs.append(doc)

            logger.info(

                f"[{rank}] "

                f"Raw={raw_score:.4f} | "

                f"Normalized={normalized_score:.3f} | "

                f"{doc.metadata.get('company', 'Unknown')} | "

                f"{doc.metadata.get('document_year', doc.metadata.get('year', '-'))} | "

                f"{doc.metadata.get('quarter', '-')} | "

                f"{doc.metadata.get('document_type', '-')} | "

                f"{doc.metadata.get('file_name', '-')}"

            )

        logger.info("=" * 80)

        return reranked_docs[:top_k]


reranker = CrossEncoderReranker()