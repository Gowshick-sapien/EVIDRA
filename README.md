# EVIDRA

## Evidence-Driven Knowledge Layer for Multi-Document Fact Validation and Reconciliation

---

## 1. Overview

**EVIDRA** is an autonomous, auditable Fact Knowledge Layer designed to evaluate, validate, and reconcile numerical disclosures across complex corporate documents (such as IPO prospectuses, annual reports, and quarterly earnings presentations).

### The Challenge
When financial analysts and auditors compare multiple corporate filings, determining whether stated numbers agree, conflict, or describe different metrics is critical. Conventional Large Language Model (LLM) pipelines and Retrieval-Augmented Generation (RAG) systems fail in this domain because they:
- Split tables arbitrarily, losing table headers, reporting currencies, and stated units.
- Compare numbers without checking measurement types (for example, comparing an absolute revenue with a percentage growth rate).
- Conflate different time periods or accounting standards, hallucinating false contradictions.
- Speculatively guess answers when information is missing instead of acknowledging uncertainty.

### The EVIDRA Solution
EVIDRA establishes an evidence-first architecture where **the document itself is the guide**:
- **Physical Geometry Provenance:** Every extracted claim is anchored to its page number and bounding box coordinates `[x0, y0, x1, y1]`.
- **4-Gate Contextual Fact Resolution:** Claims must pass four sequential isolation gates (Canonical Entity, Temporal Period, Measurement Type, and Accounting Context) before any numerical comparison occurs.
- **Zero-LLM Deterministic Verdict Gate:** Large Language Models are used strictly for initial extraction and hypothesis drafting. All final relationship verdicts are computed by deterministic Python truth tables.
- **Honest Uncertainty:** Incomplete or single-source disclosures are explicitly preserved as `UNRESOLVED` with documented missing evidence.

---

## 2. The Four Canonical Outcomes

Every relationship between financial facts across documents is classified into one of four mutually exclusive, fully audited verdicts:

| Verdict | Definition | Mathematical and Evidentiary Rule | Real-World Corporate Example |
| :--- | :--- | :--- | :--- |
| **CORROBORATED** | Independent Agreement | Stated figures match within 0.01% arithmetic tolerance under identical entity, time period, and accounting scope. | Delhivery Prospectus (Page 22 vs Page 27): Revenue from Operations identically stated as `36,465.27 million INR` (0.0% variance). |
| **CONTRADICTION** | Genuine Irreconcilable Conflict | Direct numerical divergence under identical context where all specialist reconciliation hypotheses have been refuted. | Delhivery Prospectus (Page 22): Conflicting intragroup restatement adjustment rows reporting `-1.98`, `-4.56`, and `-5.67` million INR. |
| **RECONCILED** | Contextually Explained Divergence | Divergent numbers explained by documented structural context (accounting standards, reporting scope, or non-GAAP adjustments) that survive adversarial critique. | Statutory Operating Profit (`INR 1,200 Cr`) vs Adjusted EBITDA (`INR 1,450 Cr`) reconciled via Non-GAAP disclosure note bridging ESOP and amortization. |
| **UNRESOLVED** | Incomplete or Isolated Evidence | Claims appearing in only a single source, or lacking sufficient context for definitive adjudication. | Isolated fleet logistics disclosure reported on a single page, preserved as `UNRESOLVED` requiring second-source confirmation. |

---

## 3. Quickstart Guide

EVIDRA runs entirely on local infrastructure with zero recurring API costs or cloud dependencies.

