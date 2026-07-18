import re
from typing import Any, Dict, List, Optional


# ============================================================
# Companies
# ============================================================

COMPANIES = {
    "apple": "APPLE",
    "aapl": "APPLE",

    "microsoft": "MICROSOFT",
    "msft": "MICROSOFT",

    "nvidia": "NVIDIA",
    "nvda": "NVIDIA",

    "amazon": "AMAZON",
    "amzn": "AMAZON",

    "alphabet": "ALPHABET",
    "google": "ALPHABET",
    "goog": "ALPHABET",

    "meta": "META",
    "facebook": "META",

    "tesla": "TESLA",
    "tsla": "TESLA",
}


# ============================================================
# Financial Metrics
# ============================================================

FINANCIAL_METRICS = {

    "revenue": [
        "revenue",
        "net sales",
        "sales",
        "total revenue",
    ],

    "net income": [
        "net income",
        "net earnings",
        "earnings",
        "profit",
        "gaap net income",
    ],

    "operating income": [
        "operating income",
        "operating profit",
    ],

    "gross profit": [
        "gross profit",
    ],

    "gross margin": [
        "gross margin",
    ],

    "cash flow": [
        "cash flow",
        "operating cash flow",
        "cash generated",
        "cash generated from operating activities",
    ],

    "free cash flow": [
        "free cash flow",
    ],

    "assets": [
        "assets",
        "total assets",
    ],

    "liabilities": [
        "liabilities",
        "total liabilities",
    ],

    "equity": [
        "equity",
        "stockholders equity",
        "shareholders equity",
    ],

    "eps": [
        "eps",
        "earnings per share",
    ],
}


# ============================================================
# Business Segments
# ============================================================

BUSINESS_SEGMENTS = [

    "iphone",
    "ipad",
    "mac",
    "services",
    "wearables",
    "accessories",

    "americas",
    "greater china",
    "europe",
    "japan",
    "rest of asia pacific",
]


# ============================================================
# Section Hints
# ============================================================

SECTION_HINTS = {

    "revenue": "Income Statement",
    "net income": "Income Statement",
    "operating income": "Income Statement",
    "gross profit": "Income Statement",
    "gross margin": "Income Statement",

    "cash flow": "Cash Flow Statement",
    "free cash flow": "Cash Flow Statement",

    "assets": "Balance Sheet",
    "liabilities": "Balance Sheet",
    "equity": "Balance Sheet",

    "eps": "Income Statement",
}


# ============================================================
# Helpers
# ============================================================

def contains_word(text: str, word: str) -> bool:
    return (
        re.search(
            rf"\b{re.escape(word)}\b",
            text,
            flags=re.IGNORECASE,
        )
        is not None
    )


# ============================================================
# Company
# ============================================================

def detect_company(question: str) -> Optional[str]:

    q = question.lower()

    for keyword, company in COMPANIES.items():

        if contains_word(q, keyword):
            return company

    return None


# ============================================================
# Metrics
# IMPORTANT:
# Returns ALL matched metrics instead of only the first one.
# ============================================================

def detect_metrics(question: str) -> List[str]:

    q = question.lower()

    found = []

    for canonical, aliases in FINANCIAL_METRICS.items():

        for alias in aliases:

            if contains_word(q, alias):

                found.append(canonical)
                break

    return list(dict.fromkeys(found))


# ============================================================
# Segment
# ============================================================

def detect_segment(question: str) -> Optional[str]:

    q = question.lower()

    for segment in BUSINESS_SEGMENTS:

        if contains_word(q, segment):
            return segment

    return None


# ============================================================
# Year
# ============================================================

def detect_year(question: str) -> Optional[int]:

    match = re.search(r"\b(20\d{2})\b", question)

    if match:
        return int(match.group(1))

    return None


# ============================================================
# Quarter
# ============================================================

def detect_quarter(question: str) -> Optional[str]:

    match = re.search(
        r"\bQ([1-4])\b",
        question.upper(),
    )

    if match:
        return f"Q{match.group(1)}"

    return None


