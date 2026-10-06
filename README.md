# Bank Compliance Intelligence — Grounded RAG

A production-oriented **bank compliance document intelligence system** that helps risk and compliance teams answer questions against regulatory circulars, audit reports, internal policies, and regulatory updates without manually reading through conflicting historical documents.

The system is designed around a grounded RAG workflow:

```text
PDF / DOCX / Compliance Documents
            ↓
Document Ingestion
            ↓
Text Extraction + Cleaning
            ↓
Token-aware Chunking
            ↓
Compliance Metadata
            ↓
Local Embeddings (Ollama)
            ↓
Qdrant Vector Database
            ↓
Hybrid Retrieval
            ↓
Re-ranking
            ↓
Rule / Version Resolution
            ↓
Grounded LLM Generation (Ollama)
            ↓
Citation Validation + Guardrails
            ↓
FastAPI
            ↓
React Frontend
```

---

## Problem Statement

A large bank maintains compliance circulars, internal audit reports, policies, and regulatory updates. These documents can contain multiple versions of the same rule, overlapping guidance, and conflicting historical requirements.

Risk officers need to answer questions such as:

> **"Which rule currently governs this transaction?"**

The goal of this project is to provide a traceable answer based on the most relevant compliance evidence while preserving the source document, version, effective date, and citation information.

---

# Key Features

## 1. Production Document Ingestion

Supports:

- PDF
- DOCX

The ingestion pipeline performs:

```text
Upload
  ↓
File validation
  ↓
Compliance metadata validation
  ↓
SHA-256 content hashing
  ↓
Duplicate / concurrent processing protection
  ↓
Text extraction
  ↓
Text cleaning
  ↓
Token-aware chunking
  ↓
Embedding
  ↓
Qdrant indexing
```

Compliance metadata includes fields such as:

- `document_id`
- `document_type`
- `title`
- `issue_date`
- `effective_date`
- `status`
- `version`

Physical file type (`pdf` / `docx`) is not treated as a compliance document type.

---

## 2. Local / Zero-API-Cost AI Inference

The production inference path uses **Ollama** rather than a paid hosted model API.

Default models:

```text
Chat model:
gemma3:4b

Embedding model:
nomic-embed-text
```

This provides:

- local inference;
- no per-request model API charges;
- configurable models;
- the same embedding model for indexing and retrieval;
- explicit model readiness checks.

### Ollama configuration

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_CHAT_MODEL=gemma3:4b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
OLLAMA_TIMEOUT_SECONDS=120
```

---

## 3. Qdrant Vector Search

Qdrant stores document chunk embeddings and source metadata.

The local Ollama deployment uses a dedicated collection:

```text
compliance_chunks_ollama
```

The system protects against incompatible embedding spaces by validating vector dimensions before indexing.

This is important when migrating from one embedding model to another.

### Qdrant configuration

```env
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=
QDRANT_COLLECTION=compliance_chunks_ollama
```

---

## 4. Hybrid Retrieval

The retrieval system combines:

```text
Semantic retrieval
        +
Keyword retrieval
        ↓
Candidate fusion
        ↓
Re-ranking
        ↓
Top-K evidence
```

This allows the system to handle both:

- semantically similar compliance language;
- exact regulatory terminology, identifiers, and phrases.

Metadata filtering is also supported.

---

## 5. Rule / Version Resolution

Compliance systems cannot simply retrieve the highest-scoring document.

The system preserves document metadata such as:

```text
status
version
issue_date
effective_date
document_type
document_id
```

This allows the RAG layer to reason about which rule applies at a particular point in time.

Example:

```text
Circular v1
Effective: 2026-01-01
Rule: Manager approval required

Circular v2
Effective: 2026-04-01
Rule: Regional-head approval required
```

The system can distinguish between:

```text
"What rule applies today?"
```

and:

```text
"What rule applied on 2026-02-01?"
```

---

## 6. Grounded Answer Generation

The LLM is not treated as the source of truth.

The intended flow is:

```text
User question
      ↓
Retrieval
      ↓
Re-ranking
      ↓
Rule/version resolution
      ↓
Evidence assembly
      ↓
LLM generation
      ↓
