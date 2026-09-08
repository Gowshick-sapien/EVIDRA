# EVIDRA: System Execution and Evaluation Run Plan

## Operational Guide for Evaluators, Auditors, and Technical Reviewers

---

## 1. Executive Overview and Objective

This run plan provides a step-by-step operational guide for executing, testing, and evaluating the **EVIDRA** (Evidence-Driven Architecture for Fact Validation and Knowledge Reasoning) system.

EVIDRA evaluates financial disclosures across corporate filings (Prospectuses, Annual Reports, Earnings Presentations, Press Releases) to adjudicate whether numerical claims:
1. **CORROBORATED:** Independently match across disparate sources within 0.01% arithmetic tolerance.
2. **CONTRADICTION:** Mutually conflict under identical contextual parameters where all reconciliation hypotheses have been falsified.
3. **RECONCILED:** Diverge due to documented contextual variations (Accounting Standard differences, restatements, or organizational scopes) that survive adversarial challenge.
4. **UNRESOLVED:** Cannot be resolved due to insufficient disclosures, single-source isolation, or ungrounded assertions.

This document details:
- Environment preparation and pre-flight diagnostics.
- Methods for supplying and uploading PDF documents via CLI and REST API.
- Execution options (Production mode, Fast mode, and Interactive API server).
- Comprehensive verification procedures (Full test suite, turnkey diagnostic script, benchmark scenarios, cryptographic replay, and report audits).

---

## 2. Environment Preparation and Prerequisites

EVIDRA executes on local infrastructure without external cloud API dependencies or recurring service costs.

### 2.1 Hardware and Software Requirements
- **Operating System:** Windows 10/11, macOS, or Linux (x86_64 or ARM64).
- **Python:** Version 3.11 or 3.12 (Python 3.12.2 tested).
- **Local LLM Engine:** Ollama running locally at `http://127.0.0.1:11434`.
- **LLM Model:** `qwen2.5:3b` (default) or `qwen2.5:7b-instruct`.
- **Memory:** Minimum 8 GB RAM (16 GB recommended for multi-document parsing).

### 2.2 Step 1: Install Python Dependencies
From the repository root, install required packages:
```powershell
pip install -r requirements.txt
```

### 2.3 Step 2: Start and Verify Ollama Local Daemon
Ensure Ollama is running and has the required model pulled:
```powershell
# Start Ollama service (if not already running as a background service)
ollama serve

# In a separate terminal, pull the model
ollama pull qwen2.5:3b
```

### 2.4 Step 3: Run Pre-Flight Environment Diagnostic
Verify the execution environment, Python dependencies, local database engine, Ollama connectivity, and embedding cache:
```powershell
python scripts/verify_env.py
```
Expected output:
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

## 3. How to Upload and Supply PDF Files

EVIDRA supports two primary interfaces for submitting PDF documents: the **Command Line Interface (CLI)** and the **FastAPI REST API**.

### 3.1 Method A: Command Line Interface (CLI)

The CLI tool (`src/cli/main.py`) accepts single files, directories of files, or multiple distinct PDF paths.

#### Option 1: Process a Single PDF
```powershell
python -m src.cli.main process sample_docs/01-delhivery-prospectus-2022-excerpt.pdf
```

#### Option 2: Process an Entire Directory of PDFs
```powershell
python -m src.cli.main process sample_docs/
```

#### Option 3: Process Multiple Explicit PDF Documents Across Financial Years
```powershell
python -m src.cli.main process `
  sample_docs/01-delhivery-prospectus-2022-excerpt.pdf `
  sample_docs/02-delhivery-annual-report-fy24-excerpt.pdf `
  sample_docs/03-delhivery-q4-fy24-earnings-presentation.pdf `
  --fast `
  --max-chunks 2
