import re

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from src.config.settings import CHUNK_SIZE, CHUNK_OVERLAP
from src.processing.table_detector import is_table


# Major headings commonly found in SEC filings
SECTION_PATTERN = re.compile(
    r"(ITEM\s+\d+.*?|"
    r"Condensed Consolidated.*?|"
    r"Consolidated.*?|"
    r"Products and Services Performance|"
    r"Segment Operating Performance|"
    r"Liquidity and Capital Resources|"
    r"Results of Operations)",
    re.IGNORECASE
)


def split_documents(documents):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )

    final_chunks = []

    for doc in documents:

        text = doc.page_content
        metadata = dict(doc.metadata)

        matches = list(SECTION_PATTERN.finditer(text))

        # ---------------------------------------------------------
        # No headings → normal splitting
        # ---------------------------------------------------------
        if not matches:

            if is_table(text):
                metadata["chunk_type"] = "table"

                final_chunks.append(
                    Document(
                        page_content=text,
                        metadata=metadata
                    )
                )

            else:
                final_chunks.extend(
                    splitter.split_documents([doc])
                )

            continue

        # ---------------------------------------------------------
        # Split by sections
        # ---------------------------------------------------------
        for i, match in enumerate(matches):

            start = match.start()

            if i + 1 < len(matches):
                end = matches[i + 1].start()
            else:
                end = len(text)

            section_text = text[start:end].strip()

            if not section_text:
                continue

            section_metadata = metadata.copy()
            section_metadata["section"] = match.group().strip()

            # ---------------------------------------------------------
            # Table detected → keep as a single chunk
            # ---------------------------------------------------------
            if is_table(section_text):

                section_metadata["chunk_type"] = "table"

                final_chunks.append(
                    Document(
                        page_content=section_text,
                        metadata=section_metadata
                    )
                )

                continue

            # ---------------------------------------------------------
            # Normal text
            # ---------------------------------------------------------
            section_doc = Document(
                page_content=section_text,
                metadata=section_metadata
            )

            if len(section_text) > CHUNK_SIZE:

                final_chunks.extend(
                    splitter.split_documents([section_doc])
                )

            else:

                final_chunks.append(section_doc)

    return final_chunks