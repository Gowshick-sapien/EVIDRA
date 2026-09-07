# Software Requirements Specification (SRS)

## 1. Introduction
This document specifies the software requirements for the Fact Knowledge Layer prototype. The system is designed to ingest financial documents, extract structured observations with strict evidence provenance, and orchestrate a multi-agent reasoning workflow to reconcile competing facts.

## 2. Functional Requirements (FR)

| ID | Requirement | Mapped Deliverable |
|---|---|---|
| **FR1** | The system must ingest arbitrary digital PDF documents and extract text blocks with precise bounding box coordinates. | D2.1 |
| **FR2** | The system must detect and extract tabular data, preserving column boundaries, cell structures, and merged headers. | D2.1 |
| **FR3** | Every extracted claim must be linked to a specific Evidence Bundle containing the source document, page, and exact text/coordinates. | D2.2 |
| **FR4** | The system must extract numerical, semantic, and event-based facts using a structured LLM extraction agent. | D2.4 |
| **FR5** | An independent Evidence Verifier must validate that an extracted fact is strictly entailed by its cited evidence. | D3.1 |
| **FR6** | The system must resolve contextual dimensions for facts, including units, currencies, periods, and organizational scope. | D3.2 |
| **FR7** | Financial arithmetic and unit scaling must be performed using deterministic logic (e.g., Python Decimal), not the LLM. | D3.3 |
| **FR8** | The system must group similar facts across documents using semantic embeddings for entity and attribute matching. | D3.4 |
| **FR9** | A deterministic orchestrator must control the workflow logic, evaluating corroboration, contradiction, and reconciliation paths. | D4.1 |
| **FR10** | When facts differ, the system must generate competing reconciliation hypotheses (e.g., temporal mismatch, scope difference). | D4.2 |
| **FR11** | An Adversarial Challenge agent must attempt to falsify any proposed reconciliation using the original source evidence. | D4.3 |
| **FR12** | A deterministic Decision Policy engine must map validation results to a final categorical verdict (CORROBORATED, CONTRADICTION, RECONCILED, UNRESOLVED). | D4.4 |
| **FR13** | The system must produce a complete, inspectable audit trace for every final decision. | D5.1 |
| **FR14** | The system must expose a REST API (FastAPI) and a CLI (argparse) for job submission and inspection. | D1.3, D1.4 |

## 3. Non-Functional Requirements (NFR)

| ID | Requirement | Mapped Deliverable |
|---|---|---|
| **NFR1** | **Local Execution:** All generative reasoning must run locally via Ollama to ensure cost control and eliminate proprietary API dependencies. | D2.3 |
| **NFR2** | **Determinism in Rules:** Epistemic policies, financial math, and workflow routing must be strictly deterministic and auditable in Python code. | D3.3, D4.4 |
| **NFR3** | **Schema Strictness:** All inter-agent communication and LLM outputs must be strictly validated against Pydantic schemas. | D2.4, D4.1 |
| **NFR4** | **Storage Portability:** The primary data store must be a portable, zero-configuration relational database (SQLite). | D1.1 |
| **NFR5** | **Zero Frontend Dependency:** The system must satisfy UI review requirements using purely the Swagger UI and human-readable Markdown reports. | D1.3, D5.2 |
