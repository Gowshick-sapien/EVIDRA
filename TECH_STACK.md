# Fact Knowledge Layer -- Tech Stack Decisions

---

## 1. Overview

This document details every technology decision for the Fact Knowledge Layer project, including the rationale, alternatives considered, and how each choice maps to the system architecture. The guiding principle is:

> Build a clean, structured, explainable prototype -- not an overengineered production system.

The tech stack is deliberately conservative. Every tool earns its place by directly serving the evidence-centric architecture. No technology is included for novelty.

---

## 2. Language

| Decision | **Python** |
|----------|-----------|
| Version | 3.11+ |
| Rationale | Strongest ecosystem for PDF processing, LLM integration, data manipulation, and scientific computing. Every major library in the pipeline (PDF parsers, LLM clients, embedding models, web frameworks, orchestration) has first-class Python support. |
| Alternatives Considered | None seriously. The problem domain (PDF parsing, NLP, LLM orchestration) is overwhelmingly Python-native. |

---

## 3. LLM Runtime

| Decision | **Ollama (local)** |
|----------|-------------------|
| Rationale | Avoids dependency on proprietary APIs. Makes the reasoning pipeline fully reproducible, cost-controlled, and runnable offline. The evaluator can run the system without needing API keys or paid accounts. |
| Assignment Alignment | The assignment states: "Keep credentials out of the repository. If the project requires a paid service, include enough sample output." Using a local LLM eliminates this concern entirely. |
| Trade-off | Local models are weaker than commercial APIs (GPT-4, Claude) at complex financial language, nuanced negation, and long-context reasoning. The architecture compensates by making LLM failure recoverable -- uncertain outputs become `UNRESOLVED`, not wrong verdicts. |

### Model Selection

| Decision | **Qwen / Llama (via Ollama)** |
|----------|------------------------------|
| Rationale | Both are strong open-weight models available through Ollama. The architecture is model-agnostic -- agents call a `ReasoningService` abstraction, not Ollama directly. The model can be swapped without code changes. |
| Recommendation | Start with a model that supports structured JSON output well (Qwen2.5 or Llama 3.1 at 7B/8B parameter range for feasible local inference). |
| Scaling Path | The `LLMProvider` abstraction allows future swap to commercial APIs or larger models without architectural changes. |

### Provider Abstraction

```
LLMProvider
   |
   +-- OllamaProvider
   |     +-- Qwen
   |     +-- Llama
   |
   +-- Future provider (OpenAI, Anthropic, etc.)
```

Agents call:

```
ReasoningService.extract()
ReasoningService.verify()
ReasoningService.reconcile()
ReasoningService.challenge()
```

They never know what model or provider is behind the interface.

---

## 4. Embedding Model

| Decision | **Local embedding model (via Ollama or sentence-transformers)** |
|----------|---------------------------------------------------------------|
| Purpose | Entity canonicalization, attribute matching, semantic similarity for fact grouping. |
| Candidates | `nomic-embed-text` (via Ollama), `all-MiniLM-L6-v2` or `bge-small-en` (via sentence-transformers). |
| Rationale | Must run locally to maintain the zero-external-dependency principle. Embedding is used for candidate matching (blocking), not as the final arbiter -- the LLM or deterministic logic makes the decision. |
| Trade-off | Local embeddings are less capable than commercial embedding APIs, but for the blocking/candidate-generation role, they are sufficient. |

---

## 5. PDF Processing

### Primary Parser

| Decision | **pdfplumber** |
|----------|---------------|
| Purpose | Text extraction with positional information, table detection and extraction, page-level segmentation. |
| Rationale | Provides both text extraction and table extraction in a single library. Preserves character-level coordinates, which supports evidence anchoring (page, position). Handles most well-formed digital PDFs reliably. |
| Alternative | **PyMuPDF (fitz)** -- faster raw text extraction, better for large documents. Can be used alongside pdfplumber if performance becomes an issue. |

### Table Extraction

