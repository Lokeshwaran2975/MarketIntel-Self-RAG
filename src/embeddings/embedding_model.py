from langchain_ollama import OllamaEmbeddings

from src.config.settings import EMBEDDING_MODEL

def get_embedding_model():

    return OllamaEmbeddings(
        model=EMBEDDING_MODEL
    )