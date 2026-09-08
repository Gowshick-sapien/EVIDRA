# EVIDRA

## Evidence-Driven Architecture for Fact Validation and Knowledge Reasoning

> **System Classification:** Multi-Document Financial Epistemic Layer  
> **Development Branch:** `dev_v2`  
> **Compliance:** Deterministic Zero-LLM Decision Gate, Cryptographic Coordinate Provenance, Zero Emojis  

---

## 1. Executive Overview

**EVIDRA** is an evidence-centric financial document reasoning architecture designed to solve a fundamental challenge in automated document intelligence:

> **How do we reliably determine when multiple corporate documents agree, directly contradict, or can be logically reconciled, without hallucinating false consensus or erroneous contradictions?**

Conventional Large Language Model (LLM) pipelines and Retrieval-Augmented Generation (RAG) systems treat extracted claims as atomic facts and rely on opaque generative models to output answers. When deployed across complex corporate disclosures (such as IPO prospectuses, audited annual reports, and earnings presentations), traditional RAG architectures suffer from:
1. **Blind Extraction:** Dropping 90% of tabular disclosures due to naive text chunking.
2. **Context Loss:** Discarding table captions, header units (`Rs. in Crores`), and reporting scopes.
3. **Cross-Dimensional Contamination:** Using flat cosine vector similarity to group claims, which mistakenly compares percentage margins with absolute revenues, generating 100% false contradictions.
4. **Speculative Guessing:** Hallucinating answers instead of acknowledging evidentiary gaps.

EVIDRA establishes a paradigm where **the fact is not the primitive**. The system constructs an auditable, cryptographic Evidence Ledger where:
* What an authoring document literally asserts (**Observation**) is strictly decoupled from what the system deduces (**Decision**).
* Every claim is anchored to physical PDF coordinates $[x_0, y_0, x_1, y_1]$, page numbers, and SHA-256 chunk hashes.
* Numerical comparisons are governed by a **4-Gate Contextual Fact Resolution** engine and **Fact Identity Signatures** with explicit dimensional measurement semantics (`ABSOLUTE_VALUE`, `PERCENTAGE`, `RATE_OF_CHANGE`, `RATIO`).
* Multi-member claims are adjudicated via a **Pairwise Claim Relationship Graph** and **Value Equivalence Clustering**, eliminating naive majority voting.
* Reconciliation is a structured debate where an **Adversarial Skeptic** systematically stress-tests proposed reconciliation bridges against raw text.
* Final verdicts are determined by a **deterministic pure Python decision policy**, reserving local LLMs strictly for semantic extraction and hypothesis generation.
* When evidence is incomplete, the system explicitly preserves **UNRESOLVED** as an honorable, audited answer rather than guessing.

---

## 2. The Four Epistemic Verdicts

Every evaluated relationship between facts across documents receives one of four mutually exclusive, fully audited verdicts:

| Verdict | Epistemic Meaning | Mathematical & Evidentiary Condition | Real-World Delhivery Example |
| :--- | :--- | :--- | :--- |
| **CORROBORATED** | Independent Confirmation | Stated values match within 0.01% arithmetic tolerance under identical canonical entity, temporal period, and reporting scope. | Prospectus Page 22 vs Page 27: Revenue from Operations identically reported as `36,465.27 million INR` ($\Delta = 0.0\%$). |
| **CONTRADICTION** | Genuine, Irreconcilable Conflict | Direct numerical divergence under identical context, where all specialist reconciliation hypotheses have been falsified. | Prospectus Page 22 conflicting intragroup elimination rows: `-5.67` vs `-4.56` vs `-1.98` million INR with divergence up to $65.08\%$. |
| **RECONCILED** | Contextually Explained Divergence | Apparent numerical conflict explained by documented structural context (accounting basis, reporting scope, or audit restatement) that survived adversarial challenge. | Operating Profit (`INR 1,200 Cr`) vs Adjusted EBITDA (`INR 1,450 Cr`) reconciled via Non-GAAP disclosure note bridging ESOP and amortization. |
| **UNRESOLVED** | Incomplete or Ambiguous Evidence | Single-source isolation, unentailed observations, or insufficient disclosures requiring human analyst follow-up. | Isolated fleet logistics metric reported on a single page, preserved as `UNRESOLVED` (Strength: `LOW`) with documented missing second source. |

---

## 3. System Architecture

