# EVIDRA 2.0: Master Deliverables Specification

> **Parent Specification:** [docs/DELIVERABLES_DEFINITION.md](file:///d:/projects/superjoin/EVIDRA/docs/DELIVERABLES_DEFINITION.md)  
> **Architecture Reference:** [docs/ARCHITECTURE_V2.md](file:///d:/projects/superjoin/EVIDRA/docs/ARCHITECTURE_V2.md)  
> **SRS Reference:** [docs/SRS_V2.md](file:///d:/projects/superjoin/EVIDRA/docs/SRS_V2.md)  
> **Status:** Frozen Deliverables Specification (Development Branch: `dev_v2`)  
> **System Classification:** Backwards-Compatible Deliverables Extension of EVIDRA V1  

---

## 1. Overview and Priority Engineering Roadmap

This specification defines the granular deliverables for **EVIDRA 2.0 (Dev V2)**. EVIDRA 2.0 is **not** a separate or greenfield project; it is the direct operational upgrade and extension of the deliverables completed in **EVIDRA V1** ([docs/DELIVERABLES_DEFINITION.md](file:///d:/projects/superjoin/EVIDRA/docs/DELIVERABLES_DEFINITION.md)).

Empirical analysis of V1 proved that **reasoning cannot compensate for corrupted or context-starved facts**. Therefore, Dev V2 organizes development into five strictly prioritized engineering phases (P0 through P4), ensuring that extraction, schema induction, and identity resolution are verified before complex reasoning or active acquisition loops are activated:

```text
P0: Make Extraction Trustworthy (Upstream Foundation)
    |
    v
P1: Make Identity Trustworthy (Contextual Resolution)
    |
    v
P2: Validate Core Reasoning Tournament (Against Real Data)
    |
    v
P3: Deliver Epistemic Innovations (Lifecycle, Source Independence, Gaps)
    |
    v
P4: Comprehensive Quality Evaluation & Four-Case Demonstration
```

---

## 2. Deliverables Summary Matrix

| Phase | Deliverable | Name | Primary Target Modules | Key Artifacts / Outputs | SRS V2 Mapping |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **P0** | **D-P0.1** | **Budget-Aware Evidence Discovery** | `src/extraction/pipeline.py` | 3-tier candidate discovery; per-document extraction quota (budget=30); 100% table preservation. | REQ-DOC-EXT-03 |
| **P0** | **D-P0.2** | **Multi-Signal Layout Hierarchy & Evidence Windows** | `src/pdf/topology.py`<br>`src/extraction/windows.py` | Multi-signal layout classification with confidence scoring; `EvidenceWindow` envelopes with unit/currency inheritance. | REQ-DOC-EXT-01<br>REQ-DOC-EXT-02 |
| **P0** | **D-P0.3** | **Lightweight Schema Induction Layer** | `src/extraction/schema_induction.py`<br>`src/extraction/agents.py` | Document-derived metric families and subtypes; structural prompt envelope injection; anti-generic entity filtering. | REQ-SCH-EXT-01<br>REQ-EXT-EXT-01<br>REQ-VER-EXT-01 |
| **P1** | **D-P1.1** | **Fact Identity Signature & Temporal Comparability** | `src/extraction/schemas.py`<br>`src/matching/identity.py`<br>`src/matching/temporal.py` | `FactIdentitySignature` with Measurement Semantics; `TemporalComparability` classification (Exact, Containment, Adjacent, etc.). | REQ-ID-RES-01<br>REQ-TMP-EXT-01 |
| **P1** | **D-P1.2** | **4-Gate Contextual Fact Resolution** | `src/matching/embeddings.py` | 4-gate matching pipeline replacing single-threshold cosine clustering; clean separation of distinct metrics. | REQ-MAT-EXT-01 |
| **P1** | **D-P1.3** | **Claim Relationship Graph & Clustering** | `src/decision/engine.py` | Pairwise tournament execution across all candidates; claim equivalence clustering; synthesis verdict. | REQ-DEC-EXT-02 |
| **P2** | **D-P2.1** | **Rule-Based Evidence Sufficiency Gate** | `src/decision/sufficiency.py` | Categorical rule gate (`ADJUDICATE`, `DEFER`, `SKIP`, `CONTEXT_DIVERGENT`) eliminating false precision. | REQ-DEC-EXT-01 |
| **P2** | **D-P2.2** | **Core Reasoning Validation on Real Filings** | `src/decision/reconciliation.py`<br>`src/decision/workflow.py` | Calibrated reconciliation bridge; validated Corroboration, Contradiction, Reconciliation, and UNRESOLVED on Delhivery data. | REQ-DEC-EXT-03 |
| **P3** | **D-P3.1** | **Multi-Dimensional Claim Lifecycle** | `src/lifecycle/manager.py`<br>`src/db/schema.sql` | Decoupled dimensions: Status (5 states), Relationship (4 states), Validity (3 states), Version (2 states); audit table. | REQ-EPI-EXT-01 |
| **P3** | **D-P3.2** | **Source Independence Indicator** | `src/decision/independence.py` | Qualitative indicator (`HIGH`, `MEDIUM`, `LOW`, `UNKNOWN`) based on filing separation, Jaccard distance, and layout. | REQ-EPI-EXT-02 |
| **P3** | **D-P3.3** | **Evidence Gap Specification & Hybrid Acquisition** | `src/decision/evidence_search.py`<br>`src/db/schema.sql` | Structured `EvidenceGapSpec` articulating missing dimensions; closed-loop SQL + BGE semantic retrieval. | REQ-EPI-EXT-03 |
| **P4** | **D-P4.1** | **Gold Benchmark Quality Audit & Demo Suite** | `tests/data/gold_evaluation.json`<br>`src/observability/reports.py`<br>`tests/test_v2_e2e.py` | Manually annotated gold benchmark (50 claims / 20 pairs); audited quality metrics; Four Demonstration Cases; CLI commands. | REQ-BENCH-01<br>REQ-BENCH-02 |

---

## 3. Granular Deliverable Specifications by Priority Phase

### Phase 0: Make Extraction Trustworthy (Upstream Foundation)

#### D-P0.1: Budget-Aware Evidence Discovery (`src/extraction/pipeline.py`)
- **Objective:** Eliminate the global `max_llm_chunks=2` choke point while preserving computational efficiency.
- **Deliverables:**
  1. Implement 3-tier discovery pipeline.
  2. Guarantee 100% preservation of detected tables.
  3. Enforce per-document quota (default: 30 chunks per document) to ensure balanced multi-document representation.

#### D-P0.2: Multi-Signal Layout Hierarchy & Evidence Windows (`src/pdf/topology.py`, `src/extraction/windows.py`)
- **Objective:** Bind structural surroundings to raw chunks with explicit confidence scores, avoiding brittle single heuristics.
- **Deliverables:**
  1. Implement `DocumentTopologyBuilder` evaluating Z-score font size, font weight, margins, repetition frequency, whitespace, and table proximity.
  2. Assign structural roles (`SECTION_TITLE`, `TABLE_CAPTION`, `HEADER`, `FOOTER`, `BODY`) with confidence $C \in [0.0, 1.0]$.
  3. Implement `EvidenceWindowBuilder` wrapping raw chunks into `EvidenceWindow` envelopes containing table headers, row labels, and stated units (`crore`, `lakhs`, `millions`).

#### D-P0.3: Lightweight Schema Induction Layer (`src/extraction/schema_induction.py`, `src/extraction/agents.py`)
- **Objective:** Discover entities, metric families, and subtypes dynamically from documents without hardcoded taxonomies.
- **Deliverables:**
  1. Implement `SchemaInductionEngine` extracting corporate legal entities from cover pages and discovering metric families (`REVENUE`, `PROFITABILITY`, `VOLUME`, `EXPENSES`).
  2. Update `ExtractionAgent` prompt to ingest structural metadata headers.
  3. Implement post-extraction validation rejecting generic placeholders (`Reporting Entity`, `the Company`, `Management`, `Total`).

---

### Phase 1: Make Identity Trustworthy (Contextual Resolution)

#### D-P1.1: Fact Identity Signature & Temporal Comparability (`src/matching/identity.py`, `src/matching/temporal.py`)
- **Objective:** Establish structured semantic identities with measurement typing and classify temporal relationships before numerical comparison.
- **Deliverables:**
  1. Formalize verified candidates into `FactIdentitySignature` (entity, metric family, subtype, measurement type, surface metric, ISO period).
  2. Implement `TemporalComparabilityClassifier` classifying pairs into `EXACT_MATCH` (directly comparable), `CONTAINMENT` (related context; do not compare values), `ADJACENT_PERIOD`, `OVERLAPPING`, `NON_OVERLAPPING`.

#### D-P1.2: 4-Gate Contextual Fact Resolution (`src/matching/embeddings.py`)
- **Objective:** Replace single-pass greedy clustering with 4 disciplined matching gates.
- **Deliverables:**
  1. Gate 1: Entity identity verification.
  2. Gate 2: Temporal comparability verification.
  3. Gate 3: Metric family, subtype, and measurement type matching (blocks comparing absolute currency with rate/percentage).
  4. Gate 4: Context compatibility routing (flags scope/basis divergences for contextual reconciliation).

#### D-P1.3: Claim Relationship Graph & Clustering (`src/decision/engine.py`)
- **Objective:** Adjudicate multi-member groups by synthesizing claim equivalence clusters rather than majority voting.
- **Deliverables:**
  1. Enumerate unique candidate pairs and evaluate each across the core Architecture 1 LangGraph tournament.
  2. Construct claim relationship graph with typed edges (`CORROBORATES`, `CONFLICTS_WITH`, `RECONCILES_WITH`).
  3. Group claims into value clusters and output synthesized relationship verdicts (`UNANIMOUS_CORROBORATION`, `RECONCILED_CLUSTERS`, `CONFLICTING_CLAIM_CLUSTERS`).

---

### Phase 2: Validate Core Reasoning Tournament (Against Real Data)

#### D-P2.1: Rule-Based Evidence Sufficiency Gate (`src/decision/sufficiency.py`)
- **Objective:** Evaluate evidence readiness using transparent categorical rules, eliminating arbitrary decimal formulas.
- **Deliverables:**
  1. Implement categorical rule gate evaluating identity completeness, candidate count, entailment verification, and context compatibility.
  2. Route groups deterministically to `ADJUDICATE`, `DEFER` (Active Acquisition), `SKIP` (Fast-path UNRESOLVED), or `CONTEXT_DIVERGENT`.

#### D-P2.2: Core Reasoning Validation on Real Corporate Data
- **Objective:** Validate the unchanged Architecture 1 LangGraph tournament on clean upstream fact groups.
- **Deliverables:**
  1. Calibrate reconciliation bridge to trigger when at least one validator confirms structural differences without refutations.
  2. Validate the 4 benchmark outcomes on Delhivery data: Corroboration, Contradiction, Reconciliation, and UNRESOLVED (as mutually exclusive outcomes).

---

### Phase 3: Deliver Epistemic Innovations

#### D-P3.1: Multi-Dimensional Claim Lifecycle (`src/lifecycle/manager.py`, `src/db/schema.sql`)
- **Objective:** Decouple claim evolution into orthogonal dimensions.
- **Deliverables:**
  1. Schema migration adding `claim_transitions` table.
  2. Implement `ClaimLifecycleManager` tracking:
     - Pipeline Status (`OBSERVED`, `VERIFIED`, `CANDIDATE`, `PENDING`, `ADJUDICATED`)
     - Epistemic Relationship (`CORROBORATED`, `RECONCILED`, `CONTRADICTED`, `UNRESOLVED`)
     - Grounding Validity (`SUPPORTED`, `PARTIALLY_SUPPORTED`, `REJECTED`)
     - Version (`CURRENT`, `SUPERSEDED`)

#### D-P3.2: Source Independence Indicator (`src/decision/independence.py`)
- **Objective:** Qualify corroboration strength based on empirical source separation signals.
- **Deliverables:**
  1. Implement multi-signal evaluation: filing classification divergence, lexical Jaccard distance, and structural formatting (Table vs Text).
  2. Output discrete qualitative indicator: `HIGH`, `MEDIUM`, `LOW`, or `UNKNOWN`.

#### D-P3.3: Evidence Gap Specification & Identity-Aware Active Acquisition (`src/decision/evidence_search.py`, `src/db/schema.sql`)
- **Objective:** Articulate what evidence is missing before attempting to acquire it.
- **Deliverables:**
  1. Schema migration adding `evidence_gaps` table.
  2. Implement `MissingEvidenceEngine` constructing `EvidenceGapSpec` (matrix of missing attributes: metric, entity, period, scope, second source).
  3. Closed-loop hybrid retrieval: SQL deterministic candidate filtering + BGE embedding semantic reranking on `FactIdentitySignature`.
  4. Triggers Round-2 adjudication on retrieved candidates; persists unbridgeable gaps in `evidence_gaps`.

---

### Phase 4: Comprehensive Quality Evaluation & Four-Case Demonstration

#### D-P4.1: Gold Benchmark Quality Audit & Benchmark Demonstration (`tests/data/gold_evaluation.json`, `src/observability/reports.py`)
- **Objective:** Prove system correctness using a manually annotated benchmark and empirical engineering targets.
- **Deliverables:**
  1. Build gold evaluation dataset `tests/data/gold_evaluation.json` containing 50 audited observations and 20 pairwise claim relationships from Delhivery PDFs.
  2. Audit quality metrics against engineering targets:
     - Observation Precision (Target $\ge 90\%$)
     - Evidence Grounding Rate (Target $\ge 95\%$)
     - Entity Resolution Accuracy (Target $\ge 95\%$)
     - Metric Identity Accuracy (Target $\ge 90\%$)
     - False Contradiction Rate (Target $0\%$)
     - Audited Evidence Gap Rate (Target $100\%$)
  3. Produce comprehensive executive report detailing the Four Required Demonstration Cases on the Delhivery dataset:
     - Case 1: Cross-Document Corroboration (Revenue from Operations)
     - Case 2: Genuine Contradiction (Historical Restatements)
     - Case 3: Contextual Reconciliation (Ind AS Operating Profit vs Adjusted EBITDA)
     - Case 4: Audited Epistemic Failure (Single-source claim with populated `EvidenceGapSpec`)
  4. Automated regression test suite `tests/test_v2_e2e.py` validating the pipeline.
