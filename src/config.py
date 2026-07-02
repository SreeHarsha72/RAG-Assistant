"""Central configuration for the Internal Data RAG Assistant."""
from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CHROMA_DIR = BASE_DIR / "chroma_db"

COLLECTION_NAME = "internal_data_knowledge"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Ollama settings. You can override these using environment variables.
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

# Chunking settings.
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))

# Retrieval settings.
DEFAULT_TOP_K = int(os.getenv("DEFAULT_TOP_K", "5"))

# Chroma cosine distance: lower is better. Tune this after testing your data.
# If the best retrieved chunk is above this distance, the app returns a no-answer response.
MAX_ACCEPTABLE_DISTANCE = float(os.getenv("MAX_ACCEPTABLE_DISTANCE", "1.25"))

SUPPORTED_EXTENSIONS = {".txt", ".sql", ".md", ".csv"}
