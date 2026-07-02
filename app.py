from __future__ import annotations

import pandas as pd
import streamlit as st

from src.config import DEFAULT_TOP_K, MAX_ACCEPTABLE_DISTANCE, OLLAMA_MODEL
from src.generate import generate_rag_response
from src.ingest import rebuild_vector_database

st.set_page_config(
    page_title="RAG Assistant",
    layout="wide",
)

st.title("RAG Assistant")
st.caption("Knowledge base is dbt models, SQL, data dictionaries, pipeline logs, and internal docs")

st.write("Ask natural-language questions about internal data assets and get source-grounded answers")

with st.sidebar:
    st.header("RAG Controls")
    st.write(f"**Ollama model:** `{OLLAMA_MODEL}`")

    top_k = st.slider(
        "Top-K chunks to retrieve",
        min_value=3,
        max_value=10,
        value=DEFAULT_TOP_K,
        help="Higher values give the LLM more context, but may add noise.",
    )

    max_distance = st.slider(
        "No-answer distance threshold",
        min_value=0.50,
        max_value=2.00,
        value=float(MAX_ACCEPTABLE_DISTANCE),
        step=0.05,
        help="Lower = stricter. If the best match is worse than this, the app refuses to answer.",
    )

    if st.button("Re-index Knowledge Base", use_container_width=True):
        with st.spinner("Reading files, chunking text, embedding chunks, and rebuilding ChromaDB..."):
            result = rebuild_vector_database()

        st.success(
            f"Indexed {result['files_indexed']} files and "
            f"{result['chunks_indexed']} chunks."
        )


question = st.text_input(
    "Ask a question:",
    placeholder="Example: Why did the orders pipeline fail?",
)

ask_button = st.button("Get Business Answer", type="primary", use_container_width=True)

if ask_button:
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Retrieving context and generating answer..."):
            result = generate_rag_response(
                question=question,
                top_k=top_k,
                max_distance=max_distance,
            )

        st.subheader("Business Answer")
        if result.get("used_no_answer"):
            st.info(result["answer"])
        else:
            st.write(result["answer"])

        st.subheader("Sources and Retrieval Confidence")
        if result["sources"]:
            sources_df = pd.DataFrame(result["sources"])
            st.dataframe(sources_df, use_container_width=True, hide_index=True)
        else:
            st.warning("No sources were retrieved.")

        st.subheader("Retrieved Source Chunks")
        if result["retrieved_chunks"]:
            for i, chunk in enumerate(result["retrieved_chunks"]):
                source = result["sources"][i]
                with st.expander(
                    f"Chunk {i + 1}: {source['source_file']} | "
                    f"Type: {source['document_type']} | "
                    f"Similarity: {source['similarity_score']} | "
                    f"Distance: {source['distance']}"
                ):
                    st.markdown(f"**Path:** `{source['source_path']}`")
                    st.markdown(f"**Chunk ID:** `{source['chunk_id']}`")
                    st.write(chunk)
        else:
            st.info("No chunks to display.")

st.divider()
st.markdown(
    "**RAG flow:** User question → Embedding → ChromaDB search → Top chunks → "
    "Threshold check → Prompt → Ollama answer → Sources and confidence scores"
)
