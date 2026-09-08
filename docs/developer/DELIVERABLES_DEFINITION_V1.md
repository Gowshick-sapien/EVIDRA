# EVIDRA: Evidence-Driven Architecture for Fact Validation and Knowledge Reasoning

## Master Deliverables Specification

---

## 1. Overview and Engineering Delivery Model

This document provides the definitive, granular specification for all implementation deliverables (D0 through D5) of the **Fact Knowledge Layer (EVIDRA)** system.

The core thesis of this architecture is that document-grounded reasoning requires strict epistemic hygiene:
1. **Observation is distinct from Decision:** What a source document asserts (Observation) must never be conflated with what the system concludes (Decision).
2. **Provenance is Mandatory:** Every numerical and qualitative claim must trace to a cryptographic chunk hash, document ID, page number, and bounding box.
3. **Deterministic Separation:** Large Language Models (LLMs) are restricted to semantic reasoning, extraction, and hypothesis generation. All arithmetic verification, date logic, unit scaling, and final verdict policies are executed by deterministic pure Python modules.

The delivery lifecycle follows a linear dependency chain where each phase gates subsequent execution:

```
[ D0: Prerequisite & Environment Verification ]
                      |
                      v
[ D1: Core Infrastructure & Evidence Ledger ]
                      |
                      v
[ D2: Document Processing & Extraction Layer ]
                      |
                      v
[ D3: Verification, Context & Normalization Layer ]
                      |
                      v
[ D4: Fact Decision Engine (LangGraph Orchestration) ]
                      |
                      v
[ D5: Observability, Reporting & Evaluation Testing ]
```

---

## 2. Deliverables Summary Matrix

| Deliverable | Name | Primary Target Modules | Key Artifacts / Outputs | SRS Requirement Mapping |
|---|---|---|---|---|
| **D0** | **Prerequisite & Environment Verification** | `requirements.txt`, `scripts/verify_env.py` | Environment diagnostic log, cached BGE model, active Ollama runtime | SYS-PRE-01 to SYS-PRE-05 |
| **D1** | **Core Infrastructure & Evidence Ledger** | `src/db/`, `src/api/`, `src/cli/`, `runs/` | SQLite schema (`ledger.db`), FastAPI Swagger UI, CLI runner | LEDG-01 to LEDG-05, INTF-01, INTF-02 |
| **D2** | **Document Processing & Extraction Layer** | `src/pdf/`, `src/llm/`, `src/extraction/` | Bounding-box chunks, `Observation` records, Pydantic schemas | DOC-01 to DOC-04, EXT-01 to EXT-04 |
| **D3** | **Verification, Context & Normalization** | `src/verification/`, `src/matching/` | Verified facts, normalized units/dates, fact candidate groups | VER-01 to VER-03, NORM-01 to NORM-03, MAT-01 |
| **D4** | **Fact Decision Engine** | `src/decision/` | LangGraph state graph, hypotheses, adversarial challenge logs, final verdicts | DEC-01 to DEC-06, POL-01 to POL-04 |
| **D5** | **Observability, Reporting & Evaluation Testing** | `src/observability/`, `tests/` | Decision traces, Executive Summary, Contradiction Report, test suite | OBS-01 to OBS-03, TEST-01 to TEST-04 |

---

## 3. Granular Deliverable Specifications

### Deliverable 0: Prerequisite and Environment Verification

**Objective:** Validate that the host environment conforms to all runtime constraints, frozen dependencies, local LLM execution capabilities, and deterministic numerical requirements prior to core pipeline activation.

#### D0.1: Python Environment & Dependency Manifest
* **Target Module:** `requirements.txt`, `scripts/verify_env.py`
* **Functional Scope:**
  * Validate Python runtime compatibility (Target: Python 3.11+, actively supporting Python 3.11/3.12).
  * Confirm installation of core frozen libraries: `fastapi`, `uvicorn`, `pydantic`, `PyMuPDF` (fitz), `pdfplumber`, `langgraph`, `langchain-core`, `langchain-ollama`, `sentence-transformers`, `python-dateutil`.
  * Verify absence of forbidden heavy infrastructure dependencies (e.g., Neo4j drivers, LangChain autonomous agent loops, external vector DB clients like Chroma/Pinecone).