| Decision | **pdfplumber table extraction** (primary), with **camelot** as fallback |
|----------|------------------------------------------------------------------------|
| Purpose | Extract structured table data preserving headers, rows, columns, merged cells. |
| Rationale | pdfplumber handles most tables well. camelot (lattice/stream modes) can be used as a fallback for tables that pdfplumber misses. |
| Domain-Oriented Metadata | The table extractor enriches raw tables with semantic metadata: table title, reporting scope, currency, unit, period labels. This is implemented as a post-processing step, not a parser feature. |

### OCR (Conditional)

| Decision | **Not implemented by default; Tesseract as fallback if scanned pages detected** |
|----------|--------------------------------------------------------------------------------|
| Purpose | Handle scanned PDF pages that contain no extractable text. |
| Rationale | The starter PDFs are likely digital (text-native). OCR adds complexity and processing time. Include detection logic for scanned pages, but only invoke OCR when needed. |
| Candidate | Tesseract (via pytesseract). |

### Vision / Figure Interpretation (Conditional)

| Decision | **Not implemented in prototype; documented as Next Step** |
|----------|----------------------------------------------------------|
| Purpose | Interpret charts, diagrams, infographics. |
| Rationale | The prototype targets text and tables. If a chart is central to one of the four required demo cases, a minimal chart-extraction path can be added using the LLM's vision capabilities. Otherwise, figures are identified and preserved as evidence objects but not interpreted. |

---

## 6. Orchestration / Workflow Engine

| Decision | **LangGraph** |
|----------|--------------|
| Purpose | Orchestrate the multi-agent workflow with branching, parallel execution, state management, conditional routing, retries, structured outputs, and checkpoints. |
| Rationale | The pipeline has a predictable but non-trivial flow: parallel extraction, conditional conflict detection, branching into reconciliation vs. contradiction paths, adversarial challenge, policy evaluation. LangGraph handles this as a deterministic graph rather than an autonomous agent loop. |
| Why Not Raw Python | A hand-rolled orchestrator is feasible but would require reimplementing state management, retry logic, and conditional branching. LangGraph provides these out of the box. |
| Why Not LangChain Agents | LangChain's autonomous agent mode (ReAct, etc.) would let the LLM decide the next step. The architecture explicitly requires a **deterministic workflow** -- agents are workers, not decision-makers about the pipeline itself. |
| Why Not Prefect/Airflow | Those are task orchestrators for data pipelines, not reasoning workflows. They lack native support for LLM-specific patterns like structured output, prompt routing, and state-dependent branching. |

### Workflow Structure

```
DocumentState
    --> Parallel extraction (numerical, semantic, event)
    --> Evidence verification
    --> Context resolution
    --> Fact normalization and grouping
    --> Relationship detection
    --> [NO CONFLICT] --> CORROBORATED
    --> [CONFLICT] --> Hypothesis generation
        --> Specialist validators (numerical, temporal, semantic)
        --> Reconciliation agent
        --> Adversarial challenge
        --> Decision policy
        --> Final decision
```

---

## 7. API Framework

| Decision | **FastAPI** |
|----------|------------|
| Purpose | REST API for PDF upload, job management, and result inspection. |
| Rationale | Lightweight, async-native, automatic OpenAPI/Swagger documentation, Pydantic-based request/response validation. The auto-generated Swagger UI serves as the "simple UI" the assignment requests without building a frontend. |
| Endpoints | `POST /jobs`, `GET /jobs/{id}`, `GET /documents/{id}`, `GET /facts`, `GET /decisions/{id}` |
| Async Design | Processing is asynchronous. `POST /jobs` returns a job ID immediately; progress is polled via `GET /jobs/{id}`. This handles the potentially long Ollama inference time. |

---

## 8. CLI

| Decision | **Python click (or argparse)** |
|----------|-------------------------------|
| Purpose | Primary human debugging interface for the prototype. |
| Rationale | The CLI is the fastest way for the evaluator to run the system. No browser, no API client needed. |
| Usage | `python -m factlayer process ./documents/` |
| Output | Terminal summary + structured artifact directory. |

---

## 9. Storage

### Primary Storage