# ============================================================
# Document Type
# ============================================================

def detect_document_type(question: str) -> Optional[str]:

    q = question.lower()

    if "annual report" in q:
        return "Annual Report"

    if "annual" in q:
        return "Annual Report"

    if "quarterly report" in q:
        return "Quarterly Report"

    if "quarterly" in q:
        return "Quarterly Report"

    if "10-k" in q or "10k" in q:
        return "10-K"

    if "10-q" in q or "10q" in q:
        return "10-Q"

    if "8-k" in q or "8k" in q:
        return "8-K"

    return None

# ============================================================
# Process Query
# ============================================================

def process_query(question: str) -> Dict[str, Any]:
    """
    Convert a natural-language financial question into:

    - processed_query
    - metadata filters
    - section hint
    - retrieval intent
    """

    filters: Dict[str, Any] = {}

    company = detect_company(question)
    metrics = detect_metrics(question)
    segment = detect_segment(question)
    year = detect_year(question)
    quarter = detect_quarter(question)
    document_type = detect_document_type(question)

    # --------------------------------------------------------
    # Metadata Filters
    # --------------------------------------------------------

    if company:
        filters["company"] = company

    if year:
        filters["year"] = year

    if quarter:
        filters["quarter"] = quarter

    if document_type:
        filters["document_type"] = document_type

    filters = {
        k: v
        for k, v in filters.items()
        if v is not None
    }

    # --------------------------------------------------------
    # Build Retrieval Query
    # --------------------------------------------------------

    query_parts = []

    # Keep company in semantic search
    if company:
        query_parts.append(company)

    # Segment (iPhone, Services, etc.)
    if segment:
        query_parts.append(segment)

    # Include ALL detected metrics
    for metric in metrics:

        query_parts.append(metric)

        for alias in FINANCIAL_METRICS[metric]:

            if alias not in query_parts:
                query_parts.append(alias)

    # Preserve explicit year
    if year:
        query_parts.append(str(year))

    # Preserve explicit quarter
    if quarter:
        query_parts.append(quarter)

    # Preserve explicit document type
    if document_type:
        query_parts.append(document_type)

    # Fallback
    if not query_parts:
        processed_query = question

    else:

        processed_query = " ".join(
            dict.fromkeys(query_parts)
        )

    # --------------------------------------------------------
    # Section Hint
    # --------------------------------------------------------

    section_hint = None

    # Priority order

    if "cash flow" in metrics:
        section_hint = SECTION_HINTS["cash flow"]

    elif "free cash flow" in metrics:
        section_hint = SECTION_HINTS["free cash flow"]

    elif "assets" in metrics:
        section_hint = SECTION_HINTS["assets"]

    elif "liabilities" in metrics:
        section_hint = SECTION_HINTS["liabilities"]

    elif "equity" in metrics:
        section_hint = SECTION_HINTS["equity"]

    elif metrics:
        section_hint = SECTION_HINTS.get(metrics[0])

    # --------------------------------------------------------
    # Intent
    # --------------------------------------------------------

    financial_statement_metrics = {
        "revenue",
        "net income",
        "operating income",
        "gross profit",
        "gross margin",
        "eps",
    }

    cash_flow_metrics = {
        "cash flow",
        "free cash flow",
    }

    balance_sheet_metrics = {
        "assets",
        "liabilities",
        "equity",
    }

    if any(metric in financial_statement_metrics for metric in metrics):

        intent = "financial_statement"

    elif any(metric in cash_flow_metrics for metric in metrics):

        intent = "cash_flow"

    elif any(metric in balance_sheet_metrics for metric in metrics):

        intent = "balance_sheet"

    else:

        intent = "general"

    return {

        "processed_query": processed_query,

        "filters": filters,

        "section_hint": section_hint,

        "intent": intent,

        "metrics": metrics,

        "company": company,

        "year": year,

        "quarter": quarter,

        "document_type": document_type,

        "segment": segment,
    }