* **Defensive Fail-Safe:** Automated pip freeze comparison verifying that no missing dependencies crash downstream imports.
* **Acceptance Criteria:** `scripts/verify_env.py` executes cleanly and reports zero missing mandatory packages.

#### D0.2: Ollama Local Runtime Daemon Verification
* **Target Module:** `src/llm/provider.py`, `scripts/verify_env.py`
* **Functional Scope:**
  * Perform diagnostic health check against the local Ollama daemon at `http://127.0.0.1:11434/api/version`.
  * Confirm connectivity without requiring cloud API keys, paid accounts, or external network access.
* **Defensive Fail-Safe:** Detect connection timeout or ECONNREFUSED and emit an actionable operator message specifying how to launch `ollama serve`.
* **Acceptance Criteria:** HTTP GET to `/api/version` returns HTTP 200 with valid version string within 2000ms.

#### D0.3: LLM Model Pull and Structured Output Check
* **Target Module:** `src/llm/provider.py`
* **Functional Scope:**
  * Query `/api/tags` to ensure `qwen2.5:7b-instruct` (or user-selected local tag) is present in local storage.
  * Execute a test inference prompt enforcing JSON output format via Ollama API to confirm model weights load into GPU/CPU RAM and output compliant JSON.
* **Defensive Fail-Safe:** If the model is absent, prompt operator with `ollama pull qwen2.5:7b-instruct` command. If model returns invalid JSON, trigger schema parsing failure handling.
* **Acceptance Criteria:** Model processes test JSON prompt in under 10 seconds and returns a parseable JSON object.

#### D0.4: Embedding Model Local Cache Check
* **Target Module:** `src/matching/embeddings.py`
* **Functional Scope:**
  * Load `BAAI/bge-small-en-v1.5` via `sentence_transformers.SentenceTransformer`.
  * Validate that weights are locally cached in user huggingface cache directory (`.cache/huggingface/hub`).
  * Execute test embedding vector generation (384-dimensional dense vector) and confirm normalized float32 format.
* **Defensive Fail-Safe:** Windows symlink warning suppression via `HF_HUB_DISABLE_SYMLINKS_WARNING=1` to prevent logging noise.
* **Acceptance Criteria:** Test embedding for string produces 384-dimensional vector with L2 norm equal to 1.0 (+/- 0.001).

#### D0.5: External Binary Check (Optional Fallbacks)
* **Target Module:** `src/pdf/tables.py`, `src/pdf/parser.py`
* **Functional Scope:**
  * Probe system `PATH` for `tesseract` binary and `ghostscript` (Camelot fallback dependency).
  * Flag OCR and advanced table fallback availability as active or disabled.
* **Defensive Fail-Safe:** If absent, mark OCR and Camelot paths as unavailable, routing execution exclusively through primary PyMuPDF + pdfplumber paths. Pipeline execution must not fail when processing text-native PDFs.
* **Acceptance Criteria:** System detects presence/absence without halting baseline execution.

---

### Deliverable 1: Core Infrastructure and Evidence Ledger

**Objective:** Establish the persistent relational system of record (Evidence Ledger), the job run directory hierarchy, the REST API endpoints, and the deterministic CLI entry point.

#### D1.1: SQLite Evidence Ledger Schema & Persistence Engine
* **Target Module:** `src/db/schema.sql`, `src/db/ledger.py`
* **Functional Scope:**
  * Implement relational schema adhering strictly to the separation between source observation and derived decision:
    * `documents`: document_id, filename, file_hash (SHA-256), page_count, created_at.
    * `evidence_chunks`: chunk_id, document_id, page_number, chunk_type (text/table/figure), bounding_box (x0, y0, x1, y1), content, content_hash.
    * `observations`: observation_id, chunk_id, document_id, statement, entity, attribute, raw_value, observation_type, temporal_scope, confidence, provenance_status.
    * `fact_candidates`: fact_id, observation_id, normalized_value, normalized_unit, normalized_currency, normalized_period_start, normalized_period_end.
    * `fact_groups`: group_id, entity, attribute, period_id, member_count.
    * `group_members`: group_id, fact_id.
    * `hypotheses`: hypothesis_id, group_id, explanation_type, description, likelihood_score.
    * `validator_results`: result_id, hypothesis_id, validator_type, outcome, details_json.
    * `decisions`: decision_id, group_id, verdict (CORROBORATED, CONTRADICTION, RECONCILED, UNRESOLVED), confidence, reasoning_summary, created_at.
    * `decision_traces`: trace_id, decision_id, step_name, agent_name, input_json, output_json, execution_time_ms.
  * Provide atomic transactional commit methods, parameterized queries (SQL injection prevention), and connection context managers.
