from functools import lru_cache
from tqdm import tqdm

from langchain_chroma import Chroma
from langchain_core.documents import Document

from src.embeddings.embedding_model import get_embedding_model
from src.config.settings import CHROMA_DB_DIR


@lru_cache(maxsize=1)
def get_vector_store():

    embeddings = get_embedding_model()

    return Chroma(
        persist_directory=str(CHROMA_DB_DIR),
        embedding_function=embeddings
    )


def add_documents(vector_store, documents, batch_size=100):

    total = len(documents)

    for i in tqdm(
        range(0, total, batch_size),
        desc="🧠 Creating Embeddings",
        unit="batch"
    ):

        batch = documents[i:i + batch_size]

        vector_store.add_documents(batch)


def load_all_documents():
    """
    Load all indexed documents from ChromaDB and reconstruct
    LangChain Document objects.
    """

    vector_store = get_vector_store()

    data = vector_store.get()

    # Handle empty database
    if not data or not data.get("documents"):
        return []

    documents = []

    for text, metadata in zip(
        data["documents"],
        data["metadatas"]
    ):
        documents.append(
            Document(
                page_content=text,
                metadata=metadata or {}
            )
        )

    return documents