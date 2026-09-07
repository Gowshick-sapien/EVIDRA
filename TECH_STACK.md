# Fact Knowledge Layer -- Tech Stack Decisions

---

## 1. Overview

This document details every technology decision for the Fact Knowledge Layer prototype, including the concrete rationale, frozen selections, alternatives considered, and how each choice maps to the system architecture. The guiding principle is:

> Build a clean, structured, explainable prototype -- not an overengineered production system.

The tech stack is deliberately conservative, frozen, and free of ambiguous "A or B" choices. Every tool earns its place by directly serving the evidence-centric architecture. No technology is included for novelty.

---

## 2. Language: Python 3.11

| Decision | Python 3.11 (3.11+ compatible) |
|---|---|
| Target Runtime | Python 3.11 for submission reproducibility (3.12 supported for local development) |
| Rationale | Strongest ecosystem for PDF processing, local LLM integration, data manipulation, and structured validation. Every major library across the pipeline (PyMuPDF, pdfplumber, LangGraph, Pydantic, FastAPI, sentence-transformers) is Python-native. |
| Alternatives Considered | None. The domain is overwhelmingly Python-native. |

---

## 3. LLM Runtime and Model

### LLM Runtime: Ollama

| Decision | Ollama (Local) |
|---|---|
| Rationale | Locally runnable and cost-controlled. Avoids dependency on proprietary cloud APIs, credential management, and recurring API costs. The evaluator can run the system without API keys or paid accounts. |
| Reproducibility Note | Local LLM inference is cost-controlled and offline-capable, though not strictly bit-level deterministic across different GPU/CPU architectures. The pipeline protects against stochastic outputs through strict Pydantic validation and defensive fallback to UNRESOLVED. |
| Trade-off | Open-weight local models are less capable at zero-shot financial reasoning than frontier cloud models. The architecture compensates by scoping the LLM strictly to semantic reasoning, keeping arithmetic, date normalization, and policy decisions in deterministic code. |

### Model Selection: Qwen2.5 7B Instruct (Primary)

| Decision | Qwen2.5 7B Instruct (Default) / Qwen2.5 14B Instruct (Upgrade Path) |
|---|---|
| Primary Model | `qwen2.5:7b-instruct` |
| Upgrade Model | `qwen2.5:14b-instruct` (if host hardware supports higher VRAM/compute) |
| Why Qwen2.5 | Benchmark-leading performance on structured JSON generation, instruction following, constrained extraction, table comprehension, and multilingual tokens. It acts as a structured reasoning worker rather than a conversational chatbot. |
| Excluded Alternatives | Llama 3.1 8B was evaluated but exhibits higher JSON parse failure rates and weaker tabular reasoning in dense financial disclosures compared to Qwen2.5. |

### Provider Abstraction

All reasoning calls are mediated through an abstract `ReasoningService`. Agents do not interact with Ollama directly:

```text
                  ReasoningService
                         |
                 +-------+-------+
                 |               |
           OllamaProvider  MockProvider (Testing)
                 |
         Qwen2.5 Instruct
```

Specialist methods include:
- `ReasoningService.extract()`
- `ReasoningService.verify()`
- `ReasoningService.reconcile()`
- `ReasoningService.challenge()`

---

## 4. Embedding Model: sentence-transformers + BGE-Small

| Decision | sentence-transformers with BAAI/bge-small-en-v1.5 |
|---|---|
| Primary Model | `BAAI/bge-small-en-v1.5` (384 dimensions) |
| Runtime | `sentence-transformers` library (CPU/GPU local inference) |
| Separation of Concerns | Distinct separation between generative reasoning (Ollama + Qwen) and embedding generation (sentence-transformers + BGE). Decouples candidate matching from the Ollama daemon lifecycle. |
| Scope of Use | Restricted to candidate generation and blocking (entity canonicalization, attribute matching, fact grouping). Embeddings are never used to make final epistemic decisions. |
| Excluded Alternatives | `nomic-embed-text` via Ollama (unnecessary coupling to LLM runtime), `all-MiniLM-L6-v2` (lower retrieval precision on domain-specific financial terms than BGE-small). |

