# Internal Data Knowledge RAG Assistant

I built this project as a practical Retrieval-Augmented Generation (RAG) assistant for internal data teams. Unlike a generic chatbot, this project focuses on real data knowledge sources such as dbt models, SQL queries, data dictionaries, pipeline logs, metric definitions, SOPs, and internal documentation which allows a user to ask natural-language questions about internal data assets and get source-grounded answers using a local LLM through Ollama + Llama 3.

## Background

In many data teams, important business and technical knowledge is scattered across SQL files, dbt models, logs, dashboards, documentation, and data dictionaries. Analysts and engineers often spend time searching across multiple places to understand metric definitions, pipeline failures, model dependencies, or business logic. This project solves that problem by building a local RAG assistant that can:

## Project Demonstrates

This project demonstrates a complete RAG implementation, including:

- document ingestion from multiple file types,
- text cleaning and preprocessing,
- chunking with overlap,
- embedding generation using Sentence Transformers,
- vector storage using ChromaDB,
- semantic search and Top-K retrieval,
- retrieval distance and similarity scoring,
- no-answer thresholding to reduce hallucination,
- prompt construction using retrieved context,
- local answer generation using Ollama and Llama 3,
- source-grounded answers with retrieved chunks,
- Streamlit UI for business users,
- knowledge-base re-indexing from the UI.

---

## Business Use Case

This assistant is designed for a data or analytics engineering team that needs quick answers from internal knowledge assets.

Example use cases:

- understanding how a business metric is calculated,
- checking where a column or field is defined,
- identifying why a pipeline failed,
- finding which model or dashboard depends on a failed pipeline,
- reviewing SOPs for pipeline troubleshooting,
- helping new analysts understand data assets faster.

---

## Tech Stack

| Area | Tools Used |
|---|---|
| Programming | Python |
| UI | Streamlit |
| LLM | Llama 3 through Ollama |
| Embeddings | Sentence Transformers |
| Vector Database | ChromaDB |
| Data Handling | Pandas |
| Knowledge Sources | SQL, CSV, TXT, Markdown |

---

## Project Architecture

```text
Raw Internal Documents
(dbt models, SQL files, CSV dictionaries, logs, docs)
        ↓
Document Loader
        ↓
Text Cleaning and Preprocessing
        ↓
Chunking with Overlap
        ↓
Sentence Transformer Embeddings
        ↓
ChromaDB Vector Store
        ↓
User Question from Streamlit UI
        ↓
Question Embedding
        ↓
Top-K Semantic Retrieval
        ↓
Distance Threshold Check
        ↓
Prompt Construction with Retrieved Context
        ↓
Ollama + Llama 3 Answer Generation
        ↓
Final Answer + Source Chunks + Similarity Scores
```

---

## RAG Workflow

### 1. Document Ingestion

The project reads files from the `data/` folder. The knowledge base includes multiple types of internal data-team documents:

```text
data/
├── dbt_models/
├── sql_queries/
├── data_dictionaries/
├── pipeline_logs/
└── docs/
```

Supported file types:

```text
.txt
.md
.sql
.csv
```

Each file is loaded, cleaned, and converted into text that can be used by the RAG pipeline.

---

### 2. Chunking

Large documents are split into smaller overlapping chunks.

Chunking helps the retriever find focused and relevant context instead of sending an entire document to the model.

Default chunk settings:

```text
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150
```

The overlap helps preserve context between neighboring chunks.

---

### 3. Embedding Generation

Each chunk is converted into a numerical vector using Sentence Transformers.

Default embedding model:

```text
sentence-transformers/all-MiniLM-L6-v2
```

These embeddings allow the system to compare the meaning of a user question with the meaning of each document chunk.

---

### 4. Vector Storage with ChromaDB

The chunk embeddings and metadata are stored in ChromaDB.

Each stored chunk contains metadata such as:

- source file,
- source path,
- document type,
- chunk ID.

The `chroma_db/` folder is generated locally after indexing and should not be pushed to GitHub.

---

### 5. User Question Embedding

When the user asks a question in the Streamlit UI, the question is also converted into an embedding using the same embedding model.

The system then searches ChromaDB to find the most semantically similar chunks.

