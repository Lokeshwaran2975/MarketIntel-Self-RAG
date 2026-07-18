"""
Routing logic after grading.
"""

from src.graph.state import GraphState


MAX_RETRIES = 2


def route_after_grading(state: GraphState) -> str:
    """
    Decide the next node after document grading.

    Returns:
        - "generate": Documents are relevant.
        - "rewrite" : Documents are not relevant and retries remain.
        - "end"     : Maximum retries reached.
    """

    is_relevant = state.get("is_relevant", False)
    retry_count = state.get("retry_count", 0)

    if is_relevant:
        print("\n========== ROUTER ==========")
        print("Decision : Generate")
        print("============================\n")
        return "generate"

    if retry_count < MAX_RETRIES:
        print("\n========== ROUTER ==========")
        print(f"Decision : Rewrite (Retry {retry_count + 1}/{MAX_RETRIES})")
        print("============================\n")
        return "rewrite"

    print("\n========== ROUTER ==========")
    print("Decision : End (Maximum retries reached)")
    print("============================\n")

    return "end"