```

#### Available CLI Processing Flags:
- `--out-dir <PATH>`: Base output directory for job runs (default: `runs/`).
- `--fast`: Fast execution mode. Uses high-confidence primary LLM extraction and soft-clustering while skipping secondary entailment LLM passes, accelerating multi-document runs.
- `--max-chunks <N>`: Maximum candidate text chunks to evaluate per document (default: 2).
- `--all-chunks`: Ingest and evaluate all layout chunks in the documents without restriction.
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
1. Navigate to the `POST /jobs` endpoint (`Create Job`).
2. Click **Try it out**.
3. Under the `files` field, click **Add string item** or upload files from disk (select one or multiple PDFs, e.g., from `sample_docs/`).
4. Click **Execute**.
5. The API responds with HTTP 202 Accepted and a JSON payload containing the assigned `job_id`:
   ```json
   {
     "job_id": "JOB-20260908-104500-abcdef",
     "status": "PROCESSING",
     "message": "Job created with 3 files queued for background processing.",
     "files": [
       "01-delhivery-prospectus-2022-excerpt.pdf",
       "02-delhivery-annual-report-fy24-excerpt.pdf",
       "03-delhivery-q4-fy24-earnings-presentation.pdf"
     ]
   }
   ```

#### Step 4: Upload Files via cURL
```powershell
curl -X POST "http://127.0.0.1:8000/jobs" `
  -H "accept: application/json" `
  -H "Content-Type: multipart/form-data" `
  -F "files=@sample_docs/01-delhivery-prospectus-2022-excerpt.pdf" `
  -F "files=@sample_docs/02-delhivery-annual-report-fy24-excerpt.pdf"
```

#### Step 5: Upload Files via Python Script
```python
import requests

url = "http://127.0.0.1:8000/jobs"
files = [
    ("files", open("sample_docs/01-delhivery-prospectus-2022-excerpt.pdf", "rb")),
    ("files", open("sample_docs/02-delhivery-annual-report-fy24-excerpt.pdf", "rb")),
]
response = requests.post(url, files=files)
print(response.json())
```

---

## 4. How the System Executes (Run Directory Structure)

Every processing run generates a strictly isolated, cryptographically audited job folder in `runs/JOB-<TIMESTAMP>-<HASH>/`:

```text
runs/JOB-20260908-034754-34f962/
|-- documents/                  # Copied source PDF files with SHA-256 validation
|   |-- 01-delhivery-prospectus-2022-excerpt.pdf
|   |-- 02-delhivery-annual-report-fy24-excerpt.pdf
|   +-- 03-delhivery-q4-fy24-earnings-presentation.pdf
|-- evidence/                   # Chunk representations and structural table masks
|-- reports/                    # Production audit deliverables
|   |-- summary.md              # Executive Dashboard report
|   |-- contradictions.md       # Detailed Contradictions audit
|   |-- unresolved.md           # Unresolved disclosures analysis
|   +-- summary.json            # Machine-readable programmatic JSON export
|-- traces/                     # Cryptographic decision trace logs
|   +-- trace.jsonl             # Append-only chronological trace stream
|-- ledger.db                   # Isolated 10-table SQLite evidence database
+-- run.json                    # Job manifest with lifecycle timestamps and metrics
```

---

## 5. How to Verify and Audit the Solution

Evaluators can verify EVIDRA through five independent inspection layers.

### 5.1 Verification Layer 1: Automated Test Suite (59 Passing Tests)

Execute the full automated test suite covering API contracts, evaluation scenarios, normalizers, and reasoning engines:
```powershell
pytest tests/ -v
```
Expected summary:
```text
collected 59 items

tests\contracts\test_api.py .......                                      [ 11%]
tests\evaluation\test_scenarios.py .....                                 [ 20%]
tests\unit\test_cli.py ......                                            [ 30%]
tests\unit\test_decimal_units.py .....                                   [ 38%]
tests\unit\test_decision.py ...........                                  [ 57%]
tests\unit\test_extraction.py ...                                        [ 62%]
tests\unit\test_ledger.py .....                                          [ 71%]
tests\unit\test_llm.py ..                                                [ 74%]
tests\unit\test_pdf.py ...                                               [ 79%]
tests\unit\test_temporal_parsing.py .....                                [ 88%]
tests\unit\test_trace.py ..                                              [ 91%]
tests\unit\test_verification.py .....                                    [100%]

