"""
Rewrite Node

Responsibilities
----------------
1. Rewrite only when retrieval genuinely failed.
2. Preserve company names.
3. Preserve fiscal years.
4. Preserve quarters.
5. Preserve requested financial metrics.
6. Never answer the question.
7. Never broaden the search unnecessarily.
"""

import re

from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
)

from src.graph.state import GraphState
from src.llm.ollama_client import get_llm
from src.prompts.rewrite_prompt import (
    SYSTEM_PROMPT,
    USER_PROMPT,
)

llm = get_llm()


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

COMPANIES = [
    "APPLE",
    "NVIDIA",
    "MICROSOFT",
    "TESLA",
    "AMAZON",
    "META",
    "ALPHABET",
    "GOOGLE",
]

METRICS = [
    "revenue",
    "net income",
    "gross profit",
    "gross margin",
    "operating income",
    "operating margin",
    "cash flow",
    "free cash flow",
    "eps",
    "earnings per share",
    "operating expenses",
]


def extract_company(question):

    q = question.upper()

    for company in COMPANIES:

        if company in q:
            return company

    return None


def extract_year(question):

    match = re.search(r"(20\d{2})", question)

    if match:
        return match.group()

    return None


def extract_quarter(question):

    q = question.upper()

    match = re.search(r"Q([1-4])", q)

    if match:
        return f"Q{match.group(1)}"

    return None


def extract_metric(question):

    q = question.lower()

    for metric in METRICS:

        if metric in q:
            return metric

    return None


# ---------------------------------------------------------
# Main Rewrite Node
# ---------------------------------------------------------

def rewrite_node(state: GraphState) -> GraphState:

    print("\n========== REWRITE NODE ==========")

    original_question = state.get(
    "original_question",
    state.get("question", "")
    )

    context = state.get("context", "")

    company = extract_company(original_question)
    year = extract_year(original_question)
    quarter = extract_quarter(original_question)
    metric = extract_metric(original_question)

    prompt = USER_PROMPT.format(
        question=original_question,
        context=context
    )

    response = llm.invoke(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ]
    )

    rewritten = response.content.strip()

    # -----------------------------------------------------
    # Empty response
    # -----------------------------------------------------

    if not rewritten:
        rewritten = original_question

    # -----------------------------------------------------
    # Prevent answering
    # -----------------------------------------------------

    if len(rewritten.split()) > 40:
        rewritten = original_question

    # -----------------------------------------------------
    # Preserve Company
    # -----------------------------------------------------

    if company:

        if company.lower() not in rewritten.lower():

            rewritten = f"{company} {rewritten}"

    # -----------------------------------------------------
    # Preserve Year
    # -----------------------------------------------------

    if year:

        if year not in rewritten:

            rewritten += f" {year}"

    # -----------------------------------------------------
    # Preserve Quarter
    # -----------------------------------------------------

    if quarter:

        if quarter not in rewritten.upper():

            rewritten += f" {quarter}"

    # -----------------------------------------------------
    # Preserve Metric
    # -----------------------------------------------------

    if metric:

        if metric.lower() not in rewritten.lower():

            rewritten += f" {metric}"

    # -----------------------------------------------------
    # Don't rewrite already-good questions
    # -----------------------------------------------------

    if (
        company
        and metric
        and year
    ):

        rewritten = original_question

    # -----------------------------------------------------
    # Logging
    # -----------------------------------------------------

    print(f"Original Question : {original_question}")
    print(f"Rewritten Question: {rewritten}")

    state["rewritten_question"] = rewritten
    state["question"] = rewritten

    state["retry_count"] = state.get(
        "retry_count",
        0
    ) + 1

    print(f"Retry Count : {state['retry_count']}")
    print("========== REWRITE NODE END ==========\n")

    return state