| Decision | **SQLite** |
|----------|-----------|
| Purpose | Structured storage for observations, facts, fact groups, decisions, and traces. |
| Rationale | Zero-configuration, single-file database. Fully portable -- the evaluator can inspect the database with any SQLite client. No external database server to install. Supports the relational queries needed for fact grouping and relationship detection. |
| Why Not PostgreSQL | Unnecessary infrastructure for a prototype. SQLite handles the expected data volume (3-10 PDFs, hundreds of facts) without issues. |
| Why Not MongoDB/NoSQL | The data model is inherently relational (observations belong to documents, facts belong to groups, decisions reference hypotheses and validators). A relational model is natural. |

### Artifact Storage

| Decision | **JSON / JSONL / Markdown files on disk** |
|----------|------------------------------------------|
| Purpose | Human-readable, inspectable output artifacts. |
| Rationale | Every run produces a structured artifact directory. JSON for machine-readable data (evidence, facts, decisions, traces). Markdown for human-readable reports (summary, contradiction report, unresolved report). JSONL for streaming/append-friendly formats (observations, events). |
| Structure | `runs/JOB-{id}/` with subdirectories for documents, observations, facts, decisions, reports, and traces. |

### Why Not a Graph Database

| Decision | **No graph database** |
|----------|----------------------|
| Rationale | The assignment explicitly states: "A graph database or visualization alone is not the solution." The Evidence Ledger (SQLite + JSON) is the system of record. A graph can exist as an optional **projection** (via NetworkX) but is never the decision mechanism. This distinction is a strength of the architecture. |

### Why Not a Vector Database

| Decision | **No dedicated vector database** |
|----------|--------------------------------|
| Rationale | Embeddings are used for candidate matching (blocking step), not as a core retrieval mechanism. For the prototype's data volume, in-memory cosine similarity over a small set of embedded attributes is sufficient. A persistent vector store (Chroma, FAISS, Pinecone) is unnecessary complexity. |
| Scaling Path | If the system grows to thousands of documents, a local FAISS index or Chroma instance would be the natural upgrade. Documented as Next Steps. |

---

## 10. Data Validation and Schema

| Decision | **Pydantic** |
|----------|-------------|
| Purpose | Strict schema enforcement for all structured objects: observations, fact candidates, evidence bundles, hypotheses, validator outputs, decisions, traces. |
| Rationale | Every agent produces structured output. Pydantic enforces the output contract at runtime. Malformed LLM outputs are caught immediately, triggering retry or failure rather than propagating bad data. |
| Integration | FastAPI uses Pydantic natively for request/response models. LangGraph state objects use Pydantic. LLM structured output can be validated against Pydantic models. |

---

## 11. Deterministic Validators (Pure Python)

The following computations are explicitly **not** delegated to the LLM:

| Validator | Implementation | Why Not LLM |
|-----------|---------------|-------------|
| **Unit normalization** | Python conversion tables (crore/lakh/million/billion, INR/USD) | Arithmetic must be exact. LLMs make unit conversion errors. |
| **Currency conversion** | Python rules / lookup | Deterministic and auditable. |
| **Numerical comparison** | Python: `abs(a - b)`, relative difference, materiality threshold | LLMs cannot reliably do arithmetic. |
| **Date normalization** | Python datetime: FY parsing, quarter mapping, period overlap detection | Date logic is rule-based. |
| **Arithmetic verification** | Python: verify extracted percentages against base values | Catches extraction errors the LLM would miss. |

These validators produce structured outputs that feed into the Decision Policy, which is itself a deterministic Python function.

---

## 12. Graph Visualization (Optional)

| Decision | **NetworkX** (if time permits) |
|----------|-------------------------------|
| Purpose | Lightweight in-memory graph for optional visualization of document-evidence-fact-decision relationships. |
| Rationale | Zero infrastructure. Can produce simple visualizations via matplotlib or export to formats readable by external tools. Not a decision mechanism -- purely a projection of the Evidence Ledger for inspection. |
| Priority | Low. Decision cards, traces, and Markdown reports are more valuable than graph visualization. |

---

## 13. Testing