* **Acceptance Criteria:** Complete schema initializes cleanly in memory or on-disk SQLite; CRUD operations verified for every table via unit tests.

#### D1.2: Artifact Storage Engine & Run Directory Hierarchy
* **Target Module:** `src/observability/trace.py`
* **Functional Scope:**
  * Initialize isolated run directory structure per job: `runs/JOB-{timestamp}-{uuid}/` containing:
    * `ledger.db`: Local SQLite instance.
    * `evidence/`: Cached chunk fragments and table snapshots.
    * `reports/`: Generated Markdown summaries.
    * `traces/`: Raw JSON/JSONL execution step logs.
* **Acceptance Criteria:** Directory layout is created deterministically on job start; file permissions and relative paths operate cleanly across Windows and POSIX systems.

#### D1.3: FastAPI REST Interface
* **Target Module:** `src/api/server.py`, `src/api/models.py`
* **Functional Scope:**
  * Expose asynchronous endpoints:
    * `POST /jobs`: Accept multipart PDF uploads, generate `job_id`, initiate background processing task.
    * `GET /jobs/{job_id}`: Poll job status (`PENDING`, `PROCESSING`, `COMPLETED`, `FAILED`).
    * `GET /jobs/{job_id}/decisions`: Retrieve list of all decisions with verdicts and confidence.
    * `GET /jobs/{job_id}/decisions/{decision_id}`: Retrieve detailed verdict, evidence citations, and audit trace.
    * `GET /jobs/{job_id}/reports/{report_type}`: Fetch generated Markdown reports (Executive Summary, Contradiction Report).
  * Auto-generate OpenAPI/Swagger documentation serving as the zero-dependency inspection interface.
* **Acceptance Criteria:** FastAPI test client executes upload and retrieval flows with proper HTTP status codes (200, 202, 404, 422).

#### D1.4: Command Line Interface (CLI)
* **Target Module:** `src/cli/main.py`
* **Functional Scope:**
  * Implement zero-dependency CLI using standard library `argparse`:
    * `python -m src.cli.main process <path_to_pdf_or_folder> [--out-dir <dir>] [--strict] [--verbose]`
    * `python -m src.cli.main inspect <job_id> [--verdict <verdict_filter>]`
    * `python -m src.cli.main report <job_id> --format <markdown|json>`
  * Print formatted ANSI terminal table summarizing processing throughput, facts extracted, and verdicts.
* **Acceptance Criteria:** Running the CLI process command on a sample PDF generates a complete run directory and exits with code 0.

---

### Deliverable 2: Document Processing and Extraction Layer (Layer 1 & 2a)

**Objective:** Ingest heterogeneous financial PDFs, decompose them into spatial evidence chunks, invoke the local LLM via robust Pydantic schemas, and store source observations.

#### D2.1: Two-Tool PDF Pipeline
* **Target Module:** `src/pdf/parser.py`, `src/pdf/tables.py`
* **Functional Scope:**
  * **PyMuPDF (fitz) Engine:** Extract text blocks with exact page numbers, font sizes, flags, and geometric bounding box tuples `(x0, y0, x1, y1)`. Identify layout headers, footers, and section titles.
  * **pdfplumber Engine:** Detect explicit table boundaries, grid structures, merged header cells, and row-column relationships. Extract tables as structured matrices of text and coordinates.
  * **Heuristic Disambiguation:** Prevent double-extraction of table text by masking table bounding boxes during raw text block harvesting.
* **Defensive Fail-Safe:** If `pdfplumber` yields no tables on a page containing grid lines, trigger optional Camelot fallback or fallback to whitespace-delimited block parsing.
* **Acceptance Criteria:** Accurately extracts both unstructured narrative paragraphs and multi-column tables with valid bounding boxes and page numbers.

