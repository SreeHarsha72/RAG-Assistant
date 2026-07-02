"""Retrieval logic for the Internal Data RAG Assistant."""
from __future__ import annotations

from functools import lru_cache
from typing import Dict

import chromadb
from sentence_transformers import SentenceTransformer

from src.config import CHROMA_DIR, COLLECTION_NAME, DEFAULT_TOP_K, EMBEDDING_MODEL_NAME
from src.utils import format_sources


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """Cache the embedding model so repeated questions are faster."""
    return SentenceTransformer(EMBEDDING_MODEL_NAME)


def get_collection():
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def retrieve_context(question: str, top_k: int = DEFAULT_TOP_K) -> Dict:
    """Convert a question into an embedding and retrieve matching chunks from ChromaDB."""
    collection = get_collection()

    if collection.count() == 0:
        return {
            "documents": [],
            "metadatas": [],
            "distances": [],
            "sources": [],
        }

    question_embedding = get_embedding_model().encode([question]).tolist()[0]

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]
    sources = format_sources(metadatas, distances)

    return {
        "documents": documents,
        "metadatas": metadatas,
        "distances": distances,
        "sources": sources,
    }


# Backward-compatible function used by the earlier Streamlit app.
def retrieve_relevant_chunks(question: str, top_k: int = DEFAULT_TOP_K):
    retrieved = retrieve_context(question, top_k=top_k)
    return retrieved["documents"], retrieved["metadatas"], retrieved["distances"]
