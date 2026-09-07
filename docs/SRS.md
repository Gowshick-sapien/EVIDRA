# EVIDRA: Evidence-Driven Architecture for Fact Validation and Knowledge Reasoning

## Software Requirements Specification (SRS)

---

## 1. Introduction and Architectural Vision

### 1.1 Purpose
This Software Requirements Specification (SRS) establishes the complete functional, non-functional, and interface requirements for the **Fact Knowledge Layer (EVIDRA)** system. EVIDRA is a local-first, evidence-centric financial document intelligence system that ingests unstructured PDFs, extracts factual claims with strict spatial coordinates, identifies cross-document corroborations and contradictions, and resolves variances using structured adversarial debate.

### 1.2 Scope of the System
The system is built as a self-contained, reproducible prototype that operates without external cloud dependencies, paid API keys, graph databases, or external vector stores. EVIDRA implements a four-layer architecture orchestrated by LangGraph, powered by local LLMs via Ollama, persisted in a relational SQLite Evidence Ledger, and inspected via FastAPI and a command-line interface.

### 1.3 Core Epistemic Principles
1. **The Fact is Not the Primitive:** Systems must maintain a strict epistemic hierarchy: Evidence Chunk -> Observation -> Fact Candidate -> Fact Group -> Hypothesis Tournament -> Decision -> Decision Trace.
2. **Observations are Distinct from Decisions:** What a source document literally states (Observation) is immutable and distinct from what the system deduces (Decision).
3. **Mandatory Provenance:** Every claim must trace to a specific document ID, page number, and geometric bounding box `(x0, y0, x1, y1)`.
4. **Extract-Then-Verify Decoupling:** Claim extraction is independently verified against raw source text to reject hallucinations before fact construction.
5. **Deterministic Separation:** Generative LLMs handle semantic reasoning and hypothesis formulation; deterministic Python code (`Decimal`, `dateutil`) handles arithmetic, scaling, and final verdict policies.
6. **UNRESOLVED is a First-Class Output:** The system must report unresolved ambiguity rather than forcing an unsupported conclusion.

### 1.4 Definitions, Acronyms, and Abbreviations
* **Bounding Box (BBox):** Physical rectangle `(x0, y0, x1, y1)` identifying text or table coordinates on a PDF page.
* **Evidence Chunk:** An immutable, cryptographically hashed span of text or table extracted from a source document.
* **Observation:** A structured assertion extracted from an evidence chunk representing what the document states.
* **Fact Candidate:** A verified observation with normalized units, currencies, and ISO 8601 temporal intervals.
* **Fact Group:** A cluster of fact candidates across multiple documents referring to the same entity and attribute over overlapping time periods.
* **Hypothesis Tournament:** A multi-agent evaluation where competing explanations (restatement, accounting standard, scope mismatch, contradiction) are tested against evidence.
* **Adversarial Skeptic:** An agent that systematically attempts to falsify proposed reconciliations using original evidence chunks.
* **Decision Card:** The standardized output summarizing the comparison between claims, final verdict, confidence strength, provenance citations, and audit narrative.
* **Decision Trace:** A cryptographic, step-by-step audit record of all pipeline actions written to `trace.jsonl`.

---

## 2. Overall Description

### 2.1 Product Perspective
EVIDRA functions as an intermediate epistemic reasoning layer between raw financial documents and downstream decision makers (analysts, compliance officers, automated financial systems). It does not replace human judgment but provides transparent, audited, and falsifiable factual assessments.

### 2.2 User Classes and Operating Profiles
* **Financial Analyst:** Evaluates company performance across filings (10-K, 10-Q, 8-K, Press Releases) and requires immediate detection of restatements and Non-GAAP discrepancies.
* **Systems Auditor:** Requires end-to-end cryptographic traceability from final verdicts back to physical PDF bounding boxes.
* **Prototype Evaluator:** Runs automated evaluation suites locally without API keys, configuration hurdles, or network connectivity.