#### D2.2: Cryptographic Evidence Chunk Bundle Generator
* **Target Module:** `src/extraction/schemas.py`, `src/pdf/parser.py`
* **Functional Scope:**
  * Assign deterministic, reproducible `chunk_id` for every text block and table using SHA-256 hash of `(document_id, page_number, bounding_box, raw_content)`.
  * Serialize chunks into Pydantic model `EvidenceChunk` with `chunk_id`, `document_id`, `page_number`, `chunk_type`, `bounding_box`, `content`, and `content_hash`.
* **Acceptance Criteria:** Identical document re-processed produces identical `chunk_id` values across separate executions.

#### D2.3: ReasoningService Abstraction & Local LLM Client
* **Target Module:** `src/llm/provider.py`
* **Functional Scope:**
  * Implement unified `ReasoningService` protocol decoupling agent prompts from the underlying runtime.
  * Implement `OllamaProvider` wrapping `langchain-ollama` / direct Ollama client with automatic retry logic (maximum 3 retries), schema-enforced prompt formatting, and defensive JSON repair.
* **Defensive Fail-Safe:** If local Ollama output fails Pydantic schema validation after retries, capture raw text, flag extraction as `PARSE_ERROR`, and prevent system crash.
* **Acceptance Criteria:** Provider reliably forces Qwen2.5 to emit conforming JSON objects mapped directly into target Pydantic instances.

#### D2.4: Extraction Agents (Numerical, Semantic, Event)
* **Target Module:** `src/extraction/agents.py`, `src/extraction/schemas.py`
* **Functional Scope:**
  * **Numerical Extractor:** Extract financial metrics, revenues, margins, growth percentages, EPS, and debt figures with explicit unit and currency strings.
  * **Semantic Extractor:** Extract qualitative statements, management commentary, risk disclosures, accounting policy choices, and operational guidance.
  * **Event Extractor:** Extract corporate actions, board decisions, restructuring dates, merger announcements, and fiscal year revisions.
  * Ensure extracted `Observation` strictly captures what the text states without extrapolation or evaluation.
* **Acceptance Criteria:** Extraction agent processes test financial statements, generating valid `Observation` objects linked to source `chunk_id` without dropping key financial figures.

---

### Deliverable 3: Verification, Context, and Normalization Layer (Layer 2b)

**Objective:** Validate extracted observations against raw source text, resolve contextual ambiguities, deterministically normalize numbers and dates, and group related facts.

#### D3.1: Independent Evidence Verifier Agent
* **Target Module:** `src/verification/verifier.py`
* **Functional Scope:**
  * Implement adversarial verification step: An independent agent call receives ONLY the raw content of the cited `EvidenceChunk` and the candidate `Observation.statement`.
  * Evaluate entailment: Check whether the raw source directly supports the claim, contradicts it, or contains insufficient context.
  * Assign provenance verification status: `ENTAILED`, `HALLUCINATED`, `AMBIGUOUS`.
* **Defensive Fail-Safe:** Any observation flagged as `HALLUCINATED` is immediately excluded from downstream decision grouping and logged in the trace as an ungrounded candidate.
* **Acceptance Criteria:** Synthetic hallucination test cases (where an observation claims a figure not present in the chunk) are correctly rejected with `HALLUCINATED` status.

#### D3.2: Context Resolver Agent
* **Target Module:** `src/verification/context.py`
* **Functional Scope:**
  * Disambiguate multidimensional financial qualifiers:
    * **Accounting Basis:** GAAP, Non-GAAP, Adjusted, IFRS.
    * **Organizational Scope:** Consolidated, Standalone, Segmental (e.g., North America, Cloud).
    * **Filing Type:** Press Release, Unaudited Preliminary, Audited 10-K / Annual Report.
    * **Restatement / Version:** Initial Filing, Amended (10-K/A), Restated.
* **Acceptance Criteria:** Correctly extracts and tags contextual dimensions from surrounding headers and footnote references.