Citation validation
```

The answer is generated from retrieved compliance evidence.

When there is insufficient evidence, the system returns an explicit insufficient-evidence response rather than inventing a rule.

---

## 7. Citation and Guardrails

Generated responses retain evidence references.

A response can include:

```text
Answer
Evidence ID
Chunk ID
Document ID
Source text
Page
Document type
Version
Effective date
Status
```

This makes the answer auditable and allows a reviewer to trace the output back to the source document.

---

## 8. Production Ingestion Lifecycle

The ingestion manifest is backed by SQLite rather than a simple JSON read/write flow.

It supports:

- transactional claims;
- duplicate detection;
- concurrent upload protection;
- stale-processing recovery;
- failed-state persistence;
- safe retry;
- source integrity verification.

Retry flow:

```text
failed / stale
      ↓
verify stored source
      ↓
verify SHA-256
      ↓
reclaim processing slot
      ↓
re-run ingestion
      ↓
re-index
      ↓
indexed
```

---

# Architecture

```text
                         ┌───────────────────────┐
                         │ PDF / DOCX Documents  │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │ Ingestion Service     │
                         │ Validation            │
                         │ Hashing               │
                         │ Lifecycle Manifest    │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │ Extraction + Cleaning │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │ Token-aware Chunking  │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │ Ollama Embeddings     │
                         │ nomic-embed-text      │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │ Qdrant                │
                         │ compliance_chunks_    │
                         │ ollama                │
                         └───────────┬───────────┘
                                     │
                         User Query │
                                     ▼
                         ┌───────────────────────┐
                         │ Hybrid Retrieval      │
                         └───────────┬───────────┘
                                     ▼
                         ┌───────────────────────┐
                         │ Re-ranking            │
                         └───────────┬───────────┘
                                     ▼
                         ┌───────────────────────┐
                         │ Rule / Version        │
                         │ Resolution             │
                         └───────────┬───────────┘
                                     ▼
                         ┌───────────────────────┐
                         │ Ollama LLM            │
                         │ gemma3:4b             │
                         └───────────┬───────────┘
                                     ▼
                         ┌───────────────────────┐
                         │ Citation Validation   │
                         │ + Guardrails          │
                         └───────────┬───────────┘
                                     ▼
                         ┌───────────────────────┐
                         │ FastAPI               │
                         └───────────┬───────────┘
                                     ▼
                         ┌───────────────────────┐
                         │ React / TypeScript UI │
                         └───────────────────────┘
```

---

# Project Structure

```text
.
├── app/
│   ├── api/
│   │   ├── middleware.py
│   │   ├── rag_routes.py
│   │   └── routes.py
│   │
│   ├── embeddings/
│   │   └── embedder.py
│   │
│   ├── generation/
│   │   ├── llm.py
│   │   ├── models.py
│   │   └── service.py
│   │
│   ├── ingestion/
│   │   ├── cleaner.py
│   │   ├── chunker.py
│   │   ├── loaders.py
│   │   ├── metadata.py
│   │   └── pipeline.py
│   │
│   ├── ollama/
│   │   └── client.py
│   │
│   ├── retrieval/
│   │   ├── filters.py
│   │   ├── hybrid.py
│   │   ├── models.py
│   │   ├── pipeline.py
│   │   ├── reranker.py
│   │   └── service.py
│   │
│   ├── schemas/
│   │   ├── document.py
│   │   └── rag.py
│   │
│   ├── services/
│   │   ├── ingestion_config.py
│   │   ├── ingestion_service.py
│   │   ├── manifest_service.py
│   │   └── rag_application.py
│   │
│   ├── validation/
│   │   └── document_validator.py
│   │
│   └── vectorstore/
│       ├── indexer.py
│       └── qdrant.py
│
├── data/
│   ├── raw/
│   └── processed/
│
├── scripts/
│
├── tests/
│
├── .env.example
├── requirements.txt
└── README.md
```

---

# Technology Stack

## Backend

- Python
- FastAPI
- Pydantic
- Uvicorn

## Document Processing

- PyMuPDF
- python-docx
- tiktoken

## AI / RAG

- Ollama
- `gemma3:4b`
- `nomic-embed-text`

## Vector Database

- Qdrant

## Retrieval

- semantic retrieval
- keyword retrieval
- hybrid retrieval
- result re-ranking

## Frontend

- React
- TypeScript
- Vite
- React Router
- Tailwind CSS
- React Query
- Zustand
- Recharts

The React frontend is being integrated with the FastAPI backend as the application UI layer.

---

# Environment Setup

## 1. Clone the repository

```powershell
git clone <repository-url>
cd S67_0926_Team1_Large-bank-conflicting-documents
```

---

## 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

---

## 3. Configure environment variables

Copy:

```text
.env.example
```

to:

```text
.env
```

Recommended local configuration:

```env
APP_NAME=Compliance RAG
DEBUG=False

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_CHAT_MODEL=gemma3:4b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
OLLAMA_TIMEOUT_SECONDS=120

QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=
QDRANT_COLLECTION=compliance_chunks_ollama

EMBEDDING_BATCH_SIZE=32
RAG_DEFAULT_TOP_K=5
RAG_MAX_TOP_K=10

CORS_ORIGINS=http://localhost:5173

MAX_UPLOAD_BYTES=26214400
INGESTION_MANIFEST_DB=data/ingestion_manifest.db
INGESTION_PROCESSING_TTL_SECONDS=1800
```

Never commit real secrets or `.env` files.

---

# Start Ollama

Install Ollama, then pull the project models:

```powershell
ollama pull gemma3:4b
ollama pull nomic-embed-text
```

Check installed models:

```powershell
ollama list
```

Check the Ollama API:

```powershell
Invoke-RestMethod http://localhost:11434/api/tags
```

---

# Start Qdrant

With Docker Desktop running:

```powershell
docker pull qdrant/qdrant
```

Start Qdrant:

```powershell
docker run -d `
  --name qdrant `
  -p 127.0.0.1:6333:6333 `
  -p 127.0.0.1:6334:6334 `
  qdrant/qdrant
```

Check:

```powershell
docker ps
```

Qdrant dashboard:

```text
http://localhost:6333/dashboard
```

If the container already exists:

```powershell
docker start qdrant
```

---

# Start FastAPI

From the project root:

```powershell
uvicorn app.main:app --reload
```

API:

```text
http://localhost:8000
```

Swagger UI:

```text
http://localhost:8000/docs
```

---

# Verify the Runtime

## Basic health

```http
GET /api/health
```

Expected:

```json
{
  "status": "ok"
}
```

## Ingestion readiness

```http
GET /api/ready
```

## RAG readiness

```http
GET /api/rag/ready
```

Expected:

```json
{
  "status": "ready"
}
```

The RAG readiness endpoint verifies the local inference stack rather than only checking that configuration values exist.

---

# Core API

## Upload a compliance document

```http
POST /api/upload
```

Multipart fields include:

```text
file
document_type
title
issue_date
effective_date
status
version
document_id
```

Supported compliance document types include:

```text
circular
audit_report
regulatory_update
policy
```

---

## Check document status

```http
GET /api/documents/{document_id}/status
```

Returns operational information such as:

```json
{
  "document_id": "CIRC-2026-001",
  "filename": "circular.pdf",
  "status": "indexed",
  "chunk_count": 12,
  "indexed_count": 12,
  "version": "2",
  "updated_at": "2026-10-06T..."
}
```

---

## Query the compliance RAG system

```http
POST /api/query
```

Example:

```json
{
  "question": "What approval is currently required for this transaction?",
  "top_k": 5
}
```

Historical query:

```json
{
  "question": "What rule applied to this transaction?",
  "top_k": 5,
  "as_of_date": "2026-02-01"
}
```

Optional retrieval controls include metadata such as:

```text
document_type
status
document_id
version
effective_date
```

The response includes:

```text
query
answer
used_chunk_ids
evidence
```

---

# Example RAG Workflow

Suppose the corpus contains:

```text
Circular v1
Effective: 2026-01-01
Requirement: Manager approval

Circular v2
Effective: 2026-04-01
Requirement: Regional-head approval
Status: active
```

Query:

```text
What approval is currently required?
```

The system should:

```text
1. Embed the question
2. Retrieve relevant chunks
3. Combine semantic + keyword results
4. Re-rank evidence
5. Resolve the applicable rule/version
6. Generate an answer from the selected evidence
7. Validate the citations
8. Return the answer + evidence
```

Historical query:

```text
What approval was required on 2026-02-01?
```

The rule-resolution layer should consider the effective dates rather than simply choosing the newest document.

---

# Testing

Run the complete test suite:

```powershell
python -m pytest -q
```

Compile-check the application and tests:

```powershell
python -m compileall -q app tests
```

A production-ready branch should reach:

```text
0 failed
```

before demonstration or merge.

The test suite covers areas including:

- document ingestion;
- metadata validation;
- manifest lifecycle;
- duplicate protection;
- stale processing;
- embeddings;
- Ollama;
- Qdrant behavior;
- retrieval;
- hybrid retrieval;
- reranking;
- RAG generation;
- rule resolution;
- citation validation;
- API behavior.

---

# Important Migration Note

The project previously used a different embedding provider.

The current local-Ollama configuration uses:

```text
nomic-embed-text
```

with:

```text
compliance_chunks_ollama
```

Do not mix vectors created by incompatible embedding models in the same collection.

When changing embedding models:

```text
Old embedding collection
        ↓