---

## 5. PDF Processing: Two-Tool Strategy

Rather than treating PDF parsers as competing alternatives, the system adopts a deliberate two-tool division of responsibilities:

```text
                    PDF Document
                         |
             +-----------+-----------+
             |                       |
             v                       v
          PyMuPDF                pdfplumber
      (Primary Engine)       (Specialist Tables)
             |                       |
       Document loading       Table detection
       Page iteration         Cell boundaries
       Text blocks & bbox     Merged header handling
       Page metadata          Table coordinate extraction
             |                       |
             +-----------+-----------+
                         |
                         v
             Structured Evidence Objects
```

### Component Breakdown

| Role | Library | Purpose |
|---|---|---|
| Primary Parser | **PyMuPDF (fitz)** | High-speed document loading, text extraction with bounding boxes, font metadata, page slicing, coordinate anchoring. |
| Table Specialist | **pdfplumber** | Precise extraction of table cells, column lines, and multi-line headers into structured 2D matrices. |
| Table Fallback | **Camelot (camelot-py)** | Invoked only when pdfplumber fails to parse complex bordered/unbordered tables (lattice/stream mode). |
| OCR Fallback | **Tesseract (pytesseract)** | Conditional fallback triggered only when a page yields near-zero text layer (scanned/rasterized page). |
| Vision Models | **Excluded from Prototype** | Figures and charts are recorded as `FIGURE`/`CHART` evidence metadata objects with bounding boxes, but visual reasoning is out of prototype scope. |

---

## 6. Orchestration and Workflow Engine: LangGraph

| Decision | LangGraph |
|---|---|
| Purpose | Deterministic multi-agent state orchestration with conditional branching, validation loops, parallel node execution, and checkpointing. |
| Key Principle | **LangGraph controls the workflow; the LLM does not.** Agents are functional execution units, not autonomous planners. |
| Why LangGraph | Out-of-the-box support for cyclic graphs, conditional routing (corroboration vs. contradiction vs. reconciliation), and typed state objects. |
| Excluded Alternatives | LangChain autonomous agents / ReAct (non-deterministic routing violates explainability), Prefect / Airflow (designed for batch data engineering, lack fine-grained prompt/state graph semantics). |

### Graph Topology

```text
                  Document Evidence State
                            |
           +----------------+----------------+
           |                |                |
           v                v                v
       Numerical         Semantic          Event
       Extractor         Extractor       Extractor
           |                |                |
           +----------------+----------------+
                            |
                            v
                   Evidence Verifier
                            |
                            v
                    Context Resolver
                            |
                            v
                   Fact Grouping Node
                            |
            +---------------+---------------+
            |                               |
     [Direct Match]                 [Value Variance]
            |                               |
            v                               v
       CORROBORATED               Hypothesis Generator
                                            |
                               +------------+------------+
                               |            |            |
                               v            v            v
                           Numerical     Temporal     Semantic
                           Validator    Validator    Validator
                               |            |            |
                               +------------+------------+
                                            |
                                            v
                                   Reconciliation Agent
                                            |
                                            v
                                   Adversarial Challenge
                                            |
                                            v
                                      Decision Policy
                                            |
                                            v
                                      Final Decision
```

---

## 7. API Framework: FastAPI

| Decision | FastAPI + Uvicorn |
|---|---|
| Purpose | REST API for asynchronous job management, PDF upload, and result inspection. |
| Features Used | Typed endpoints via Pydantic, automatic OpenAPI documentation, interactive Swagger UI (`/docs`). |
| Interactive UI | Swagger UI serves as the zero-code inspection interface, satisfying UI review requirements without frontend overhead. |
| Async Pattern | Long-running extraction jobs return `202 Accepted` with a `job_id`. Status is polled via `GET /jobs/{job_id}`. |
| Testing Utility | `httpx` is used as the test client for API endpoint integration tests. |

---

