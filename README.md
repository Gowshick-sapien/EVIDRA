# EVIDRA

## Evidence-Driven Architecture for Fact Validation and Knowledge Reasoning

---

## Executive Overview

**EVIDRA** is an evidence-centric financial document reasoning architecture designed to solve a fundamental challenge in automated intelligence: **How do we reliably determine when multiple corporate documents agree, directly contradict, or can be logically reconciled?**

Conventional Large Language Model (LLM) pipelines and Retrieval-Augmented Generation (RAG) systems treat extracted claims as atomic facts and rely on opaque generative models to output answers. When faced with conflicting financial disclosures across earnings press releases, quarterly Form 10-Q filings, and annual Form 10-K reports, traditional systems either hallucinate false consensus or declare erroneous contradictions.

EVIDRA introduces a paradigm where **the fact is not the primitive**. The system establishes an auditable, cryptographic Evidence Ledger where:
* What a document literally asserts (**Observation**) is strictly decoupled from what the system deduces (**Decision**).
* Every claim is anchored to physical PDF coordinates (x0, y0, x1, y1), page numbers, and SHA-256 cryptographic chunk hashes.
* Reconciliation is not a subjective LLM generation, but a structured debate where an **Adversarial Skeptic** systematically attempts to falsify proposed reconciliation bridges using original source documents.
* Financial arithmetic, unit scaling, date intervals, and final verdict policies are executed by **deterministic pure Python modules**, reserving local LLMs strictly for semantic extraction and hypothesis formulation.
* When evidence is insufficient, contradictory without an explanatory bridge, or unentailed, the system explicitly reports **UNRESOLVED** as a first-class epistemic verdict rather than guessing.

---

## The Core Philosophy

EVIDRA operates on five foundational axioms:

1. **Evidence Before Fact:** No claim enters the reasoning pipeline without an immutable link to its source document, page, and geometric bounding box.
2. **Observation is Distinct from Decision:** A source document's assertion is an immutable historical observation. The system's verdict is a derived, falsifiable conclusion. Conflating the two destroys auditability.
3. **Context Before Contradiction:** If Document A reports Revenue of  and Document B reports , they do not automatically contradict. The system systematically investigates multidimensional contextual differences: reporting periods, accounting standards (GAAP vs. Non-GAAP), organizational scopes (Consolidated vs. Standalone), and post-period audit restatements.
4. **Adversarial Skepticism:** Whenever a reconciliation explanation is proposed, an independent adversarial agent attempts to falsify that explanation using the raw source text. A reconciliation only survives if it cannot be refuted by the evidence.
5. **UNRESOLVED is a First-Class Citizen:** In financial and regulatory intelligence, forcing a binary verdict when evidence is incomplete is catastrophic. Admitting uncertainty with an explicit diagnostic explanation is superior to confident hallucination.

---

## System Architecture

EVIDRA organizes document intelligence into four distinct, inspectable layers:

`
+-----------------------------------------------------------------------------------+
|                        LAYER 1: DOCUMENT EVIDENCE PREPARATION                     |
|                                                                                   |
|  * PyMuPDF (fitz): Spatial text blocks, font flags, and bounding box geometry.   |
|  * pdfplumber: Structural table grids, cell coordinates, and multi-row headers.   |
|  * Spatial Disambiguation: Masks table regions to eliminate duplicate text.       |
|  * Output: Document Manifest, Context Envelopes, and Evidence-Tagged Markdown.    |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                        LAYER 2: FACT CONSTRUCTION & VERIFICATION                  |
|                                                                                   |
|  * Dual Extraction: Table-native direct cell parsing and prose LLM extraction.    |
|  * Extract-Then-Verify: Independent verifier tests raw chunk entailment.          |
|  * Deterministic Normalizers: Exact Python Decimal math and ISO 8601 date intervals|
|  * Two-Tier Candidate Blocking: Hard entity/period filter + BGE-Small embeddings. |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                        LAYER 3: FACT DECISION ENGINE (LangGraph)                  |
|                                                                                   |
|  * Three Adaptive Decision Paths: Deterministic, Contextual, and Conflict Debate. |
|  * Hypothesis Tournament: 5 variance classes (Restatement, GAAP, Scope, etc.).   |
|  * Specialist Validators: Pure Python rules and targeted evidence probes.         |
|  * Adversarial Challenge: Reconciliation Proposer vs. Adversarial Skeptic.        |
|  * Deterministic Decision Policy: Pure Python truth tables for final verdicts.    |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                        LAYER 4: OBSERVABILITY & INSPECTION                        |
|                                                                                   |
|  * Evidence Ledger: 10-table relational SQLite database (ledger.db).              |
|  * Cryptographic Audit Logs: Millisecond-precision streaming trace.jsonl.         |
|  * Human Reports: Executive Summary, Contradiction Report, Unresolved Report.     |
|  * Inspection Interfaces: Interactive FastAPI Swagger UI (/docs) and CLI.         |
+-----------------------------------------------------------------------------------+
`

