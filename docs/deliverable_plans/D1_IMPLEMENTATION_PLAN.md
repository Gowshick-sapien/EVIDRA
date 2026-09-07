# EVIDRA: Evidence-Driven Architecture for Fact Validation and Knowledge Reasoning

## Deliverable 1 (D1) Implementation Plan: Core Infrastructure and Evidence Ledger

---

## 1. Executive Overview and Epistemic Objective

Deliverable 1 (**D1**) establishes the foundational persistence, execution, and inspection infrastructure for the **Fact Knowledge Layer (EVIDRA)** system. 

The core architectural thesis of EVIDRA demands that:
1. **The Evidence Ledger is the Primary System of Record:** Decisions are never derived in transient memory or unpersisted LLM contexts. Every proposition, candidate, hypothesis, and verdict must enter a persistent relational database.
2. **Separation of Observation from Decision:** The database schema must strictly isolate raw document assertions (`observations`) from derived system verdicts (`decisions`).
3. **Reproducible Isolation:** Each processing run must initialize an independent job directory (`runs/JOB-{timestamp}-{uuid}/`) containing its own SQLite ledger, cached document evidence, Markdown reports, and streaming JSONL audit traces.
4. **Dual Interaction Modalities:** Programmatic access is provided via an asynchronous REST API (FastAPI with OpenAPI/Swagger UI), while human local evaluation is supported via a zero-dependency CLI (`argparse`).

---

## 2. Scope and Boundaries of Deliverable 1

### 2.1 In-Scope Deliverables
* **D1.1: SQLite Evidence Ledger:** Relational database schema across 10 tables, connection pooling, transactional context managers, parameterized queries, and typed record mapping.
* **D1.2: Artifact Storage Engine & Run Directory Hierarchy:** Deterministic creation and lifecycle management of isolated run folders under `runs/JOB-{id}/`.
* **D1.3: FastAPI REST Interface:** Asynchronous server exposing `/jobs`, `/jobs/{id}`, `/jobs/{id}/decisions`, `/jobs/{id}/reports/{type}`, and `/health` endpoints with interactive Swagger UI.
* **D1.4: Command Line Interface (CLI):** Full-featured terminal interface providing `process`, `inspect`, and `report` subcommands with ANSI-formatted terminal summary tables.
* **D1.5: Automated Test Suite:** Unit tests for ledger operations, contract tests for API endpoints, and CLI argument parsing tests.

### 2.2 Out-of-Scope (Deferred to D2-D5)
* PDF layout extraction and table parsing algorithms (Deferred to D2: `src/pdf/`).
* Local LLM prompt dispatch and extraction agents (Deferred to D2: `src/extraction/`, `src/llm/`).
* Evidence entailment verification and deterministic normalizers (Deferred to D3: `src/verification/`).
* LangGraph decision state machine and adversarial debate agents (Deferred to D4: `src/decision/`).

---

## 3. Requirements Coverage (SRS & NFR Mapping)

### 3.1 Functional Requirements (FR)
| SRS ID | Requirement Statement | D1 Implementation Mechanism |
|---|---|---|
| **OBS-REP-01** | Maintain an isolated relational Evidence Ledger across 10 structured tables with parameterized queries and atomic commits. | `src/db/schema.sql`, `src/db/ledger.py` |
| **OBS-REP-02** | Initialize dedicated run directory `runs/JOB-{timestamp}-{uuid}/` containing ledger, evidence, reports, and traces. | `src/observability/trace.py` (`RunContext`) |
| **OBS-REP-06** | Expose asynchronous REST endpoints for job creation, status polling, decision inspection, and report retrieval. | `src/api/server.py`, `src/api/models.py` |
| **OBS-REP-07** | Implement zero-dependency CLI supporting `process`, `inspect`, and `report` commands. | `src/cli/main.py` |