## 8. CLI Interface: argparse

| Decision | Python Standard Library argparse |
|---|---|
| Purpose | Primary local debugging and evaluation command-line interface. |
| Invocation | `python -m factlayer process ./documents/` |
| Rationale | Zero third-party dependencies, standard library stability, straightforward evaluator execution without dependency conflicts. |
| Excluded Alternatives | Click was excluded to avoid unnecessary external dependencies for a single command entry point. |

---

## 9. Storage and Artifact Architecture

### Relational Store: SQLite

| Decision | SQLite (sqlite3 standard library) |
|---|---|
| Role | System of record for documents, evidence chunks, extracted facts, fact groups, validator results, hypotheses, decisions, and audit traces. |
| Schema Design | Normalized relational schema matching the epistemic hierarchy: `documents` -> `evidence_chunks` -> `observations` -> `fact_candidates` -> `fact_groups` -> `hypotheses` -> `decisions`. |
| Implementation | Direct Python `sqlite3` without ORM abstraction (no SQLAlchemy) to maintain zero overhead, inspectability, and simple migration management. |

### Inspectable Artifacts: JSON + JSONL + Markdown

The system stores human- and machine-readable artifacts under `runs/JOB-{id}/`:

| Format | Role | Examples |
|---|---|---|
| **SQLite** | Queryable relational state | `ledger.db` |
| **JSON** | Machine-readable structured objects | `facts.json`, `decisions.json`, `evidence_index.json` |
| **JSONL** | Append-only event streams and audit trails | `agent_trace.jsonl`, `extraction_events.jsonl` |
| **Markdown** | Human-readable executive reports | `executive_summary.md`, `contradictions_report.md` |

### Excluded Storage Paradigms

| Paradigm | Status | Rational Rationale |
|---|---|---|
| Dedicated Vector DB (Chroma/FAISS) | Excluded | Candidate matching volume (hundreds of facts) runs efficiently in memory via NumPy/cosine similarity. |
| Graph Database (Neo4j/ArangoDB) | Excluded | The assignment notes a graph is not the decision mechanism. NetworkX provides an optional projection. |
| Document Store (MongoDB) | Excluded | Data model is intrinsically relational with strong relational integrity requirements. |

---

## 10. Data Validation and Contracts: Pydantic v2

| Decision | Pydantic v2 |
|---|---|
| Purpose | Strict boundary enforcement for all inter-agent messages, LLM outputs, state payloads, and API requests. |
| Failure Recovery | LLM responses that fail schema validation trigger a single targeted retry with schema hints. Continued failure defaults safely to an extraction failure or `UNRESOLVED` fact status. |
| Core Schemas | `EvidenceChunk`, `Observation`, `FactCandidate`, `FactGroup`, `Hypothesis`, `ValidatorReport`, `DecisionRecord`, `TraceEvent`. |

---

## 11. Deterministic Processing and Exact Arithmetic

Computations requiring exact logic are strictly forbidden from being executed by the LLM:

| Task | Implementation | Epistemic Rule |
|---|---|---|
| **Financial Arithmetic** | Python `Decimal` | Exact decimal precision for currency and percentages. Floating-point types are avoided for money calculations. |
| **Unit Normalization** | Python deterministic lookup tables | Normalizes scale within same currency (crore, lakh, thousand, million, billion). |
| **Currency Conversion** | Conditional conversion only | Automatic cross-currency conversion is prohibited unless the source text explicitly provides an exchange rate and reference date. Without explicit context, cross-currency variations yield `CURRENCY_MISMATCH` -> `UNRESOLVED`. |
| **Temporal Logic** | `python-dateutil` + `datetime` | Normalizes fiscal years (FY23, FY2022-23), quarters (Q1, Q4), trailing twelve months (TTM), and overlap intervals. |
| **Policy Decision Engine** | Pure Python deterministic function | Maps validator outputs and challenge results to final verdicts (`CORROBORATED`, `CONTRADICTION`, `RECONCILED`, `UNRESOLVED`). |

---