### 2.3 Operating Environment
* **Host OS:** Windows 10/11, macOS, or Linux (POSIX).
* **Python Runtime:** Python 3.11+ (tested on Python 3.11 and 3.12).
* **Local LLM Engine:** Ollama daemon running locally at `http://127.0.0.1:11434`.
* **Primary LLM Model:** Qwen2.5 (3B / 7B / 14B Instruct).
* **Local Embedding Model:** `BAAI/bge-small-en-v1.5` cached via `sentence-transformers`.
* **Database:** SQLite 3 (zero configuration, embedded).

### 2.4 Design and Implementation Constraints
1. **No External Cloud APIs:** All generative extraction and reasoning must execute offline via local Ollama.
2. **No Graph Database Dependency:** Graphs are optional visual projections (NetworkX); the SQLite Evidence Ledger is the sole system of record.
3. **No External Vector Store:** Attribute blocking uses in-memory cosine similarity over local BGE embeddings.
4. **Deterministic Financial Mathematics:** Floating-point operations are prohibited for currency/unit math; all calculations must use Python `decimal.Decimal`.
5. **Zero Dedicated Frontend:** UI review requirements are fulfilled via auto-generated FastAPI Swagger documentation and Markdown reports.

---

## 3. External Interface Requirements

### 3.1 User Interfaces
* **Command Line Interface (CLI):** Implemented via standard Python `argparse` providing commands: `process`, `inspect`, and `report`.
* **API Swagger Documentation:** Interactive OpenAPI/Swagger UI served at `http://127.0.0.1:8000/docs` for testing endpoints, uploading PDFs, and retrieving results.
* **Markdown Reports:** Clean, GitHub Flavored Markdown reports (`summary.md`, `contradictions.md`, `unresolved.md`) rendered in the run directory.

### 3.2 Software Interfaces
* **Ollama REST API:** HTTP communication on port 11434 for version checks (`/api/version`), model tags (`/api/tags`), and structured completions (`/api/generate`).
* **PyMuPDF (fitz):** Native Python bindings for high-speed page parsing and bounding-box geometry extraction.
* **pdfplumber:** Table extraction engine for cell matrices, multi-row headers, and explicit borders.
* **Sentence-Transformers:** HuggingFace integration for local 384-dimensional dense vector generation.
* **SQLite C-API:** Standard Python `sqlite3` interface for atomic relational transactions.

---

## 4. System Features and Detailed Functional Requirements

### 4.1 System Prerequisites and Environment (SYS-PRE)

* **SYS-PRE-01: Python Runtime and Core Package Verification**
  * The system must verify that Python version is 3.11 or greater.
  * The system must verify the installation and importability of: `fastapi`, `uvicorn`, `pydantic`, `PyMuPDF`, `pdfplumber`, `langgraph`, `langchain-core`, `langchain-ollama`, `sentence-transformers`, `python-dateutil`.
* **SYS-PRE-02: Ollama Local Runtime Daemon Probing**
  * The system must perform an HTTP GET request to `http://127.0.0.1:11434/api/version` and confirm an HTTP 200 response within 2000 milliseconds.
  * If the daemon is unreachable, the system must emit an actionable diagnostic instruction (`ollama serve`).
* **SYS-PRE-03: Local LLM Model and Structured Output Verification**
  * The system must query `/api/tags` to verify the presence of a supported local model (`qwen2.5:3b`, `qwen2.5:7b-instruct`, etc.).
  * The system must dispatch a test prompt enforcing `format: "json"` to confirm that the model emits valid JSON matching a target schema.
* **SYS-PRE-04: Embedding Model Local Cache Verification**
  * The system must verify that `BAAI/bge-small-en-v1.5` is cached locally in the HuggingFace hub cache.
  * The system must generate a test embedding vector and confirm that its dimension is exactly 384 and its L2 norm is equal to 1.0 (+/- 0.001).
* **SYS-PRE-05: External Binary Fallback Detection**
  * The system must probe system `PATH` for `tesseract` and `ghostscript`. If absent, fallback paths must be cleanly marked disabled without crashing baseline execution.

### 4.2 Document Ingestion and Evidence Preparation (DOC-ING) - Layer 1

* **DOC-ING-01: Multi-Document PDF Ingestion**
  * The system must ingest arbitrary financial PDF documents through the REST API or CLI directory scanner.
  * The system must compute a SHA-256 hash for every ingested file to detect duplicates and ensure audit integrity.