#### D3.3: Pure Python Deterministic Normalizers
* **Target Module:** `src/verification/normalizers.py`
* **Functional Scope:**
  * **Financial Arithmetic Normalizer (`Decimal`):** Convert string values to exact Python `Decimal` objects. Normalize magnitude scales (Thousand -> 1e3, Million -> 1e6, Billion -> 1e9, Lakh -> 1e5, Crore -> 1e7). Never use standard IEEE 754 floating-point numbers.
  * **Currency Normalizer:** Standardize ISO currency codes (USD, INR, EUR, GBP). Currency conversion is strictly prohibited unless explicit exchange rate context is present in the source documents.
  * **Temporal Normalizer (`python-dateutil`):** Map fiscal and calendar dates to ISO 8601 intervals `(period_start, period_end)`. Support quarters (Q1, Q2, Q3, Q4, FY), trailing twelve months (TTM), and point-in-time dates.
* **Defensive Fail-Safe:** Unparseable strings or ambiguous periods fail gracefully to raw value retention with a normalization warning, rather than throwing uncaught exceptions.
* **Acceptance Criteria:** Complete unit test suite (`tests/unit/test_decimal_units.py`, `tests/unit/test_temporal_parsing.py`) achieves 100% pass rate across Indian (Crore/Lakh) and Western (Million/Billion) number systems.

#### D3.4: Candidate Fact Grouping & Blocking Engine
* **Target Module:** `src/matching/embeddings.py`
* **Functional Scope:**
  * Formulate `FactCandidate` from verified observations and normalized values.
  * Implement two-tier candidate blocking:
    1. **Hard Blocking:** Filter candidates by exact entity match and temporal interval overlap.
    2. **Soft Semantic Matching:** Compute cosine similarity over `attribute` descriptions using the local `BAAI/bge-small-en-v1.5` embeddings.
  * Group facts with cosine similarity >= 0.82 into candidate `FactGroup` clusters for dispute resolution.
* **Acceptance Criteria:** Successfully groups "Revenues from operations" and "Operating Revenue" for the same fiscal quarter into a unified `FactGroup` without human intervention.

---

### Deliverable 4: Fact Decision Engine (Layer 3)

**Objective:** Implement the stateful LangGraph reasoning workflow to detect corroboration, formulate reconciliation hypotheses, execute adversarial skepticism, and apply deterministic decision policies.

#### D4.1: LangGraph Workflow Orchestrator
* **Target Module:** `src/decision/workflow.py`
* **Functional Scope:**
  * Construct a deterministic state graph governing pipeline execution:
    ```
    Input FactGroup
          |
          v
    [ Numerical Variance Check ]
       /                     \
    [Within Tol.]        [Exceeds Tol.]
     /                         \
    v                           v
    [CORROBORATED]      [Hypothesis Generation]
                                |
                                v
                        [Specialist Validators]
                                |
                                v
                        [Reconciliation Agent]
                                |
                                v
                        [Adversarial Challenge]
                                |
                                v
                        [Deterministic Decision Policy]
    ```
  * Maintain immutable, inspectable state at every graph node using Pydantic state representations.
* **Acceptance Criteria:** State graph transitions deterministically; runs without infinite recursion or uncontrolled agent loops.

#### D4.2: Hypothesis Generation & Specialist Validators
* **Target Module:** `src/decision/hypothesis.py`, `src/decision/validators.py`
* **Functional Scope:**
  * **Hypothesis Generator:** For variance exceeding tolerance (0.01%), propose structured hypotheses explaining the difference:
    * `RESTATEMENT`: Subsequent audit adjustment.
    * `ACCOUNTING_BASIS`: GAAP vs Non-GAAP variance.
    * `SCOPE_MISMATCH`: Standalone vs Consolidated entity.
    * `TIMING_DIFFERENCE`: Calendar quarter vs fiscal cycle variation.
    * `ERRONEOUS_CONTRADICTION`: Incompatible claims with no explanatory basis.
  * **Specialist Validators:** Pure Python and targeted LLM evaluators that test each hypothesis against available evidence:
    * `RestatementValidator`: Check document dates and explicit "restated" or "amended" keywords.
    * `ScopeValidator`: Verify corporate legal entity hierarchy.
    * `AccountingStandardValidator`: Check reconciliation bridge tables between GAAP and Non-GAAP.