do not mix vectors
        ↓
New embedding model
        ↓
new/re-indexed Qdrant collection
```

---

# Production Safety Principles

The system is designed around several safety boundaries.

### Evidence before generation

The LLM generates from retrieved evidence instead of acting as the compliance database.

### Explicit insufficient evidence

When the retrieval layer cannot provide sufficient evidence, the system should return an insufficient-evidence response rather than inventing a rule.

### Source traceability

Every returned evidence item retains source metadata.

### Embedding compatibility

Qdrant vector dimensions are checked before indexing.

### Duplicate protection

The ingestion manifest prevents the same document from being indexed concurrently multiple times.

### Source integrity

Retry operations verify the original file using SHA-256.

### Safe API errors

Infrastructure details and raw internal failures are not returned directly to API clients.

### Restricted CORS

Frontend access is limited to configured origins.

---

# Mentor Demo Flow

A strong demonstration should use a deliberately conflicting compliance corpus.

### Step 1 — Show the architecture

Explain:

```text
Ingestion
→ Embeddings
→ Qdrant
→ Hybrid Retrieval
→ Re-ranking
→ Rule Resolution
→ Ollama
→ Citation Validation
```

### Step 2 — Upload documents

Upload two versions of the same rule with different effective dates.

### Step 3 — Ask a current-rule question

Example:

```text
Which rule currently governs this transaction?
```

### Step 4 — Show evidence

Point out:

- document ID;
- version;
- effective date;
- page;
- source chunk;
- evidence ID.

### Step 5 — Ask a historical question

Change the `as_of_date`.

Demonstrate that the answer can change because a different rule was effective at that time.

### Step 6 — Demonstrate insufficient evidence

Ask about a rule that is not present in the corpus.

The system should refuse to invent a compliance requirement.

---

# Development Principles

The project is organized so that provider-specific concerns remain isolated.

For example:

```text
OllamaClient
     ↓
OllamaEmbedder
     ↓
SemanticRetriever
```

and:

```text
OllamaClient
     ↓
OllamaLLMProvider
     ↓
RagService
```

This keeps the higher-level RAG pipeline independent of the specific model provider.

---

# Current Project Status

The backend currently contains the major RAG building blocks:

- production ingestion;
- embeddings;
- Qdrant indexing;
- semantic retrieval;
- hybrid retrieval;
- reranking;
- rule/version resolution;
- grounded generation;
- citation validation;
- FastAPI query API;
- local Ollama inference;
- ingestion lifecycle hardening.

The React frontend has a dashboard/application shell and an Active Rules interface under the frontend development branches. Final production integration should connect those screens to the FastAPI endpoints rather than relying on static mock data.

---

# Roadmap

## Backend

- complete final ingestion lifecycle integration;
- finalize regression-free test suite;
- continue evaluation/observability improvements;
- improve production deployment configuration.

## Frontend

- connect dashboard to backend data;
- connect query interface to `/api/query`;
- display evidence and citations;
- connect Active Rules to real compliance metadata;
- add loading/error/empty states.

## Evaluation

Future evaluation can measure:

- retrieval relevance;
- evidence coverage;
- citation correctness;
- answer grounding;
- latency;
- failure behavior.

---

# Troubleshooting

## Ollama not ready

Check:

```powershell
ollama list
```

and:

```powershell
Invoke-RestMethod http://localhost:11434/api/tags
```

Then make sure:

```text
gemma3:4b
nomic-embed-text
```

are installed.

## Qdrant not ready

Check:

```powershell
docker ps
```

and:

```text
http://localhost:6333
```

Start an existing container with:

```powershell
docker start qdrant
```

## RAG not ready

Check:

```http
GET /api/rag/ready
```

Then verify:

1. Ollama is running.
2. Required Ollama models are installed.
3. Qdrant is running.
4. `.env` points to the correct URLs.
5. `compliance_chunks_ollama` has been indexed with the current embedding model.

## Tests fail during collection

Check for stale provider imports:

```powershell
git grep -n "OpenAIEmbedder"
```

The current production embedding path should use:

```text
OllamaEmbedder
```

---

# License / Academic Use

This project is developed as an academic software-engineering / data-product project.

Replace this section with the final institution or team licensing details before public release.

---

# Team Responsibilities

The implementation has been developed as a multi-contributor project with responsibilities across:

- ingestion and production data quality;
- analytics and RAG logic;
- frontend/dashboard integration.

For the final submission, add the team's names, GitHub handles, and contribution summary here.