### 3.1 Prerequisites
- **Operating System:** Windows 10/11, macOS, or Linux
- **Python:** Version 3.11 or 3.12 (Python 3.12 tested and verified)
- **Local LLM Engine:** [Ollama](https://ollama.com/) running locally with the `qwen2.5:3b` model
- **Hardware:** Minimum 8 GB RAM (16 GB recommended)

### 3.2 Step 1: Install Dependencies
Clone the repository and install dependencies:
```powershell
pip install -r requirements.txt
```

### 3.3 Step 2: Start Ollama Local Engine
Ensure Ollama is running and has the default model downloaded:
```powershell
# Start the Ollama background service (if not already running)
ollama serve

# Pull the high-efficiency reasoning model
ollama pull qwen2.5:3b
```

### 3.4 Step 3: Run Pre-Flight Environment Diagnostic
Verify local dependencies, database connectivity, and the Ollama server:
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

## 4. Execution Guide

EVIDRA provides two primary interfaces: a Command Line Interface (CLI) and an interactive REST API.

### 4.1 Command Line Interface (CLI)

#### Process a Single Document Excerpt
```powershell
python -m src.cli.main process sample_docs/01-delhivery-prospectus-2022-excerpt.pdf --max-chunks 15
```

#### Process Multiple Corporate Filings
```powershell
python -m src.cli.main process `
  sample_docs/01-delhivery-prospectus-2022-excerpt.pdf `
  sample_docs/02-delhivery-annual-report-2024-excerpt.pdf `
  sample_docs/03-delhivery-earnings-presentation-q4fy24.pdf `
  --max-chunks 30
```

#### Process an Entire Directory
```powershell
python -m src.cli.main process sample_docs/ --max-chunks 15
```

#### Key CLI Flags
- `--max-chunks <N>`: Sets the maximum evidence chunks to evaluate per document (default: 30). Tables are prioritized to guarantee 100% table preservation within quota.
- `--all-chunks`: Ingests and processes all detected chunks without budget caps.
- `--skip-llm`: Runs structural PDF layout analysis and table extraction without generative LLM calls (ideal for CI/CD and rapid layout testing).
- `--verbose`: Outputs step-by-step progress and execution traces in the terminal.

---

### 4.2 FastAPI REST API and Swagger UI

Launch the API server for interactive web inspection and programmatic integration:

```powershell
python -m src.cli.main serve --port 8000
```
Or directly with Uvicorn:
```powershell
uvicorn src.api.server:app --host 127.0.0.1 --port 8000
```

Once started, open your browser to access the interactive Swagger documentation:
- **Interactive Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc UI:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

Available Endpoints:
- `POST /jobs`: Upload one or more PDF files to trigger an asynchronous processing job.
- `GET /jobs/{job_id}`: Poll job status, progress percentages, and timing metrics.
- `GET /jobs/{job_id}/results`: Retrieve structured JSON results, extracted facts, and relationship verdicts.
- `GET /jobs/{job_id}/reports/summary`: Download the Markdown Executive Summary report.
- `GET /jobs/{job_id}/reports/contradictions`: Download the Markdown Contradictions audit report.
- `GET /jobs/{job_id}/reports/unresolved`: Download the Markdown Unresolved disclosures report.

---

## 5. Verification and Validation Guide

Evaluators can verify the correctness and reliability of EVIDRA through three mechanisms:

### 5.1 Automated Test Suite (110 Tests Passing)
Run the full automated test suite covering unit logic, API contracts, and evaluation scenarios:
```powershell
pytest tests/ -v
```
All 110 tests execute and pass in approximately 60 seconds.

### 5.2 SQLite Audit Ledger Inspection
Every execution creates an isolated SQLite database at `runs/JOB-<timestamp>/ledger.db` with Write-Ahead Logging (WAL) enabled:
```powershell
# Inspect verified Fact Identities and their measurement classifications
sqlite3 runs/JOB-20260908-133430-8f0093/ledger.db "SELECT fact_id, measurement_type, metric_family, metric_subtype FROM fact_identities LIMIT 5;"

# Inspect the Claim Relationship Graph and computed variances
sqlite3 runs/JOB-20260908-133430-8f0093/ledger.db "SELECT relationship_id, relationship_type, variance_percentage FROM claim_relationships LIMIT 5;"

# Inspect the final Decision breakdown
sqlite3 runs/JOB-20260908-133430-8f0093/ledger.db "SELECT verdict, decision_strength, count(*) FROM decisions GROUP BY verdict, decision_strength;"
```

### 5.3 Human-Readable Audit Reports
Inspect the generated reports located in `runs/JOB-<timestamp>/reports/`:
- **`summary.md`:** Executive dashboard with document metadata, chunk distributions, group topologies, and final decision tallies.
- **`contradictions.md`:** Comprehensive conflict audit displaying competing claims side-by-side with bounding box coordinates, verbatim context, and hypothesis evaluation logs.
- **`unresolved.md`:** Evidentiary gap analysis detailing single-source disclosures and missing second sources.

---

## 6. Project Documentation Index

EVIDRA provides two distinct tiers of documentation:

### 6.1 Evaluator and User Documentation
- **[Repository Overview & Inspection Guide](docs/REPOSITORY_OVERVIEW.md):** Complete directory map outlining document purposes, source code modules, test locations, and real-world manual verification artifacts.
- **[Proposed Solution](docs/PROPOSED_SOLUTION.md):** The comprehensive architectural blueprint, detailing the 6 core pillars, 4-stage pipeline, and real-world case studies on corporate data.
- **[Operational Runbook & Execution Guide](docs/RUN_PLAN.md):** Complete operational manual with step-by-step diagnostic workflows, advanced CLI options, and API reference.

### 6.2 Internal Developer Documentation
For developers, system engineers, and auditors reviewing technical specifications, engineering blueprints, and requirements:
- **[Developer Documentation Index](docs/developer/README.md):** Full directory of internal engineering specifications.
  - Comprehensive Architecture Reference: [Architecture Specification](docs/developer/ARCHITECTURE_README.md)
  - Evidence Resolution & 4-Gate Matching: [Structural Evidence & Resolution Specification](docs/developer/ARCHITECTURE_V2.md)
  - Reasoning Tournament & Specialist Validators: [Reasoning Engine & Adjudication Specification](docs/developer/ARCHITECTURE_V1.md)
  - Software Requirements Specifications: [Software Requirements Specifications](docs/developer/SRS_V2.md)
  - Engineering Phase Roadmaps: [Phase Deliverable Plans](docs/deliverable_plans/)
  - Technology Stack Analysis: [Tech Stack Specification](docs/developer/TECH_STACK.md)
  - Foundational Design Philosophy: [Project Ideation](docs/developer/PROJECT_IDEATION.md)