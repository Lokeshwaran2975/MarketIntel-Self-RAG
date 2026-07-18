from pathlib import Path

# Project Root
PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"

CHROMA_DB_DIR = PROJECT_ROOT / "chroma_db"

EMBEDDING_MODEL = "nomic-embed-text"

CHUNK_SIZE = 800

CHUNK_OVERLAP = 150

TOP_K = 5