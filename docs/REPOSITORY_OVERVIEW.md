# EVIDRA: Repository Overview and Inspection Guide

## Navigational Map for Evaluators, Auditors, and Technical Reviewers

---

## 1. Purpose of this Guide

This document serves as the primary navigational directory for evaluating the **EVIDRA** repository. It outlines:
1. The purpose and scope of every document in the repository.
2. Where to inspect the source code and architectural components.
3. Where to verify automated test suites and test coverage.
4. Where to find and inspect real-world manual verification artifacts (reports, SQLite ledgers, execution traces).
5. A recommended 15-minute evaluation pathway for examiners and auditors.

---

## 2. Documentation Directory Map

The documentation is organized into two distinct tiers: **Primary Publishable Documentation** (for evaluators, examiners, and users) and **Internal Developer Specifications** (for engineers and system maintainers).

```text
EVIDRA/
├── README.md                           # Main repository entry point and quickstart
└── docs/
    ├── REPOSITORY_OVERVIEW.md          # This document: navigation guide and inspection directory
    ├── PROPOSED_SOLUTION.md            # Comprehensive solution blueprint and evaluation guide
    ├── RUN_PLAN.md                     # Operational verification runbook (CLI, API, test procedures)
    ├── deliverable_plans/              # Granular phase implementation and verification records
    │   ├── P0_IMPLEMENTATION_PLAN.md   # Phase P0: Evidence extraction and geometry
    │   ├── P0_TESTING_AND_VERIFICATION_PLAN.md
    │   ├── P1_IMPLEMENTATION_PLAN.md   # Phase P1: 4-gate resolution and claim graph
    │   ├── P1_TESTING_AND_VERIFICATION_PLAN.md
    │   ├── P2_IMPLEMENTATION_PLAN.md   # Phase P2: Evidence sufficiency and tournament
    │   └── P2_TESTING_AND_VERIFICATION_PLAN.md # Real-world Delhivery run verification
    └── developer/                      # Detailed engineering specifications
        ├── README.md                   # Developer index and navigation guide
        ├── ARCHITECTURE_README.md      # Comprehensive 4-layer system architecture specification
        ├── ARCHITECTURE_V1.md          # Reasoning tournament and validator specification
        ├── ARCHITECTURE_V2.md          # Structural evidence resolution and 4-gate matching specification
        ├── SRS_V1.md & SRS_V2.md       # Software Requirements Specifications
        ├── DELIVERABLES_DEFINITION_V1.md & DELIVERABLES_DEFINITION_V2.md # Engineering phase roadmaps
        ├── TECH_STACK.md               # Technology choices, dependencies, and rationale
        ├── PROJECT_IDEATION.md         # Epistemic whitepaper ("The Fact is Not the Primitive")
        ├── DEV_RUN_PLAN.md             # Developer runbook and debugging diagnostics
        └── REPOSITORY_STRUCTURE.md     # Package architecture layout
```

### 2.1 Primary Publishable Documentation (Root & `docs/`)