## 12. Graph Projection: NetworkX (Optional)

| Decision | NetworkX (Projection Only) |
|---|---|
| Role | In-memory graph projection of the Evidence Ledger for topological inspection and visualization. |
| Constraint | Strictly downstream of the Decision Engine. NetworkX never participates in fact verification, contradiction detection, or decision logic. |
| Priority | Optional secondary utility. |

---

## 13. Testing Framework: pytest

| Decision | pytest |
|---|---|
| Purpose | Comprehensive automated verification of unit math, agent contracts, and epistemic evaluation benchmarks. |

### Test Suite Structure

```text
tests/
|-- unit/
|   |-- test_decimal_units.py       # Crore, lakh, million, billion scaling
|   |-- test_temporal_parsing.py    # Fiscal calendars and period overlaps
|   +-- test_decision_policy.py     # Deterministic policy rules
|-- contracts/
|   |-- test_extractor_schema.py    # Pydantic schema validation on LLM output
|   |-- test_verifier_schema.py     # Evidence grounding schema validation
|   +-- test_reconciler_schema.py   # Reconciliation hypothesis schema
+-- evaluation/
    |-- test_corroboration.py       # Identical facts across documents
    |-- test_contradiction.py       # Direct numerical/temporal conflicts
    |-- test_reconciliation.py      # Scope/definition reconciled variance
    +-- test_failure_handling.py    # Degraded/malformed input resilience
```

---

## 14. Technology-to-Architecture Mapping

```text
                         FACT KNOWLEDGE LAYER
                                  |
                +-----------------+-----------------+
                |                                   |
         DOCUMENT PROCESSING                    REASONING
                |                                   |
          +-----+-----+                       +-----+------+
          |           |                       |            |
       PyMuPDF    pdfplumber                Ollama      BGE-small
       (Engine)    (Tables)                (Qwen2.5)   (Embeddings)
          |           |                       |            |
          |        Camelot                    |            |
          |       (Fallback)                  |            |
          +-----+-----+                       |            |
                |                             |            |
                v                             |            |
         Evidence Objects                     |            |
                |                             |            |
                +-------------+---------------+------------+
                              |
                              v
                         Pydantic v2
                              |
                              v
                          LangGraph
                              |
        +---------------------+---------------------+
        |                     |                     |
   Extraction            Verification            Context
     Agents                 Agent               Resolver
        +---------------------+---------------------+
                              |
                              v
                         Fact Groups
                              |
                     Hypothesis Generator
                              |
                   +----------+----------+
                   |          |          |
                   v          v          v
               Numerical   Temporal   Semantic
               Validator  Validator  Validator
               (Decimal)  (dateutil)  (Rules)
                   +----------+----------+
                              |
                              v
                     Reconciliation Agent
                              |
                              v
                    Adversarial Challenge
                              |
                              v
                    Decision Policy (Pure Python)
                              |
                              v
                        Final Decision
                              |
                     +--------+--------+
                     |                 |
                     v                 v
                  SQLite         JSON / JSONL / MD
                     |
                     v
               FastAPI + CLI (argparse)
```

---

## 15. What is Deliberately NOT in the Stack

| Component | Status | Rational Rationale |
|---|---|---|
| Frontend (React/Vue) | Excluded | FastAPI Swagger UI + CLI provide complete verification access. |
| Graph Database (Neo4j) | Excluded | Graph is a visual projection, not an epistemic decision engine. |
| Vector Database (Pinecone/Chroma) | Excluded | Prototype volume runs reliably in memory without database overhead. |
| Paid Cloud APIs (OpenAI/Anthropic) | Excluded | Zero external dependency, no API keys, fully local and cost-free. |
| Database ORM (SQLAlchemy) | Excluded | Plain sqlite3 queries are direct, transparent, and easier to audit. |
| CLI Framework (Click/Typer) | Excluded | Standard library argparse is self-contained and sufficient. |
| Task Queues (Celery/RabbitMQ) | Excluded | LangGraph state transitions handle prototype pipeline workflow. |
| Serialization Engine (orjson) | Excluded | Standard library json and Pydantic serialization suffice. |
| Containerization (Docker) | Excluded Initially | Native Python virtual environment eliminates deployment friction. |

