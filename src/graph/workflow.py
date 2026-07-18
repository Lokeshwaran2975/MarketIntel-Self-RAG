"""
MarketIntel LangGraph Workflow
"""

from langgraph.graph import (
    StateGraph,
    START,
    END
)

from src.graph.state import GraphState

from src.agents.retrieve_node import retrieve_node
from src.agents.grade_node import grade_node
from src.agents.rewrite_node import rewrite_node
from src.agents.generate_node import generate_node

from src.graph.router import route_after_grading

from src.utils.logger import logger


# ---------------------------------------------------------
# Build Graph
# ---------------------------------------------------------

workflow = StateGraph(GraphState)

logger.info("=" * 80)
logger.info("Initializing LangGraph Workflow")
logger.info("=" * 80)

# ---------------------------------------------------------
# Register Nodes
# ---------------------------------------------------------

workflow.add_node(
    "retrieve",
    retrieve_node
)

workflow.add_node(
    "grade",
    grade_node
)

workflow.add_node(
    "rewrite",
    rewrite_node
)

workflow.add_node(
    "generate",
    generate_node
)

# ---------------------------------------------------------
# Graph Edges
# ---------------------------------------------------------

workflow.add_edge(
    START,
    "retrieve"
)

workflow.add_edge(
    "retrieve",
    "grade"
)

workflow.add_conditional_edges(
    "grade",
    route_after_grading,
    {
        "generate": "generate",
        "rewrite": "rewrite",
        "end": END,
    },
)

workflow.add_edge(
    "rewrite",
    "retrieve"
)

workflow.add_edge(
    "generate",
    END
)

# ---------------------------------------------------------
# Compile
# ---------------------------------------------------------

logger.info("Compiling LangGraph...")

app = workflow.compile()

logger.info("LangGraph compiled successfully.")
logger.info("=" * 80)