### 3.2 Non-Functional Requirements (NFR)
| NFR ID | Requirement Statement | D1 Implementation Mechanism |
|---|---|---|
| **NFR-DET-02** | Full Provenance Replay: Every decision must be traceable to raw PDF chunk coordinates. | Foreign key constraints linking `decisions` -> `fact_groups` -> `group_members` -> `fact_candidates` -> `observations` -> `evidence_chunks` -> `documents`. |
| **NFR-SEC-02** | SQL Injection Prevention: All queries must be strictly parameterized. | `EvidenceLedger` uses parameterized SQL exclusively; string concatenation is prohibited. |
| **NFR-PORT-01** | Platform Independence: Codebase must run seamlessly on Windows 10/11 and POSIX. | `pathlib.Path` used for all file system operations; SQLite handles OS-level file locking. |
| **NFR-PERF-01** | Storage Concurrency: Multi-threaded read access during background processing. | SQLite configured in WAL mode (`PRAGMA journal_mode = WAL;`) and busy timeout set to 5000ms. |

---

## 4. Relational Schema Architecture (SQLite DDL)

The Evidence Ledger schema consists of 10 tables organized into three relational layers: Evidence Layer, Fact Construction Layer, and Decision Layer.

```sql
-- Pragmas for performance and data integrity
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA busy_timeout = 5000;

-- ============================================================================
-- 1. EVIDENCE LAYER (Source Provenance)
-- ============================================================================

CREATE TABLE IF NOT EXISTS documents (
    document_id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    file_hash TEXT NOT NULL UNIQUE,
    page_count INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS evidence_chunks (
    chunk_id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL,
    page_number INTEGER NOT NULL,
    chunk_type TEXT CHECK(chunk_type IN ('text', 'table', 'figure')),
    bounding_box TEXT NOT NULL, -- JSON array: [x0, y0, x1, y1]
    content TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(document_id) REFERENCES documents(document_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_chunks_doc_page ON evidence_chunks(document_id, page_number);

-- ============================================================================
-- 2. FACT CONSTRUCTION LAYER (Claims & Normalization)
-- ============================================================================

CREATE TABLE IF NOT EXISTS observations (
    observation_id TEXT PRIMARY KEY,
    chunk_id TEXT NOT NULL,
    document_id TEXT NOT NULL,
    statement TEXT NOT NULL,
    entity TEXT NOT NULL,
    attribute TEXT NOT NULL,
    raw_value TEXT NOT NULL,
    observation_type TEXT CHECK(observation_type IN ('numerical', 'semantic', 'event')),
    temporal_scope TEXT NOT NULL,
    provenance_status TEXT CHECK(provenance_status IN ('ENTAILED', 'HALLUCINATED', 'AMBIGUOUS')),
    confidence REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(chunk_id) REFERENCES evidence_chunks(chunk_id) ON DELETE CASCADE,
    FOREIGN KEY(document_id) REFERENCES documents(document_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_observations_entity_attr ON observations(entity, attribute);

CREATE TABLE IF NOT EXISTS fact_candidates (
    fact_id TEXT PRIMARY KEY,
    observation_id TEXT NOT NULL UNIQUE,
    normalized_value TEXT NOT NULL,
    normalized_unit TEXT NOT NULL,
    normalized_currency TEXT NOT NULL,
    period_start TEXT NOT NULL, -- ISO 8601 YYYY-MM-DD
    period_end TEXT NOT NULL,   -- ISO 8601 YYYY-MM-DD
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(observation_id) REFERENCES observations(observation_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_facts_period ON fact_candidates(period_start, period_end);

CREATE TABLE IF NOT EXISTS fact_groups (
    group_id TEXT PRIMARY KEY,
    entity TEXT NOT NULL,
    attribute TEXT NOT NULL,
    period_id TEXT NOT NULL,
    member_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS group_members (
    group_id TEXT NOT NULL,
    fact_id TEXT NOT NULL,
    PRIMARY KEY(group_id, fact_id),
    FOREIGN KEY(group_id) REFERENCES fact_groups(group_id) ON DELETE CASCADE,
    FOREIGN KEY(fact_id) REFERENCES fact_candidates(fact_id) ON DELETE CASCADE
);

-- ============================================================================
-- 3. DECISION ENGINE LAYER (Reasoning, Hypotheses & Verdicts)
-- ============================================================================

CREATE TABLE IF NOT EXISTS hypotheses (
    hypothesis_id TEXT PRIMARY KEY,
    group_id TEXT NOT NULL,
    explanation_type TEXT NOT NULL,
    description TEXT NOT NULL,
    likelihood_score REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(group_id) REFERENCES fact_groups(group_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS validator_results (
    result_id TEXT PRIMARY KEY,
    hypothesis_id TEXT NOT NULL,
    validator_type TEXT NOT NULL,
    outcome TEXT CHECK(outcome IN ('SUPPORTED', 'REFUTED', 'INCONCLUSIVE')),
    details_json TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(hypothesis_id) REFERENCES hypotheses(hypothesis_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS decisions (
    decision_id TEXT PRIMARY KEY,
    group_id TEXT NOT NULL UNIQUE,
    verdict TEXT CHECK(verdict IN ('CORROBORATED', 'CONTRADICTION', 'RECONCILED', 'UNRESOLVED')),
    decision_strength TEXT CHECK(decision_strength IN ('HIGH', 'MEDIUM', 'LOW', 'INSUFFICIENT')),
    reasoning_summary TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(group_id) REFERENCES fact_groups(group_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_decisions_verdict ON decisions(verdict);

CREATE TABLE IF NOT EXISTS decision_traces (
    trace_id TEXT PRIMARY KEY,
    decision_id TEXT NOT NULL,
    step_name TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    input_json TEXT NOT NULL,
    output_json TEXT NOT NULL,
    execution_time_ms REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(decision_id) REFERENCES decisions(decision_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_traces_decision ON decision_traces(decision_id);
```