---

## The Four Epistemic Verdicts

Every evaluated relationship between facts across documents receives one of four categorical verdicts:

| Verdict | Meaning | Required Epistemic Condition |
|---|---|---|
| **CORROBORATED** | Independent confirmation | Multiple independent sources assert matching values (within 0.01% tolerance) under identical entity, period, and scope. |
| **CONTRADICTION** | Genuine, irreconcilable conflict | Material numerical or qualitative disagreement with matching context, where all reconciliation hypotheses have been falsified. |
| **RECONCILED** | Apparent conflict explained | Variance is fully explained by documented context (audit restatement, GAAP-to-Non-GAAP bridge, scope variation) that survived adversarial challenge. |
| **UNRESOLVED** | Incomplete or ambiguous evidence | Insufficient contextual disclosures, unentailed observations, or conflicting non-reconciled claims requiring human analyst investigation. |

---

## Inspecting the Results

EVIDRA is designed from the ground up for total transparency and human auditability:

### 1. The Decision Card
Every evaluated fact relationship produces a structured **Decision Card** displaying:
* Target entity, attribute, and temporal interval.
* Side-by-side claim comparison with normalized values.
* Physical provenance citations: source document name, page number, and geometric bounding box coordinates.
* Detailed reconciliation narrative and arithmetic bridge breakdown.
* Adversarial skeptic audit summary detailing hypotheses tested and falsification outcomes.

### 2. Automated Markdown Reports
Every processing run generates three human-readable reports in uns/JOB-{id}/reports/:
* **Executive Summary (summary.md):** Complete job dashboard detailing total documents ingested, evidence chunks generated, fact groups formed, and verdict breakdowns.
* **Contradiction Report (contradictions.md):** Deep-dive report on all detected conflicts, highlighting variance magnitudes and failed reconciliation paths.
* **Unresolved Analysis Report (unresolved.md):** Diagnostic breakdown of ambiguous observations with targeted recommendations for human analysts.

### 3. Relational Evidence Ledger (ledger.db)
An isolated SQLite database per run recording the entire relational progression across 10 tables: documents, evidence_chunks, observations, act_candidates, act_groups, group_members, hypotheses, alidator_results, decisions, and decision_traces.

---

## Quick Start and Local Execution

EVIDRA runs entirely on local infrastructure without external cloud dependencies or paid API keys.

### 1. Prerequisites
* **Python:** Version 3.11 or greater (Python 3.11 and 3.12 supported).
* **Ollama Daemon:** Running locally at http://127.0.0.1:11434 with model qwen2.5:3b or qwen2.5:7b-instruct.
* **Dependencies:** Installed via pip install -r requirements.txt.

### 2. Verify Environment (Pre-Flight Diagnostics)
Execute the automated pre-flight diagnostic runner to confirm Python dependencies, Ollama connectivity, structured JSON inference, and local embedding cache readiness:
`powershell
python scripts/verify_env.py
`

### 3. Run Automated Test Suites
Execute the full test suite verifying database integrity, API contracts, trace loggers, and CLI commands:
`powershell
pytest -v
`

### 4. Process Documents via CLI
Submit a directory of PDF documents for processing:
`powershell
python -m src.cli.main process sample_docs/
`

### 5. Inspect Results
Inspect decisions from a completed run:
```powershell
python -m src.cli.main inspect <JOB_ID>
```

Export job reports in Markdown or JSON:
```powershell
python -m src.cli.main report <JOB_ID> --type summary
python -m src.cli.main report <JOB_ID> --type contradictions
python -m src.cli.main report <JOB_ID> --type unresolved
python -m src.cli.main report <JOB_ID> --format json
```

Forensically replay cryptographic decision traces:
```powershell
python -m src.cli.main replay <JOB_ID>
python -m src.cli.main replay <JOB_ID> --decision-id <DECISION_ID>
```

Execute automated evaluation benchmarks:
```powershell
python -m src.cli.main benchmark
python -m src.cli.main benchmark --format json
```