* **DOC-ING-02: Spatial Text Block Extraction**
  * The system must utilize PyMuPDF to extract text spans with exact page numbers, font sizes, structural flags, and bounding boxes `(x0, y0, x1, y1)`.
* **DOC-ING-03: Domain-Oriented Table Extraction**
  * The system must utilize pdfplumber to detect table grids, column headers, row labels, and cell text matrices.
  * The system must extract table metadata including reporting scope, currency, scale, and footnote associations.
* **DOC-ING-04: Spatial Disambiguation Masking**
  * The system must mask out table bounding boxes during raw text block harvesting to prevent duplicate extraction of tabular text.
* **DOC-ING-05: Deterministic Evidence Chunk Generation**
  * Every extracted span must receive a deterministic `chunk_id` derived from `SHA-256(document_id + page + bbox + raw_content)`.
* **DOC-ING-06: Document Representation Package**
  * The system must serialize each ingested document into a standardized package in `runs/JOB-{id}/documents/{doc_id}/` containing `manifest.json`, `document.md`, `pages/`, and `tables/`.

### 4.3 Fact Construction and Observation Extraction (FACT-EXT) - Layer 2a

* **FACT-EXT-01: Table-Native Direct Metric Extraction**
  * The system must translate table cells `(row_header, col_header, cell_value)` directly into structured metrics without generative paraphrasing.
* **FACT-EXT-02: Prose Extraction via Constrained LLM Prompting**
  * Narrative paragraphs must be processed by extraction agents with strict Pydantic schema boundaries (`NumericalExtractor`, `SemanticExtractor`, `EventExtractor`).
* **FACT-EXT-03: Dynamic Fact Schema Support**
  * Attribute names must not be hardcoded to rigid enums; raw attributes (e.g., "Revenues from operations", "Operating Revenue") must be captured dynamically.
* **FACT-EXT-04: Strict Pydantic Output Enforcement**
  * All LLM extraction responses must validate against `Observation` models. Malformed JSON must trigger automatic retry (max 3 attempts); persistent failures must be recorded as extraction errors without halting the pipeline.

### 4.4 Fact Verification and Normalization (FACT-VER) - Layer 2b

* **FACT-VER-01: Extract-Then-Verify Entailment Check**
  * An independent Evidence Verifier agent must evaluate candidate observations against the cited raw evidence chunk in isolation.
  * The agent must assign an entailment verdict: `ENTAILED`, `HALLUCINATED`, or `AMBIGUOUS`.
* **FACT-VER-02: Hallucination Filtering**
  * Any observation classified as `HALLUCINATED` must be discarded from the reasoning pipeline and recorded in the audit trace.
* **FACT-VER-03: Multidimensional Context Resolution**
  * The system must extract accounting basis (`GAAP`, `NON-GAAP`, `ADJUSTED`), organizational scope (`CONSOLIDATED`, `STANDALONE`, `SEGMENT`), and filing version (`ORIGINAL`, `RESTATED`).
* **FACT-VER-04: Deterministic Arithmetic Normalization**
  * All numerical metrics must be parsed into Python `decimal.Decimal` objects. Floating-point arithmetic is strictly prohibited.
* **FACT-VER-05: Scale Multiplier Normalization**
  * Scale terms (Thousand, Million, Billion, Lakh, Crore) must be scaled to standard base units deterministically (`5 Crore` -> `50,000,000`).
* **FACT-VER-06: Temporal Interval Resolution**
  * Fiscal quarters, calendar years, and point-in-time dates must be resolved to ISO 8601 calendar intervals `(period_start, period_end)` using `dateutil`.
* **FACT-VER-07: Two-Tier Candidate Fact Grouping**
  * Verified facts must be grouped into `FactGroup` clusters using hard filtering (exact entity match + temporal overlap) followed by soft semantic matching (BGE-Small cosine similarity >= 0.82).

---

### 4.5 Fact Decision Engine and Reasoning (DEC-ENG) - Layer 3

