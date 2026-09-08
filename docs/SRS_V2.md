# EVIDRA 2.0: Software Requirements Specification (SRS)

> **Parent Specification:** [docs/SRS.md](file:///d:/projects/superjoin/EVIDRA/docs/SRS.md)  
> **Architecture Reference:** [docs/ARCHITECTURE_V2.md](file:///d:/projects/superjoin/EVIDRA/docs/ARCHITECTURE_V2.md)  
> **Status:** Frozen Requirements Specification (Development Branch: `dev_v2`)  
> **System Classification:** Backwards-Compatible Epistemic Requirements Extension of EVIDRA V1  

---

## 1. Introduction and Architectural Lineage

### 1.1 Purpose
This Software Requirements Specification (SRS V2) establishes the extended functional, non-functional, and interface requirements for the **Fact Knowledge Layer (EVIDRA 2.0)**. EVIDRA 2.0 is not a separate, competing, or disconnected project; it is the direct, backwards-compatible, and systematic extension of **EVIDRA V1** ([docs/SRS.md](file:///d:/projects/superjoin/EVIDRA/docs/SRS.md)).

Empirical evaluation of V1 on real corporate filings (Delhivery Annual Report, Earnings Presentation, Prospectus) revealed that **the primary bottleneck is upstream fact construction, not downstream reasoning**:
- Rigid candidate filtering (`max_llm_chunks=2`) bottlenecked extraction yield to 0.56%.
- Isolated chunks stripped critical table column titles, section headers, and stated units.
- Unconstrained attribute clustering without schema grounding produced 100% false-positive contradictions.
- Temporal interval overlap was confused with identical temporal claims.
- Conflating absolute metrics with rate/percentage metrics produced false conflicts.
- Binary pairwise evaluation (`candidates[0], candidates[1]`) dropped multi-member claims.
- Single-source claims terminated as UNRESOLVED without articulating what evidence was missing.

SRS V2 specifies the exact software requirements necessary to eliminate these empirical failure modes while preserving 100% of the foundational V1 substrate.

### 1.2 Epistemic Continuity: Invariant Principles
EVIDRA 2.0 inherits and strictly preserves all six foundational epistemic principles established in SRS V1 Section 1.3:
1. **The Fact is Not the Primitive:** Systems must maintain a strict epistemic hierarchy: Evidence Chunk -> Observation -> Fact Candidate -> Fact Group -> Hypothesis Tournament -> Decision -> Decision Trace.
2. **Observations are Distinct from Decisions:** What a source document literally states (Observation) is immutable and distinct from what the system deduces (Decision).
3. **Mandatory Spatial Provenance:** Every numerical and semantic assertion must bind directly to a document ID, page number, and geometric bounding box `(x0, y0, x1, y1)`.
4. **Extract-Then-Verify Decoupling:** Claim extraction is independently verified against raw source text to reject hallucinations before fact candidate construction.
5. **Strict Boundary Separation:** Large Language Models (LLMs) are restricted to semantic reasoning, extraction, and hypothesis generation. All financial arithmetic, unit scaling, date parsing, and final decision policies are executed by deterministic pure Python modules.
6. **UNRESOLVED is a First-Class Output:** The system must report unresolved ambiguity rather than forcing an unsupported conclusion.

### 1.3 Extended Epistemic Principles (V2 Extensions)
7. **Context-Enriched Evidence:** Raw textual chunks are insufficient primitives for financial tables; an evidence chunk must be enveloped in an **Evidence Window** carrying layout hierarchy, section titles, table captions, and stated units.
8. **Document-Derived Schema Induction:** The system must discover entities, metric families, and subtypes dynamically from documents without requiring hardcoded, document-specific taxonomies, preserving verbatim surface terms.
9. **Semantic Fact Identity Signatures:** Numerical variance checks must never precede identity verification; two facts may only be compared if their **Fact Identity Signatures** match across entity, metric family, subtype, and measurement type.
10. **Temporal Comparability Classification:** Temporal interval overlap does not establish identical temporal facts; temporal relations must be classified into explicit comparability classes (`EXACT_MATCH`, `CONTAINMENT`, `ADJACENT_PERIOD`, etc.). Containment denotes related context, not competing claims.
11. **Claim Relationship Graphs over Majority Votes:** Adjudication across multi-member groups must partition claims into evidential clusters and synthesize relationship graphs rather than taking an epistemic vote.
12. **Rule-Based Evidence Sufficiency:** Evidence readiness must be gated by transparent categorical logic rather than arbitrary decimal equations.
13. **Orthogonal Claim Lifecycles:** Claim evolution must be tracked across decoupled dimensions: Pipeline Status, Epistemic Relationship, Grounding Validity, and Version.
14. **Articulated Evidence Gaps:** An UNRESOLVED verdict is an actionable gap; the system must generate a formal **Evidence Gap Specification** detailing missing dimensions before querying for evidence.

---

## 2. Specific Functional Requirements (V2 Extensions)

### 2.1 Document Processing & Evidence Preparation Extensions (DOC-EXT)

#### REQ-DOC-EXT-01: Multi-Signal Layout Hierarchy Inference with Confidence
* **Description:** The system shall classify document layout structure during PyMuPDF parsing using multi-signal evidence inference, outputting explicit confidence scores rather than brittle single-threshold heuristics.
* **Signals Considered:**
  1. Font size relative to page distribution (Z-score).
  2. Font style flags (bold, italic, uppercase).
  3. Spatial alignment and page margins (top 10%, bottom 10%, indentation).
  4. Repetition frequency across multiple pages.
  5. Whitespace and vertical distance to nearest table grid.
  6. Lexical pattern matching (e.g., "Statement of", "Table N", "Notes to").
* **Output:** Structural classification (`SECTION_TITLE`, `TABLE_CAPTION`, `HEADER`, `FOOTER`, `FOOTNOTE`, `BODY`) bound to each chunk with a confidence score ($C \in [0.0, 1.0]$).

#### REQ-DOC-EXT-02: Context-Enriched Evidence Windows
* **Description:** The system shall wrap each raw extracted chunk (`ExtractedBlock`) in an `EvidenceWindow` data envelope binding inherited structural context.
* **Functional Criteria:**
  1. For table chunks, bind column headers (row 0) and row labels (column 0).
  2. Inherit active `section_title` and `section_confidence` from parent layout blocks.
  3. Extract stated units (`crore`, `lakhs`, `millions`) and currencies (`INR`, `USD`) using deterministic regex from headers, captions, and the 3 preceding text blocks.
  4. Parse temporal tokens in column headers using `TemporalNormalizer` and bind normalized date ranges to column indices.

#### REQ-DOC-EXT-03: 3-Tier Budget-Aware Candidate Discovery
* **Description:** The system shall replace the global top-N chunk truncation (`max_llm_chunks=2`) with a deterministic 3-tier discovery pipeline with per-document quotas.
* **Functional Criteria:**
  1. **Tier 1 (Structural Filter):** Automatically retain 100% of detected tables. Filter out boilerplate headers, footers, and text blocks with < 50 characters.
  2. **Tier 2 (Relevance Ranking):** Rank surviving text chunks within document boundaries using lexical keyword density, numeric density, and section context.
  3. **Tier 3 (Per-Document Allocation):** Allocate a configurable quota (default: 30 chunks per document), prioritizing tables and filling remaining slots with top text blocks.

---

### 2.2 Schema Induction & Fact Construction Extensions (SCH-EXT & EXT-EXT)

#### REQ-SCH-EXT-01: Document-Derived Schema Induction Layer
* **Description:** The system shall dynamically induce legal entities, metric families, and metric subtypes from ingested documents without requiring hardcoded, document-specific taxonomies.
* **Functional Criteria:**
  1. Discover legal entities from filing metadata, cover pages, and recurring title blocks.
  2. Discover Metric Families (e.g., `REVENUE`, `PROFITABILITY`, `VOLUME`, `EXPENSES`) based on table titles and statement headers.
  3. Preserve specific surface variants (e.g., `Revenue from Operations` vs `Revenue from Services`) as distinct subtypes under the shared family rather than collapsing them.

#### REQ-EXT-EXT-01: Structural Prompt Envelope Ingestion
* **Description:** The `ExtractionAgent` shall ingest the full `EvidenceWindow` envelope, presenting structural section titles, table captions, and stated units in the extraction prompt.

#### REQ-VER-EXT-01: Anti-Generic Entity and Entailment Validation
* **Description:** The system shall reject observations whose entity matches generic corporate placeholders (`Reporting Entity`, `the Company`, `Management`, `Total`).
* **Entailment Verification:** The system shall verify that `raw_value` is an exact verbatim substring of `window.content` and that temporal scopes parse to valid ISO-8601 boundaries.

---

### 2.3 Fact Identity & Contextual Resolution Extensions (ID-RES & MAT-EXT)

#### REQ-ID-RES-01: Fact Identity Signature Formalization
* **Description:** Every verified fact candidate shall be bound to a structured `FactIdentitySignature` comprising:
  $$	ext{FactIdentitySignature} = \langle 	ext{entity\_canonical}, 	ext{metric\_family}, 	ext{metric\_subtype}, 	ext{measurement\_type}, 	ext{surface\_metric}, 	ext{period\_start}, 	ext{period\_end}, 	ext{scope}, 	ext{basis}, 	ext{definition} angle$$
* **Measurement Semantics:** Measurement type must be classified as `ABSOLUTE_VALUE`, `PERCENTAGE`, `RATE_OF_CHANGE`, or `RATIO`.

#### REQ-TMP-EXT-01: Temporal Comparability Classification (Gate 2)
* **Description:** The system shall evaluate the temporal relationship between candidates into explicit comparability classes:
  - `EXACT_MATCH`: Direct numerical comparison permitted.
  - `CONTAINMENT`: Related temporal context (e.g., Q4 inside FY24); **values are not directly compared**.
  - `ADJACENT_PERIOD`: Sequential reporting periods (e.g., FY23 and FY24); trend context only.
  - `OVERLAPPING`: Disjoint period shift; routed to specialized reconciliation.
  - `NON_OVERLAPPING`: Distinct periods; grouping blocked.
  - `UNKNOWN`: Ambiguous temporal boundaries.

#### REQ-MAT-EXT-01: 4-Gate Contextual Fact Resolution
* **Description:** The system shall group fact candidates across documents using 4 sequential gates:
  1. **Gate 1 (Entity):** Matching canonical entity.
  2. **Gate 2 (Temporal):** Must evaluate to `DIRECTLY_COMPARABLE` for numerical comparison groups.
  3. **Gate 3 (Metric & Measurement):** Must share identical `measurement_type`, metric family, and subtype.
  4. **Gate 4 (Context):** Flags scope/basis mismatches for Path B (Contextual Reconciliation).

---

### 2.4 Fact Decision Engine Extensions (DEC-EXT)

#### REQ-DEC-EXT-01: Rule-Based Evidence Sufficiency Indicator
* **Description:** The system shall evaluate evidence sufficiency via a transparent categorical rule gate:
  - Incomplete identity -> `INSUFFICIENT_IDENTITY` (Route: fast-path UNRESOLVED).
  - Comparable candidates < 2 -> `SINGLE_SOURCE_PENDING` (Route: Evidence Gap Engine).
  - Evidence unverified -> `UNVERIFIED_EVIDENCE` (Route: SKIP).
  - Context divergent -> `CONTEXT_DIVERGENT` (Route: Contextual Reconciliation).
  - Otherwise -> `SUFFICIENT_FOR_ADJUDICATION` (Route: Adjudication Tournament).

#### REQ-DEC-EXT-02: Claim Relationship Graph & Cluster-Based Adjudication
* **Description:** For groups with $N \ge 2$ members, the system shall construct a claim relationship graph based on pairwise tournament evaluations and synthesize value clusters:
  1. Evaluate all unique pairs across the core Architecture 1 LangGraph tournament.
  2. Partition claims into equivalence clusters based on verified value and stated units.
  3. Output structured epistemic relationships (`UNANIMOUS_CORROBORATION`, `RECONCILED_CLUSTERS`, or `CONFLICTING_CLAIM_CLUSTERS`).
  4. Preserve `UNRESOLVED` as a mutually exclusive sibling outcome alongside `CORROBORATED`, `RECONCILED`, and `CONTRADICTED`.

---

### 2.5 Dynamic Epistemology & Active Evidence Gaps (EPI-EXT)

#### REQ-EPI-EXT-01: Multi-Dimensional Claim Lifecycle
* **Description:** The system shall decouple claim evolution into four orthogonal dimensions:
  1. **Claim Status:** `OBSERVED`, `VERIFIED`, `CANDIDATE`, `PENDING`, `ADJUDICATED`.
  2. **Epistemic Relationship:** `CORROBORATED`, `RECONCILED`, `CONTRADICTED`, `UNRESOLVED`.
  3. **Grounding Validity:** `SUPPORTED`, `PARTIALLY_SUPPORTED`, `REJECTED`.
  4. **Version:** `CURRENT`, `SUPERSEDED`.
* All transitions shall be logged in `claim_transitions` with timestamps and causal triggers.

#### REQ-EPI-EXT-02: Source Independence Indicator
* **Description:** Corroborated decisions shall be qualified by a qualitative source independence indicator: `HIGH`, `MEDIUM`, `LOW`, or `UNKNOWN`, evaluated over document separation, filing type divergence, lexical Jaccard distance, and structural formatting.

#### REQ-EPI-EXT-03: Evidence Gap Specification & Identity-Aware Active Acquisition
* **Description:** When an adjudication terminates in UNRESOLVED, the system shall construct a structured `EvidenceGapSpec` articulating missing dimensions (`has_entity`, `has_metric`, `has_period`, `has_scope`, `has_second_source`).
* **Hybrid Retrieval:** The system shall execute SQL deterministic candidate filtering followed by BGE embedding semantic reranking on the `FactIdentitySignature`. If matches are found, it extracts observations and re-adjudicates in Round 2; otherwise, it persists the gap specification in `evidence_gaps`.

---

## 3. Quality-Oriented Evaluation Requirements & Gold Benchmark

### 3.1 Manually Annotated Gold Evaluation Set
* **REQ-BENCH-01:** The repository shall contain a manually annotated gold benchmark dataset (`tests/data/gold_evaluation.json`) comprising 50 verified claims and 20 pairwise claim relationships spanning the three Delhivery starter filings.

### 3.2 Engineering Targets (Empirical Evaluation)
* **REQ-BENCH-02:** System performance shall be evaluated against empirical engineering targets on the gold benchmark:
  - Observation Precision: Target $\ge 90\%$.
  - Evidence Grounding Rate: Target $\ge 95\%$.
  - Entity Resolution Accuracy: Target $\ge 95\%$.
  - Metric Identity Accuracy: Target $\ge 90\%$.
  - False Contradiction Rate: Target $0\%$.
  - Audited Evidence Gap Rate on UNRESOLVED: Target $100\%$.