* **Acceptance Criteria:** Emits structured validator outcomes indicating support, refutation, or inconclusive evidence for each hypothesis.

#### D4.3: Reconciliation and Adversarial Challenge Agents
* **Target Module:** `src/decision/reconciliation.py`
* **Functional Scope:**
  * **Reconciliation Proposer:** Synthesize supported validator findings into a candidate explanation (e.g., "Revenue difference of $15M represents stock-based compensation exclusion in Non-GAAP reporting").
  * **Adversarial Skeptic:** Critically attack the proposed reconciliation:
    * Does the source evidence explicitly confirm the arithmetic bridge?
    * Is there evidence that the two numbers refer to distinct entities or time frames?
    * If the reconciliation relies on unstated assumptions, flag as `UNGROUNDED_RECONCILIATION`.
* **Acceptance Criteria:** Reconciliations that cannot cite explicit textual or arithmetic evidence from the documents are downgraded to `CONTRADICTION` or `UNRESOLVED`.

#### D4.4: Deterministic Decision Policy Engine
* **Target Module:** `src/decision/policy.py`
* **Functional Scope:**
  * Implement strict, pure Python rules mapping validator and skeptic outcomes to final verdicts:
    * **CORROBORATED:** Values match within defined tolerance (e.g., <= 0.01% or exact textual agreement), same entity, same period, verified provenance.
    * **CONTRADICTION:** Mutually exclusive claims, same context, no valid reconciliation hypothesis supported by evidence.
    * **RECONCILED:** Variance verified by explicit evidence (restatement, GAAP bridge, organizational scope difference) that survives adversarial challenge.
    * **UNRESOLVED:** Missing context, unverified claims, contradictory non-reconciled evidence, or low confidence.
* **Defensive Fail-Safe:** If an error occurs anywhere in the reasoning chain, the fallback verdict is strictly `UNRESOLVED`. Never produce an unverified assertion.
* **Acceptance Criteria:** Policy engine executes zero LLM calls, evaluated 100% deterministically via unit tests across all edge conditions.

---

### Deliverable 5: Observability, Reporting, and Evaluation Testing (Layer 4)

**Objective:** Provide end-to-end auditability, human-readable executive and contradiction reports, and exhaustive test coverage across the mandatory assignment evaluation scenarios.

#### D5.1: Cryptographic Decision Trace Engine
* **Target Module:** `src/observability/trace.py`
* **Functional Scope:**
  * Record every intermediate state transformation, agent prompt, raw LLM completion, validation result, and policy rule fired into `decision_traces`.
  * Stream trace steps to `runs/JOB-{id}/traces/trace.jsonl`.
  * Ensure full provenance replay: Any third-party evaluator must be able to inspect why a specific verdict was reached from source coordinates.
* **Acceptance Criteria:** Generated JSONL log contains complete step-by-step chronology for every decision in the run.

#### D5.2: Automated Markdown Report Generators
* **Target Module:** `src/observability/reporters.py`
* **Functional Scope:**
  * **Executive Summary (`summary.md`):** High-level dashboard showing total documents parsed, evidence chunks created, fact groups evaluated, and breakdown of verdicts (Corroborated, Contradicted, Reconciled, Unresolved).
  * **Contradiction Report (`contradictions.md`):** Comprehensive report detailing all identified discrepancies, showing side-by-side claim comparisons, source document names, page numbers, bounding box snippets, and why reconciliation failed.
  * **Unresolved Analysis Report (`unresolved.md`):** Diagnostic breakdown of ambiguous observations, missing disclosures, or unentailed claims requiring human analyst review.
* **Acceptance Criteria:** Reports are cleanly formatted GitHub Flavored Markdown with file links, tables, and no extraneous emojis.

#### D5.3: Automated Test Suites
* **Target Module:** `tests/unit/`, `tests/contracts/`, `tests/evaluation/`
* **Functional Scope:**
  * **Unit Tests (`tests/unit/`):**
    * `test_decimal_units.py`: Validation of arithmetic and unit conversion logic.
    * `test_temporal_parsing.py`: Verification of calendar and fiscal interval resolution.
    * `test_decision_policy.py`: Full truth-table coverage of the pure Python decision policy.
  * **Contract Tests (`tests/contracts/`):**
    * Validate Pydantic schema serialization/deserialization against sample LLM outputs.
  * **Evaluation Tests (`tests/evaluation/`):**
    * End-to-end integration tests confirming pipeline integrity under real and synthetic document inputs.