======================= 59 passed, 3 warnings in 33.79s =======================
```

---

### 5.2 Verification Layer 2: Turnkey Diagnostic Audit Script

Execute the turnkey Deliverable 5 verification script:
```powershell
python scripts/verify_d5.py
```
This script audits:
1. **Trace Engine & Replayer:** Validates JSONL writing, SQLite querying, and timeline rendering.
2. **Production Reporting Suite:** Validates Markdown reports, bounding boxes, verbatim evidence context, and JSON exports.
3. **Evaluation Framework:** Validates metrics engine (Accuracy, Precision, Recall, F1, Hallucination Rate).
4. **Four Mandatory Assignment Scenarios:** Executes all 4 benchmark cases sequentially.

Expected result:
```text
============================================================
  EVIDRA Deliverable 5 (D5) Observability & Evaluation Audit
============================================================

[1/4] Auditing Cryptographic Trace Engine & TraceReplayer...
      PASS: TraceLogger and TraceReplayer validated.
[2/4] Auditing Production Reporting Suite (Markdown & JSON)...
      PASS: Reports generated with bounding boxes and structured JSON.
[3/4] Auditing Evaluation Framework & Metrics Calculation...
      PASS: Metric calculations and scorecard generation verified.
[4/4] Executing Mandatory Assignment Benchmark Scenarios...
      - BENCH-01: Dual-Source Corroboration Benchmark -> CORROBORATED (Latency: 85.9ms) [PASS]
      - BENCH-02: Direct Numerical Contradiction Benchmark -> CONTRADICTION (Latency: 170.2ms) [PASS]
      - BENCH-03: Defensible Reconciliation Benchmark -> RECONCILED (Latency: 155.9ms) [PASS]
      - BENCH-04: Defensive Failure Handling Benchmark -> UNRESOLVED (Latency: 85.5ms) [PASS]

============================================================
  ALL DELIVERABLE 5 (D5) QUALITY CHECKS PASSED
============================================================
```

---

### 5.3 Verification Layer 3: Mandatory Assignment Evaluation Benchmark

Execute the evaluation benchmark suite directly via the CLI:
```powershell
python -m src.cli.main benchmark
```
For machine-readable JSON output:
```powershell
python -m src.cli.main benchmark --format json
```
Expected output:
```text
Running EVIDRA mandatory assignment benchmark scenarios...

# EVIDRA Evaluation Benchmark Scorecard

- **Total Scenarios Evaluated:** 4
- **Passed Scenarios:** 4
- **Overall Accuracy:** 100.0%
- **Hallucination Rate:** 0.0%

## 1. Metric Breakdown by Epistemic Verdict

| Verdict Class | Precision | Recall | F1 Score |
| :--- | :--- | :--- | :--- |
| **CORROBORATED** | 100.0% | 100.0% | 100.0% |
| **CONTRADICTION** | 100.0% | 100.0% | 100.0% |
| **RECONCILED** | 100.0% | 100.0% | 100.0% |
| **UNRESOLVED** | 100.0% | 100.0% | 100.0% |

## 2. Individual Scenario Results