| Decision | **pytest** |
|----------|-----------|
| Purpose | Unit tests for deterministic validators, integration tests for agent contracts, end-to-end pipeline tests. |
| Rationale | Standard Python testing framework. The architecture is designed for testability: stateless agents with defined input/output contracts, deterministic validators with known expected outputs, decision policies with explicit rule sets. |
| Key Test Targets | Unit normalization, numerical comparison, date parsing, decision policy logic, evidence verification contract, structured output validation. |

---

## 14. Technology-to-Architecture Mapping

| Architecture Layer | Technologies Used |
|-------------------|-------------------|
| **Layer 1: Document Evidence Preparation** | pdfplumber, PyMuPDF, (Tesseract if OCR needed), Python text processing |
| **Layer 2: Fact Construction** | Ollama (extraction, verification, context), Pydantic (schemas), embedding model (matching), Python (normalization) |
| **Layer 3: Fact Decision Engine** | LangGraph (orchestration), Ollama (reconciliation, challenge, hypothesis), Python (numerical/temporal/decision policy validators) |
| **Layer 4: Observability** | FastAPI (API), click (CLI), SQLite (storage), JSON/JSONL/Markdown (artifacts) |
| **Cross-cutting** | Pydantic (validation), pytest (testing), NetworkX (optional graph) |

---

## 15. What is Deliberately NOT in the Stack

| Technology | Reason for Exclusion |
|-----------|---------------------|
| React / Vue / Angular | No frontend needed. Swagger UI is sufficient. |
| Neo4j / ArangoDB | Graph is not the decision mechanism. |
| Kafka / RabbitMQ | No event streaming needed for a prototype. |
| Redis | No caching layer needed at this scale. |
| Docker / Kubernetes | Prototype runs locally. Containerization is a deployment concern, not a prototype concern. |
| Elasticsearch | No full-text search needed beyond what SQLite and embeddings provide. |
| Chroma / Pinecone / FAISS | Unnecessary for the prototype's data volume. Upgrade path documented. |
| OpenAI / Anthropic APIs | Avoids credential management, cost, and external dependency. |
| Celery / distributed task queues | LangGraph handles workflow orchestration. No need for distributed job processing. |

---

## 16. Dependency Summary

### Core Dependencies

```
# LLM and Orchestration
ollama                  # Local LLM runtime (system-level install)
langchain-ollama        # Ollama integration for LangGraph
langgraph               # Workflow orchestration
langchain-core          # Base abstractions

# PDF Processing
pdfplumber              # Text and table extraction
PyMuPDF                 # Fast text extraction, fallback

# API and CLI
fastapi                 # REST API
uvicorn                 # ASGI server
click                   # CLI framework

# Data and Validation
pydantic                # Schema validation
sqlite3                 # Built-in, no install needed

# Embeddings
sentence-transformers   # Local embedding models
  OR
ollama embeddings       # Via Ollama's embedding endpoint

# Utilities
python-dateutil         # Date parsing
```

### Optional Dependencies

```
# Table extraction fallback
camelot-py              # Alternative table extraction

# OCR (only if scanned pages detected)
pytesseract             # Tesseract OCR wrapper
Pillow                  # Image processing for OCR

# Visualization
networkx                # Graph projection
matplotlib              # Graph rendering

# Testing
pytest                  # Test framework
```

---

## 17. Key Engineering Decisions Summary

| Decision | Choice | Principle |
|----------|--------|-----------|
| LLM location | Local (Ollama) | Reproducibility, cost control, no credentials |
| LLM role | Semantic reasoning only | Deterministic code handles arithmetic, dates, rules |
| Agent autonomy | None -- orchestrator-controlled | Reproducibility, debuggability |
| Storage | SQLite + files | Simplicity, portability, inspectability |
| Graph database | Not used | Graph is projection, not intelligence |
| Vector database | Not used | Blocking step uses in-memory similarity |
| Frontend | Not built | Swagger + CLI + Markdown reports |
| Schema enforcement | Pydantic everywhere | Catch LLM output errors at boundary |
| Model coupling | Abstracted behind ReasoningService | Model-agnostic, future-proof |
| Workflow engine | LangGraph | Deterministic graph, not autonomous agents |

---

*End of Tech Stack Decisions Document*
