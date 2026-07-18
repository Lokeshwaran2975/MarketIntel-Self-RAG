"""
MarketIntel - Document Ingestion Pipeline

Pipeline
--------
1. Discover documents
2. Skip duplicate files
3. Skip already indexed files
4. Load documents
5. Clean extracted text
6. Extract metadata
7. Split into chunks
8. Build BM25 Index
9. Generate embeddings
10. Store embeddings in ChromaDB
"""

import time
from tqdm import tqdm

from src.loaders.loader_factory import load_document

from src.processing.cleaner import clean_text
from src.processing.metadata import add_metadata
from src.processing.splitter import split_documents

from src.ingestion.duplicate_detector import DuplicateDetector
from src.ingestion.index_tracker import IndexTracker

from src.retriever.bm25 import bm25_retriever

from src.vectorstore.collection_manage import (
    get_vector_store,
    add_documents
)

from src.utils.logger import logger

from src.config.settings import (
    DATA_DIR,
    CHROMA_DB_DIR
)


def ingest_documents():

    start_time = time.time()

    all_documents = []

    loaded_files = 0
    failed_files = 0
    skipped_files = 0

    duplicate_detector = DuplicateDetector()
    index_tracker = IndexTracker()

    logger.info("=" * 80)
    logger.info("🚀 MARKETINTEL DOCUMENT INGESTION STARTED")
    logger.info("=" * 80)

    files = sorted(
        [
            file
            for file in DATA_DIR.rglob("*")
            if file.is_file()
        ]
    )

    logger.info(f"Found {len(files)} files")

    for file in tqdm(
        files,
        desc="📂 Loading Documents",
        unit="file",
        colour="green"
    ):

        try:

            # -------------------------------------------------
            # Duplicate Detection
            # -------------------------------------------------

            if duplicate_detector.is_duplicate(file):

                logger.warning(
                    f"Duplicate file skipped : {file.name}"
                )

                skipped_files += 1
                continue

            # -------------------------------------------------
            # Incremental Indexing
            # -------------------------------------------------

            if not index_tracker.should_index(file):

                logger.info(
                    f"Already Indexed : {file.name}"
                )

                skipped_files += 1
                continue

            # -------------------------------------------------
            # Load Document
            # -------------------------------------------------

            docs = load_document(str(file))

            # -------------------------------------------------
            # Clean Text
            # -------------------------------------------------

            for doc in docs:
                doc.page_content = clean_text(doc.page_content)

            # -------------------------------------------------
            # Add Metadata
            # -------------------------------------------------

            docs = add_metadata(docs, file)

            # -------------------------------------------------
            # Debug Metadata
            # -------------------------------------------------

            if docs:

                meta = docs[0].metadata

                logger.debug(
                    f"""
Loaded : {file.name}

Company       : {meta.get('company')}
Year          : {meta.get('year')}
Quarter       : {meta.get('quarter')}
Document Type : {meta.get('document_type')}
Priority      : {meta.get('priority')}
Folder        : {meta.get('source_folder')}
"""
                )

            all_documents.extend(docs)

            loaded_files += 1

            # -------------------------------------------------
            # Update Index Tracker
            # -------------------------------------------------

            index_tracker.update(file)

        except Exception:

            failed_files += 1

            logger.exception(
                f"Failed loading {file.name}"
            )

    # -------------------------------------------------
    # Save Incremental Index
    # -------------------------------------------------

    index_tracker.save()

    logger.info(
        f"Successfully Loaded {loaded_files} files"
    )

    # -------------------------------------------------
    # Split Documents
    # -------------------------------------------------

    logger.info("Splitting documents into chunks...")

    chunks = split_documents(all_documents)

    logger.info(
        f"Generated {len(chunks)} chunks"
    )

    # -------------------------------------------------
    # Build BM25 Index
    # -------------------------------------------------

    logger.info("Building BM25 index...")

    bm25_retriever.build(chunks)

    logger.info(
        f"✅ BM25 Index Built ({len(chunks)} chunks)"
    )

    # -------------------------------------------------
    # Generate Embeddings & Store in ChromaDB
    # -------------------------------------------------

    logger.info(
        "Generating embeddings and storing vectors..."
    )

    vector_store = get_vector_store()

    add_documents(
        vector_store,
        chunks
    )

    # -------------------------------------------------
    # Summary
    # -------------------------------------------------

    total_time = time.time() - start_time

    logger.info("=" * 80)
    logger.info("🎉 INGESTION COMPLETED")
    logger.info("=" * 80)

    logger.info(f"Files Found       : {len(files)}")
    logger.info(f"Files Indexed     : {loaded_files}")
    logger.info(f"Files Skipped     : {skipped_files}")
    logger.info(f"Files Failed      : {failed_files}")

    logger.info(f"Pages Loaded      : {len(all_documents)}")
    logger.info(f"Chunks Created    : {len(chunks)}")

    logger.info(
        f"Vector Database   : {CHROMA_DB_DIR}"
    )

    logger.info(
        f"Execution Time    : {total_time:.2f} seconds"
    )

    logger.info("=" * 80)


if __name__ == "__main__":

    ingest_documents()