### 6. Launch the Interactive API Server
Start the FastAPI server with auto-generated Swagger documentation:
```powershell
python -m src.cli.main serve --port 8000
```
Navigate to http://127.0.0.1:8000/docs in any browser to interactively upload documents, inspect decision cards, stream traces, and query job statuses.

---

## Complete Project Documentation

| Document | Purpose |
|---|---|
| [docs/RUN_PLAN.md](file:///d:/projects/superjoin/project/docs/RUN_PLAN.md) | Operational run plan, PDF upload instructions, and verification guide for evaluators. |
| [docs/PROJECT_IDEATION.md](file:///d:/projects/superjoin/project/docs/PROJECT_IDEATION.md) | Original design philosophy, scope boundaries, and thesis statement. |
| [docs/ARCHITECTURE.md](file:///d:/projects/superjoin/project/docs/ARCHITECTURE.md) | Comprehensive 4-layer system architecture and data topology specification. |
| [docs/SRS.md](file:///d:/projects/superjoin/project/docs/SRS.md) | IEEE 830-aligned Software Requirements Specification and traceability matrix. |
| [docs/TECH_STACK.md](file:///d:/projects/superjoin/project/docs/TECH_STACK.md) | Frozen technology stack selections, dependencies, and explicit exclusions. |
| [docs/DELIVERABLES_DEFINITION.md](file:///d:/projects/superjoin/project/docs/DELIVERABLES_DEFINITION.md) | Master deliverables definition and phase gate exit criteria (D0 through D5). |
| [docs/repository_structure.md](file:///d:/projects/superjoin/project/docs/repository_structure.md) | Complete directory tree layout and module responsibility guide. |
| [docs/deliverable_plans/D1_IMPLEMENTATION_PLAN.md](file:///d:/projects/superjoin/project/docs/deliverable_plans/D1_IMPLEMENTATION_PLAN.md) | Technical implementation plan for Deliverable 1. |
| [docs/deliverable_plans/D0_AND_D1_TESTING_AND_VERIFICATION_PLAN.md](file:///d:/projects/superjoin/project/docs/deliverable_plans/D0_AND_D1_TESTING_AND_VERIFICATION_PLAN.md) | Automated and manual testing guide for D0 and D1. |
| [docs/deliverable_plans/D2_IMPLEMENTATION_PLAN.md](file:///d:/projects/superjoin/project/docs/deliverable_plans/D2_IMPLEMENTATION_PLAN.md) | Technical implementation plan for Deliverable 2 (Ingestion & Extraction). |
| [docs/deliverable_plans/D2_TESTING_AND_VERIFICATION_PLAN.md](file:///d:/projects/superjoin/project/docs/deliverable_plans/D2_TESTING_AND_VERIFICATION_PLAN.md) | Testing and verification guide for Deliverable 2. |
| [docs/deliverable_plans/D3_IMPLEMENTATION_PLAN.md](file:///d:/projects/superjoin/project/docs/deliverable_plans/D3_IMPLEMENTATION_PLAN.md) | Technical implementation plan for Deliverable 3 (Normalization & Grouping). |
| [docs/deliverable_plans/D3_TESTING_AND_VERIFICATION_PLAN.md](file:///d:/projects/superjoin/project/docs/deliverable_plans/D3_TESTING_AND_VERIFICATION_PLAN.md) | Testing and verification guide for Deliverable 3. |
| [docs/deliverable_plans/D4_IMPLEMENTATION_PLAN.md](file:///d:/projects/superjoin/project/docs/deliverable_plans/D4_IMPLEMENTATION_PLAN.md) | Technical implementation plan for Deliverable 4 (Fact Decision Engine). |
| [docs/deliverable_plans/D4_TESTING_AND_VERIFICATION_PLAN.md](file:///d:/projects/superjoin/project/docs/deliverable_plans/D4_TESTING_AND_VERIFICATION_PLAN.md) | Testing and verification guide for Deliverable 4. |
| [docs/deliverable_plans/D5_IMPLEMENTATION_PLAN.md](file:///d:/projects/superjoin/project/docs/deliverable_plans/D5_IMPLEMENTATION_PLAN.md) | Technical implementation plan for Deliverable 5 (Observability & Evaluation). |
| [docs/deliverable_plans/D5_TESTING_AND_VERIFICATION_PLAN.md](file:///d:/projects/superjoin/project/docs/deliverable_plans/D5_TESTING_AND_VERIFICATION_PLAN.md) | Testing and verification guide for Deliverable 5. |