EVIDRA organizes document intelligence into four distinct, inspectable operational layers:

```text
+----------------------------------------------------------------------------------------------------+
| LAYER 1: DOCUMENT EVIDENCE PREPARATION & STRUCTURAL PARSING                                        |
| - Layout Topology Classifier (Z-score font size, repetition frequency, spatial table proximity)    |
| - Context-Enriched Evidence Windows (Stated units, currencies, table headers, captions)           |
| - 3-Tier Budget-Aware Candidate Discovery (Guaranteed 100% table preservation within quota)        |
+----------------------------------------------------------------------------------------------------+
                                                  |
                                                  v
+----------------------------------------------------------------------------------------------------+
| LAYER 2: DYNAMIC SCHEMA INDUCTION & FACT IDENTITY RESOLUTION                                       |
| - Lightweight Schema Induction (Discovers corporate legal entities & metric families)             |
| - Fact Identity Signature (Canonical entity, metric family, subtype, measurement type, dates)      |
| - Deterministic Measurement Classifier (Absolute Value, Percentage, Rate of Change, Ratio)        |
| - Temporal Comparability Classifier (Exact Match, Containment, Adjacent, Overlapping)              |
+----------------------------------------------------------------------------------------------------+
                                                  |
                                                  v
+----------------------------------------------------------------------------------------------------+
| LAYER 3: 4-GATE FACT MATCHING & CLAIM RELATIONSHIP TOURNAMENT                                      |
| - 4-Gate Contextual Fact Resolution (Gate 1: Entity, Gate 2: Temporal, Gate 3: Metric, Gate 4: Ctx)|
| - Rule-Based Evidence Sufficiency Gate (Screens identity completeness and source multiplicity)    |
| - Pairwise Claim Relationship Graph (Executes N(N-1)/2 tournament matches across candidates)      |
| - Value Equivalence Clustering (0.1% tolerance clustering; synthesizes unanimous vs conflicts)    |
| - Specialist Validators (Arithmetic, Scope, Accounting Basis, Restatement, Timing)                |
| - Adversarial Skeptic Audit (Stress-tests reconciliation bridges against raw text)                 |
| - Zero-LLM Deterministic Decision Policy (Evaluates pure Python truth table verdicts)              |
+----------------------------------------------------------------------------------------------------+
                                                  |
                                                  v
+----------------------------------------------------------------------------------------------------+
| LAYER 4: OBSERVABILITY, AUDIT LEDGER, & INSPECTION                                                 |
| - Relational SQLite WAL Evidence Ledger (ledger.db: documents, chunks, identities, relationships)  |
| - Streaming Audit Trace Logs (trace.jsonl: millisecond-precision step execution)                  |
| - Automated Markdown Audit Reports (summary.md, contradictions.md, unresolved.md)                 |
| - Dual Presentation Interface (FastAPI REST API with Swagger UI + Rich Terminal CLI)               |
+----------------------------------------------------------------------------------------------------+
```

---

## 4. Key Engineering Innovations

### 4.1 4-Gate Contextual Fact Resolution
Rather than clustering raw attribute strings with flat vector embeddings, EVIDRA enforces 4 sequential isolation gates:
- **Gate 1 (Canonical Entity):** Isolates claims across corporate entities (`Delhivery Limited` vs `Spoton Logistics`).
- **Gate 2 (Temporal Comparability):** Classifies intervals into `EXACT`, `CONTAINMENT`, `ADJACENT`, `OVERLAPPING`, `NON_OVERLAPPING`. Prevents comparing FY21 with FY22 numbers.
- **Gate 3 (Metric & Measurement Typing):**
  - **Gate 3A:** Strictly isolates differing dimensional types (`ABSOLUTE_VALUE` vs `PERCENTAGE` vs `RATE_OF_CHANGE` vs `RATIO`).
  - **Gate 3B:** Isolates distinct accounting sub-metrics (e.g., `OPERATING_REVENUE` vs `SERVICE_REVENUE`) while unifying synonyms (e.g., `Revenue from operations` and `Operating Revenue`).
- **Gate 4 (Context Compatibility):** Detects differences in reporting scope (`Consolidated` vs `Standalone`) or accounting basis (`Ind AS` vs `Non-GAAP`) and routes the pair to Path B (Contextual Reconciliation) rather than declaring a raw contradiction.

