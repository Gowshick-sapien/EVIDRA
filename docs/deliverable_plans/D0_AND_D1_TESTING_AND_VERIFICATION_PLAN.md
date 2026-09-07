# EVIDRA: Evidence-Driven Architecture for Fact Validation and Knowledge Reasoning

## D0 and D1 Testing and Verification Plan

---

## 1. Testing Philosophy and Quality Architecture

The Fact Knowledge Layer (**EVIDRA**) enforces a rigorous quality assurance methodology anchored in its core epistemic thesis:
1. **Mathematical and Epistemic Determinism:** All financial arithmetic, unit conversions, date logic, and final verdict rules must be covered by deterministic unit tests with 100% truth-table coverage.
2. **Contract-Driven Boundaries:** All LLM inputs and outputs, REST API requests, and CLI arguments must be validated against strict Pydantic models.
3. **Reproducible Provenance:** Every test case evaluating a decision must confirm that foreign key relationships trace cleanly back to physical document IDs and PDF coordinates.
4. **Zero-Flake Local Execution:** Automated suites must execute entirely on the local machine without cloud API keys, paid accounts, or external network calls.

### Testing Pyramid

```
                +-----------------------------+
                |    Epistemic Evaluation     |
                |   (4 Mandatory Benchmarks)  |
                +-----------------------------+
               /                               \
              +---------------------------------+
              |     Contract / Boundary Tests   |
              |   (FastAPI & Pydantic Schemas)  |
              +---------------------------------+
             /                                   \
            +-------------------------------------+
            |        Deterministic Unit Tests     |
            |   (Ledger CRUD, Normalizers, Policy)|
            +-------------------------------------+
           /                                       \
          +-----------------------------------------+
          |      Environment Diagnostic Checks      |
          |       (Python, Ollama, Embeddings)      |
          +-----------------------------------------+
```

---

## 2. Automated Testing Suites

### 2.1 Pre-Flight Environment Verification (`scripts/verify_env.py`)

* **Objective:** Validate that Python 3.11+, all core dependencies, the local Ollama daemon, and the `BAAI/bge-small-en-v1.5` embedding cache are ready.
* **Execution Command:**
  ```powershell
  python scripts/verify_env.py
  ```
* **Step-by-Step Procedure:**
  1. Opens terminal in repository root (`d:\projects\superjoin\EVIDRA`).
  2. Executes `python scripts/verify_env.py`.
  3. Probes Python version (verifies >= 3.11).
  4. Attempts imports for `fastapi`, `uvicorn`, `pydantic`, `fitz` (PyMuPDF), `pdfplumber`, `langgraph`, `langchain_core`, `langchain_ollama`, `sentence_transformers`, `dateutil`.
  5. Dispatches HTTP GET to `http://127.0.0.1:11434/api/version`.
  6. Queries `/api/tags` and dispatches test structured prompt enforcing `format: "json"`.
  7. Loads `BAAI/bge-small-en-v1.5` and generates a 384-dimensional test embedding.
* **Verified Terminal Output:**
  ```
  ==================================================
    EVIDRA - Fact Knowledge Layer D0 Verification   
  ==================================================
  [1/5] Checking Python Version...
        PASS: Python version compatible.
  [2/5] Checking Core Dependencies...
        PASS: All core dependencies installed.
  [3/5] Checking Ollama Runtime Connection...
        PASS: Ollama daemon active.
  [4/5] Checking Local LLM Model & Structured Generation...
        PASS: LLM structured inference operational.
  [5/5] Checking SentenceTransformer Embedding Cache...
        PASS: BAAI/bge-small-en-v1.5 cached and operational.
  ==================================================
  ALL D0 PREREQUISITE CHECKS PASSED SUCCESSFULLY.
  ```

---

### 2.2 Database and Ledger Unit Tests (`tests/unit/test_ledger.py`)