| Case ID | Scenario Name | Expected | Actual | Latency | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `BENCH-01` | Dual-Source Corroboration Benchmark | **CORROBORATED** | **CORROBORATED** | 115.37ms | **PASS** |
| `BENCH-02` | Direct Numerical Contradiction Benchmark | **CONTRADICTION** | **CONTRADICTION** | 150.33ms | **PASS** |
| `BENCH-03` | Defensible Reconciliation Benchmark | **RECONCILED** | **RECONCILED** | 138.50ms | **PASS** |
| `BENCH-04` | Defensive Failure Handling Benchmark | **UNRESOLVED** | **UNRESOLVED** | 71.46ms | **PASS** |
```

---

### 5.4 Verification Layer 4: Cryptographic Decision Trace Replay

Evaluators can forensically replay any adjudicated decision chronologically to inspect the exact prompts, validator tests, and policy rules fired.

#### Replay an Entire Job Run
```powershell
python -m src.cli.main replay <JOB_ID>
```

#### Replay a Specific Decision by ID
Example using the cross-document reconciliation decision `DEC-57c1248a` from the Delhivery run:
```powershell
python -m src.cli.main replay JOB-20260908-034754-34f962 --decision-id DEC-57c1248a
```
Expected output:
```text
================================================================================
  EVIDRA Cryptographic Audit Replay (Decision: DEC-57c1248a)
================================================================================
[01] Step: analyze_variance | Agent: VarianceAnalyzer | Decision: DEC-57c1248a | Latency: 0.05ms
     Timestamp: 2026-09-08 03:53:06
     Input:     {"candidates_count": 3}
     Output:    {"decision_path": "B", "arithmetic_equal": false, "matching_context": false}
--------------------------------------------------------------------------------
[02] Step: route_context | Agent: ContextRouter | Decision: DEC-57c1248a | Latency: 0.22ms
     Timestamp: 2026-09-08 03:53:06
     Input:     {"context_differences": true}
     Output:    {"hypotheses_count": 2, "validator_results_count": 1}
