# EVIDRA Architecture V2: Evolutionary Extension and Empirical Enhancement of Architecture 1

> **Parent Specification:** [docs/ARCHITECTURE.md](file:///d:/projects/superjoin/EVIDRA/docs/ARCHITECTURE.md)  
> **Status:** Frozen Architectural Specification (Development Branch: `dev_v2`)  
> **System Classification:** Backwards-Compatible Epistemic Extension of Architecture 1  

---

## 0. Architectural Continuity and Evolution Charter

EVIDRA Architecture V2 is **not** a replacement, disconnected rewrite, or greenfield system. It is the direct, backwards-compatible, and systematic extension of **EVIDRA Architecture 1** ([docs/ARCHITECTURE.md](file:///d:/projects/superjoin/EVIDRA/docs/ARCHITECTURE.md)).

Architecture 1 established the core epistemic foundation:
- The distinction between Observations and Decisions (*The Fact is Not the Primitive*).
- The Evidence Ledger (SQLite + WAL) as the immutable system of record.
- Strict deterministic and LLM boundary separation (LLMs propose; deterministic Python validates and decides).
- The Extract-Then-Verify separation with spatial bounding box provenance.
- The 8-node LangGraph hypothesis tournament with 5 specialist deterministic validators.
- UNRESOLVED as a first-class epistemic verdict.

When Architecture 1 was evaluated against real multi-document corporate filings (Delhivery Annual Report, Earnings Presentation, Prospectus), the core reasoning was validated, but empirical analysis revealed that **the primary bottleneck is upstream fact construction, not downstream reasoning**:

```text
6,553 Chunks
     |
     v
37 Observations (0.56% yield via rigid global chunk caps)
     |
     v
20 Groups (Flat cosine similarity grouping without structural grounding)
     |
     v
False Contradictions & Orphan Claims
```

**Architecture V2 moves intelligence upstream.** It ensures high-integrity evidence preparation, document-derived schema induction, measurement semantic typing, and structured identity resolution *before* claims enter the reasoning tournament.

---

## 0.1 Architecture 1 vs Architecture V2 Direct Extension Matrix

| Pipeline Layer | Architecture 1 Substrate (Retained 100%) | V1 Empirical Limitation | Architecture V2 Extension (Grounded & Generalized) | Compatibility |
| :--- | :--- | :--- | :--- | :--- |
| **Layer 1: Evidence Prep** | Dual-engine PDF parsing (`PyMuPDF` + `pdfplumber`), text blocks, table grids, bounding boxes. | Chunks lack surrounding context; global `max_llm_chunks=2` cap bottlenecks extraction. | **Evidence Windows** (context envelopes) + **Multi-Signal Layout Hierarchy with Confidence** + **3-Tier Budget Discovery**. | 100% Backwards-Compatible; wraps `ExtractedBlock`. |
| **Layer 2: Schema & Identity** | Dual extraction (Numerical + Semantic), spatial coordinate binding, entailment checking. | Hardcoded or missing taxonomies; unconstrained clustering creates 100% false contradictions. | **Lightweight Schema Induction Layer** + **Fact Identity Signature** with Measurement Semantics. | Preserves open-ended dynamic schemas; zero hardcoded document rules. |
| **Layer 2: Grouping & Comparability** | BGE embedding model, single-pass cosine similarity grouping (`FactGroupEngine`). | Temporal overlap confused with identical periods; unrelated metrics clustered together. | **4-Gate Contextual Fact Resolution** + **Temporal Comparability Classification** (Exact, Containment, Adjacent, etc.). | Drop-in upgrade to `FactGroupEngine`; BGE retained for semantic fallback. |
| **Layer 3: Decision Engine** | 8-node LangGraph tournament, 5 specialist validators, hypothesis tournament, adversarial skeptic. | Binary `candidates[0], candidates[1]` ignores multi-member groups; majority vote is epistemically flawed. | **Claim Relationship Graph & Cluster Adjudication** + **Rule-Based Evidence Sufficiency Indicator**. | LangGraph tournament preserved; wrapped in relationship clustering. |
| **Layer 4: Storage & Epistemology** | SQLite + WAL ledger, JSONL cryptographic audit log, bounding box provenance citations. | Decisions were static terminal states; no mechanism to identify what evidence is missing. | **Multi-Dimensional Claim Lifecycle** (Status, Relationship, Validity, Version) + **Evidence Gap Specification** (Hybrid Retrieval). | Additive SQLite migrations (`ALTER TABLE` and new tables). |

---

## 1. Empirical Failure Map to Architecture 1 Extensions

| # | V1 Empirical Failure | Root Cause in Implementation | Architecture V2 Extension | Section |
| :--- | :--- | :--- | :--- | :--- |
| **F1** | 37 observations from 6,553 chunks (0.56% yield) | `max_llm_chunks=2` global cap selected only 2 chunks per document | **Evidence Candidate Discovery** -- 3-tier budget discovery with per-document quota (budget=30) | 3.1 |
| **F2** | Isolated chunks sent to LLM without surrounding context | Table cells lacked headers, section titles, units, and currency definitions | **Evidence Windows** -- structural envelopes inheriting table columns, units, and page hierarchy | 3.2 |
| **F3** | Brittle layout heuristics risk failing on unseen PDFs | Single hardcoded thresholds (e.g., font > 1.3x median) are layout-dependent | **Multi-Signal Evidence Hierarchy Inference with Confidence Scoring** | 3.3 |
| **F4** | Generic entities ("Reporting Entity") & conflated metrics | Lack of schema grounding; hardcoded taxonomies violate generalization rules | **Lightweight Schema Induction Layer** (document-derived metric families and subtypes) | 4.1 |
| **F5** | False contradictions from temporal mismatch | Temporal interval overlap was treated as identical temporal claims (FY24 vs Q4 FY24) | **Temporal Comparability Classification** (EXACT, CONTAINMENT, ADJACENT, etc.) | 4.2 |
| **F6** | False contradictions from mixing absolute vs rate metrics | Conflating Revenue with Revenue Growth % due to shared keyword "Revenue" | **Measurement Semantics** (ABSOLUTE_VALUE, RATE_OF_CHANGE, PERCENTAGE, RATIO) | 4.3 |
| **F7** | 0 RECONCILED verdicts on real corporate data | Reconciliation engine received corrupt candidate groupings | **Cascading Reconciliation Fix** -- clean grouping feeds valid pairs to hypothesis tournament | 5.1 |
| **F8** | Groups with 3+ members ignored candidates beyond c1, c2 | Binary pairwise assumption; majority voting fails on multi-value clusters | **Claim Relationship Graph & Cluster-Based Adjudication** | 5.2 |
| **F9** | Arbitrary quantitative formulas create false precision | Weighted decimal sums (0.3*a + 0.2*b) pretend to be objective probabilities | **Rule-Based Evidence Sufficiency Indicator** (categorical gate) | 5.3 |
| **F10** | 13/20 decisions = UNRESOLVED without guidance | System stopped on missing data without specifying what was missing | **Evidence Gap Specification & Identity-Aware Active Acquisition** | 6.3 |

---

## 2. Extended System Topology

```text
                 +---------------------------------------+
                 |          INGESTED DOCUMENTS           |
                 +-------------------+-------------------+
                                     |
                                     v
                 +---------------------------------------+
                 |   LAYER 1: EVIDENCE PREPARATION       |
                 |                                       |
                 | - Multi-Signal Layout Hierarchy       |
                 | - Confidence-Scored Document Topology |
                 | - Deterministic Table Structure       |
                 | - Context-Enriched Evidence Windows   |
                 | - 3-Tier Per-Document Budget Discovery|
                 +-------------------+-------------------+
                                     |
                                     v
                 +---------------------------------------+
                 |   LAYER 2A: SCHEMA INDUCTION LAYER    |
                 |                                       |
                 | - Document-Derived Entities           |
                 | - Discovered Metric Families (REVENUE)|
                 | - Metric Subtypes (OPERATING, SERVICE)|
                 | - Measurement Semantics (ABS vs RATE) |
                 +-------------------+-------------------+
                                     |
                                     v
                 +---------------------------------------+
                 |   LAYER 2B: FACT CONSTRUCTION         |
                 |                                       |
                 | - Grounded Dual Extraction (Prompt Env|
                 | - Extract-Then-Verify Entailment Check|
                 | - Fact Identity Signature Binding     |
                 +-------------------+-------------------+
                                     |
                                     v
                 +---------------------------------------+
                 |   LAYER 2C: CONTEXTUAL RESOLUTION     |
                 |                                       |
                 | - Gate 1: Entity Canonical Resolution |
                 | - Gate 2: Temporal Comparability Class|
                 | - Gate 3: Metric & Measurement Typing |
                 | - Gate 4: Context Routing (Scope/Basis|
                 +-------------------+-------------------+
                                     |
                                     v
                 +---------------------------------------+
                 |   LAYER 3A: EVIDENCE SUFFICIENCY      |
                 |   (Rule-Based Indicator: Categorical) |
                 +-------------------+-------------------+
                                     |
                                     v
                 +---------------------------------------+
                 |   LAYER 3B: CLAIM RELATIONSHIP GRAPH  |
                 |   & CLUSTER-BASED ADJUDICATION        |
                 +-------------------+-------------------+
                                     |
                                     v
                 +---------------------------------------+
                 |   CORE LANGGRAPH TOURNAMENT (CORE V1) |
                 |   - 5 Specialist Deterministic Valid. |
                 |   - Reconciliation Proposer           |
                 |   - Adversarial Skeptic               |
                 |   - Zero-LLM Decision Policy Gate     |
                 +-------------------+-------------------+
                                     |
         +-------------------+-------+-------+-------------------+
         |                   |               |                   |
         v                   v               v                   v
   CORROBORATED         RECONCILED     CONTRADICTED         UNRESOLVED
                                                                 |
                                                                 v
                                                 +-------------------------------+
                                                 | LAYER 4: EVIDENCE GAP ENGINE  |
                                                 | - Articulate Missing Spec     |
                                                 | - Identity-Aware Retrieval    |
                                                 | - Re-evaluate / Audit Gap     |
                                                 +-------------------------------+

                     ORTHOGONAL CLAIM LIFECYCLE
                                 |
         +-----------------------+-----------------------+
         |                       |                       |
         v                       v                       v
    Claim Status           Relationship            Validity & Version
  (OBSERVED ->            (CORROBORATED,          (SUPPORTED,
   VERIFIED ->             RECONCILED,             CURRENT,
   CANDIDATE ->            CONTRADICTED,           SUPERSEDED)
   ADJUDICATED)            UNRESOLVED)
```

---

## 3. Layer 1 Extension: Context-Aware Evidence Preparation

### 3.1 Evidence Candidate Discovery
**Principle:** Proportional, budget-aware extraction across documents.

Replace the global `max_llm_chunks=2` cap with a deterministic 3-tier discovery pipeline enforcing per-document quotas:
1. **Tier 1 (Structural Filter):** 100% of detected tables are automatically retained as candidate chunks. Text blocks with < 50 characters or matching header/footer boilerplate are excluded.
2. **Tier 2 (Relevance Scoring):** Surviving text chunks are ranked within document boundaries using lexical keyword density, numeric density, and section context.
3. **Tier 3 (Per-Document Allocation):** A configurable quota (default: 30 chunks per document) ensures multi-document representation. All tables are prioritized; remaining slots are filled by top-ranked text blocks.

### 3.2 Evidence Windows
**Governing Principle:** *Never ask the reasoning model to reconstruct document structure that the parser already knows.*

An `EvidenceWindow` wraps each raw chunk with structural metadata inherited from its layout environment:

```python
class EvidenceWindow(BaseModel):
    chunk_id: str
    document_id: str
    page_number: int
    chunk_type: Literal["text", "table", "figure"]
    bounding_box: list[float]
    content: str
    content_hash: str

    # Inherited context with confidence
    section_title: str = ""
    section_confidence: float = 0.0
    table_caption: str = ""
    stated_unit: str = ""           # e.g., "lakhs", "crore", "millions"
    stated_currency: str = ""       # e.g., "INR", "USD"
    column_headers: list[str] = Field(default_factory=list)
    row_context: str = ""
    page_header: str = ""
    footnotes: list[str] = Field(default_factory=list)
```

### 3.3 Multi-Signal Layout Hierarchy Inference (Confidence-Based)
Avoid brittle single heuristics (e.g., `font > 1.3x median` or `caption within 20px`). Financial PDFs vary drastically in formatting.

EVIDRA 2.0 infers layout hierarchy using multi-signal classification with explicit confidence scores:

```text
Extracted Block
       |
Multi-Signal Classifier:
  - Font Size Relative to Page Distribution (Z-score)
  - Font Weight & Style Flags (Bold, Italic)
  - Geometric Position & Alignment (Top 10%, Centered, Indented)
  - Page-to-Page Repetition Frequency
  - Surrounding Whitespace & Vertical Margins
  - Proximity & Spatial Containment relative to Table Grids
  - Lexical Pattern Matches (e.g., "Statement of", "Table N", "Notes to")
       |
       v
Structural Role Assignment + Confidence Score:
  Role: SECTION_TITLE | TABLE_CAPTION | HEADER | FOOTER | FOOTNOTE | BODY
  Confidence: [0.0, 1.0]
```

**Robust Invariant:** Downstream extraction and prompt builders use `section_title` only when `section_confidence >= 0.70`, falling back gracefully to page coordinates when structural signals are ambiguous.

---

## 4. Layer 2 Extension: Schema Induction & Grounded Fact Construction

### 4.1 Lightweight Schema Induction Layer
**Governing Principle:** Avoid hardcoding massive financial taxonomies. The system must adaptively induce schemas from the documents while strictly preserving verbatim surface terms.

The Schema Induction Layer operates as an evidence-backed induction pipeline:

```text
Surface Observations from Ingested Documents
                  |
                  v
Candidate Concepts Discovery (table headers, row labels, bold text)
                  |
                  v
Semantic Grouping & Concept Clustering
                  |
                  v
LLM Proposes Candidate Family & Subtype (with evidence quotes)
                  |
                  v
Evidence-Backed Validation Gate (checks concepts against document text)
                  |
                  v
Document-Derived Schema:
  Family: REVENUE
    ├── Subtype: OPERATING_REVENUE (Source: "Revenue from Operations")
    └── Subtype: SERVICE_REVENUE   (Source: "Revenue from Services")
```

**Critical Invariant:** The system preserves both the specific surface variant and the broader family relationship. It does not collapse `Revenue from Operations` into `Revenue from Services`, but recognizes them as distinct subtypes within the shared family.

### 4.2 Fact Identity Signature
Renamed from "Vector" to **Fact Identity Signature** (`FactIdentitySignature`). It represents a structured semantic identity signature, including **Measurement Semantics**:

```python
class MeasurementType(str, Enum):
    ABSOLUTE_VALUE = "ABSOLUTE_VALUE"   # Currency amounts (e.g., INR 8,142 Cr), item counts
    PERCENTAGE = "PERCENTAGE"           # Margins, ratios expressed as % (e.g., EBITDA Margin 12.5%)
    RATE_OF_CHANGE = "RATE_OF_CHANGE"   # Growth rates, YoY, QoQ changes (e.g., +29.8% YoY)
    RATIO = "RATIO"                     # Multiples, debt-to-equity ratios (e.g., 1.4x)
    UNKNOWN = "UNKNOWN"

class FactIdentitySignature(BaseModel):
    entity_canonical: str           # Resolved legal entity (e.g., "Delhivery Limited")
    metric_family: str              # Document-derived family (e.g., "REVENUE")
    metric_subtype: str             # Specific metric variant (e.g., "OPERATING_REVENUE")
    measurement_type: MeasurementType # Dimensional typing (ABSOLUTE vs RATE vs PERCENTAGE)
    surface_metric: str             # Verbatim extracted metric string
    period_start: str               # Normalized ISO start date
    period_end: str                 # Normalized ISO end date
    scope: str = "UNKNOWN"           # CONSOLIDATED | STANDALONE | SEGMENT
    basis: str = "UNKNOWN"           # GAAP | NON_GAAP | IFRS | IND_AS
    definition: str = ""            # Qualifying definitions or footnotes
    geography: str = ""             # Geographic segment
    source_type: str = ""           # ANNUAL_REPORT | PRESENTATION | PROSPECTUS
```

### 4.3 Temporal Comparability vs Comparability Action
Temporal overlap does NOT equal identical temporal claims. For example, `FY2024 (12 months)` and `Q4 FY2024 (3 months)` overlap temporally, but comparing their revenues directly would produce a false contradiction.

Gate 2 evaluates temporal relations into explicit comparability classes with defined comparison actions:

| Temporal Relation | Comparability Classification | Comparison Action | Example |
| :--- | :--- | :--- | :--- |
| **EXACT** | `DIRECTLY_COMPARABLE` | Direct numerical comparison permitted | FY2024 vs FY2024 |
| **CONTAINMENT** | `CONTEXTUALLY_RELATED` | Related temporal context; **do NOT compare values** | Q4 FY2024 inside FY2024 |
| **ADJACENT** | `CONTEXTUALLY_RELATED` | Sequential period; trend context only | FY2023 vs FY2024 |
| **OVERLAPPING** | `SPECIALIZED_TREATMENT` | Partial shift; requires specialized reconciler | TTM vs Calendar Year |
| **NON_OVERLAPPING** | `NON_COMPARABLE` | Disjoint periods; **do NOT group or compare** | FY2020 vs FY2024 |
| **UNKNOWN** | `UNRESOLVED` | Ambiguous temporal boundaries | Unstated period |

### 4.4 4-Gate Contextual Fact Resolution
Candidates are grouped through 4 disciplined gates:
1. **Gate 1 (Entity Grounding):** Canonical entity must match (`c1.entity_canonical == c2.entity_canonical`).
2. **Gate 2 (Temporal Comparability):** Must evaluate to `DIRECTLY_COMPARABLE` for numerical comparison groups. `CONTEXTUALLY_RELATED` forms contextual context groups without numerical variance evaluation.
3. **Gate 3 (Metric & Measurement Compatibility):**
   - Must share identical `measurement_type` (e.g., cannot group `ABSOLUTE_VALUE` with `RATE_OF_CHANGE`).
   - Same Family + Same Subtype -> Direct Comparison Group.
   - Same Family + Different Subtype -> Contextual Family Group (routed to reconciliation).
   - Different Family -> Grouping blocked.
4. **Gate 4 (Context Compatibility):** Mismatches in `scope` (Consolidated vs Standalone) or `basis` (GAAP vs Non-GAAP) tag the group for Path B (Contextual Reconciliation) rather than pure corroboration.

---

## 5. Layer 3 Extension: Scaled Decision Engine & Relationship Adjudication

### 5.1 Claim Relationship Graph & Cluster-Based Adjudication
Majority voting across $N(N-1)/2$ pairs is epistemically invalid for financial claims. If two filings report ₹500 and two report ₹700, majority vote cannot declare truth.

EVIDRA 2.0 constructs a **Claim Relationship Graph** within each fact group:

```text
Fact Group with N Members
           |
Pairwise Evaluation across Core LangGraph Tournament
           |
Construct Relationship Graph:
  Nodes: Candidate Claims (Value + Source Citation)
  Edges: CORROBORATES, CONFLICTS_WITH, RECONCILES_WITH
           |
Cluster Claims by Equivalence:
  Cluster 1: Value = ₹500 (Sources: Annual Report p.36, Earnings Presentation p.6)
  Cluster 2: Value = ₹700 (Sources: Prospectus p.27, Restatement Note p.88)
           |
Graph-Level Synthesis Verdict:
  - If 1 Cluster: UNANIMOUS_CORROBORATION
  - If 2+ Clusters with Valid Reconciliation Bridge: RECONCILED_CLUSTERS
  - If 2+ Clusters with Direct Unreconciled Variance: CONFLICTING_CLAIM_CLUSTERS
```

This presents the user with structured epistemic clusters rather than an arbitrary majority winner.

### 5.2 Rule-Based Evidence Sufficiency Indicator
Eliminate arbitrary decimal equations (`0.3*a + 0.2*b`) that introduce false precision.

The `EvidenceSufficiencyIndicator` operates as a transparent categorical rule gate:

```text
IDENTITY COMPLETE? (Entity, Metric Family, Subtype, and Period resolved?)
       |
       +--- NO  --> Indicator: INSUFFICIENT_IDENTITY (Route: SKIP to fast-path UNRESOLVED)
       |
       v
COMPARABLE CANDIDATES >= 2? (From 2+ distinct pages or documents?)
       |
       +--- NO  --> Indicator: SINGLE_SOURCE_PENDING (Route: DEFER to Evidence Gap Engine)
       |
       v
EVIDENCE GROUNDED & VERIFIED? (Extract-then-verify entailment passed?)
       |
       +--- NO  --> Indicator: UNVERIFIED_EVIDENCE (Route: SKIP)
       |
       v
CONTEXT COMPATIBLE? (Scope and Accounting Basis aligned or bridgeable?)
       |
       +--- NO  --> Indicator: CONTEXT_DIVERGENT (Route: Contextual Reconciliation Tournament)
       |
       v
Indicator: SUFFICIENT_FOR_ADJUDICATION (Route: Standard Tournament)
```

### 5.3 Cascading Reconciliation Enhancement
Preserves the 5 specialist validators (Arithmetic, Restatement, Accounting Basis, Scope, Timing) from Architecture 1. When clean groups arrive from Layer 2, reconciliation is proposed when at least one validator confirms a structural difference (e.g., Non-GAAP reconciliation adjustment) and no validator refutes it with high confidence.

---

## 6. Layer 4 Extension: Dynamic Epistemology & Active Evidence Gaps

### 6.1 Multi-Dimensional Claim Lifecycle
Do not combine relationship, version, validity, and status into a single 12-state enum. Separate them into four clean, orthogonal dimensions:

```text
1. Claim Status (Pipeline Progression):
   OBSERVED -> VERIFIED -> CANDIDATE -> PENDING -> ADJUDICATED

2. Relationship (Multi-Source Epistemic Result):
   CORROBORATED | RECONCILED | CONTRADICTED | UNRESOLVED

3. Validity (Grounding & Entailment Quality):
   SUPPORTED | PARTIALLY_SUPPORTED | REJECTED

4. Version (Temporal & Filing Evolution):
   CURRENT | SUPERSEDED
```

This cleanly decouples whether a claim is verified from how it relates to other claims or whether newer filings have restated it.

### 6.2 Source Independence Indicator
EVIDRA assesses independence between **sources**, not absolute epistemic independence.

The system reports a **Source Independence Indicator**:
- `HIGH`: Confirmed across distinct document filings (e.g., Audited Annual Report vs Investor Deck) with lexical Jaccard overlap < 25% and distinct visual presentations (Table vs Body Text).
- `MEDIUM`: Distinct physical documents with moderate lexical overlap (25% - 60%).
- `LOW`: High textual overlap (> 60%) or shared authorship metadata suggesting derived quotation.
- `UNKNOWN`: Insufficient filing metadata to establish separation.

### 6.3 Evidence Gap Specification & Identity-Aware Active Acquisition
**Core Epistemic Thesis:** *The system must articulate what evidence is missing before attempting to acquire it.*

When an adjudication terminates in UNRESOLVED, the system constructs a structured **Evidence Gap Specification**:

```python
class EvidenceGapSpec(BaseModel):
    gap_id: str
    target_entity: str
    metric_family: str
    metric_subtype: str
    measurement_type: MeasurementType
    target_period: tuple[str, str]
    
    # Gap Audit Matrix
    has_entity: bool = True
    has_metric: bool = True
    has_value: bool = True
    has_period: bool = True
    has_scope: bool = False
    has_independent_second_source: bool = False
    
    # Retrieval Requirements (Identity-Aware)
    retrieval_query_terms: list[str]
    target_document_types: list[str]
    candidate_chunk_ids: list[str] = Field(default_factory=list)
```

**Identity-Aware Hybrid Retrieval:**
1. **Deterministic Metadata Filter (SQL):** Query `evidence_chunks` filtering for chunks from uninspected documents (`document_id != origin_doc`).
2. **Semantic Re-ranking (BGE Embeddings):** Rank filtered chunks against the `FactIdentitySignature` representation (`entity + metric_family + metric_subtype + surface_metric + definition`).
3. **Re-Extraction & Re-Adjudication:** Top candidates (up to 5 chunks) are wrapped in Evidence Windows, parsed for observations, and fed into Round-2 tournament adjudication.
4. **Audit Gaps:** If no matching evidence exists, the system outputs an audited UNRESOLVED verdict with the full `EvidenceGapSpec` persisted in `evidence_gaps`.

---

## 7. Phased Implementation Roadmap (P0 to P4)

Development is strictly sequenced to ensure intelligence is solid upstream before complex reasoning is tested:

```text
P0: Make Extraction Trustworthy (Upstream Foundation)
    ├── Evidence Candidate Discovery (3-Tier Budget, Per-Doc Quota)
    ├── Evidence Windows (Context Envelopes)
    ├── Multi-Signal Layout Hierarchy (Confidence Scoring)
    └── Lightweight Schema Induction (Metric Families & Subtypes)

P1: Make Identity Trustworthy (Contextual Resolution)
    ├── Fact Identity Signature with Measurement Semantics
    ├── Temporal Comparability Classification
    ├── 4-Gate Contextual Fact Resolution
    └── Claim Relationship Graph & Cluster Adjudication

P2: Validate Core Reasoning Tournament
    ├── Corroboration on Delhivery Dataset (Revenue from Operations)
    ├── Contradiction on Historical Restatements
    ├── Reconciliation on Ind AS vs Adjusted EBITDA
    └── Verified UNRESOLVED on Ambiguous Metrics

P3: Add Epistemic Innovations
    ├── Multi-Dimensional Claim Lifecycle
    ├── Source Independence Indicator
    └── Evidence Gap Specification & Identity-Aware Active Acquisition

P4: Comprehensive Quality Evaluation & Documentation
    ├── Manually Annotated Gold Evaluation Set (50 claims / 20 pairs)
    ├── Quality Metrics Audit against Targets
    ├── Four-Case Demonstration Artifacts
    └── System Verification & Demo Recording
```

---

## 8. Quality-Oriented Evaluation Framework & Gold Benchmark

Success is measured against empirical **Engineering Targets** evaluated over a manually annotated Gold Evaluation Set (`tests/data/gold_evaluation.json` containing 50 representative observations and 20 pairwise claim relationships):

| Metric | Definition | Engineering Target |
| :--- | :--- | :--- |
| **Observation Precision** | Fraction of extracted claims representing genuine corporate financial assertions. | Target $\ge 90\%$ |
| **Evidence Grounding Rate** | Fraction of claims whose raw value and units strictly entail from the cited Evidence Window. | Target $\ge 95\%$ |
| **Entity Resolution Accuracy** | Fraction of claims correctly attributed to legal corporate entities (zero generic placeholders). | Target $\ge 95\%$ |
| **Metric Identity Accuracy** | Fraction of claims correctly assigned to appropriate Metric Family, Subtype, and Measurement Type. | Target $\ge 90\%$ |
| **False Grouping Rate** | Fraction of candidate pairs grouped despite representing distinct financial concepts. | Target $\le 5\%$ |
| **False Contradiction Rate** | Fraction of contradictory verdicts resulting from metric, measurement, or temporal mismatch. | Target $0\%$ |
| **Reconciliation Grounding** | Fraction of RECONCILED verdicts supported by verifiable accounting adjustment notes. | Target $100\%$ |
| **Audited Gap Rate** | Fraction of UNRESOLVED verdicts accompanied by a complete, actionable `EvidenceGapSpec`. | Target $100\%$ |
