"""
LangGraph State

Shared state flowing through the workflow.
"""

from typing import Any, Dict, List, Optional, TypedDict


class GraphState(TypedDict, total=False):
    """
    Shared state across all LangGraph nodes.
    """

    # =====================================================
    # Original User Input
    # =====================================================

    original_question: str

    question: str

    processed_query: str

    rewritten_question: Optional[str]

    # =====================================================
    # Retrieval
    # =====================================================

    filters: Dict[str, Any]

    section_hint: Optional[str]

    retrieval_time: float

    documents: List[Any]

    reranked_documents: List[Any]

    retrieved_sources: List[Dict[str, Any]]

    retrieval_strategy: str

    # =====================================================
    # Context
    # =====================================================

    context: str

    context_length: int

    # =====================================================
    # Generation
    # =====================================================

    answer: str

    # =====================================================
    # Document Grading
    # =====================================================

    relevance_score: float

    is_relevant: bool

    confidence: float

    next_step: str

    # =====================================================
    # Workflow Control
    # =====================================================

    retry_count: int

    max_retries: int

    # =====================================================
    # Metadata
    # =====================================================

    metadata: Dict[str, Any]

    # =====================================================
    # Diagnostics
    # =====================================================

    debug: Dict[str, Any]

    # =====================================================
    # Error Handling
    # =====================================================

    error: Optional[str]