* **Acceptance Criteria:** `pytest` runs across all suites with 100% pass rate.

#### D5.4: Mandatory Assignment Evaluation Scenarios
* **Target Module:** `tests/evaluation/`
* **Functional Scope:**
  * Verify that the system correctly executes the four required evaluation cases:
    1. **Corroboration Benchmark:** Identical revenue/profit figures reported in Press Release and Form 10-K yield `CORROBORATED` with dual evidence links.
    2. **Direct Contradiction Benchmark:** Differing revenue numbers for the same entity, period, and accounting standard yield `CONTRADICTION` with highlighted variance.
    3. **Defensible Reconciliation Benchmark:** Preliminary vs Restated figures or GAAP vs Non-GAAP variances yield `RECONCILED` with explicit citation of restatement footnote or reconciliation bridge.
    4. **Defensive Failure Handling Benchmark:** Corrupted PDF text, missing pages, or ungrounded claims gracefully yield `UNRESOLVED` with diagnostic warnings rather than system crashes or false verdicts.
* **Acceptance Criteria:** All four benchmark scenarios produce expected verdicts and audit traces in automated evaluation runs.

---

## 4. Deliverable Phase Gate Verification Protocol

To maintain architectural integrity, no delivery phase may begin until the preceding phase satisfies 100% of its exit criteria:

```
+---------------+     +---------------+     +---------------+
| Phase D0 Gate | --> | Phase D1 Gate | --> | Phase D2 Gate |
| Prereqs Green |     | Ledger & API  |     | Extraction OK |
+---------------+     +---------------+     +---------------+
                            |
                            v
+---------------+     +---------------+     +---------------+
| Phase D5 Gate | <-- | Phase D4 Gate | <-- | Phase D3 Gate |
| Reports & E2E |     | Decision Graph|     | Normalization |
+---------------+     +---------------+     +---------------+
```

### Phase Gate Checklist

1. **Gate D0 -> D1:**
   * Python 3.11+ environment verified.
   * Core packages in `requirements.txt` installed without conflict.
   * Local Ollama daemon running and responding.
   * `qwen2.5:7b-instruct` model weights verified.
   * `BAAI/bge-small-en-v1.5` cached locally.

2. **Gate D1 -> D2:**
   * SQLite database schema creates all 10 relational tables.
   * CRUD queries in `src/db/ledger.py` pass automated unit tests.
   * FastAPI runs and serves Swagger documentation at `/docs`.
   * CLI entry point `python -m src.cli.main` executes without error.

3. **Gate D2 -> D3:**
   * PyMuPDF extracts text blocks and bounding boxes from sample PDFs.
   * pdfplumber extracts structured tables with cell coordinates.
   * Evidence chunks possess deterministic SHA-256 identifiers.
   * Extraction agents produce Pydantic-validated `Observation` objects.

4. **Gate D3 -> D4:**
   * Evidence Verifier catches synthetic hallucinated observations.
   * Decimal normalizer processes crore, lakh, million, billion, and thousand scales.
   * Date normalizer maps fiscal quarters and calendar years to ISO intervals.
   * BGE-small embeddings group semantically equivalent facts into `FactGroup` clusters.

5. **Gate D4 -> D5:**
   * LangGraph state graph compiles and executes branching flows.
   * Specialist validators evaluate restatement, accounting basis, and scope hypotheses.
   * Adversarial skeptic rejects ungrounded reconciliations.
   * Pure Python decision policy emits correct verdicts (`CORROBORATED`, `CONTRADICTION`, `RECONCILED`, `UNRESOLVED`).

6. **Gate D5 -> Final Sign-off:**
   * Cryptographic decision trace logs written to `runs/JOB-{id}/traces/`.
   * Executive Summary, Contradiction Report, and Unresolved Report generated as clean Markdown.
   * Unit test suite, contract test suite, and evaluation test suite pass at 100%.
   * All 4 mandatory assignment evaluation scenarios pass validation.
