"""
Retrieve Node

Responsibilities
----------------
1. Preserve original user question
2. Process user query
3. Perform hybrid retrieval
4. Build LLM context
5. Update graph state
"""

import time

from src.graph.state import GraphState

from src.retriever.query_processor import process_query
from src.retriever.hybrid_retriever import hybrid_retriever
from src.retriever.context_builder import build_context

from src.utils.logger import logger


# ---------------------------------------------------------
# Retrieve Node
# ---------------------------------------------------------

def retrieve_node(state: GraphState) -> GraphState:
    """
    Retrieve relevant documents and prepare context.
    """

    logger.info("=" * 80)
    logger.info("RETRIEVE NODE")
    logger.info("=" * 80)

    start_time = time.perf_counter()

    # -------------------------------------------------
    # Preserve original question
    # -------------------------------------------------

    if not state.get("original_question"):
        state["original_question"] = state["question"]

    question = state["question"]

    try:

        # -------------------------------------------------
        # Query Processing
        # -------------------------------------------------

        query_info = process_query(question)

        processed_query = query_info["processed_query"]

        filters = query_info.get("filters", {})

        section_hint = query_info.get("section_hint")

        logger.info(f"Original Question : {state['original_question']}")
        logger.info(f"Current Question  : {question}")
        logger.info(f"Processed Query   : {processed_query}")
        logger.info(f"Filters           : {filters}")
        logger.info(f"Section Hint      : {section_hint}")

        # -------------------------------------------------
        # Hybrid Retrieval
        # -------------------------------------------------

        retrieved_docs = hybrid_retriever.retrieve(
            question=question,
            query=processed_query,
            filters=filters,
            top_k=5,
        )

        logger.info(f"Retrieved Documents : {len(retrieved_docs)}")

        # -------------------------------------------------
        # Empty Retrieval
        # -------------------------------------------------

        if not retrieved_docs:

            logger.warning("No relevant documents retrieved.")

            state["processed_query"] = processed_query
            state["filters"] = filters
            state["section_hint"] = section_hint

            state["documents"] = []
            state["reranked_documents"] = []

            state["context"] = ""
            state["context_length"] = 0

            state["retrieval_time"] = (
                time.perf_counter() - start_time
            )

            return state

        # -------------------------------------------------
        # Build Context
        # -------------------------------------------------

        context = build_context(retrieved_docs)

        context_length = len(context)

        logger.info(
            f"Context Size : {context_length} characters"
        )

        # -------------------------------------------------
        # Collect Source Metadata
        # -------------------------------------------------

        retrieved_sources = []

        for doc in retrieved_docs:

            meta = doc.metadata

            retrieved_sources.append(
                {
                    "company": meta.get("company"),
                    "year": meta.get("year"),
                    "quarter": meta.get("quarter"),
                    "document_type": meta.get("document_type"),
                    "file_name": meta.get("file_name"),
                    "section": meta.get("section"),
                    "page": meta.get("page"),
                    "semantic_score": meta.get("semantic_score"),
                    "metadata_score": meta.get("metadata_score"),
                    "final_score": meta.get("final_score"),
                    "confidence": meta.get("confidence"),
                }
            )

        # -------------------------------------------------
        # Update State
        # -------------------------------------------------

        state["processed_query"] = processed_query
        state["filters"] = filters
        state["section_hint"] = section_hint

        state["documents"] = retrieved_docs
        state["reranked_documents"] = retrieved_docs

        state["retrieved_sources"] = retrieved_sources

        state["context"] = context
        state["context_length"] = context_length

        state["retrieval_time"] = (
            time.perf_counter() - start_time
        )

        logger.info(
            f"Retrieval Time : {state['retrieval_time']:.2f} sec"
        )

        logger.info("Retrieve Node Completed")
        logger.info("=" * 80)

        return state

    except Exception as e:

        logger.exception(f"Retrieve Node Failed : {e}")

        state["documents"] = []
        state["reranked_documents"] = []
        state["retrieved_sources"] = []

        state["context"] = ""
        state["context_length"] = 0

        state["answer"] = (
            "An error occurred while retrieving documents."
        )

        state["error"] = str(e)

        return state