---

## 5. Software Architecture of D1 Components

### 5.1 Evidence Ledger Engine (`src/db/ledger.py`)

The `EvidenceLedger` class encapsulates all SQLite interactions:

```python
class EvidenceLedger:
    def __init__(self, db_path: Path | str):
        self.db_path = Path(db_path)
        self.initialize_schema()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=5.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")
        return conn

    @contextmanager
    def transaction(self):
        conn = self.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
```

#### Typed Record Schemas (Pydantic / Dataclasses)
* `DocumentRecord`: `document_id`, `filename`, `file_hash`, `page_count`.
* `EvidenceChunkRecord`: `chunk_id`, `document_id`, `page_number`, `chunk_type`, `bounding_box`, `content`, `content_hash`.
* `ObservationRecord`: `observation_id`, `chunk_id`, `document_id`, `statement`, `entity`, `attribute`, `raw_value`, `observation_type`, `temporal_scope`, `provenance_status`, `confidence`.
* `FactCandidateRecord`: `fact_id`, `observation_id`, `normalized_value`, `normalized_unit`, `normalized_currency`, `period_start`, `period_end`.
* `FactGroupRecord`: `group_id`, `entity`, `attribute`, `period_id`, `member_count`.
* `HypothesisRecord`: `hypothesis_id`, `group_id`, `explanation_type`, `description`, `likelihood_score`.
* `ValidatorResultRecord`: `result_id`, `hypothesis_id`, `validator_type`, `outcome`, `details_json`.
* `DecisionRecord`: `decision_id`, `group_id`, `verdict`, `decision_strength`, `reasoning_summary`.
* `DecisionTraceRecord`: `trace_id`, `decision_id`, `step_name`, `agent_name`, `input_json`, `output_json`, `execution_time_ms`.

#### Core Query API
* `insert_document(doc: DocumentRecord) -> str`
* `insert_evidence_chunks(chunks: list[EvidenceChunkRecord]) -> int`
* `insert_observations(observations: list[ObservationRecord]) -> int`
* `insert_fact_candidates(facts: list[FactCandidateRecord]) -> int`
* `create_fact_group(entity: str, attribute: str, period_id: str, fact_ids: list[str]) -> str`
* `insert_hypothesis(hyp: HypothesisRecord) -> str`
* `insert_validator_result(res: ValidatorResultRecord) -> str`
* `record_decision(decision: DecisionRecord) -> str`
* `append_decision_trace(trace: DecisionTraceRecord) -> str`
* `get_job_summary() -> dict[str, Any]`
* `get_decisions(verdict_filter: Optional[str] = None) -> list[dict[str, Any]]`
* `get_decision_card(decision_id: str) -> dict[str, Any]`