---

### 6. Top-K Retrieval

The app retrieves the top matching chunks from ChromaDB.

The user can control the number of chunks from the sidebar using:

```text
Top-K chunks to retrieve
```

Default value:

```text
DEFAULT_TOP_K = 5
```

A higher Top-K gives the LLM more context, but it can also introduce noise. A lower Top-K keeps the context focused, but it may miss supporting details.

---

### 7. No-Answer Threshold

The app uses a distance threshold to reduce hallucination.

In ChromaDB retrieval:

```text
Lower distance = better match
Higher distance = weaker match
```

If the best retrieved chunk is above the allowed threshold, the app refuses to answer and returns a safe response instead of making up information.

Default threshold:

```text
MAX_ACCEPTABLE_DISTANCE = 1.25
```

This makes the project stronger because it shows that the RAG system does not blindly answer every question.

---

### 8. Prompt Construction

After retrieval, the app builds a prompt using:

- the user question,
- the retrieved source chunks,
- instructions to answer only from the provided context.

This step grounds the LLM response in the retrieved internal documents.

---

### 9. Local LLM Generation with Ollama and Llama 3

The final prompt is sent to a local Llama 3 model through Ollama.

Default model:

```text
llama3
```

This keeps the project local and avoids sending internal data to an external API.

---

### 10. Source-Grounded Output

After generation, the app displays:

- the final business answer,
- retrieved source files,
- document type,
- chunk ID,
- vector distance,
- similarity score,
- retrieved source chunks.

This makes the answer explainable and traceable.

---

## Streamlit UI

The UI is intentionally simple and focused.

Main user-facing text:

```text
Ask natural-language questions about internal data assets and get source-grounded answers
```

The sidebar includes:

- Ollama model name,
- Top-K chunks slider,
- no-answer distance threshold slider,
- Re-index Knowledge Base button.

After a question is submitted, the app shows:

- business answer,
- sources and retrieval confidence,
- retrieved source chunks.

---

## Key Features

### Local RAG Assistant

The project runs locally using Ollama and Llama 3, which makes it suitable for internal knowledge-base use cases.

### Multi-Source Document Ingestion

The system can ingest dbt models, SQL files, data dictionaries, pipeline logs, and internal documentation.

### ChromaDB Vector Search

ChromaDB stores document embeddings and performs semantic similarity search.

### Similarity and Distance Scores

The UI displays retrieval confidence so users can understand how strongly the retrieved chunks matched the question.

### No-Answer Handling

The assistant avoids hallucination by refusing to answer when retrieved context is weak.

### Re-Index Knowledge Base

Users can rebuild the vector database from the Streamlit UI when documents change.

### Source Transparency

The app shows exactly which chunks were used to generate the answer.

---

## Project Structure

```text
internal-data-rag-assistant/
├── app.py
├── requirements.txt
├── README.md
├── SAMPLE_QUESTIONS.md
├── project-archi.txt
├── project-flow.txt
├── .env.example
├── .gitignore
│
├── data/
│   ├── dbt_models/
│   │   ├── dim_customers.sql
│   │   ├── fct_orders.sql
│   │   └── int_payments.sql
│   │
│   ├── sql_queries/
│   │   ├── churn_query.sql
│   │   └── revenue_analysis.sql
│   │
│   ├── data_dictionaries/
│   │   ├── customers_dictionary.csv
│   │   └── orders_dictionary.csv
│   │
│   ├── pipeline_logs/
│   │   ├── airflow_log_2026_06_10.txt
│   │   └── dbt_run_log_2026_06_10.txt
│   │
│   └── docs/
│       ├── confluence_notes.txt
│       ├── data_platform_sop.txt
│       └── metric_definitions.txt
│
└── src/
    ├── __init__.py
    ├── config.py
    ├── ingest.py
    ├── retrieve.py
    ├── generate.py
    └── utils.py









## Final Summary

This project is a complete local RAG implementation for internal data knowledge search. It combines document ingestion, chunking, embeddings, ChromaDB retrieval, no-answer thresholding, prompt construction, local Llama 3 generation, and source-grounded answer display inside a simple Streamlit UI.
