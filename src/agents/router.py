from src.graph.state import GraphState


def route_after_grading(state: GraphState):

    if state["next_step"] == "accept":

        return "end"

    return "rewrite"