### 5.2 Run Directory and Trace Logger (`src/observability/trace.py`)

Each execution creates an isolated run environment:

```
runs/
+-- JOB-20260907-XXXXXX/
    |-- run.json             # Job metadata (timestamps, file list, status)
    |-- ledger.db            # SQLite database instance for this run
    |-- evidence/            # Cached chunk snippets and table snapshots
    |-- reports/             # Generated Markdown reports
    +-- traces/
        +-- trace.jsonl      # Streaming step-by-step cryptographic audit log
```

#### `RunContext` Specification
* Initializes directories on creation.
* Generates unique `job_id`: `JOB-{YYYYMMDD}-{HHMMSS}-{uuid4[:6]}`.
* Exposes resolved paths: `run_dir`, `db_path`, `evidence_dir`, `reports_dir`, `traces_dir`.
* Writes `run.json` on initialization and updates status on job completion or failure.

#### `TraceLogger` Specification
* Appends structured JSON lines to `trace.jsonl`.
* Fields per line: `timestamp`, `job_id`, `trace_id`, `step_name`, `agent_name`, `input_payload`, `output_payload`, `latency_ms`.

### 5.3 FastAPI REST Interface (`src/api/server.py` & `src/api/models.py`)

#### API Endpoints
1. `GET /health`
   * Diagnostic probe returning system health, SQLite status, and Ollama connectivity.
2. `POST /jobs`
   * Accepts multipart PDF uploads (`files: list[UploadFile]`).
   * Saves uploaded files into job run directory.
   * Dispatches background processing task.
   * Returns `202 Accepted` with `JobCreateResponse(job_id=..., status="PENDING")`.
3. `GET /jobs/{job_id}`
   * Returns `JobStatusResponse` with counts of processed documents, observations, facts, and decisions.
4. `GET /jobs/{job_id}/decisions`
   * Query parameters: `verdict` (optional filter: `CORROBORATED`, `CONTRADICTION`, `RECONCILED`, `UNRESOLVED`).
   * Returns list of decision summaries.
5. `GET /jobs/{job_id}/decisions/{decision_id}`
   * Returns detailed Decision Card including evidence citations, bounding boxes, and audit trace.
6. `GET /jobs/{job_id}/reports/{report_type}`
   * Query parameter `report_type`: `summary`, `contradictions`, `unresolved`.
   * Returns the raw Markdown report.

### 5.4 Command Line Interface (`src/cli/main.py`)

Standard library `argparse` implementation with subcommands:

1. `python -m src.cli.main process <path_to_pdf_or_dir> [--out-dir runs/] [--verbose]`
   * Scans target directory for PDF files.
   * Initializes `RunContext` and `EvidenceLedger`.
   * Dispatches pipeline execution.
   * Prints ANSI-formatted summary table showing document count, chunks, fact groups, and verdict breakdown.
2. `python -m src.cli.main inspect <job_id> [--verdict VERDICT]`
   * Opens `runs/<job_id>/ledger.db`.
   * Queries and prints decision cards in terminal.
3. `python -m src.cli.main report <job_id> [--format markdown|json]`
   * Outputs the executive summary or contradiction report to stdout or file.

---

## 6. Complete File Manifest for Deliverable 1