* **DEC-ENG-01: Three Adaptive Decision Paths**
  * The system must route fact groups based on variance characteristics:
    * **Path A (Deterministic Corroboration):** Exact normalized equality within 0.01% tolerance; bypasses LLM inference entirely; emits `CORROBORATED` in < 10ms.
    * **Path B (Contextual Resolution):** Dimensional variance detected (different accounting standard or scope); routes to specialist context validators; emits `RECONCILED` if bridge context is confirmed.
    * **Path C (Conflict Debate):** Material variance with identical context; triggers full Hypothesis Tournament, Reconciliation Proposer, Adversarial Skeptic, and Decision Policy.
* **DEC-ENG-02: Hypothesis Tournament Generation**
  * When facts within a group conflict, the system must generate structured competing hypotheses across 5 classes:
    1. `RESTATEMENT`: Subsequent revision or amended filing.
    2. `ACCOUNTING_BASIS`: GAAP vs Non-GAAP / Adjusted metric difference.
    3. `SCOPE_MISMATCH`: Consolidated group vs Standalone parent entity.
    4. `TIMING_DIFFERENCE`: Calendar quarter vs custom fiscal period variation.
    5. `ERRONEOUS_CONTRADICTION`: Genuine irreconcilable disagreement.
* **DEC-ENG-03: Specialist Domain Validators**
  * Independent validators must evaluate hypotheses against source evidence:
    * `RestatementValidator`: Validates filing dates, amendment flags (10-K/A), and restatement disclosure notes.
    * `AccountingBasisValidator`: Inspects GAAP-to-Non-GAAP reconciliation bridge tables and stock-based compensation footnotes.
    * `ScopeValidator`: Evaluates legal entity definitions, subsidiaries, and segmental reporting disclosures.
    * `ArithmeticValidator`: Computes exact numerical deltas using Python `Decimal` and tests reconciliation math.
* **DEC-ENG-04: Reconciliation Proposer Formulation**
  * The Reconciliation Agent must synthesize supported validator outcomes into an explicit explanation bridging the variance.
  * The agent must cite supporting document IDs, pages, and bounding boxes for every asserted reconciliation bridge.
* **DEC-ENG-05: Adversarial Skeptic Falsification Protocol**
  * The Adversarial Challenge agent must systematically attempt to falsify the proposed reconciliation using the original source chunks.
  * The agent must determine if the explanation relies on ungrounded assumptions or if conflicting evidence exists.
  * The outcome must be classified as: `SURVIVED`, `FALSIFIED`, or `INSUFFICIENT_EVIDENCE`.
* **DEC-ENG-06: Pure Python Deterministic Decision Policy**
  * The final verdict must be evaluated by deterministic Python rule logic based on validator and skeptic states:
    * `CORROBORATED`: Numerical match within 0.01% tolerance, matching entity and period, verified provenance.
    * `RECONCILED`: Documented context variance, supported by specialist validators, and survived adversarial challenge.
    * `CONTRADICTION`: Material numerical or qualitative disagreement, matching context, and falsified or refuted reconciliation.
    * `UNRESOLVED`: Missing context, unentailed observations, or unresolved conflicting evidence.
* **DEC-ENG-07: Categorical Decision Strength Assignment**
  * Every decision must be assigned an ordinal strength: `HIGH`, `MEDIUM`, `LOW`, or `INSUFFICIENT`.
  * Arbitrary probabilistic floating-point confidence values are prohibited.
* **DEC-ENG-08: Decision Card Generation**
  * Every evaluated fact relationship must produce a structured `DecisionCard` containing claim comparisons, dual-source provenance coordinates, reconciliation narrative, and adversarial audit results.
* **DEC-ENG-09: Cryptographic Decision Trace**
  * Every state transition, agent prompt, completion, and rule execution must be streamed to `runs/JOB-{id}/traces/trace.jsonl` for full provenance replay.

### 4.6 Observability, Storage, and Reporting (OBS-REP) - Layer 4

* **OBS-REP-01: SQLite Relational Evidence Ledger**
  * The system must maintain an isolated `ledger.db` SQLite database with 10 tables: `documents`, `evidence_chunks`, `observations`, `fact_candidates`, `fact_groups`, `group_members`, `hypotheses`, `validator_results`, `decisions`, and `decision_traces`.
  * All database operations must utilize parameterized queries and atomic transactional commits.
* **OBS-REP-02: Isolated Run Directory Hierarchy**
  * Every execution must initialize a dedicated run directory `runs/JOB-{timestamp}-{uuid}/` housing documents, ledger, reports, and traces.