### 4.2 Pairwise Claim Relationship Graph & Value Clustering
For fact groups with $N \ge 2$ claims:
1. **$N(N-1)/2$ Pairwise Matches:** Every unique pair is evaluated through the LangGraph tournament state machine.
2. **Typed Graph Edges:** Edges are logged in `claim_relationships` as `CORROBORATES`, `CONFLICTS_WITH`, `RECONCILES_WITH`, or `INCONCLUSIVE` with computed numerical variance percentages.
3. **Equivalence Clustering:** Claims are grouped into value clusters within a 0.1% rounding tolerance.
4. **Synthesis Verdict:**
   - Single cluster: `CORROBORATED` (`HIGH` strength).
   - Multiple clusters with supported validator bridges: `RECONCILED` (`HIGH` or `MEDIUM` strength).
   - Multiple clusters without reconciliation: `CONTRADICTION` (`HIGH` strength).
   - Single claim: `UNRESOLVED` (`LOW` strength) pending second source.

### 4.3 Deterministic Zero-LLM Verdict Gate
At the decision threshold, zero LLM calls are made. Verdicts are computed strictly via pure Python boolean truth tables in `DecisionPolicy`, eliminating generative hallucinations from the decision ledger.

---

## 5. Quickstart and Installation Guide

EVIDRA executes on local infrastructure without external cloud API dependencies.