| File Path | Operation | Component | Purpose |
|---|---|---|---|
| `src/db/schema.sql` | **[NEW]** | Ledger | SQLite DDL for 10 tables, indices, and foreign key cascades. |
| `src/db/ledger.py` | **[NEW]** | Ledger | `EvidenceLedger` class, connection factory, CRUD methods, transactions. |
| `src/observability/trace.py` | **[NEW]** | Observability | `RunContext` directory manager, `TraceLogger` JSONL streaming. |
| `src/api/models.py` | **[NEW]** | API | Pydantic request/response models for all endpoints. |
| `src/api/server.py` | **[NEW]** | API | FastAPI application, CORS, Swagger UI, async endpoints. |
| `src/cli/main.py` | **[NEW]** | CLI | `argparse` CLI entry point (`process`, `inspect`, `report`). |
| `tests/unit/test_ledger.py` | **[NEW]** | Tests | Unit test suite for SQLite schema and `EvidenceLedger` CRUD. |
| `tests/contracts/test_api.py` | **[NEW]** | Tests | FastAPI `TestClient` contract tests for all REST endpoints. |
| `tests/unit/test_cli.py` | **[NEW]** | Tests | CLI argument parser and command execution tests. |

---

## 7. Defensive Edge Cases and Fail-Safe Handling

1. **SQLite Database Locking Under Concurrency:**
   * *Risk:* Multiple async workers or endpoints writing simultaneously produce `sqlite3.OperationalError: database is locked`.
   * *Defensive Measure:* Set `PRAGMA journal_mode = WAL;` and configure connection timeout to `5.0` seconds with retry loops.
2. **Foreign Key Integrity Violations:**
   * *Risk:* Inserting an observation referencing a non-existent `chunk_id` or `document_id`.
   * *Defensive Measure:* Enforce `PRAGMA foreign_keys = ON;`. Wrap all related insertions (Document + Chunks + Observations) in single atomic transactions. If any step fails, roll back completely.
3. **Corrupted or Unreadable Upload Files:**
   * *Risk:* User uploads non-PDF files or zero-byte files via `POST /jobs`.
   * *Defensive Measure:* Validate file magic bytes (`%PDF-`), verify file size > 0, and reject invalid uploads with HTTP 422 before initializing the run context.
4. **FastAPI Port Conflicts:**
   * *Risk:* Port 8000 is occupied by another local service.
   * *Defensive Measure:* Allow configurable port via `--port` argument or `PORT` environment variable, defaulting to 8000.

---

## 8. Step-by-Step Implementation Sequence

```
Step 1: Database DDL & Ledger Implementation
        * Create src/db/schema.sql
        * Implement src/db/ledger.py with connection pooling, transactions, and CRUD
        * Verify with tests/unit/test_ledger.py

Step 2: Run Hierarchy & Observability Context
        * Implement src/observability/trace.py (RunContext, TraceLogger)
        * Validate directory initialization and JSONL trace streaming

Step 3: FastAPI REST Server & Request Models
        * Define Pydantic models in src/api/models.py
        * Implement endpoints in src/api/server.py
        * Verify with tests/contracts/test_api.py

Step 4: Command Line Interface
        * Implement src/cli/main.py with argparse subcommands
        * Verify with tests/unit/test_cli.py

Step 5: Full Integration & D1 Gate Verification
        * Execute full pytest test suite
        * Verify Swagger UI at /docs and CLI help menu
```

---

## 9. Exhaustive Verification Plan & Acceptance Gates

### 9.1 Automated Tests Execution
```powershell
# 1. Run database unit tests
pytest tests/unit/test_ledger.py -v

# 2. Run API contract tests
pytest tests/contracts/test_api.py -v

# 3. Run CLI argument parsing tests
pytest tests/unit/test_cli.py -v

# 4. Run full test suite with coverage
pytest tests/ -v
```

### 9.2 Deliverable 1 Exit Criteria (Phase Gate D1 -> D2)
* [x] `schema.sql` initializes all 10 tables cleanly without syntax errors.
* [x] `EvidenceLedger` passes all CRUD, transaction, and rollback unit tests.
* [x] `RunContext` creates `runs/JOB-{id}/` hierarchy with correct permissions.
* [x] FastAPI server starts and responds to `/health` with HTTP 200.
* [x] FastAPI `/docs` renders Swagger UI with complete endpoint specifications.
* [x] CLI `python -m src.cli.main --help` displays all subcommands without errors.
* [x] 100% test pass rate across all D1 test suites.