* **OBS-REP-03: Executive Summary Report Generation**
  * The system must generate `reports/summary.md` detailing documents parsed, chunks created, fact groups formed, and verdict breakdowns.
* **OBS-REP-04: Contradiction Report Generation**
  * The system must generate `reports/contradictions.md` detailing every detected conflict with side-by-side claim comparisons, source bounding boxes, and why reconciliation attempts failed.
* **OBS-REP-05: Unresolved Report Generation**
  * The system must generate `reports/unresolved.md` highlighting ambiguous facts, missing context, and specific recommendations for human analysts.
* **OBS-REP-06: FastAPI Asynchronous Endpoints**
  * The system must expose REST endpoints: `POST /jobs`, `GET /jobs/{id}`, `GET /jobs/{id}/decisions`, `GET /jobs/{id}/decisions/{decision_id}`, and `GET /jobs/{id}/reports/{type}`.
  * Interactive Swagger documentation must be available at `/docs`.
* **OBS-REP-07: Command Line Interface (CLI)**
  * The CLI must support `process <path>`, `inspect <job_id>`, and `report <job_id>` commands with ANSI terminal summary tables.

---

## 5. Non-Functional Requirements (NFR)

### 5.1 Performance and Latency
* **NFR-PERF-01 (Path A Latency):** Deterministic corroboration checks must execute in under 20 milliseconds per fact group.
* **NFR-PERF-02 (Path B Latency):** Contextual resolution must complete in under 2.5 seconds per fact group on local hardware.
* **NFR-PERF-03 (Path C Latency):** Full adversarial tournament reasoning must complete in under 8.0 seconds per fact group.
* **NFR-PERF-04 (Embedding Blocking):** Candidate blocking of 500 facts using BGE-Small must complete in under 500 milliseconds.

### 5.2 Reliability and Defensive Fault Tolerance
* **NFR-REL-01 (Defensive Fallback):** Any unhandled exception or parsing failure in the reasoning chain must automatically fallback to `UNRESOLVED` with diagnostic error logging. The pipeline must never crash.
* **NFR-REL-02 (LLM Output Retry):** If the local LLM emits malformed JSON, the provider must automatically retry with temperature 0.0 up to 3 times before failing gracefully.

### 5.3 Determinism and Auditability
* **NFR-DET-01 (Arithmetic Determinism):** All financial operations must use `decimal.Decimal` with exact scaling to eliminate IEEE 754 precision artifacts.
* **NFR-DET-02 (Provenance Replay):** Every decision must be 100% reconstructible from the `trace.jsonl` log and source PDF coordinates.

### 5.4 Security and Safety
* **NFR-SEC-01 (Zero Credential Leakage):** The system must not require external cloud credentials, API keys, or internet egress during execution.
* **NFR-SEC-02 (SQL Injection Prevention):** All database interactions must use parameterized statements; string concatenation in SQL queries is strictly prohibited.

### 5.5 Portability
* **NFR-PORT-01 (Platform Independence):** The codebase must execute identically on Windows 10/11, macOS, and Linux without platform-specific dependencies.

---

## 6. Requirements Traceability and Verification Matrix

