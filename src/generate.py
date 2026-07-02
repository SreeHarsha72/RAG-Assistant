"""Prompt building and answer generation using local Ollama models."""
from __future__ import annotations

from typing import Dict, List

import requests

from src.config import MAX_ACCEPTABLE_DISTANCE, OLLAMA_MODEL, OLLAMA_URL
from src.retrieve import retrieve_context

NO_ANSWER_MESSAGE = "I could not find enough information in the internal knowledge base."


def build_prompt(question: str, chunks: List[str], sources: List[dict]) -> str:
    """Build a grounded prompt using retrieved chunks and source metadata."""
    context_parts = []

    for i, chunk in enumerate(chunks):
        source = sources[i]
        context_parts.append(
            f"""
Source {i + 1}
File: {source.get('source_file', 'unknown')}
Document Type: {source.get('document_type', 'unknown')}
Chunk ID: {source.get('chunk_id', 'unknown')}
Similarity Score: {source.get('similarity_score', 'unknown')}

Content:
{chunk}
"""
        )

    context = "\n\n".join(context_parts)

    return f"""
You are a senior Analytics Engineering assistant for an internal data team.

Your job is to answer internal data questions using ONLY the retrieved context.

Rules:
1. Do not make up facts.
2. Do not use outside knowledge.
3. If the answer is not available in the context, say exactly:
   "{NO_ANSWER_MESSAGE}"
4. Use clear business-friendly language.
5. Mention source file names only in the Sources section.
6. If the question is about a pipeline failure, include the failing model, root cause, impact, and recommended action.
7. If the question is about a metric or column, include definition, formula if available, owner if available, and source files.

Output format:

Answer:
<direct answer>

Business Impact:
<impact if applicable, otherwise write N/A>

Recommended Action:
<recommended action if applicable, otherwise write N/A>

Sources:
<bullet list of source file names used>

User Question:
{question}

Retrieved Context:
{context}
"""


def call_ollama(prompt: str) -> str:
    """Call Ollama through the local HTTP API."""
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0},
    }

    response = requests.post(OLLAMA_URL, json=payload, timeout=120)
    response.raise_for_status()
    result = response.json()
    return result.get("response", "No response generated.")


def build_explanation(question: str, sources: List[dict], max_distance: float) -> List[str]:
    """Explain the RAG workflow in plain English for the UI."""
    source_names = sorted({source.get("source_file", "unknown") for source in sources})
    best_distance = min([source.get("distance", 999) for source in sources], default=999)

    return [
        f"The user asked: '{question}'.",
        "The app converted the question into an embedding using Sentence Transformers.",
        "ChromaDB compared that embedding against stored document chunk embeddings.",
        f"The top retrieved chunks came from: {', '.join(source_names) if source_names else 'no sources'}.",
        f"The best vector distance was {best_distance}. The no-answer threshold is {max_distance}.",
        "Retrieved chunks were inserted into a grounded prompt.",
        f"Ollama generated the final answer using the local model: {OLLAMA_MODEL}.",
        "The UI displayed answer, source files, chunk IDs, similarity scores, and retrieved text.",
    ]


def generate_rag_response(question: str, top_k: int = 5, max_distance: float = MAX_ACCEPTABLE_DISTANCE) -> Dict:
    """Run the complete RAG pipeline and return answer plus retrieval evidence."""
    retrieved = retrieve_context(question, top_k=top_k)

    chunks = retrieved["documents"]
    distances = retrieved["distances"]
    sources = retrieved["sources"]

    if not chunks:
        return {
            "answer": "No documents found. Please click 'Re-index Knowledge Base' or run `python -m src.ingest` first.",
            "sources": [],
            "retrieved_chunks": [],
            "distances": [],
            "explanation": build_explanation(question, [], max_distance),
            "used_no_answer": True,
        }

    best_distance = min(distances) if distances else 999

    if best_distance > max_distance:
        return {
            "answer": NO_ANSWER_MESSAGE,
            "sources": sources,
            "retrieved_chunks": chunks,
            "distances": distances,
            "explanation": build_explanation(question, sources, max_distance),
            "used_no_answer": True,
        }

    prompt = build_prompt(question, chunks, sources)

    try:
        answer = call_ollama(prompt)
    except requests.exceptions.ConnectionError:
        answer = (
            "Could not connect to Ollama. Make sure Ollama is installed and running.\n\n"
            "Run:\n"
            "1. `ollama pull llama3`\n"
            "2. `ollama serve`"
        )
    except requests.exceptions.Timeout:
        answer = "The local Ollama model took too long to respond. Try a shorter question or a smaller model."
    except Exception as exc:
        answer = f"Error while generating answer: {exc}"

    return {
        "answer": answer,
        "sources": sources,
        "retrieved_chunks": chunks,
        "distances": distances,
        "explanation": build_explanation(question, sources, max_distance),
        "used_no_answer": False,
    }


# Backward-compatible function used by the earlier app.
def generate_answer(question: str, chunks: List[str], metadatas: List[dict]) -> str:
    sources = []
    for metadata in metadatas:
        sources.append(
            {
                "source_file": metadata.get("source", "unknown"),
                "document_type": metadata.get("document_type", "unknown"),
                "chunk_id": metadata.get("chunk_index", "unknown"),
                "similarity_score": "not calculated",
            }
        )

    prompt = build_prompt(question, chunks, sources)

    try:
        return call_ollama(prompt)
    except Exception as exc:
        return f"Error while generating answer: {exc}"
