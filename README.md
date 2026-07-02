# Internal Data Knowledge RAG Assistant

I built this project as a practical Retrieval-Augmented Generation (RAG) assistant for internal data teams. Unlike a generic chatbot, this project focuses on real data knowledge sources such as dbt models, SQL queries, data dictionaries, pipeline logs, metric definitions, SOPs, and internal documentation which allows a user to ask natural-language questions about internal data assets and get source-grounded answers using a local LLM through Ollama + Llama 3.

## Background

In many data teams, important business and technical knowledge is scattered across SQL files, dbt models, logs, dashboards, documentation, and data dictionaries. Analysts and engineers often spend time searching across multiple places to understand metric definitions, pipeline failures, model dependencies, or business logic. This project solves that problem by building a local RAG assistant that provides quick answers from internal knowledge assets.

## Project Demonstrates

This project demonstrates a complete RAG implementation which includes:
- ingest internal data documents,
- split them into searchable chunks,
- convert chunks into embeddings,
- store them in a vector database,
- retrieve the most relevant context for a user question,
- generate an answer using Llama 3,
- show the exact source chunks used for the answer.

```text
Document Loading
        ↓
Chunking with Overlap
        ↓
Embeddings with Sentence Transformer 
        ↓
Vector Store in ChromaDB 
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
   Final Response 
```

## Tech Stack

- **Knowledge Sources:** SQL, CSV, TXT, Markdown
- **Programming:** Python, Pandas
- **UI:** Streamlit
- **LLM:**  Llama 3 through Ollama
- **Embeddings:** Sentence Transformers
- **Vector Database:** ChromaDB


## RAG Workflow

### 1. Document Ingestion

The project reads files from the `data/` folder. The knowledge base includes multiple types of internal data-team documents (.txt, .md, .sql, .csv). Each file is loaded, cleaned, and converted into text that can be used by the RAG pipeline.

### 2. Chunking

Large documents are split into smaller overlapping chunks. Chunking helps the retriever find focused and relevant context instead of sending an entire document to the model. The overlap helps preserve context between neighboring chunks.

**Chunk settings:** CHUNK_SIZE = 800,  CHUNK_OVERLAP = 150


### 3. Embedding Generation

Each chunk is converted into a numerical vector using Sentence Transformers. These embeddings allow the system to compare the meaning of a user question with the meaning of each document chunk.

**Embedding model:** sentence-transformers/all-MiniLM-L6-v2

### 4. Vector Storage with ChromaDB

The chunk embeddings and metadata are stored in ChromaDB. The `chroma_db/` folder is generated locally after indexing.

Each stored chunk contains metadata such as:
- source file,
- source path,
- document type,
- chunk ID.

### 5. User Question Embedding

The question user asks in Streamlit UI is also converted into an embedding using the same embedding model. The system then searches ChromaDB to find the most semantically similar chunks.


### 6. Top-K Retrieval

The app retrieves the top matching chunks from ChromaDB. The user can control the number of chunks to consider for the response from the sidebar in hte UI. A higher Top-K gives the LLM more context, but it can also introduce noise. A lower Top-K keeps the context focused, but it may miss supporting details.

### 7. Distance Threshold

The app uses a distance threshold to reduce hallucination.

In ChromaDB retrieval:
- Lower distance = better match
- Higher distance = weaker match

If the best retrieved chunk is above the allowed threshold, the app refuses to answer and returns a safe response instead of making up information. This makes the project stronger because it shows that the RAG system does not blindly answer every question.

### 8. Response Construction

After retrieval, the app builds a response prompt using:
- the user question,
- the retrieved source chunks,
- instructions to answer only from the provided context.

This step grounds the LLM response in the retrieved internal documents.


### 9. Final Response
The final prompt is sent to a local Llama3 model through Ollama. This keeps the project local and avoids sending internal data to an external API.

After repsonse generation, the app displays the following 
- the final business answer,
- retrieved source files,
- document type,
- chunk ID,
- vector distance,
- similarity score,
- retrieved source chunks.

This makes the answer explainable and traceable.

### 10. Re-Index Knowledge Base

Users can rebuild the vector database from the Streamlit UI when documents change.

## Streamlit UI

image

output images










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


This project is a complete local RAG implementation for internal data knowledge search. It combines document ingestion, chunking, embeddings, ChromaDB retrieval, no-answer thresholding, prompt construction, local Llama 3 generation, and source-grounded answer display inside a simple Streamlit UI.
