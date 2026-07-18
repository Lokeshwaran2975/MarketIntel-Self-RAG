"""
MarketIntel
Duplicate Handler
"""

import re
from typing import List

from langchain_core.documents import Document


class DuplicateHandler:

    @staticmethod
    def normalize(text: str) -> str:
        """
        Normalize text for duplicate detection.
        """

        text = text.lower()

        text = re.sub(r"\s+", " ", text)

        return text.strip()

    @classmethod
    def remove(
        cls,
        docs: List[Document]
    ) -> List[Document]:

        unique_docs = []

        seen = set()

        for doc in docs:

            key = (

                doc.metadata.get(
                    "file_name",
                    "unknown"
                ),

                cls.normalize(
                    doc.page_content
                )

            )

            if key not in seen:

                seen.add(key)

                unique_docs.append(doc)

        return unique_docs