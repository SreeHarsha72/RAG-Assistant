"""Knowledge-base ingestion for the Internal Data RAG Assistant."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List

import chromadb
from sentence_transformers import SentenceTransformer

from src.config import (
    CHROMA_DIR,
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    COLLECTION_NAME,
    DATA_DIR,
    EMBEDDING_MODEL_NAME,
)
from src.utils import (
    build_chunk_id,
    clean_text,
    get_supported_files,
    infer_document_type,
    load_file_as_text,
    simple_chunk_text,
)


def get_embedding_model() -> SentenceTransformer:
    """Load the embedding model."""
    return SentenceTransformer(EMBEDDING_MODEL_NAME)


def reset_collection(client: chromadb.PersistentClient):
    """Delete and recreate the ChromaDB collection."""
    try:
        client.delete_collection(name=COLLECTION_NAME)
    except Exception:
        pass

    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def rebuild_vector_database() -> Dict[str, int | str]:
    """
    Re-index the knowledge base.

    Steps:
    1. Read supported files from /data.
    2. Clean and chunk each document.
    3. Generate embeddings.
    4. Store chunks, metadata, and embeddings in ChromaDB.
    """
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = reset_collection(client)
    embedding_model = get_embedding_model()

    all_ids: List[str] = []
    all_chunks: List[str] = []
    all_metadatas: List[dict] = []

    files = get_supported_files(DATA_DIR)

    for file_path in files:
        raw_text = load_file_as_text(file_path)
        cleaned_text = clean_text(raw_text)
        chunks = simple_chunk_text(cleaned_text, CHUNK_SIZE, CHUNK_OVERLAP)

        source_file = os.path.basename(file_path)
        document_type = infer_document_type(file_path)
        relative_path = str(Path(file_path).relative_to(DATA_DIR))

        for chunk_index, chunk in enumerate(chunks):
            all_ids.append(build_chunk_id(source_file, chunk_index))
            all_chunks.append(chunk)
            all_metadatas.append(
                {
                    "source": source_file,
                    "path": str(file_path),
                    "relative_path": relative_path,
                    "document_type": document_type,
                    "chunk_index": chunk_index,
                }
            )

    if all_chunks:
        embeddings = embedding_model.encode(all_chunks).tolist()
        collection.add(
            ids=all_ids,
            documents=all_chunks,
            embeddings=embeddings,
            metadatas=all_metadatas,
        )

    return {
        "files_indexed": len(files),
        "chunks_indexed": len(all_chunks),
        "collection_name": COLLECTION_NAME,
    }


# Backward-compatible name used by the earlier version of the project.
def ingest_documents() -> Dict[str, int | str]:
    return rebuild_vector_database()


if __name__ == "__main__":
    result = rebuild_vector_database()
    print(
        f"Successfully indexed {result['files_indexed']} files and "
        f"{result['chunks_indexed']} chunks into '{result['collection_name']}'."
    )