* **Target Module:** [src/db/ledger.py](file:///d:/projects/superjoin/EVIDRA/src/db/ledger.py), [src/db/schema.sql](file:///d:/projects/superjoin/EVIDRA/src/db/schema.sql)
* **Execution Command:**
  ```powershell
  pytest tests/unit/test_ledger.py -v
  ```
* **Test Cases Covered:**
  1. `test_schema_initialization`: Verifies that all 10 relational tables (`documents`, `evidence_chunks`, `observations`, `fact_candidates`, `fact_groups`, `group_members`, `hypotheses`, `validator_results`, `decisions`, `decision_traces`) are created on startup.
  2. `test_document_crud`: Verifies document insertion, retrieval, and unique constraint enforcement on `file_hash`.
  3. `test_evidence_chunks_and_observations`: Verifies chunk insertion with JSON-serialized bounding boxes `[x0, y0, x1, y1]` and foreign key linking from observations.
  4. `test_fact_grouping_and_decision_card`: Tests the entire relationship lifecycle (Facts -> Fact Group -> Hypothesis -> Validator Result -> Final Decision -> Audit Trace) and verifies that `get_decision_card` aggregates claims, provenance coordinates, and reasoning traces.
  5. `test_transaction_rollback`: Verifies that an invalid operation (e.g., referencing a non-existent chunk ID) triggers a clean transactional rollback without database corruption.

---

### 2.3 Observability and Run Context Tests (`tests/unit/test_trace.py`)

* **Target Module:** [src/observability/trace.py](file:///d:/projects/superjoin/EVIDRA/src/observability/trace.py)
* **Execution Command:**
  ```powershell
  pytest tests/unit/test_trace.py -v
  ```
* **Test Cases Covered:**
  1. `test_run_context_lifecycle`: Verifies that `RunContext` creates the isolated directory structure (`documents/`, `evidence/`, `reports/`, `traces/`) under `runs/JOB-{id}/`, serializes initial `run.json`, and updates status on completion.
  2. `test_trace_logger`: Verifies that `TraceLogger` appends valid JSON objects to `traces/trace.jsonl` with timestamps, agent names, latency in milliseconds, and optional `decision_id` links.

---

### 2.4 Command Line Interface Tests (`tests/unit/test_cli.py`)

* **Target Module:** [src/cli/main.py](file:///d:/projects/superjoin/EVIDRA/src/cli/main.py)
* **Execution Command:**
  ```powershell
  pytest tests/unit/test_cli.py -v
  ```
* **Test Cases Covered:**
  1. `test_cli_help`: Verifies that `evidra --help` renders without errors and lists subcommands: `process`, `inspect`, `report`, `serve`.
  2. `test_cli_process_single_pdf`: Verifies that passing a mock PDF file to the `process` command initializes an isolated run directory, records document metadata, and renders the ANSI summary table.
  3. `test_cli_inspect_job`: Verifies that `inspect <job_id>` opens the run database and renders formatted decision cards.
  4. `test_cli_report_json`: Verifies that `report <job_id> --format json` outputs the run manifest in valid JSON format.

---

### 2.5 REST API Contract Tests (`tests/contracts/test_api.py`)

* **Target Module:** [src/api/server.py](file:///d:/projects/superjoin/EVIDRA/src/api/server.py), [src/api/models.py](file:///d:/projects/superjoin/EVIDRA/src/api/models.py)
* **Execution Command:**
  ```powershell
  pytest tests/contracts/test_api.py -v
  ```
* **Test Cases Covered:**
  1. `test_health_check`: Probes `GET /health` and validates response schema (`status`, `sqlite`, `ollama`, `timestamp`).
  2. `test_create_job_and_poll_status`: Tests `POST /jobs` multipart upload, validates HTTP 202 response with `job_id`, and tests status polling via `GET /jobs/{job_id}`.
  3. `test_job_decisions_and_details`: Populates a test ledger with a decision and validates `GET /jobs/{job_id}/decisions`, verdict filtering (`?verdict=CORROBORATED`), and full Decision Card retrieval via `GET /jobs/{job_id}/decisions/{decision_id}`.
  4. `test_empty_file_upload_rejection`: Confirms defensive HTTP 422 response when an empty file is submitted.
  5. `test_nonexistent_job_returns_404`: Confirms HTTP 404 response when querying a non-existent job ID.

---

### 2.6 Full Automated Suite Execution

To run all automated test suites in a single command with summary reporting:

```powershell
pytest tests/ -v
```

Verified execution result:
```
tests/contracts/test_api.py .....                                        [ 31%]
tests/unit/test_cli.py ....                                              [ 56%]
tests/unit/test_ledger.py .....                                          [ 87%]
tests/unit/test_trace.py ..                                              [100%]

======================== 16 passed, 1 warning in 0.78s ========================
```

---

## 3. Manual Verification Suite (Interactive Procedures)

Manual verification procedures allow evaluators, analysts, and operators to interactively audit the system at every layer.

---

### Manual Test Case MTC-01: Environment and Ollama Runtime Probing

* **Goal:** Verify Ollama daemon accessibility and live structured JSON generation independently of automated test harnesses.
* **Prerequisites:** Ollama daemon running (`ollama serve`).

#### Step-by-Step Procedure
1. **Check Ollama Daemon Version:**
   ```powershell
   Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/version" -Method Get
   ```
   *Pass Criteria:* Returns JSON with `version` string (e.g. `0.32.4`).

2. **List Available Models:**
   ```powershell
   Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" -Method Get | Select-Object -ExpandProperty models | Format-Table name, size
   ```
   *Pass Criteria:* Displays list of installed local models (e.g. `qwen2.5:3b`).

3. **Verify Structured JSON Generation:**
   ```powershell
   $body = @{
       model = "qwen2.5:3b"
       prompt = "Return a JSON object with keys: entity (string) and test (string, value OK). Output ONLY valid JSON."
       stream = $false
       format = "json"
   } | ConvertTo-Json

   $response = Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/generate" -Method Post -Body $body -ContentType "application/json"
   $response.response
   ```
   *Pass Criteria:* Terminal outputs a valid JSON object: `{"entity": "...", "test": "OK"}`.

---

### Manual Test Case MTC-02: SQLite Evidence Ledger Direct Inspection

* **Goal:** Manually inspect relational integrity, foreign key cascades, and data persistence directly inside the generated `ledger.db`.
* **Prerequisites:** A completed job run must exist in `runs/` (created via CLI `process` or API `POST /jobs`).

#### Step-by-Step Procedure
Execute the automated turnkey verification script:
```powershell
python scripts/verify_manual.py
```

*Pass Criteria (Verified Output):*
```text
==================================================
  EVIDRA MTC-02: SQLite Ledger Direct Inspection  
==================================================
Target Database: D:\projects\superjoin\EVIDRA\runs\JOB-...\ledger.db

[1/3] Tables in Ledger (10 tables):
      - decision_traces
      - decisions
      - documents
      - evidence_chunks
      - fact_candidates
      - fact_groups
      - group_members
      - hypotheses
      - observations
      - validator_results
      PASS: All 10 expected relational tables exist.

[2/3] Testing Foreign Key Enforcement...
      PASS: Foreign key constraint caught orphaned record: FOREIGN KEY constraint failed

[3/3] Inspecting Ledger Summary via EvidenceLedger...
      Documents count:        1
      Evidence chunks count:  0
      Fact candidates count:  0
      Decisions count:        0
      PASS: Summary statistics retrieved successfully.
```

---

### Manual Test Case MTC-03: FastAPI Interactive Swagger UI Verification

* **Goal:** Interactively test API endpoints and file upload capabilities through the browser interface.
* **Prerequisites:** `uvicorn` installed, server running via `python -m src.cli.main serve --port 8000`.

#### Technical Configuration Note
FastAPI defaults to OpenAPI 3.1.0, generating `contentMediaType: "application/octet-stream"` for `UploadFile` arrays without `"format": "binary"`. In Swagger UI, this causes array items to render as string fields rather than file picker controls. [src/api/server.py](file:///d:/projects/superjoin/EVIDRA/src/api/server.py) explicitly configures `openapi_version="3.0.2"` and normalizes array schemas to inject `format: "binary"`, ensuring native file selection.

#### Step-by-Step Procedure
1. **Launch API Server:**
   ```powershell
   python -m src.cli.main serve --port 8000
   ```
   *Pass Criteria:* Terminal prints `Starting EVIDRA API server on http://127.0.0.1:8000 (Swagger docs at /docs)...`

2. **Access Swagger UI:**
   Open a browser and navigate to:
   ```
   http://127.0.0.1:8000/docs
   ```
   *Pass Criteria:* Browser displays Swagger UI titled **"EVIDRA - Evidence-Driven Architecture for Fact Validation and Knowledge Reasoning"** with endpoint tags: `Health`, `Jobs`, `Decisions`, `Reports`.

3. **Test `GET /health`:**
   Expand `GET /health`, click **Try it out**, then **Execute**.
   *Pass Criteria:* Returns HTTP 200 with JSON payload:
   ```json
   {
     "status": "OK",
     "sqlite": "READY",
     "ollama": "CONNECTED",
     "timestamp": "2026-09-07T..."
   }
   ```

4. **Test `POST /jobs` File Upload:**
   * Expand `POST /jobs`, click **Try it out**.
   * Under **Request body**, locate `files * array<string>` and click **Add string item**.
   * An item row appears containing a native **Choose File** (or **Browse...**) button.
   * Click **Choose File** and select `sample_docs/sample_earnings.pdf`.
   * Click **Execute**.
   * *Verified Response (HTTP 202 Accepted):*
     ```json
     {
       "job_id": "JOB-20260907-181006-dbba83",
       "status": "PENDING",
       "created_at": "2026-09-07T18:10:06.327301+00:00",
       "file_count": 1,
       "message": "Job created and queued for execution."
     }
     ```

5. **Test `GET /jobs/{job_id}`:**
   * Expand `GET /jobs/{job_id}`, click **Try it out**.
   * In `job_id`, enter `JOB-20260907-181006-dbba83`.
   * Click **Execute**.
   * *Verified Response (HTTP 200 OK):*
     ```json
     {
       "job_id": "JOB-20260907-181006-dbba83",
       "status": "PROCESSING",
       "created_at": "2026-09-07T18:10:06.253297+00:00",
       "completed_at": null,
       "input_files": [
         "sample_earnings.pdf"
       ],
       "summary": {
         "documents_count": 0,
         "evidence_chunks_count": 0,
         "observations_count": 0,
         "fact_candidates_count": 0,
         "fact_groups_count": 0,
         "decisions_count": 0,
         "verdicts": {
           "CORROBORATED": 0,
           "CONTRADICTION": 0,
           "RECONCILED": 0,
           "UNRESOLVED": 0
         }
       },
       "errors": []
     }
     ```

---

### Manual Test Case MTC-04: CLI Workflow Verification

* **Goal:** Verify that the zero-dependency CLI operates correctly from the terminal for processing, inspecting, and exporting job data.

#### Step-by-Step Procedure
1. **Execute CLI `process` Subcommand:**
   ```powershell
   python -m src.cli.main process sample_docs/
   ```
   *Verified Output:*
   ```text
   ============================================================
     EVIDRA Fact Knowledge Layer - Job Summary
   ============================================================
     Job ID:            JOB-20260907-181558-564240
     Run Directory:     runs\JOB-20260907-181558-564240
     Documents Ingested:1
     Evidence Chunks:   0
     Fact Candidates:   0
     Decisions Made:    0
   ------------------------------------------------------------
     Corroborated:      0
     Contradictions:    0
     Reconciled:        0
     Unresolved:        0
   ============================================================
   ```

2. **Execute CLI `inspect` Subcommand:**
   Query decisions for the job (do not enclose Job ID in `<>` brackets in PowerShell):
   ```powershell
   python -m src.cli.main inspect JOB-20260907-181006-dbba83
   ```
   *Verified Output:*
   ```text
   No decisions found for job 'JOB-20260907-181006-dbba83'.
   ```

3. **Execute CLI `report` Subcommand:**
   Export the full run manifest as formatted JSON:
   ```powershell
   python -m src.cli.main report JOB-20260907-181006-dbba83 --format json
   ```
   *Verified Output:*
   ```json
   {
     "job_id": "JOB-20260907-181006-dbba83",
     "status": "PROCESSING",
     "created_at": "2026-09-07T18:10:06.253297+00:00",
     "completed_at": null,
     "input_files": [
       "sample_earnings.pdf"
     ],
     "summary": {},
     "errors": []
   }
   ```

---

### Manual Test Case MTC-05: Audit Trace and Provenance Inspection

* **Goal:** Verify that streaming audit traces in `trace.jsonl` are strictly chronological, well-formed, and contain all required telemetry metadata.
* **Prerequisites:** A completed job run via CLI `process` or API `POST /jobs`.

#### Step-by-Step Procedure
Execute via [scripts/verify_manual.py](file:///d:/projects/superjoin/EVIDRA/scripts/verify_manual.py):
```powershell
python scripts/verify_manual.py
```

*Verified Output:*
```text
==================================================
  EVIDRA MTC-05: Audit Trace Stream Inspection    
==================================================
Target Trace: D:\projects\superjoin\EVIDRA\runs\JOB-...\traces\trace.jsonl
      Total trace entries logged: 1
      Entry 1: [2026-09-07T18:17:07.295572+00:00] Step: document_ingestion | Agent: cli_pipeline
      PASS: Streaming audit records are well-formed and schema-compliant.

==================================================
ALL MANUAL VERIFICATIONS (MTC-02 to MTC-05) PASSED
==================================================
```

---

## 4. Test Maintenance and Troubleshooting Guide

### 4.1 SQLite Database Locked (`sqlite3.OperationalError: database is locked`)
* **Root Cause:** Multiple concurrent processes writing to SQLite without WAL mode or insufficient timeout.
* **Resolution:** Ensure all connections execute `PRAGMA journal_mode = WAL;` and configure `timeout=5.0` on connection initialization (implemented in `src/db/ledger.py`).

### 4.2 Ollama Connection Refused (`ECONNREFUSED` on port 11434)
* **Root Cause:** The Ollama background service is not running on the Windows host.
* **Resolution:** Open a terminal and run `ollama serve`, or launch the Ollama Windows tray application.

### 4.3 `python-multipart` Missing during File Upload
* **Root Cause:** FastAPI requires `python-multipart` for `UploadFile = File(...)`.
* **Resolution:** Run `pip install python-multipart` (already included in `requirements.txt`).

### 4.4 Port 8000 Conflict
* **Root Cause:** Another local development process is using port 8000.
* **Resolution:** Specify an alternative port using `python -m src.cli.main serve --port 8080`.

### 4.5 Swagger UI Array File Upload (`array<string>` in OpenAPI 3.1)
* **Root Cause:** FastAPI defaults to OpenAPI 3.1.0 where array items use `contentMediaType: "application/octet-stream"`. Swagger UI treats these as text items rather than file pickers.
* **Resolution:** In `src/api/server.py`, set `openapi_version="3.0.2"` in `FastAPI(...)` and `get_openapi(...)`. Normalize schemas to set `items: {"type": "string", "format": "binary"}` and strip `contentMediaType`. In the UI, click **Add string item** to display the file picker.

### 4.6 PowerShell Reserved Operator `<` with Placeholders
* **Root Cause:** Running commands with placeholder brackets (e.g. `inspect <JOB_ID>`) fails with `The '<' operator is reserved for future use.`
* **Resolution:** Provide literal Job IDs without angle brackets (e.g. `inspect JOB-20260907-181006-dbba83`).

### 4.7 Windows Case-Insensitive Path Matching in Glob
* **Root Cause:** In Windows PowerShell, matching `*.pdf` and `*.PDF` returns duplicate entries for the same file, violating the unique constraint on `documents.file_hash`.
* **Resolution:** In `src/cli/main.py`, de-duplicate paths using canonical resolved paths (`p.resolve().lower()`).

---

## 5. Deliverables D0 and D1 Execution Verification Matrix

| Test ID | Category | Component Tested | Execution Command | Result |
| :--- | :--- | :--- | :--- | :--- |
| **ATC-01** | Diagnostic | Python, Ollama, Models, Embeddings | `python scripts/verify_env.py` | **PASS** |
| **ATC-02** | Unit | SQLite Ledger (10 tables, CRUD, Rollbacks) | `pytest tests/unit/test_ledger.py -v` | **PASS** |
| **ATC-03** | Unit | RunContext & TraceLogger JSONL Streaming | `pytest tests/unit/test_trace.py -v` | **PASS** |
| **ATC-04** | Unit | CLI Subcommands (`process`, `inspect`, `report`) | `pytest tests/unit/test_cli.py -v` | **PASS** |
| **ATC-05** | Contract | FastAPI Server (Health, Jobs, Decisions) | `pytest tests/contracts/test_api.py -v` | **PASS** |
| **MTC-01** | Manual | Ollama Daemon & Structured JSON Output | Direct PowerShell REST probing | **PASS** |
| **MTC-02** | Manual | SQLite Direct Inspection & Foreign Keys | `python scripts/verify_manual.py` | **PASS** |
| **MTC-03** | Manual | Swagger UI Interactive File Upload & Status | `http://127.0.0.1:8000/docs` | **PASS** |
| **MTC-04** | Manual | CLI Workflow Execution (`process`, `inspect`, `report`) | `python -m src.cli.main ...` | **PASS** |
| **MTC-05** | Manual | Streaming Audit Traces (`trace.jsonl`) | `python scripts/verify_manual.py` | **PASS** |

**Status:** Deliverables D0 and D1 are fully implemented, tested, and verified with a 100% pass rate. Ready to proceed to **Deliverable 2: Document Processing and Extraction Layer**.
