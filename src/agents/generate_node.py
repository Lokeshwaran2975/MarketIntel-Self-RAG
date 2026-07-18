"""
Generate Node

Responsibilities
----------------
1. Generate final answer
2. Preserve original user intent
3. Collect source metadata
4. Return clean ranked sources
"""

from langchain_core.messages import HumanMessage, SystemMessage

from src.graph.state import GraphState
from src.llm.ollama_client import get_llm
from src.prompts.generator_prompt import (
    SYSTEM_PROMPT,
    USER_PROMPT
)

from src.utils.logger import logger


llm = get_llm()


def generate_node(state: GraphState) -> GraphState:

    logger.info("=" * 80)
    logger.info("GENERATOR NODE")
    logger.info("=" * 80)

    context = state.get("context", "")

    # Always prefer original question
    question = state.get(
        "original_question",
        state.get("question", "")
    )

    if not context.strip():

        logger.warning("Empty context received.")

        state["answer"] = (
            "I couldn't find enough information to answer your question."
        )

        return state

    prompt = USER_PROMPT.format(

        question=question,

        context=context

    )

    logger.info("Sending prompt to LLM...")

    response = llm.invoke(

        [

            SystemMessage(content=SYSTEM_PROMPT),

            HumanMessage(content=prompt)

        ]

    )

    answer = response.content.strip()

    if not answer:

        answer = (
            "I couldn't generate a reliable answer from the retrieved documents."
        )

    logger.info("LLM generation completed.")

    # --------------------------------------------------------
    # Source Collection
    # --------------------------------------------------------

    documents = state.get("reranked_documents", [])

    # Sort by final score

    documents = sorted(

        documents,

        key=lambda d: d.metadata.get(

            "final_score",

            0

        ),

        reverse=True

    )

    seen = set()

    sources = []

    for doc in documents:

        meta = doc.metadata

        key = (

            meta.get("file_name"),

            meta.get("page"),

            meta.get("section")

        )

        if key in seen:
            continue

        seen.add(key)

        sources.append(

            {

                "company": meta.get("company"),

                "year": meta.get("year"),

                "quarter": meta.get("quarter"),

                "document_type": meta.get("document_type"),

                "section": meta.get("section"),

                "page": meta.get("page"),

                "file_name": meta.get("file_name"),

                "source": meta.get("source"),

                "semantic_score": round(

                    meta.get("semantic_score", 0),

                    4

                ),

                "metadata_score": round(

                    meta.get("metadata_score", 0),

                    4

                ),

                "final_score": round(

                    meta.get("final_score", 0),

                    4

                ),

                "confidence": meta.get(

                    "confidence",

                    "UNKNOWN"

                )

            }

        )

    # Keep only top 10 unique sources

    sources = sources[:10]

    # --------------------------------------------------------
    # Update Graph State
    # --------------------------------------------------------

    state["answer"] = answer

    metadata = state.setdefault(

        "metadata",

        {}

    )

    metadata["sources"] = sources

    metadata["num_sources"] = len(sources)

    state["metadata"] = metadata

    logger.info("")
    logger.info("=" * 80)
    logger.info("Answer Generated Successfully")
    logger.info("=" * 80)

    logger.info(f"Sources Used : {len(sources)}")

    for idx, src in enumerate(sources, start=1):

        logger.info(

            f"[{idx}] "

            f"{src['company']} | "

            f"{src['year']} | "

            f"{src['document_type']} | "

            f"{src['file_name']} | "

            f"Score={src['final_score']:.3f}"

        )

    logger.info("=" * 80)

    return state