---

## 16. Dependency Specification

### requirements.txt

```text
# LLM and Orchestration
ollama>=0.4.0
langchain-core>=0.3.0
langchain-ollama>=0.2.0
langgraph>=0.2.0

# Document and PDF Processing
PyMuPDF>=1.24.0
pdfplumber>=0.11.0

# Table Extraction Fallback
camelot-py[cv]>=0.11.0

# OCR Fallback (Conditional)
pytesseract>=0.3.10
Pillow>=10.0.0

# Embeddings
sentence-transformers>=3.0.0

# API and Server
fastapi>=0.115.0
uvicorn>=0.30.0
httpx>=0.27.0

# Validation and Data Contracts
pydantic>=2.8.0

# Temporal Utilities
python-dateutil>=2.9.0

# Graph Projection (Optional)
networkx>=3.2.0

# Testing Suite
pytest>=8.0.0
```

### Standard Library Capabilities (No External Install Required)

- `sqlite3`: Relational database engine
- `argparse`: Command-line interface parser
- `decimal`: Exact financial arithmetic
- `datetime`: Standard timestamp handling
- `pathlib`: Filesystem path manipulation
- `json`: Machine-readable artifact serialization
- `hashlib`: Evidence chunk hashing and provenance tracking

---

## 17. Frozen Decisions Matrix

| Area | Final Frozen Choice | Concrete Rationale |
|---|---|---|
| Language | Python 3.11 | Maximum reproducibility across evaluators. |
| LLM Runtime | Ollama | Local, cost-free, zero-credential execution. |
| Primary Model | Qwen2.5 7B Instruct | Superior structured output, table extraction, and JSON compliance. |
| Model Upgrade Path | Qwen2.5 14B Instruct | Drop-in parameter scale for machines with higher VRAM. |
| Embeddings Library | sentence-transformers | Clean separation between reasoning model and candidate matcher. |
| Embedding Model | BAAI/bge-small-en-v1.5 | Lightweight, highly performant local candidate blocking model. |
| Primary PDF Parser | PyMuPDF (fitz) | Fast, robust page geometry, text blocks, bounding boxes, metadata. |
| Table Extraction | pdfplumber | Explicit table cell, row, and merged header boundary extraction. |
| Table Fallback | Camelot | Fallback specialist when pdfplumber encounters complex lattices. |
| OCR Engine | Tesseract (pytesseract) | Conditional fallback triggered only on zero-text scanned pages. |
| Vision Reasoning | Excluded from Prototype | Figures recorded as evidence metadata; no visual LLM inference. |
| Workflow Engine | LangGraph | Deterministic conditional agent graphs; LLM does not route workflow. |
| API Layer | FastAPI + Swagger UI | Typed REST endpoints with built-in interactive review interface. |
| CLI Tooling | argparse | Standard library zero-dependency execution. |
| Relational Storage | SQLite (sqlite3) | Relational system of record, single file, zero installation. |
| Database ORM | None (Direct sqlite3) | Direct SQL queries ensure maximum transparency and zero bloat. |
| Artifact Storage | JSON + JSONL + Markdown | Machine-actionable state paired with human-readable reports. |
| Schema Validation | Pydantic v2 | Strict validation boundaries and retry mechanisms for LLM outputs. |
| Financial Math | Python Decimal | Exact decimal arithmetic avoiding binary floating-point roundoff. |
| Currency Handling | Source-explicit only | Unit conversion permitted; cross-currency conversion requires explicit context. |
| Vector Database | None (In-memory) | In-memory similarity over candidate vectors; no external vector DB. |
| Graph Database | None (NetworkX optional) | Graph used solely as optional projection; never a decision engine. |
| Testing | pytest | Strict unit, schema contract, and four-outcome evaluation tests. |

---

*End of Tech Stack Decisions Document*