| Document | Target Audience | Primary Content & Purpose |
| :--- | :--- | :--- |
| **[README.md](file:///d:/projects/superjoin/EVIDRA/README.md)** | Evaluators, Users | Executive overview, the 4 canonical outcomes table, quickstart setup, CLI/API execution instructions, validation instructions, and documentation index. |
| **[docs/REPOSITORY_OVERVIEW.md](file:///d:/projects/superjoin/EVIDRA/docs/REPOSITORY_OVERVIEW.md)** | Evaluators, Auditors | Comprehensive directory mapping: what each document conveys, where to check source modules, and where to inspect manual verification artifacts. |
| **[docs/PROPOSED_SOLUTION.md](file:///d:/projects/superjoin/EVIDRA/docs/PROPOSED_SOLUTION.md)** | Evaluators, Architects | The solution blueprint: contrasts conventional RAG failures with EVIDRA's 6 pillars, describes the 4-stage pipeline, and walks through 4 real corporate case studies. |
| **[docs/RUN_PLAN.md](file:///d:/projects/superjoin/EVIDRA/docs/RUN_PLAN.md)** | Evaluators, Operators | Step-by-step operational runbook: pre-flight diagnostics, CLI options, interactive FastAPI server, 110 automated tests, and SQLite audit queries. |

### 2.2 Phase Implementation and Verification Plans (`docs/deliverable_plans/`)

| Phase Plan | Scope and Deliverables | Verification Record |
| :--- | :--- | :--- |
| **Phase P0** | Document Evidence Preparation & Structural Layout Extraction (PyMuPDF geometry, pdfplumber tables, layout topology, evidence windows, candidate budget). | [P0 Verification Plan](file:///d:/projects/superjoin/EVIDRA/docs/deliverable_plans/P0_TESTING_AND_VERIFICATION_PLAN.md): Unit tests for geometry, layout topology, and tabular grid preservation. |
| **Phase P1** | Fact Identity Signatures, 4-Gate Contextual Fact Resolution, Temporal Comparability Algebra, Pairwise Claim Graph, and Equivalence Clustering. | [P1 Verification Plan](file:///d:/projects/superjoin/EVIDRA/docs/deliverable_plans/P1_TESTING_AND_VERIFICATION_PLAN.md): 4-gate isolation tests and zero cross-dimensional contamination checks. |
| **Phase P2** | Rule-Based Evidence Sufficiency Gate, Calibrated Specialist Validators, Adversarial Challenge, and End-to-End Delhivery Prospectus Run. | [P2 Verification Plan](file:///d:/projects/superjoin/EVIDRA/docs/deliverable_plans/P2_TESTING_AND_VERIFICATION_PLAN.md): 110 passing automated tests and real-world run analysis (`JOB-20260908-133430-8f0093`). |

### 2.3 Internal Developer Specifications (`docs/developer/`)

| Specification | Technical Focus |
| :--- | :--- |
| **[ARCHITECTURE_README.md](file:///d:/projects/superjoin/EVIDRA/docs/developer/ARCHITECTURE_README.md)** | Complete technical blueprint of all 4 operational layers, dataflow diagrams, and system invariants. |
| **[ARCHITECTURE_V2.md](file:///d:/projects/superjoin/EVIDRA/docs/developer/ARCHITECTURE_V2.md)** | Detailed specification of layout topology, context-enriched evidence windows, dynamic schema induction, and 4-gate fact resolution. |
| **[ARCHITECTURE_V1.md](file:///d:/projects/superjoin/EVIDRA/docs/developer/ARCHITECTURE_V1.md)** | Detailed specification of the LangGraph tournament state machine, specialist validators, and adversarial challenger. |
| **[SRS_V2.md](file:///d:/projects/superjoin/EVIDRA/docs/developer/SRS_V2.md)** | Formal software requirements specification for document layout extraction, schema induction, identity resolution, and 4-gate matching. |
| **[TECH_STACK.md](file:///d:/projects/superjoin/EVIDRA/docs/developer/TECH_STACK.md)** | Exhaustive evaluation of PyMuPDF, pdfplumber, Ollama (`qwen2.5:3b`), SQLite WAL mode, and Pydantic v2. |
| **[PROJECT_IDEATION.md](file:///d:/projects/superjoin/EVIDRA/docs/developer/PROJECT_IDEATION.md)** | Foundational philosophical paper establishing the core premise: "The Fact is Not the Primitive." |

---

## 3. Where to Check the Source Code

The implementation is located in `src/`, cleanly separated into modular layers:

```text
src/
├── pdf/                    # Layer 1: Physical Geometry & Layout Extraction
│   ├── parser.py           # PyMuPDF block, line, and bounding box extraction
│   ├── tables.py           # pdfplumber tabular grid extraction and coordinate alignment
│   ├── topology.py         # Z-score font distribution analysis and layout hierarchy classification
│   └── windows.py          # Context-enriched evidence windows (headers, captions, units)
│
├── extraction/             # Layer 2a: Fact Generation & Candidate Management
│   ├── schemas.py          # Core Pydantic contracts (EvidenceChunk, FactCandidate)
│   ├── agents.py           # Local LLM prompts for extracting raw candidate assertions
│   ├── schema_induction.py # Dynamic induction of corporate legal entities and metric families
│   └── budget.py           # 3-tier candidate discovery ensuring 100% table preservation
│
├── verification/           # Layer 2b: Fact Verification & Semantic Normalization
│   ├── verifier.py         # Verbatim source entailment verification
│   ├── normalizers.py      # Decimal arithmetic scaling and temporal date parsing
│   └── pipeline.py         # Layer 2 verification orchestrator
│
├── matching/               # Layer 2c: Fact Identity & 4-Gate Matching Engine
│   ├── identity.py         # FactIdentitySignature and deterministic measurement typing
│   ├── temporal.py         # TemporalComparabilityClassifier (6 topological intervals)
│   ├── engine.py           # 4-Gate Contextual Fact Resolution engine (Entity, Time, Metric, Context)
│   ├── graph.py            # Pairwise Claim Relationship Graph construction
│   └── clustering.py       # Value equivalence clustering (<0.1% tolerance)
│
├── decision/               # Layer 3: Fact Decision Engine & Reasoning Tournament
│   ├── sufficiency.py      # Rule-Based Evidence Sufficiency Gate (screening single/incomplete claims)
│   ├── workflow.py         # LangGraph state machine orchestrating pairwise debate
│   ├── hypothesis.py       # Hypothesis generator proposing candidate reconciliations
│   ├── validators.py       # 5 Specialist validators (Arithmetic, Scope, Accounting Basis, Restatement, Timing)
│   ├── reconciliation.py   # Reconciliation proposer and Adversarial Skeptic agents
│   ├── policy.py           # Pure Python deterministic verdict truth tables (Zero-LLM Gate)
│   └── engine.py           # Full decision orchestrator across fact groups
│
├── db/                     # Layer 4: Relational Evidence Ledger
│   ├── schema.sql          # SQLite DDL defining documents, chunks, identities, relationships, decisions
│   └── ledger.py           # SQLite WAL connection manager and query interfaces
│
├── observability/          # Layer 4: Observability, Tracing, and Reporting
│   ├── reports.py          # Markdown report generator (summary.md, contradictions.md, unresolved.md)
│   └── trace.py            # Append-only JSONL streaming execution tracer
│
├── api/                    # Layer 4: Interactive Web API
│   ├── server.py           # FastAPI application, CORS, Swagger UI, and background task dispatch
│   └── models.py           # Pydantic request/response schemas for REST endpoints
│
└── cli/                    # Layer 4: Command Line Interface
    └── main.py             # CLI entry point (process, serve, replay, verify)
```

---

## 4. Where to Check Automated Test Verification

EVIDRA includes **110 passing automated tests** across three testing categories:

```powershell
pytest tests/ -v
```

### Test Directory Breakdown:
- **`tests/unit/` (98 tests):**
  - [`test_sufficiency.py`](file:///d:/projects/superjoin/EVIDRA/tests/unit/test_sufficiency.py): Evidence Sufficiency Gate logic (single-source isolation, missing dimensions).
  - [`test_validators_p2.py`](file:///d:/projects/superjoin/EVIDRA/tests/unit/test_validators_p2.py): Specialist validators (Ind AS vs Non-GAAP, restatement, timing).
  - [`test_p2_pipeline.py`](file:///d:/projects/superjoin/EVIDRA/tests/unit/test_p2_pipeline.py): End-to-end P2 integration pipeline.
  - [`test_4gate_resolution.py`](file:///d:/projects/superjoin/EVIDRA/tests/unit/test_4gate_resolution.py): 4-gate isolation rules (entity, temporal, metric typing, context).
  - [`test_claim_graph.py`](file:///d:/projects/superjoin/EVIDRA/tests/unit/test_claim_graph.py): Pairwise graph edge construction and value clustering.
  - [`test_decimal_units.py`](file:///d:/projects/superjoin/EVIDRA/tests/unit/test_decimal_units.py): Decimal unit normalization and arithmetic precision.
  - [`test_decision.py`](file:///d:/projects/superjoin/EVIDRA/tests/unit/test_decision.py): Deterministic decision policy truth tables.
  - [`test_temporal_comparability.py`](file:///d:/projects/superjoin/EVIDRA/tests/unit/test_temporal_comparability.py): Topological interval algebra.
  - [`test_topology.py`](file:///d:/projects/superjoin/EVIDRA/tests/unit/test_topology.py): Z-score font distribution and layout hierarchy.
  - [`test_windows.py`](file:///d:/projects/superjoin/EVIDRA/tests/unit/test_windows.py): Context-enriched evidence windows.
  - [`test_ledger.py`](file:///d:/projects/superjoin/EVIDRA/tests/unit/test_ledger.py): SQLite WAL database schema and queries.
  - [`test_cli.py`](file:///d:/projects/superjoin/EVIDRA/tests/unit/test_cli.py): CLI argument parsing and flags.
- **`tests/contracts/` (7 tests):**
  - [`test_api.py`](file:///d:/projects/superjoin/EVIDRA/tests/contracts/test_api.py): FastAPI REST endpoint contracts and Swagger schema compliance.
- **`tests/evaluation/` (5 tests):**
  - [`test_scenarios.py`](file:///d:/projects/superjoin/EVIDRA/tests/evaluation/test_scenarios.py): Comprehensive evaluations of the four canonical outcomes.

---

## 5. Where to Check Manual Real-World Verification

To verify that the system operates effectively on real-world financial documents, inspect the completed execution artifacts from the manual test run on the Delhivery IPO Prospectus excerpt (`sample_docs/01-delhivery-prospectus-2022-excerpt.pdf`).

### 5.1 Real-World Execution Job: `runs/JOB-20260908-133430-8f0093/`

This run processed 15 chunks from the prospectus, extracted 48 candidate claims, formed 48 fact groups, and rendered 48 audited decisions:
- **3 Corroborated Decisions:** Independent confirmation across pages (including Revenue from Operations at `36,465.27 million INR` on Pages 22 and 27).
- **1 Contradiction Decision:** Genuine conflict across intragroup elimination adjustments (`-1.98` vs `-4.56` vs `-5.67 million INR`).
- **44 Unresolved Decisions:** Single-source disclosures correctly isolated by the Evidence Sufficiency Gate without speculative guessing.

### 5.2 Specific Artifacts to Inspect:

1. **Executive Dashboard:**
   - Path: [`runs/JOB-20260908-133430-8f0093/reports/summary.md`](file:///d:/projects/superjoin/EVIDRA/runs/JOB-20260908-133430-8f0093/reports/summary.md)
   - What to check: Document metadata, chunk topology breakdown, candidate counts, and decision distribution.

2. **Contradictions Audit:**
   - Path: [`runs/JOB-20260908-133430-8f0093/reports/contradictions.md`](file:///d:/projects/superjoin/EVIDRA/runs/JOB-20260908-133430-8f0093/reports/contradictions.md)
   - What to check: Side-by-side comparison of conflicting figures with exact page bounding boxes `[x0, y0, x1, y1]`, verbatim source sentences, and falsification logs.

3. **Unresolved Disclosures Audit:**
   - Path: [`runs/JOB-20260908-133430-8f0093/reports/unresolved.md`](file:///d:/projects/superjoin/EVIDRA/runs/JOB-20260908-133430-8f0093/reports/unresolved.md)
   - What to check: Complete ledger of single-source disclosures marked as `UNRESOLVED` (Strength: `LOW`) with documented missing second sources.

4. **Relational SQLite WAL Ledger:**
   - Path: `runs/JOB-20260908-133430-8f0093/ledger.db`
   - How to inspect:
     ```powershell
     # Query 1: Fact Identities and Measurement Types
     sqlite3 runs/JOB-20260908-133430-8f0093/ledger.db "SELECT fact_id, measurement_type, metric_family, metric_subtype FROM fact_identities LIMIT 5;"

     # Query 2: Claim Relationships and Variances
     sqlite3 runs/JOB-20260908-133430-8f0093/ledger.db "SELECT relationship_id, relationship_type, variance_percentage FROM claim_relationships LIMIT 5;"

     # Query 3: Final Decisions Breakdown
     sqlite3 runs/JOB-20260908-133430-8f0093/ledger.db "SELECT verdict, decision_strength, count(*) FROM decisions GROUP BY verdict, decision_strength;"
     ```

5. **Chronological Event Stream:**
   - Path: `runs/JOB-20260908-133430-8f0093/traces/trace.jsonl`
   - What to check: Millisecond-precision audit stream recording every lifecycle event, state transition, and tool call.

6. **Extracted Financial Tables:**
   - Path: `runs/JOB-20260908-133430-8f0093/evidence/tables/`
   - What to check: Clean markdown tables extracted by `pdfplumber` with structural headers preserved.

7. **Comprehensive Verification Plan & Audit:**
   - Path: [`docs/deliverable_plans/P2_TESTING_AND_VERIFICATION_PLAN.md`](file:///d:/projects/superjoin/EVIDRA/docs/deliverable_plans/P2_TESTING_AND_VERIFICATION_PLAN.md)
   - What to check: Detailed walkthrough of the manual test run, command executed, outputs, and validation checklists.

---

## 6. Recommended 15-Minute Evaluation Pathway

For an evaluator or examiner reviewing EVIDRA for the first time, the following sequential path is recommended:

```text
[Step 1: 3 Minutes] -> Read docs/PROPOSED_SOLUTION.md (Executive Summary, 6 Pillars, 4 Outcomes)
         |
         v
[Step 2: 3 Minutes] -> Run Automated Tests: pytest tests/ -v (Verify 110 tests pass)
         |
         v
[Step 3: 4 Minutes] -> Inspect Real Run Reports in runs/JOB-20260908-133430-8f0093/reports/
                        - summary.md
                        - contradictions.md
                        - unresolved.md
         |
         v
[Step 4: 3 Minutes] -> Query SQLite Ledger (Verify physical coordinates and relationships in ledger.db)
         |
         v
[Step 5: 2 Minutes] -> Check Source Code:
                        - src/matching/engine.py (4-Gate contextual isolation)
                        - src/decision/policy.py (Zero-LLM deterministic verdict logic)
```

---

## 7. Sample Corporate Filings Dataset

The `sample_docs/` directory contains real corporate PDF filings from Delhivery Limited used during system evaluation:
- `sample_docs/01-delhivery-prospectus-2022-excerpt.pdf`: Excerpt from the audited IPO prospectus containing restated financial statements, intragroup eliminations, and capitalization tables.
- `sample_docs/02-delhivery-annual-report-2024-excerpt.pdf`: Excerpt from the audited 2024 annual report.
- `sample_docs/03-delhivery-earnings-presentation-q4fy24.pdf`: Q4 FY24 earnings presentation containing investor metrics and Non-GAAP reconciliations.
