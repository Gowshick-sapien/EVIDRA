# Deliverables Definition

This document outlines the concrete deliverables for the Fact Knowledge Layer prototype, mapped directly to the Implementable Scope defined in the project ideation.

## D0: Prerequisite and Environment Verification
**Goal:** Ensure the local environment is fully prepared before starting implementation, minimizing runtime and external dependency issues.
* **D0.1 Python Environment Check:** Verification of Python 3.11+ installation and successful installation of all core packages from 
equirements.txt.
* **D0.2 Ollama Runtime Check:** Verification that the Ollama local daemon is installed, actively running, and accessible via local HTTP port.
* **D0.3 LLM Model Pull Verification:** Verification that the specific primary reasoning model (qwen2.5:7b-instruct) is pulled and successfully loads into memory.
* **D0.4 Embedding Model Cache Check:** Verification that sentence-transformers can successfully fetch, cache, and initialize the BAAI/bge-small-en-v1.5 model for candidate matching.
* **D0.5 External Binary Check (Optional):** Verification of Tesseract OCR binary availability (only if the scanned-document fallback path is invoked).

## D1: Core Infrastructure and Evidence Ledger
**Goal:** Establish the foundational storage, API, and CLI components.
* **D1.1 SQLite Evidence Ledger:** Implementation of the relational schema for documents, evidence chunks, observations, fact candidates, fact groups, hypotheses, decisions, and traces.
* **D1.2 Artifact Engine:** Utilities to generate structured JSON, JSONL, and Markdown reports.
* **D1.3 FastAPI Skeleton:** Basic REST endpoints for job submission and inspection.
* **D1.4 CLI Entry Point:** The rgparse based command-line interface for local execution.

## D2: Document Processing and Extraction Layer (Layer 1 & 2a)
**Goal:** Ingest PDFs and extract structured observations with strict evidence provenance.
* **D2.1 Two-Tool PDF Pipeline:** Integration of PyMuPDF (text/blocks) and pdfplumber (tables).
* **D2.2 Evidence Bundle Generator:** System to assign stable IDs and bounding boxes to text and table fragments.
* **D2.3 ReasoningService Abstraction:** The interface for LLM calls, configured for Ollama (Qwen2.5).
* **D2.4 Extraction Agents:** Prompts and Pydantic schemas for numerical, semantic, and event extraction.

## D3: Verification, Context, and Normalization Layer (Layer 2b)
**Goal:** Validate extracted claims and resolve their context.
* **D3.1 Evidence Verifier:** Agent that independently checks if an observation is entailed by its cited evidence.
* **D3.2 Context Resolver:** Agent that extracts dimensions of meaning (unit, currency, period, scope).
* **D3.3 Deterministic Normalizers:** Pure Python logic for financial arithmetic (Decimal), unit scaling (crore/lakh), and temporal parsing (dateutil).
* **D3.4 Candidate Matching:** Implementation of sentence-transformers (BGE-Small) to group facts by entity and attribute similarity.

## D4: Fact Decision Engine (Layer 3)
**Goal:** Orchestrate the reasoning workflow to detect corroboration, contradiction, and reconciliation.
* **D4.1 LangGraph Orchestrator:** The state graph defining the deterministic workflow.
* **D4.2 Hypothesis Generator & Validators:** Logic to propose explanations for variances and specialized validators to test them.
* **D4.3 Reconciliation & Adversarial Agents:** The core debate mechanism where reconciliations are proposed and challenged against original evidence.
* **D4.4 Decision Policy Engine:** Pure Python deterministic rules mapping validator outcomes to final verdicts (CORROBORATED, CONTRADICTION, RECONCILED, UNRESOLVED).

## D5: Observability, Reporting, and Testing (Layer 4)
**Goal:** Ensure the system is auditable, explainable, and verified.
* **D5.1 Decision Trace Generator:** Full audit trail generation for every decision.
* **D5.2 Markdown Reporters:** Generation of Executive Summary, Contradiction Report, and Unresolved Report.
* **D5.3 Test Suites:** Implementation of unit tests, contract tests, and evaluation benchmarks.
* **D5.4 Required Demo Cases:** Verification that the system successfully processes the four required assignment cases.
