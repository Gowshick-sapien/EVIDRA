# Repository Structure

This document defines the complete base repository structure for the Fact Knowledge Layer project. This layout enforces the strict separation of concerns outlined in the architecture and provides a scalable foundation for implementation.

## Directory Tree

```text
EVIDRA/
|-- .gitignore                  # Git ignore rules
|-- README.md                   # Viewer-centric project overview
|-- PROJECT_IDEATION.md         # Core philosophical and scope definitions
|-- TECH_STACK.md               # Frozen technology and dependency decisions
|-- DELIVERABLES.md             # Implementation phases and deliverables
|-- SRS.md                      # Software Requirements Specification
|-- ARCHITECTURE.md             # 4-Layer system architecture
|-- repository_structure.md     # This document
|-- requirements.txt            # Python dependencies (Ollama, PyMuPDF, FastAPI, etc.)
|-- pyproject.toml              # Build and package configuration
|-- sample_docs/                # Directory for input PDF test cases
|-- runs/                       # Output directory for job artifacts (SQLite, JSONL, Markdown)
|
|-- src/                        # Core Application Code
|   |-- __init__.py
|   |
|   |-- api/                    # Layer 4: API endpoints and request models
|   |   |-- __init__.py
|   |   |-- server.py           # FastAPI application and routing
|   |   +-- models.py           # Pydantic request/response models for API
|   |
|   |-- cli/                    # Layer 4: Command Line Interface
|   |   |-- __init__.py
|   |   +-- main.py             # argparse CLI entry point
|   |
|   |-- db/                     # Layer 4: Evidence Ledger Storage
|   |   |-- __init__.py
|   |   |-- schema.sql          # SQLite table definitions
|   |   +-- ledger.py           # sqlite3 manager for documents, facts, and traces
|   |
|   |-- pdf/                    # Layer 1: Document Evidence Preparation
|   |   |-- __init__.py
|   |   |-- parser.py           # PyMuPDF integration (text, blocks, geometry)
|   |   +-- tables.py           # pdfplumber integration (table structures)
|   |
|   |-- llm/                    # LLM Provider Abstraction
|   |   |-- __init__.py
|   |   +-- provider.py         # ReasoningService interface wrapping Ollama (Qwen2.5)
|   |
|   |-- extraction/             # Layer 2a: Fact Generation
|   |   |-- __init__.py
|   |   |-- schemas.py          # Pydantic contracts (EvidenceChunk, FactCandidate)
|   |   +-- agents.py           # Prompts and extraction routines
|   |
|   |-- verification/           # Layer 2b: Fact Verification & Context
|   |   |-- __init__.py
|   |   |-- verifier.py         # Evidence Verifier agent
|   |   |-- context.py          # Context Resolver agent
|   |   +-- normalizers.py      # Deterministic logic (Decimal math, dateutil parsing)
|   |
|   |-- matching/               # Layer 2c: Candidate Grouping
|   |   |-- __init__.py
|   |   +-- embeddings.py       # sentence-transformers BGE-Small integration
|   |
|   |-- decision/               # Layer 3: Fact Decision Engine
|   |   |-- __init__.py
|   |   |-- workflow.py         # LangGraph state graph orchestrator
|   |   |-- hypothesis.py       # Hypothesis Generator agent
|   |   |-- validators.py       # Specialist temporal/semantic validators
|   |   |-- reconciliation.py   # Reconciliation and Adversarial Challenge agents
|   |   +-- policy.py           # Pure Python deterministic verdict engine
|   |
|   +-- observability/          # Layer 4: Tracing and Reporting
|       |-- __init__.py
|       |-- trace.py            # JSON/JSONL audit trace generators
|       +-- reporters.py        # Markdown executive and contradiction report generators
|
+-- tests/                      # Automated Testing Suite
    |-- __init__.py
    |
    |-- unit/                   # Deterministic logic and normalizers
    |   |-- test_decimal_units.py
    |   |-- test_temporal_parsing.py
    |   +-- test_decision_policy.py
    |
    |-- contracts/              # Schema validation against LLM boundaries
    |   |-- test_extractor_schema.py
    |   |-- test_verifier_schema.py
    |   +-- test_reconciler_schema.py
    |
    +-- evaluation/             # Epistemic workflow edge cases
        |-- test_corroboration.py
        |-- test_contradiction.py
        |-- test_reconciliation.py
        +-- test_failure_handling.py
```

## Module Responsibilities

1. **`src/pdf/`**: Extracts raw text, tables, and bounding boxes. Operates with zero semantic reasoning.
2. **`src/extraction/`**: Contains LLM prompts that convert text/tables into structured observations. Enforces Pydantic boundaries.
3. **`src/verification/`**: Houses independent agents that verify claims against raw evidence and normalizes numbers/dates deterministically.
4. **`src/matching/`**: Uses local embeddings to group related facts.
5. **`src/decision/`**: The core LangGraph workflow. Houses the hypothesis generator, challenge skeptic, and final deterministic policy.
6. **`src/db/`**: Isolates all SQLite logic. Maintains the Evidence Ledger.
7. **`src/api/` & `src/cli/`**: The human/machine interfaces for job submission and inspection.
8. **`src/observability/`**: Writes artifacts to the `runs/` directory for full transparency.
