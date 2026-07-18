import json
import re

from langchain_core.messages import HumanMessage, SystemMessage

from src.graph.state import GraphState
from src.llm.ollama_client import get_llm
from src.prompts.grader_prompt import SYSTEM_PROMPT, USER_PROMPT

llm = get_llm()


def parse_json_response(text: str):
    """
    Extract JSON from LLM response.
    """

    text = text.strip()

    try:
        return json.loads(text)
    except Exception:
        pass

    match = re.search(r"\{.*\}", text, re.DOTALL)

    if match:
        try:
            return json.loads(match.group())
        except Exception:
            pass

    return None


# ------------------------------------------------------------------
# Fast heuristic
# ------------------------------------------------------------------

def heuristic_accept(question: str, context: str) -> bool:

    q = question.lower()
    c = context.lower()

    metrics = [
        "revenue",
        "net income",
        "operating income",
        "gross profit",
        "cash flow",
        "free cash flow",
        "operating margin",
        "gross margin",
        "eps",
        "earnings",
    ]

    found_metric = any(metric in q and metric in c for metric in metrics)

    companies = [
        "apple",
        "nvidia",
        "microsoft",
        "amazon",
        "meta",
        "alphabet",
        "tesla",
    ]

    company_found = any(company in q and company in c for company in companies)

    year_found = True

    year_match = re.search(r"(20\d{2})", q)

    if year_match:
        year_found = year_match.group(1) in c

    financial_doc = any(
        keyword in c
        for keyword in [
            "annual report",
            "10-k",
            "10-q",
            "8-k",
            "financial statements",
            "consolidated statements",
            "income statement",
            "gaap",
            "non-gaap",
        ]
    )

    return company_found and year_found and (found_metric or financial_doc)


# ------------------------------------------------------------------
# Main Node
# ------------------------------------------------------------------

def grade_node(state: GraphState) -> GraphState:

    print("\n========== GRADER NODE ==========")

    question = state.get(
        "original_question",
        state.get("question", "")
    )

    context = state.get("context", "")

    metadata = state.setdefault("metadata", {})

    # ------------------------------------------------------------
    # Fast heuristic
    # ------------------------------------------------------------

    if heuristic_accept(question, context):

        metadata["grader_response"] = {
            "score": 1.0,
            "decision": "accept",
            "reason": "Accepted by heuristic."
        }

        state["metadata"] = metadata
        state["relevance_score"] = 1.0
        state["confidence"] = 1.0
        state["is_relevant"] = True
        state["next_step"] = "accept"

        print("\nHeuristic Accepted Retrieval\n")

        return state

    # ------------------------------------------------------------
    # Ask LLM
    # ------------------------------------------------------------

    prompt = USER_PROMPT.format(
        question=question,
        context=context
    )

    response = llm.invoke(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ]
    )

    raw = response.content.strip()

    print("\nGrader Raw Response:\n")
    print(raw)

    parsed = parse_json_response(raw)

    # ------------------------------------------------------------
    # Invalid JSON
    # ------------------------------------------------------------

    if parsed is None:

        print("\nInvalid JSON from grader.")

        metadata["grader_response"] = raw

        state["metadata"] = metadata
        state["relevance_score"] = 0.0
        state["confidence"] = 0.0
        state["is_relevant"] = False
        state["next_step"] = "rewrite"

        return state

    # ------------------------------------------------------------
    # Parse Result
    # ------------------------------------------------------------

    score = float(parsed.get("score", 0.0))
    score = max(0.0, min(score, 1.0))

    decision = parsed.get(
        "decision",
        "rewrite"
    ).lower()

    if decision not in ["accept", "rewrite"]:
        decision = "rewrite"

    metadata["grader_response"] = parsed

    state["metadata"] = metadata
    state["relevance_score"] = score
    state["confidence"] = score
    state["is_relevant"] = decision == "accept"
    state["next_step"] = decision

    print("\n========== GRADER RESULT ==========")
    print(f"Score      : {score:.2f}")
    print(f"Decision   : {decision}")
    print(f"Confidence : {score:.2f}")
    print("===================================\n")

    return state