| SRS ID | Requirement Name | Architecture Layer | Target Module | Mapped Deliverable | Test Suite |
|---|---|---|---|---|---|
| **SYS-PRE-01..05** | Environment & Prerequisite Verification | Layer 0 | `scripts/verify_env.py` | D0.1 - D0.5 | `scripts/verify_env.py` |
| **DOC-ING-01..02** | PDF Ingestion & Text Extraction | Layer 1 | `src/pdf/parser.py` | D2.1 | `tests/contracts/test_extractor_schema.py` |
| **DOC-ING-03..04** | Table Extraction & Spatial Masking | Layer 1 | `src/pdf/tables.py` | D2.1 | `tests/contracts/test_extractor_schema.py` |
| **DOC-ING-05..06** | Chunking & Document Package | Layer 1 | `src/pdf/parser.py` | D2.2 | `tests/unit/test_provenance.py` |
| **FACT-EXT-01..04** | Dual Fact Extraction & Schemas | Layer 2a | `src/extraction/agents.py` | D2.4 | `tests/contracts/test_extractor_schema.py` |
| **FACT-VER-01..02** | Extract-Then-Verify Entailment | Layer 2b | `src/verification/verifier.py` | D3.1 | `tests/contracts/test_verifier_schema.py` |
| **FACT-VER-03** | Multidimensional Context Resolution | Layer 2b | `src/verification/context.py` | D3.2 | `tests/unit/test_context_resolver.py` |
| **FACT-VER-04..06** | Deterministic Normalization (Decimal/Dates)| Layer 2b | `src/verification/normalizers.py` | D3.3 | `tests/unit/test_decimal_units.py`, `test_temporal_parsing.py` |
| **FACT-VER-07** | Candidate Grouping & Blocking | Layer 2c | `src/matching/embeddings.py` | D3.4 | `tests/unit/test_embeddings.py` |
| **DEC-ENG-01** | Three Adaptive Decision Paths | Layer 3 | `src/decision/workflow.py` | D4.1 | `tests/evaluation/test_corroboration.py` |
| **DEC-ENG-02..03** | Hypothesis Tournament & Validators | Layer 3 | `src/decision/hypothesis.py`, `validators.py` | D4.2 | `tests/evaluation/test_contradiction.py` |
| **DEC-ENG-04..05** | Reconciliation & Adversarial Challenge| Layer 3 | `src/decision/reconciliation.py` | D4.3 | `tests/evaluation/test_reconciliation.py` |
| **DEC-ENG-06..07** | Pure Python Decision Policy | Layer 3 | `src/decision/policy.py` | D4.4 | `tests/unit/test_decision_policy.py` |
| **DEC-ENG-08..09** | Decision Cards & Decision Tracing | Layer 3/4 | `src/observability/trace.py` | D5.1 | `tests/evaluation/test_traces.py` |
| **OBS-REP-01..02** | SQLite Evidence Ledger & Runs | Layer 4 | `src/db/ledger.py` | D1.1, D1.2 | `tests/unit/test_ledger.py` |
| **OBS-REP-03..05** | Markdown Reporting Suite | Layer 4 | `src/observability/reporters.py` | D5.2 | `tests/evaluation/test_reports.py` |
| **OBS-REP-06..07** | FastAPI REST Server & CLI | Layer 4 | `src/api/server.py`, `src/cli/main.py` | D1.3, D1.4 | `tests/contracts/test_api.py` |

---

## 7. Mandatory Assignment Evaluation Benchmarks

The system requirements guarantee successful execution and formal evaluation across four mandatory benchmark scenarios:

1. **Benchmark Case 1: Cross-Document Corroboration**
   * *Scenario:* Identical Q3 revenues reported in an earnings press release and SEC Form 10-K.
   * *Requirement:* System must route through Path A, confirm exact normalized numerical match, and assign verdict `CORROBORATED` (Strength: `HIGH`) linking dual bounding boxes.
2. **Benchmark Case 2: Direct Factual Contradiction**
   * *Scenario:* Investor presentation asserts FY2024 revenue of $120M; Audited 10-K states $98M with no explanatory footnotes.
   * *Requirement:* System must route through Path C, generate competing hypotheses, falsify reconciliation via Adversarial Skeptic, and assign verdict `CONTRADICTION` (Strength: `HIGH`).
3. **Benchmark Case 3: Defensible Fact Reconciliation**
   * *Scenario:* Press release reports Q3 Operating Income of $45M; Form 10-Q reports $38M. Footnote 4 details a $7M stock compensation exclusion in the Non-GAAP figure.
   * *Requirement:* Context Resolver must detect GAAP vs Non-GAAP; AccountingBasisValidator must verify the bridge table; Adversarial Skeptic must confirm the bridge matches the delta; system assigns verdict `RECONCILED` (Strength: `HIGH`).
4. **Benchmark Case 4: Defensive Failure Handling**
   * *Scenario:* Input PDF contains corrupted text blocks, missing pages, or unentailed claims.
   * *Requirement:* Extract-Then-Verify must flag claims as `AMBIGUOUS` or `UNENTAILED`; Decision Policy must assign verdict `UNRESOLVED` (Strength: `INSUFFICIENT`) and record diagnostic explanations in `unresolved.md` without crashing.
