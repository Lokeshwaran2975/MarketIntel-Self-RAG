"""
Context Builder

Combines retrieved chunks into
one LLM-ready context.
"""

from typing import List
from langchain_core.documents import Document


def build_context(documents: List[Document]) -> str:

    if not documents:
        return ""

    context = []

    for i, doc in enumerate(documents, start=1):

        source = doc.metadata.get("source", "Unknown")
        company = doc.metadata.get("company", "Unknown")
        year = doc.metadata.get("year", "")

        section = f"""
==============================
Document {i}

Company : {company}
Year    : {year}
Source  : {source}

Content:
{doc.page_content}
"""

        context.append(section)

    # Print only once
    print("\n" + "=" * 80)
    print("LLM CONTEXT")
    print("=" * 80)
    print("\n".join(context))
    print("=" * 80 + "\n")

    return "\n".join(context)