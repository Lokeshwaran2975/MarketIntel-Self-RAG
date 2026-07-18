from src.graph.state import GraphState

from src.retriever.query_processor import process_query
from src.retriever.context_builder import build_context
from src.retriever.hybrid_retriever import hybrid_retriever

from src.utils.logger import logger


def retrieve_node(state: GraphState):

    question = state["question"]

    # Process Query
    processed = process_query(question)

    query = processed["processed_query"]
    filters = processed["filters"]
    section_hint = processed["section_hint"]

    logger.info("=" * 60)
    logger.info("📝 Query Processor")
    logger.info("=" * 60)
    logger.info(f"Original Question : {question}")
    logger.info(f"Processed Query   : {query}")
    logger.info(f"Filters           : {filters}")
    logger.info(f"Section Hint      : {section_hint}")
    logger.info("=" * 60)

    # Hybrid Retrieval
    docs = hybrid_retriever.retrieve(
        question=question,
        query=query,
        filters=filters,
        top_k=5
    )

    if not docs:
        logger.warning("No relevant documents retrieved.")

        return {
            "processed_query": query,
            "retrieved_docs": [],
            "context": "",
            "filters": filters,
            "section_hint": section_hint
        }

    # Build Context
    context = build_context(docs)

    logger.info(
        f"📄 Context built from {len(docs)} retrieved document(s)"
    )

    return {
        "processed_query": query,
        "retrieved_docs": docs,
        "context": context,
        "filters": filters,
        "section_hint": section_hint
    }