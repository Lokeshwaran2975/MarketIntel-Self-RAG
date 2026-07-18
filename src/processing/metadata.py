"""
Metadata Processing

This module extracts metadata from the document filename,
normalizes it, and attaches it to every document chunk
before storing it in ChromaDB.
"""

from src.ingestion.metadata_parser import extract_metadata


def add_metadata(documents, file_path):
    """
    Extract, normalize and attach metadata to all chunks.
    """

    metadata = extract_metadata(file_path)

    # ---------------------------------------------------------
    # Company
    # ---------------------------------------------------------

    metadata["company"] = (
        metadata.get("company", "UNKNOWN")
        .strip()
        .upper()
    )

    # ---------------------------------------------------------
    # Document Year
    # ---------------------------------------------------------

    document_year = metadata.get("document_year")

    if document_year is not None:
        document_year = int(document_year)

    metadata["document_year"] = document_year

    # Backward compatibility
    metadata["year"] = document_year

    # ---------------------------------------------------------
    # Quarter
    # ---------------------------------------------------------

    quarter = metadata.get("quarter")

    metadata["quarter"] = (
        quarter.upper().strip()
        if quarter
        else None
    )

    # ---------------------------------------------------------
    # Document Type
    # ---------------------------------------------------------

    metadata["document_type"] = (
        metadata.get(
            "document_type",
            "Unknown"
        ).strip()
    )

    # ---------------------------------------------------------
    # Priority
    # ---------------------------------------------------------

    metadata["priority"] = int(
        metadata.get(
            "priority",
            0
        )
    )

    # ---------------------------------------------------------
    # File Name
    # ---------------------------------------------------------

    metadata["file_name"] = (
        metadata.get(
            "file_name",
            ""
        ).strip()
    )

    # ---------------------------------------------------------
    # Source Folder
    # ---------------------------------------------------------

    metadata["source_folder"] = (
        metadata.get(
            "source_folder",
            ""
        ).strip()
    )

    # ---------------------------------------------------------
    # Attach Metadata
    # ---------------------------------------------------------

    for doc in documents:

        doc.metadata.update(metadata)

    return documents