--------------------------------------------------------------------------------
[03] Step: propose_reconciliation | Agent: ReconciliationProposerAgent | Decision: DEC-57c1248a | Latency: 0.04ms
     Timestamp: 2026-09-08 03:53:06
     Input:     {"supported_validators": 1}
     Output:    {"proposal": {"supported_hypothesis_id": "HYP-BASIS-cfac76", "explanation_type": "ACCOUNTING_BASIS", "root_cause": "A...
--------------------------------------------------------------------------------
[04] Step: critique_reconciliation | Agent: AdversarialSkepticAgent | Decision: DEC-57c1248a | Latency: 0.03ms
     Timestamp: 2026-09-08 03:53:06
     Input:     {"proposal_root_cause": "Accounting Standard Discrepancy (GAAP vs Non-GAAP)"}
     Output:    {"skeptic_status": "SURVIVED", "critique": "Accounting standard variance explicitly verified: NON_GAAP vs UNKNOWN."}
--------------------------------------------------------------------------------
[05] Step: apply_policy | Agent: DecisionPolicy | Decision: DEC-57c1248a | Latency: 0.03ms
     Timestamp: 2026-09-08 03:53:06
     Input:     {"arithmetic_equal": false, "path": "B"}
     Output:    {"verdict": "RECONCILED", "decision_strength": "HIGH", "summary": "Reconciled: Reporting basis difference between NON...
--------------------------------------------------------------------------------
```

---

### 5.5 Verification Layer 5: Terminal Inspection and Report Auditing

#### Inspect Decisions via CLI
Filter decisions by verdict:
```powershell
python -m src.cli.main inspect <JOB_ID> --verdict RECONCILED
python -m src.cli.main inspect <JOB_ID> --verdict CONTRADICTION
python -m src.cli.main inspect <JOB_ID> --verdict UNRESOLVED
```

#### Display or Export Reports via CLI
```powershell
# Display Executive Summary
python -m src.cli.main report <JOB_ID> --type summary

# Display Contradictions Audit Report
python -m src.cli.main report <JOB_ID> --type contradictions

# Display Unresolved Disclosures Report
python -m src.cli.main report <JOB_ID> --type unresolved

# Export Structured JSON Report
python -m src.cli.main report <JOB_ID> --format json
```

#### Direct File Inspection in `runs/<JOB_ID>/reports/`
Open the generated Markdown files directly in any editor:
1. `summary.md`: Document manifest, candidate count, cluster count, and verdict summary.
2. `contradictions.md`: Tabular comparative claims with exact PDF coordinates `[x0, y0, x1, y1]`, verbatim source evidence text, and hypothesis refutations.
3. `unresolved.md`: Itemized list of ambiguous or single-source observations with actionable follow-up guidance for analysts.

---

### 5.6 Verification Layer 6: Interactive REST API Inspection

When the server is running (`python -m src.cli.main serve`), query the REST API endpoints directly:

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/health` | `GET` | System health probe, SQLite status, and Ollama model connectivity. |
| `/jobs` | `POST` | Upload multi-part PDF files to launch an asynchronous processing job. |
| `/jobs/{id}` | `GET` | Query job status (`PENDING`, `PROCESSING`, `COMPLETED`, `FAILED`) and live counts. |
| `/jobs/{id}/decisions` | `GET` | Retrieve list of adjudicated decisions with optional `?verdict=` filter. |
| `/jobs/{id}/decisions/{dec_id}` | `GET` | Retrieve granular Decision Card (bounding boxes, hypotheses, skeptic audit). |
| `/jobs/{id}/reports/{type}` | `GET` | Retrieve Markdown report (`summary`, `contradictions`, `unresolved`). |
| `/jobs/{id}/traces` | `GET` | Retrieve full chronological execution trace steps with latencies. |
| `/jobs/{id}/traces/{dec_id}` | `GET` | Retrieve trace steps specific to a single decision. |
| `/evaluate` | `POST` | Execute automated benchmark scenarios and return scorecards. |

---

## 6. End-to-End Case Study: Delhivery Multi-Document Corpus

Evaluators can reproduce the full multi-document verification across the three real-world filings included in `sample_docs/`:

1. `sample_docs/01-delhivery-prospectus-2022-excerpt.pdf` (100 pages, IPO Prospectus)
2. `sample_docs/02-delhivery-annual-report-fy24-excerpt.pdf` (100 pages, FY24 Audited Annual Report)
3. `sample_docs/03-delhivery-q4-fy24-earnings-presentation.pdf` (27 pages, Q4 FY24 Investor Presentation)

### Step 1: Execute Multi-Document Ingestion
```powershell
python -m src.cli.main process `
  sample_docs/01-delhivery-prospectus-2022-excerpt.pdf `
  sample_docs/02-delhivery-annual-report-fy24-excerpt.pdf `
  sample_docs/03-delhivery-q4-fy24-earnings-presentation.pdf `
  --fast `
  --max-chunks 2
```

### Step 2: Note the Assigned Job ID
From the terminal summary, locate the generated Job ID (e.g. `JOB-20260908-034754-34f962`).

### Step 3: Inspect Adjudications
```powershell
# Inspect reconciled cross-document metric
python -m src.cli.main inspect <JOB_ID> --verdict RECONCILED

# Inspect contradictions detected across filings
python -m src.cli.main inspect <JOB_ID> --verdict CONTRADICTION

# Replay decision trace
python -m src.cli.main replay <JOB_ID>
```

---

## 7. Troubleshooting and Defensive Behaviors

### 7.1 Ollama Connectivity Issues
- **Symptom:** `verify_env.py` reports `Ollama is not responding`.
- **Remedy:** Ensure Ollama is running (`ollama serve` in a terminal) and verify `curl http://127.0.0.1:11434` returns `Ollama is running`.

### 7.2 Defensive Failure Handling (`UNRESOLVED`)
- When documents contain ambiguous disclosures, ungrounded figures, corrupt text, or single-source claims lacking cross-document validation, EVIDRA deliberately outputs **`UNRESOLVED`** rather than hallucinating a false consensus.
- Check `runs/<JOB_ID>/reports/unresolved.md` for specific follow-up guidance on what additional filings or footnotes are required.

### 7.3 Large Document Memory Optimization
- For long PDF filings (>100 pages), use `--max-chunks 2` or `--fast` to optimize LLM extraction latency while retaining complete layout parsing, table extraction, and bounding box indexing.
