# EVIDRA 2.0: System Execution and Evaluation Run Plan

## Operational Verification Runbook for Evaluators, Auditors, and Technical Reviewers

> **System Version:** EVIDRA 2.0  
> **Development Branch:** `dev_v2`  
> **Target Audience:** Technical Evaluators, System Auditors, Academic Examiners  
> **Compliance:** Zero-LLM Deterministic Verdict Gate, SQLite WAL Audit Ledger, Zero Emojis  

---

## 1. Executive Overview and Objective

This runbook provides complete, reproducible operational instructions for executing, evaluating, and auditing the **EVIDRA 2.0** Fact Knowledge Layer.

EVIDRA evaluates financial disclosures across corporate filings (Prospectuses, Annual Reports, Earnings Presentations, Press Releases) to adjudicate whether numerical claims:
1. **CORROBORATED:** Independently match across disparate sources within 0.01% arithmetic tolerance.
2. **CONTRADICTION:** Mutually conflict under identical contextual parameters where all reconciliation hypotheses have been falsified.
3. **RECONCILED:** Diverge due to documented structural variations (Accounting Basis, reporting scope, or audit restatements) that survive adversarial challenge.
4. **UNRESOLVED:** Cannot be resolved due to single-source isolation, unentailed observations, or insufficient disclosures.

This document details:
- Pre-flight environment diagnostics and dependency validation.
- Command Line Interface (CLI) execution and multi-document processing options.
- Interactive FastAPI REST API server operation and Swagger UI inspection.
- Complete verification procedures:
  - Full automated regression suite (100 passing tests).
  - SQLite WAL evidence ledger verification (`ledger.db`).
  - Cryptographic timeline replaying (`trace.jsonl`).
  - Human-readable markdown audit reports (`summary.md`, `contradictions.md`, `unresolved.md`).
  - Four canonical demonstration cases verified on real Delhivery corporate data.

---

## 2. Environment Preparation and Prerequisites

EVIDRA 2.0 executes on local infrastructure without external cloud API dependencies or recurring service costs.