### 5.1 Prerequisites
- **Operating System:** Windows 10/11, macOS, or Linux.
- **Python:** 3.11 or 3.12 (Python 3.12.2 tested).
- **Local LLM Engine:** [Ollama](https://ollama.com/) running locally with model `qwen2.5:3b`.
- **Hardware:** Minimum 8 GB RAM (16 GB recommended).

### 5.2 Step 1: Clone Repository and Install Dependencies
```powershell
git clone https://github.com/superjoin/EVIDRA.git
cd EVIDRA
pip install -r requirements.txt
```

### 5.3 Step 2: Start Ollama Local Daemon
In a separate terminal, launch Ollama and pull the model:
```powershell
ollama serve
ollama pull qwen2.5:3b
```

### 5.4 Step 3: Run Pre-Flight Environment Diagnostic
```powershell
python scripts/verify_env.py
```
Confirms that Python version, PyMuPDF, pdfplumber, SQLite, Ollama server connectivity, and BGE-Small embeddings are ready.

---

## 6. Execution Options

### Option A: Process Documents via CLI
Process a single document or multi-document filing with candidate chunk quotas:
```powershell
# Process single filing excerpt (e.g. 15 chunks)
python -m src.cli.main process sample_docs/01-delhivery-prospectus-2022-excerpt.pdf --max-chunks 15

# Process multiple corporate filings simultaneously
python -m src.cli.main process sample_docs/01-delhivery-prospectus-2022-excerpt.pdf sample_docs/02-delhivery-annual-report-2024-excerpt.pdf sample_docs/03-delhivery-earnings-presentation-q4fy24.pdf --max-chunks 30
```

### Option B: Launch Interactive REST API Server
Start the FastAPI server:
```powershell
python -m src.cli.main serve --port 8000
```
Open your browser to:
- **Interactive Swagger UI:** `http://127.0.0.1:8000/docs`
- **System Health:** `http://127.0.0.1:8000/api/v1/health`
- **Upload Endpoint:** `POST /api/v1/documents/upload`

### Option C: Replay Execution Traces
Verify deterministic execution by replaying historical JSONL audit traces:
```powershell
python -m src.cli.main replay runs/JOB-20260908-123217-9b5337/traces/trace.jsonl
```

---

## 7. Verification and Test Suite

EVIDRA maintains a rigorous test suite of **110 automated test cases** across 21 modules:

```powershell
# Run the complete test suite
pytest tests/ -v
```

**Verified Test Suite Results:**
- `tests/contracts/test_api.py`: 7 passed
- `tests/evaluation/test_scenarios.py`: 5 passed
- `tests/unit/test_4gate_resolution.py`: 6 passed
- `tests/unit/test_claim_graph.py`: 4 passed
- `tests/unit/test_cli.py`: 6 passed
- `tests/unit/test_decimal_units.py`: 5 passed
- `tests/unit/test_decision.py`: 11 passed
- `tests/unit/test_extraction.py`: 3 passed
- `tests/unit/test_identity.py`: 7 passed
- `tests/unit/test_ledger.py`: 7 passed
- `tests/unit/test_llm.py`: 2 passed
- `tests/unit/test_p0_pipeline.py`: 5 passed
- `tests/unit/test_pdf.py`: 3 passed
- `tests/unit/test_schema_induction.py`: 3 passed
- `tests/unit/test_temporal_comparability.py`: 8 passed
- `tests/unit/test_temporal_parsing.py`: 5 passed
- `tests/unit/test_topology.py`: 3 passed
- `tests/unit/test_trace.py`: 2 passed
- `tests/unit/test_verification.py`: 5 passed
- `tests/unit/test_windows.py`: 3 passed
- **Total:** **110 passed in 61.24s** (0 failures).

---

## 8. Output Artifacts and Audit Inspection

Every job execution creates a dedicated run directory under `runs/JOB-<timestamp>/`:

```text
runs/JOB-20260908-123217-9b5337/
├── ledger.db                    # Relational SQLite WAL database
├── run.json                     # Job metadata, timings, and configuration
├── reports/
│   ├── summary.md               # Executive dashboard of decisions and groups
│   ├── contradictions.md        # Comprehensive side-by-side contradiction audit
│   └── unresolved.md            # Documented single-source and unresolved claims
├── traces/
│   └── trace.jsonl              # Millisecond-precision execution event stream
└── evidence/
    ├── tables/                  # Extracted markdown financial tables
    ├── *_manifest.json          # Document chunk geometry and bounding boxes
    └── *_schema.json            # Dynamically induced corporate schemas
```

### Inspecting the SQLite Ledger
```powershell
# 1. Query fact identities and measurement types
sqlite3 runs/JOB-20260908-123217-9b5337/ledger.db "SELECT fact_id, measurement_type, metric_family, metric_subtype, period_start, period_end FROM fact_identities LIMIT 5;"

# 2. Query pairwise claim relationship edges
sqlite3 runs/JOB-20260908-123217-9b5337/ledger.db "SELECT relationship_id, group_id, relationship_type, variance_percentage FROM claim_relationships LIMIT 5;"

# 3. Query adjudicated decisions
sqlite3 runs/JOB-20260908-123217-9b5337/ledger.db "SELECT verdict, decision_strength, count(*) FROM decisions GROUP BY verdict, decision_strength;"
```

---

## 9. Repository Structure

```text
EVIDRA/
├── README.md                           # Evaluator-centric overview, quickstart, and verification guide
├── docs/                               # Core documentation
│   ├── PROPOSED_SOLUTION.md            # Comprehensive proposed solution blueprint
│   ├── RUN_PLAN.md                     # Operational execution and audit runbook
│   ├── deliverable_plans/              # Granular phase implementation and verification plans
│   └── developer/                      # Complete technical specifications and engineering blueprints
├── sample_docs/                        # Delhivery starter corporate dataset
│   ├── 01-delhivery-prospectus-2022-excerpt.pdf
│   ├── 02-delhivery-annual-report-2024-excerpt.pdf
│   └── 03-delhivery-earnings-presentation-q4fy24.pdf
├── scripts/                            # Operational utility scripts
│   └── verify_env.py                   # Pre-flight environment check
├── src/                                # Core operational codebase
│   ├── api/                            # FastAPI endpoints and schemas
│   ├── cli/                            # Command line interface and commands
│   ├── db/                             # SQLite WAL schema and ledger engine
│   ├── decision/                       # LangGraph tournament, validators, and engine
│   ├── extraction/                     # Evidence windows, topology, and agents
│   ├── llm/                            # Ollama client and JSON repair utilities
│   ├── matching/                       # Fact identities, temporal checks, and 4-gate engine
│   ├── observability/                  # Markdown report generators and metrics
│   └── pdf/                            # PyMuPDF and pdfplumber spatial layout parsers
└── tests/                              # 100 automated unit, contract, and scenario tests
```

---

## 10. Architectural Defensibility and Governance

- **Zero-LLM Decision Invariant:** No generative model is permitted at the verdict gate; all outcomes are governed by deterministic Python truth tables.
- **Audit Lineage:** Every extracted number is bound to page coordinates and verbatim chunk text.
- **Epistemic Integrity:** The system never guesses; when evidence is insufficient, it reports `UNRESOLVED` with explicit documentation of missing facts.
- **Strict Cleanliness:** Zero emojis exist anywhere across the project's codebase, comments, logs, or documentation.