"""Utility functions for loading, cleaning, chunking, and formatting RAG sources."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List

import pandas as pd

from src.config import DATA_DIR, SUPPORTED_EXTENSIONS


def clean_text(text: str) -> str:
    """Basic whitespace cleaning while keeping content readable for retrieval."""
    return " ".join(str(text).split())


def read_text_file(file_path: str | Path) -> str:
    """Read TXT, SQL, or Markdown files."""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
        return file.read()


def read_csv_as_text(file_path: str | Path) -> str:
    """Convert CSV data dictionaries into readable text for RAG ingestion."""
    df = pd.read_csv(file_path)

    rows = []
    for index, row in df.iterrows():
        row_text = ", ".join([f"{col}: {row[col]}" for col in df.columns])
        rows.append(f"Row {index + 1}: {row_text}")

    return "\n".join(rows)


def load_file_as_text(file_path: str | Path) -> str:
    """Load supported file types and convert them into plain text."""
    file_path = Path(file_path)
    extension = file_path.suffix.lower()

    if extension in {".txt", ".sql", ".md"}:
        return read_text_file(file_path)

    if extension == ".csv":
        return read_csv_as_text(file_path)

    raise ValueError(f"Unsupported file type: {extension}")


def get_supported_files(data_folder: str | Path = DATA_DIR) -> List[Path]:
    """Recursively collect supported files from the data folder."""
    data_folder = Path(data_folder)
    supported_files: List[Path] = []

    if not data_folder.exists():
        return supported_files

    for root, _, files in os.walk(data_folder):
        for file_name in files:
            file_path = Path(root) / file_name
            if file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
                supported_files.append(file_path)

    return sorted(supported_files)


def infer_document_type(file_path: str | Path) -> str:
    """Infer document type from folder name."""
    normalized_path = str(file_path).replace("\\", "/").lower()

    if "/dbt_models/" in normalized_path:
        return "dbt_model"
    if "/sql_queries/" in normalized_path:
        return "sql_query"
    if "/data_dictionaries/" in normalized_path:
        return "data_dictionary"
    if "/pipeline_logs/" in normalized_path:
        return "pipeline_log"
    if "/docs/" in normalized_path:
        return "documentation"

    return "unknown"


def simple_chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
    """
    Split text into overlapping chunks.

    Character-based chunking keeps this project easy to understand while still showing
    the core RAG idea: smaller searchable context windows.
    """
    text = text.strip()
    if not text:
        return []

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - chunk_overlap

    return chunks


def build_chunk_id(source_file: str, chunk_index: int) -> str:
    """Create a stable chunk ID for ChromaDB."""
    safe_source = source_file.replace(" ", "_").replace("/", "_").replace("\\", "_")
    return f"{safe_source}_chunk_{chunk_index}"


def distance_to_similarity(distance: float) -> float:
    """
    Convert Chroma distance into an easy-to-read similarity score.

    With cosine distance, lower distance is better. This score is not a probability;
    it is a user-friendly retrieval confidence indicator.
    """
    return round(max(0.0, 1.0 - float(distance)), 4)


def format_sources(metadatas: List[Dict], distances: List[float]) -> List[Dict]:
    """Create clean source objects for UI display."""
    sources = []

    for metadata, distance in zip(metadatas, distances):
        sources.append(
            {
                "source_file": metadata.get("source", "unknown"),
                "source_path": metadata.get("relative_path", metadata.get("path", "unknown")),
                "chunk_id": metadata.get("chunk_index", "unknown"),
                "document_type": metadata.get("document_type", "unknown"),
                "distance": round(float(distance), 4),
                "similarity_score": distance_to_similarity(float(distance)),
            }
        )

    return sources