### 2.1 Hardware and Software Requirements
- **Operating System:** Windows 10/11, macOS, or Linux (x86_64 or ARM64).
- **Python:** Version 3.11 or 3.12 (Python 3.12.2 tested and verified).
- **Local LLM Engine:** [Ollama](https://ollama.com/) running locally at `http://127.0.0.1:11434`.
- **LLM Model:** `qwen2.5:3b` (default high-efficiency model) or `qwen2.5:7b-instruct`.
- **Memory:** Minimum 8 GB RAM (16 GB recommended for multi-document parsing).

### 2.2 Step 1: Install Python Dependencies
From the repository root, install the required packages:
```powershell
pip install -r requirements.txt
```

### 2.3 Step 2: Start and Verify Ollama Local Daemon
Ensure Ollama is running and has the required model pulled:
```powershell
# Start Ollama service (if not already running as a system service)
ollama serve

# In a separate terminal, pull the model
ollama pull qwen2.5:3b
```

### 2.4 Step 3: Run Pre-Flight Environment Diagnostic
Verify the execution environment, Python dependencies, local database engine, Ollama connectivity, and embedding cache:
```powershell
python scripts/verify_env.py
```

Expected diagnostic output:
```text
============================================================
  EVIDRA Pre-Flight Environment Diagnostics
============================================================
[1/5] Checking Python Version...
      Python 3.12.2 detected. [PASS]
[2/5] Checking Core Dependencies...
      fitz (PyMuPDF): INSTALLED
      pdfplumber: INSTALLED
      pydantic: INSTALLED
      langgraph: INSTALLED
      fastapi: INSTALLED
      uvicorn: INSTALLED
      sqlite3: INSTALLED
[3/5] Checking Ollama Local Server Readiness...
      Ollama responding on http://127.0.0.1:11434. [PASS]
      Model 'qwen2.5:3b' is loaded and ready. [PASS]
[4/5] Checking SQLite Database Engine...
      SQLite operational. [PASS]
[5/5] Checking SentenceTransformer Embedding Model...
      BGE-Small embedding model ready. [PASS]
============================================================
  ALL PRE-FLIGHT DIAGNOSTICS PASSED
============================================================
```

---

## 3. Document Submission and Execution Interfaces

EVIDRA supports two primary interfaces for submitting PDF documents: the **Command Line Interface (CLI)** and the **FastAPI REST API**.

### 3.1 Method A: Command Line Interface (CLI)

The CLI tool (`src/cli/main.py`) provides fine-grained control over extraction budgets and document paths.

#### Option 1: Process a Single PDF Excerpt
```powershell
python -m src.cli.main process sample_docs/01-delhivery-prospectus-2022-excerpt.pdf --max-chunks 15
```

#### Option 2: Process an Entire Directory of Corporate Filings
```powershell
python -m src.cli.main process sample_docs/ --max-chunks 15
```

#### Option 3: Process Multiple Explicit Corporate Filings
```powershell
python -m src.cli.main process `
  sample_docs/01-delhivery-prospectus-2022-excerpt.pdf `
  sample_docs/02-delhivery-annual-report-2024-excerpt.pdf `
  sample_docs/03-delhivery-earnings-presentation-q4fy24.pdf `
  --max-chunks 30
```

#### Available CLI Processing Flags:
- `--out-dir <PATH>`: Base output directory for job runs (default: `runs/`).
- `--max-chunks <N>`: Maximum candidate evidence chunks to evaluate per document (default: 30 in P0/P1). 100% of detected financial tables are preserved first.
- `--all-chunks`: Ingest and evaluate all layout chunks across the documents without budget limits.
- `--fast`: Fast execution mode for rapid verification.
- `--skip-llm`: Ingest document layout, extract structural tabular grids directly from `pdfplumber`, and bypass generative LLM inference.
- `--verbose`: Output step-by-step terminal execution traces.

---

### 3.2 Method B: FastAPI REST API and Interactive Swagger UI

EVIDRA includes a production-grade FastAPI server supporting asynchronous job creation, multi-file uploads, status polling, and report retrieval.

#### Step 1: Start the API Server
```powershell
python -m src.cli.main serve --port 8000
```
Or run directly via uvicorn:
```powershell
uvicorn src.api.server:app --host 127.0.0.1 --port 8000
```

#### Step 2: Access Interactive Swagger UI
Open your browser and navigate to:
```
http://127.0.0.1:8000/docs
```

#### Step 3: Upload Files via Swagger UI
1. Navigate to the `POST /api/v1/jobs` endpoint (`Create Job`).
2. Click **Try it out**.
3. Under the `files` field, upload files from disk (select one or multiple PDFs from `sample_docs/`).
4. Click **Execute**.
5. The API responds with HTTP 202 Accepted and a JSON payload containing the assigned `job_id`:
   ```json
   {
     "job_id": "JOB-20260908-123217-9b5337",
     "status": "PROCESSING",
     "message": "Job created with 3 files queued for background processing.",
     "files": [
       "01-delhivery-prospectus-2022-excerpt.pdf",
       "02-delhivery-annual-report-2024-excerpt.pdf",
       "03-delhivery-earnings-presentation-q4fy24.pdf"
     ]
   }
   ```

#### Step 4: Upload Files via cURL
```powershell
curl -X POST "http://127.0.0.1:8000/api/v1/jobs" `
  -H "accept: application/json" `
  -H "Content-Type: multipart/form-data" `
  -F "files=@sample_docs/01-delhivery-prospectus-2022-excerpt.pdf" `
  -F "files=@sample_docs/02-delhivery-annual-report-2024-excerpt.pdf"
```

---

## 4. Run Directory Structure and Artifact Organization

Every job execution creates a strictly isolated, cryptographically audited job folder in `runs/JOB-<TIMESTAMP>-<HASH>/`:

```text
runs/JOB-20260908-123217-9b5337/
|-- documents/                  # Copied source PDF files with SHA-256 validation
|   |-- 01-delhivery-prospectus-2022-excerpt.pdf
|   |-- 02-delhivery-annual-report-2024-excerpt.pdf
|   +-- 03-delhivery-earnings-presentation-q4fy24.pdf
|-- evidence/                   # Chunk representations and structural table masks
|   |-- tables/                 # Extracted markdown table files
|   |-- *_manifest.json         # Document chunk geometry and bounding boxes
|   +-- *_schema.json           # Dynamically induced corporate schemas
|-- reports/                    # Production audit deliverables
|   |-- summary.md              # Executive dashboard report
|   |-- contradictions.md       # Detailed Contradictions audit
|   |-- unresolved.md           # Unresolved disclosures analysis
|   +-- summary.json            # Machine-readable programmatic JSON export
|-- traces/                     # Cryptographic decision trace logs
|   +-- trace.jsonl             # Append-only chronological trace stream
|-- ledger.db                   # Isolated SQLite WAL evidence database
+-- run.json                    # Job manifest with lifecycle timestamps and metrics
```

---

## 5. Verification and Audit Procedures

Evaluators can verify EVIDRA through five independent inspection layers.

### 5.1 Verification Layer 1: Automated Test Suite (100 Passing Tests)

Execute the full automated test suite covering unit tests, API contracts, and evaluation scenarios:
```powershell
pytest tests/ -v
```

Expected summary (100% Passing in ~68s):
```text
tests\contracts\test_api.py .......                                      [  7%]
tests\evaluation\test_scenarios.py .....                                 [ 12%]
tests\unit\test_4gate_resolution.py ......                               [ 18%]
tests\unit\test_claim_graph.py ....                                      [ 22%]
tests\unit\test_cli.py ......                                            [ 28%]
tests\unit\test_decimal_units.py .....                                   [ 33%]
tests\unit\test_decision.py ...........                                  [ 44%]
tests\unit\test_extraction.py ...                                        [ 47%]
tests\unit\test_identity.py .......                                      [ 54%]
tests\unit\test_ledger.py .......                                        [ 61%]
tests\unit\test_llm.py ..                                                [ 63%]
tests\unit\test_p0_pipeline.py .....                                     [ 68%]
tests\unit\test_pdf.py ...                                               [ 71%]
tests\unit\test_schema_induction.py ...                                  [ 74%]
tests\unit\test_temporal_comparability.py ........                       [ 82%]
tests\unit\test_temporal_parsing.py .....                                [ 87%]
tests\unit\test_topology.py ...                                          [ 90%]
tests\unit\test_trace.py ..                                              [ 92%]
tests\unit\test_verification.py .....                                    [ 97%]
tests\unit\test_windows.py ...                                           [100%]

================= 100 passed, 3 warnings in 68.31s (0:01:08) ==================
```

---

### 5.2 Verification Layer 2: SQLite WAL Evidence Ledger Queries

Open the SQLite ledger generated in a job run using the Python or SQLite CLI to verify relational tables:

```powershell
# Query 1: Verify Fact Identities and Dimensional Measurement Semantics
python -c "import sqlite3; conn = sqlite3.connect('runs/JOB-20260908-123217-9b5337/ledger.db'); c = conn.cursor(); [print(r) for r in c.execute('SELECT fact_id, measurement_type, metric_family, metric_subtype, period_start, period_end FROM fact_identities LIMIT 5;').fetchall()];"

# Query 2: Verify Pairwise Claim Relationship Graph Edges and Variances
python -c "import sqlite3; conn = sqlite3.connect('runs/JOB-20260908-123217-9b5337/ledger.db'); c = conn.cursor(); [print(r) for r in c.execute('SELECT relationship_id, group_id, source_fact_id, target_fact_id, relationship_type, variance_percentage FROM claim_relationships LIMIT 5;').fetchall()];"

# Query 3: Verify Zero Cross-Measurement Contamination in Fact Groups
python -c "import sqlite3; conn = sqlite3.connect('runs/JOB-20260908-123217-9b5337/ledger.db'); c = conn.cursor(); query = '''SELECT g.group_id, count(DISTINCT i.measurement_type) FROM fact_groups g JOIN fact_identities i ON i.fact_id IN (SELECT value FROM json_each(g.fact_ids_json)) GROUP BY g.group_id HAVING count(DISTINCT i.measurement_type) > 1;'''; res = c.execute(query).fetchall(); print('Cross-Measurement Groups (Must be 0):', len(res));"

# Query 4: Breakdown of Adjudicated Epistemic Verdicts
python -c "import sqlite3; conn = sqlite3.connect('runs/JOB-20260908-123217-9b5337/ledger.db'); c = conn.cursor(); [print(r) for r in c.execute('SELECT verdict, decision_strength, count(*) FROM decisions GROUP BY verdict, decision_strength;').fetchall()];"
```

Expected Output:
```text
('CONTRADICTION', 'HIGH', 1)
('CORROBORATED', 'HIGH', 3)
('UNRESOLVED', 'LOW', 44)
```

---

### 5.3 Verification Layer 3: Cryptographic Trace Replayer

To verify that the system is fully deterministic, audit any execution by replaying its streaming JSONL trace log:

```powershell
python -m src.cli.main replay runs/JOB-20260908-123217-9b5337/traces/trace.jsonl
```

The trace replayer parses the chronological event log, renders step durations, verifies cryptographic chunk hashes, and outputs an audit summary.

---

### 5.4 Verification Layer 4: Production Audit Reports

Inspect the generated Markdown reports in `runs/JOB-<timestamp>/reports/`:
- **`summary.md`:** Executive breakdown of ingested documents, evidence chunks, extracted observations, normalized fact candidates, and final decision distributions.
- **`contradictions.md`:** Detailed audit of every detected conflict, showing competing claims side-by-side with physical PDF coordinates $[x_0, y_0, x_1, y_1]$, verbatim evidence text, evaluated hypotheses, and adversary skeptic falsification status.
- **`unresolved.md`:** Complete audit of single-source or inconclusive facts, documenting the exact reason why a decision could not be reached.

---

## 6. Real-World Demonstration Walkthrough (Delhivery Prospectus)

The Delhivery starter dataset demonstrates the four required canonical epistemic outcomes:

### Case 1: Corroboration (Revenue from Operations)
- **Source:** `sample_docs/01-delhivery-prospectus-2022-excerpt.pdf` (Page 22 vs Page 27).
- **Observation:** `Revenue from operations` for the year ended March 31, 2021 stated as `36,465.27 million INR` in both table excerpts.
- **System Behavior:**
  1. `DocumentTopologyBuilder` extracts tables with stated unit `million` and currency `INR`.
  2. `MeasurementClassifier` assigns `ABSOLUTE_VALUE`.
  3. `TemporalComparabilityClassifier` confirms `EXACT` period (`2021-04-01` to `2022-03-31`).
  4. 4-Gate resolution unifies candidates into `GRP-DELHIVERY-REV-FY21`.
  5. Value clustering detects 1 cluster ($\Delta = 0.0\%$).
  6. Verdict: `CORROBORATED` (Decision Strength: `HIGH`).

### Case 2: Genuine Contradiction (Intragroup Eliminations)
- **Source:** `sample_docs/01-delhivery-prospectus-2022-excerpt.pdf` (Page 22).
- **Observation:** Competing figures for intragroup eliminations: `-5.67`, `-4.56`, and `-1.98` million INR under identical reporting periods.
- **System Behavior:**
  1. Values are partitioned into 3 distinct numerical clusters.
  2. Pairwise tournament generates 3 `CONFLICTS_WITH` edges in `claim_relationships` with variance up to $65.08\%$.
  3. Hypothesis tournament evaluates `RESTATEMENT` and `ACCOUNTING_BASIS`; specialist validators refute reconciliation bridges.
  4. Verdict: `CONTRADICTION` (Decision Strength: `HIGH`). Recorded in `contradictions.md`.

### Case 3: Contextual Reconciliation (Operating Profit vs Adjusted EBITDA)
- **Observation:** Operating Profit of `INR 1,200 Cr` vs Adjusted EBITDA of `INR 1,450 Cr`.
- **System Behavior:**
  1. Gate 4 flags divergent accounting basis (`Ind AS` vs `Non-GAAP`).
  2. Group is routed to Path B (Contextual Reconciliation).
  3. `AccountingBasisValidator` confirms Non-GAAP bridge adding back share-based payments (ESOP) and depreciation.
  4. `AdversarialSkepticAgent` audits cited notes and verifies citations without unstated assumptions.
  5. Verdict: `RECONCILED` (Decision Strength: `HIGH`).

### Case 4: Audited Epistemic Failure (Single-Source Metric)
- **Observation:** Logistics fleet volume disclosure appearing in an isolated narrative block.
- **System Behavior:**
  1. `EvidenceSufficiencyGate` detects $N = 1$ candidate (`SINGLE_SOURCE_PENDING`).
  2. Decision engine fast-paths to `UNRESOLVED` (Decision Strength: `LOW`).
  3. Preserves claim in `reports/unresolved.md` awaiting second-source corroboration.

---

## 7. Operational Troubleshooting and FAQ

| Symptom | Probable Cause | Corrective Action |
| :--- | :--- | :--- |
| `Ollama connection refused` | Ollama daemon is not active on `127.0.0.1:11434`. | Run `ollama serve` in a dedicated terminal window. |
| `Model not found: qwen2.5:3b` | Required Ollama model has not been downloaded. | Run `ollama pull qwen2.5:3b`. |
| `SQLite database locked` | Concurrency conflict from prior abnormal exit. | Remove stale `.db-journal` files or kill orphan python processes. |
| `StarletteDeprecationWarning` | Third-party Starlette deprecation in test client. | Non-fatal warning; suppressed in production runs. |
