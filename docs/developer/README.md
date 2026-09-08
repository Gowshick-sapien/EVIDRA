# EVIDRA: Internal Developer and System Architecture Documentation

This directory contains the internal engineering specifications, software requirements specifications (SRS), foundational ideation documents, and architectural blueprints for developers, system engineers, and maintainers of the EVIDRA platform.

If you are an external evaluator, reviewer, or user looking for the high-level system overview, please refer to the primary publishable documentation:
- **Project Overview & Quickstart:** [README.md](file:///d:/projects/superjoin/EVIDRA/README.md)
- **Repository Overview & Inspection Guide:** [docs/REPOSITORY_OVERVIEW.md](file:///d:/projects/superjoin/EVIDRA/docs/REPOSITORY_OVERVIEW.md)
- **Proposed Solution:** [docs/PROPOSED_SOLUTION.md](file:///d:/projects/superjoin/EVIDRA/docs/PROPOSED_SOLUTION.md)

---

## Technical Specifications Index

The complete EVIDRA solution integrates the core LangGraph reasoning tournament and specialist validators with upstream visual topology, 4-gate contextual resolution, and the pairwise claim relationship graph into a unified architecture.

### 1. Architectural Specifications
- **[ARCHITECTURE_README.md](file:///d:/projects/superjoin/EVIDRA/docs/developer/ARCHITECTURE_README.md)**: Comprehensive system architecture specification synthesizing all 4 layers of the operational platform.
- **[ARCHITECTURE_V2.md](file:///d:/projects/superjoin/EVIDRA/docs/developer/ARCHITECTURE_V2.md)**: Structural evidence preparation, visual layout topology, 4-gate contextual fact resolution, and pairwise claim relationship graph specification.
- **[ARCHITECTURE_V1.md](file:///d:/projects/superjoin/EVIDRA/docs/developer/ARCHITECTURE_V1.md)**: Core LangGraph reasoning tournament, specialist validators, hypothesis generation, and adversarial challenge specification.

### 2. Software Requirements Specifications (SRS)
- **[SRS_V2.md](file:///d:/projects/superjoin/EVIDRA/docs/developer/SRS_V2.md)**: Extended functional requirements defining document layout extraction, schema induction, identity resolution, and 4-gate matching.
- **[SRS_V1.md](file:///d:/projects/superjoin/EVIDRA/docs/developer/SRS_V1.md)**: Foundational functional requirements defining candidate verification, reasoning tournament, and decision policy.

### 3. Engineering Deliverable Roadmaps
- **[DELIVERABLES_DEFINITION_V2.md](file:///d:/projects/superjoin/EVIDRA/docs/developer/DELIVERABLES_DEFINITION_V2.md)**: Granular engineering phase roadmaps (Phases P0 through P4).
- **[DELIVERABLES_DEFINITION_V1.md](file:///d:/projects/superjoin/EVIDRA/docs/developer/DELIVERABLES_DEFINITION_V1.md)**: Baseline deliverable specifications (Deliverables D0 through D5).
- **[Phase Deliverable Plans](file:///d:/projects/superjoin/EVIDRA/docs/deliverable_plans/)**: Granular implementation and verification plans:
  - [P0 Implementation Plan](file:///d:/projects/superjoin/EVIDRA/docs/deliverable_plans/P0_IMPLEMENTATION_PLAN.md) & [P0 Verification Plan](file:///d:/projects/superjoin/EVIDRA/docs/deliverable_plans/P0_TESTING_AND_VERIFICATION_PLAN.md)
  - [P1 Implementation Plan](file:///d:/projects/superjoin/EVIDRA/docs/deliverable_plans/P1_IMPLEMENTATION_PLAN.md) & [P1 Verification Plan](file:///d:/projects/superjoin/EVIDRA/docs/deliverable_plans/P1_TESTING_AND_VERIFICATION_PLAN.md)
  - [P2 Implementation Plan](file:///d:/projects/superjoin/EVIDRA/docs/deliverable_plans/P2_IMPLEMENTATION_PLAN.md) & [P2 Verification Plan](file:///d:/projects/superjoin/EVIDRA/docs/deliverable_plans/P2_TESTING_AND_VERIFICATION_PLAN.md)

### 4. Ideation, Technology Stack, and Run Plan
- **[PROJECT_IDEATION.md](file:///d:/projects/superjoin/EVIDRA/docs/developer/PROJECT_IDEATION.md)**: Foundational ideation whitepaper detailing the epistemic philosophy ("The Fact is Not the Primitive") and the evolutionary transition from V1 to V2.
- **[TECH_STACK.md](file:///d:/projects/superjoin/EVIDRA/docs/developer/TECH_STACK.md)**: Complete dependency analysis, local LLM integration (Ollama), PyMuPDF/pdfplumber spatial layout engines, and SQLite WAL configuration.
- **[DEV_RUN_PLAN.md](file:///d:/projects/superjoin/EVIDRA/docs/developer/DEV_RUN_PLAN.md)**: Comprehensive developer runbook and troubleshooting diagnostics.
- **[REPOSITORY_STRUCTURE.md](file:///d:/projects/superjoin/EVIDRA/docs/developer/REPOSITORY_STRUCTURE.md)**: Architectural component and package directory structure map.
