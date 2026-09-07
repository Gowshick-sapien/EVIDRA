# Fact Knowledge Layer (EVIDRA) -- System Architecture Specification

---

## 1. Architectural Philosophy and Core Thesis

The Fact Knowledge Layer (**EVIDRA**) is an evidence-centric financial reasoning system designed to ingest heterogeneous financial documents (annual reports, earnings releases, investor presentations), extract factual claims with spatial provenance, detect corroborations and contradictions across sources, and reconcile variances through structured adversarial reasoning.

### 1.1 The Fact is Not the Primitive

Conventional retrieval-augmented generation (RAG) and knowledge graph systems treat extracted claims as atomic facts. In contrast, EVIDRA establishes that:

```
[ Evidence Chunk ] (Physical text/table with PDF coordinates)
        |
        v
[ Observation ] (Literal assertion made by a source document)
        |
        v
[ Fact Candidate ] (Normalized entity-attribute-period proposition)
        |
        v
[ Fact Group ] (Cluster of related propositions across documents)
        |
        v
[ Hypothesis Tournament ] (Competing explanations for variances)
        |
        v
[ Decision ] (Epistemic verdict: Corroborated, Contradicted, Reconciled, Unresolved)
        |
        v
[ Decision Trace ] (Cryptographic, step-by-step audit record)
```

1. **Observations are distinct from Decisions:** What a source document asserts (Observation) must never be conflated with what the system concludes (Decision).
2. **Provenance is Mandatory:** Every numerical and qualitative claim must trace directly to a document ID, page number, and geometric bounding box (x0, y0, x1, y1).
3. **Extract-Then-Verify Separation:** The extraction of a claim is separated from its verification. An independent verifier validates whether the raw source text strictly entails the extracted claim before any reasoning occurs.
4. **Deterministic and LLM Boundary Separation:** Large Language Models (LLMs) are restricted to semantic reasoning, extraction, and hypothesis generation. All financial arithmetic, unit scaling, date parsing, and final decision policies are executed by deterministic pure Python modules.
5. **UNRESOLVED is a First-Class Citizen:** If evidence is ambiguous, missing, or contradictory without a documented bridge, the system declares UNRESOLVED rather than guessing.

### 1.2 Ledger as System of Record (Why Not Graph/Vector Databases)

The system does not rely on a graph database or vector database as its decision engine:
* **The Evidence Ledger (SQLite + JSON) is the single source of truth.** Graph databases represent relationships but cannot enforce epistemic provenance, arithmetic tolerances, or adversarial falsification protocols.
* Any graph representation (e.g., via NetworkX) functions strictly as an optional visual projection of the Ledger, never as the decision mechanism.
* Vector embeddings are utilized exclusively for candidate blocking (grouping similar attributes) via in-memory cosine similarity, eliminating the need for dedicated external vector databases.

---

## 2. End-to-End System Topology

```
+---------------------------------------------------------------------------------------------------+
|                                  LAYER 1: DOCUMENT EVIDENCE PREPARATION                           |
|                                                                                                   |
|   +-----------------------+     +------------------------+     +------------------------------+   |
|   |   PyMuPDF (fitz)      |     |      pdfplumber        |     |   Document Representation    |   |
|   | Text Blocks & BBoxes  |     | Table Grid Extraction  | --> | Manifest, Envelopes & Tables |   |
|   +-----------------------+     +------------------------+     +------------------------------+   |
+---------------------------------------------------------------------------------------------------+
                                                  |
                                                  v
+---------------------------------------------------------------------------------------------------+
|                                  LAYER 2: FACT CONSTRUCTION                                       |
|                                                                                                   |
|   +----------------------+     +-------------------------+     +------------------------------+   |
|   | Dual Extraction      |     | Extract-Then-Verify     |     | Deterministic Normalization  |   |
|   | Numerical & Semantic | --> | Entailment Verification | --> | Python Decimal & ISO Dates   |   |
|   +----------------------+     +-------------------------+     +------------------------------+   |
|                                                                               |                   |
|                                                                               v                   |
|                                                                +------------------------------+   |
|                                                                | Candidate Grouping (BGE)     |   |
|                                                                | Hard & Soft Blocking         |   |
|                                                                +------------------------------+   |
+---------------------------------------------------------------------------------------------------+
                                                  |
                                                  v
+---------------------------------------------------------------------------------------------------+
|                                  LAYER 3: FACT DECISION ENGINE (LangGraph)                        |
|                                                                                                   |
|                      +---------------------------------------+                                    |
|                      | Numerical & Contextual Variance Check |                                    |
|                      +---------------------------------------+                                    |
|                             /                         \                                           |
|              [Within Tol.] /                           \ [Exceeds Tol.]                           |
|                           v                             v                                         |
|                  +----------------+             +-------------------------------+                 |
|                  |  CORROBORATED  |             |     Hypothesis Tournament     |                 |
|                  +----------------+             +-------------------------------+                 |
|                                                                 |                                 |
|                                                                 v                                 |
|                                                 +-------------------------------+                 |
|                                                 |     Specialist Validators     |                 |
|                                                 +-------------------------------+                 |
|                                                                 |                                 |
|                                                                 v                                 |
|                                                 +-------------------------------+                 |
|                                                 |   Reconciliation Proposer     |                 |
|                                                 +-------------------------------+                 |
|                                                                 |                                 |
|                                                                 v                                 |
|                                                 +-------------------------------+                 |
|                                                 |     Adversarial Skeptic       |                 |
|                                                 +-------------------------------+                 |
|                                                                 |                                 |
|                                                                 v                                 |
|                                                 +-------------------------------+                 |
|                                                 | Deterministic Decision Policy |                 |
|                                                 +-------------------------------+                 |
|                                                                 |                                 |
|                                         +-----------------------+-----------------------+         |
|                                         |                       |                       |         |
|                                         v                       v                       v         |
|                                   CONTRADICTION             RECONCILED              UNRESOLVED    |
+---------------------------------------------------------------------------------------------------+
                                                  |
                                                  v
+---------------------------------------------------------------------------------------------------+
|                                  LAYER 4: OBSERVABILITY & INSPECTION                              |
|                                                                                                   |
|   +-----------------------+     +------------------------+     +------------------------------+   |
|   | SQLite Evidence Ledger|     | Cryptographic Traces   |     | Markdown Audit Reports       |   |
|   | Relational Records    |     | Step-by-Step JSONL     |     | Executive, Contradictions    |   |
|   +-----------------------+     +------------------------+     +------------------------------+   |
|                                             |                                                     |
|                                             v                                                     |
|                               +----------------------------+                                      |
|                               | FastAPI Swagger UI + CLI   |                                      |
|                               +----------------------------+                                      |
+---------------------------------------------------------------------------------------------------+
```

---

## 3. Layer 1 -- Document Evidence Preparation

Layer 1 answers the physical question: **"What is physically and semantically present in this document?"** It performs zero semantic reasoning and does not evaluate truth claims.

### 3.1 Two-Tool PDF Ingestion Strategy

```
                          Arbitrary Financial PDF
                                     |
                 +-------------------+-------------------+
                 |                                       |
                 v                                       v
         PyMuPDF (fitz)                             pdfplumber
     [Primary Text Engine]                     [Table Specialist]
                 |                                       |
                 |-- Paragraph spans                     |-- Cell matrices
                 |-- Font sizes & headers                |-- Multi-row headers
                 |-- Bounding boxes                      |-- Explicit borders
                 |                                       |
                 +-------------------+-------------------+
                                     |
                                     v
                       Spatial Disambiguation Mask
                   (Prevents duplicate text extraction)
                                     |
                                     v
                       Document Representation Package
```

* **PyMuPDF (fitz):** Primary fast engine for parsing pages, text blocks, fonts, and bounding boxes (x0, y0, x1, y1).
* **pdfplumber:** Structural table extractor for row/column matrices, merged cells, and headers.
* **Spatial Disambiguation:** When tables are extracted by `pdfplumber`, their bounding boxes are masked out of the PyMuPDF text stream to prevent double-counting narrative text inside tables.

### 3.2 Document Representation Package & Manifest

Each processed document yields a self-contained representation package:

```
runs/JOB-{id}/documents/{document_id}/
|-- manifest.json           # Document characteristics, hashes, entity cues
|-- document.md             # Evidence-tagged Markdown representation
|-- pages/                  # Page-level raw text and layout chunks
|   |-- page_001.json
|   +-- page_002.json
+-- tables/                 # Domain-oriented table matrices
    |-- table_001.json
    +-- table_002.json
```

#### Document Manifest Schema (`manifest.json`)
```json
{
  "document_id": "DOC-2024-Q3-PR",
  "filename": "Q3_2024_Earnings_Release.pdf",
  "source_hash_sha256": "3a7b8e...",
  "page_count": 14,
  "filing_date": "2024-10-24",
  "document_characteristics": {
    "contains_tables": true,
    "contains_financial_statements": true,
    "contains_gaap_reconciliation": true
  },
  "detected_currency": ["USD"],
  "detected_scales": ["millions"]
}
```

### 3.3 Domain-Oriented Table Metadata

Financial tables cannot be parsed as plain text grids. They require context metadata:

```json
{
  "table_id": "TBL-004",
  "document_id": "DOC-2024-Q3-PR",
  "page_number": 8,
  "bounding_box": [54.0, 120.5, 540.0, 480.0],
  "table_semantics": {
    "title": "Condensed Consolidated Statements of Operations",
    "reporting_scope": "consolidated",
    "accounting_standard": "US-GAAP",
    "currency": "USD",
    "scale": "thousands",
    "columns": {
      "col_0": "Line Item",
      "col_1": "Three Months Ended Sep 30, 2024",
      "col_2": "Three Months Ended Sep 30, 2023"
    },
    "footnotes": [
      "Note 1: Includes stock-based compensation of $14,200 thousand."
    ]
  }
}
```

### 3.4 Evidence-Tagged Markdown Convention

Every downstream extracted proposition points to a physical evidence chunk:

```markdown
<!-- chunk: CHK-DOC1-P03-001 | page: 3 | bbox: [72.0, 140.0, 520.0, 180.0] -->
Total revenues for the third quarter reached $8,500 million, an increase of 12% year-over-year.

<!-- chunk: CHK-DOC1-P03-002 | page: 3 | bbox: [72.0, 190.0, 520.0, 230.0] -->
Operating income was $1,200 million compared to $1,050 million in the prior year period.
```

---

## 4. Layer 2 -- Fact Construction

Layer 2 answers the semantic question: **"What claims are asserted in these observations, are they strictly entailed, and how are they normalized?"**

### 4.1 Dual Extraction Pipeline

Extraction converts evidence chunks into structured Pydantic observations using two distinct pipelines:

1. **Table-Native Extraction:**
   * Direct geometric cell translation: `(row_header, column_header, cell_value)` mapped directly to `(attribute, temporal_scope, raw_value)`.
   * Inherits table-level metadata (currency, scale, reporting scope) automatically.
2. **Prose Extraction via Constrained LLM Prompting:**
   * Narrative text blocks are processed by Ollama (Qwen2.5) with schema constraints.
   * Forces extraction of entity, attribute, raw value, unit, and exact sentence citation.

### 4.2 Extract-Then-Verify Paradigm

To protect the system against local LLM hallucinations, extraction is decoupled from verification:

```
[ Evidence Chunk ]
        |
        v
+-----------------------+       Candidate Claim
|   Extraction Agent    | ------------------------+
+-----------------------+                         |
                                                  v
                                      +-----------------------+
                                      |   Evidence Verifier   |
                                      |   (Independent Pass)  |
                                      +-----------------------+
                                                  |
                         +------------------------+------------------------+
                         |                        |                        |
                         v                        v                        v
                    [ENTAILED]             [HALLUCINATED]             [AMBIGUOUS]
                         |                        |                        |
                         v                        v                        v
                   Proceeds to               Discarded &             Flagged for
                  Normalization            Logged in Trace         Manual Review
```

* The **Evidence Verifier** receives ONLY the raw text chunk and the extracted proposition.
* It answers: *"Does this chunk strictly entail this proposition without assumption?"*
* Claims marked `HALLUCINATED` are eliminated immediately, ensuring ungrounded data never reaches the decision layer.

### 4.3 Context Resolution & Dynamic Schema

Financial metrics possess multiple dimensions of meaning. The Context Resolver extracts qualifiers:

| Dimension | Permitted / Detected Values | Example |
|---|---|---|
| **Accounting Basis** | `GAAP`, `NON-GAAP`, `ADJUSTED`, `IFRS` | Adjusted EBITDA vs Net Income |
| **Organizational Scope** | `CONSOLIDATED`, `STANDALONE`, `SEGMENT` | Cloud Segment Revenue vs Total Company |
| **Filing Type** | `PRESS_RELEASE`, `UNAUDITED_PRELIMINARY`, `AUDITED_10K` | Preliminary flash results vs Audited filing |
| **Restatement Status** | `ORIGINAL`, `AMENDED_10KA`, `RESTATED` | Post-audit revisions |

The schema is dynamic: attribute names are not restricted to an inflexible hardcoded enum. Variations like "Operating Revenues" and "Revenues from Operations" are preserved verbatim and resolved via semantic matching.

### 4.4 Deterministic Normalizers (Pure Python)

Financial facts must not be evaluated using floating-point approximations or LLM calculations:

1. **Exact Financial Arithmetic (`decimal.Decimal`):**
   * All numbers are parsed into Python `Decimal` instances.
   * Magnitude scaling applied deterministically:
     * `Thousand` -> `* 10^3`
     * `Lakh` -> `* 10^5`
     * `Million` -> `* 10^6`
     * `Crore` -> `* 10^7`
     * `Billion` -> `* 10^9`
2. **Currency Standardization:** Standardized to ISO 4217 (`USD`, `INR`, `EUR`, `GBP`). Direct numerical comparison across differing currencies is prohibited unless explicit exchange rates are present.
3. **Temporal Interval Normalization (`dateutil`):** All fiscal periods and quarters are converted to ISO 8601 calendar intervals `(period_start, period_end)`:
   * `Q3 FY2024` -> `(2024-07-01, 2024-09-30)`
   * `FY2023` -> `(2023-01-01, 2023-12-31)`

### 4.5 Candidate Fact Grouping & Blocking Engine

Comparing every extracted fact against every other fact is computationally intractable. EVIDRA implements two-stage candidate blocking:

```
All Verified Facts
        |
        v
+-------------------------------------------------------+
| Stage 1: Hard Blocking                                |
| Filter by exact Entity match AND Period overlap       |
+-------------------------------------------------------+
        |
        v
+-------------------------------------------------------+
| Stage 2: Soft Semantic Attribute Matching             |
| Compute cosine similarity over BGE-Small embeddings   |
| (Threshold: similarity >= 0.82)                       |
+-------------------------------------------------------+
        |
        v
   Candidate Fact Groups
```

---

## 5. Layer 3 -- Fact Decision Engine

Layer 3 answers the core epistemic question: **"How do facts across documents relate -- do they corroborate, contradict, or can they be reconciled?"**

### 5.1 Three Adaptive Decision Paths

To balance computational efficiency and reasoning rigor, the LangGraph orchestrator routes each `FactGroup` through one of three paths:

| Path | Trigger Condition | Execution Mechanism | Latency / Cost |
|---|---|---|---|
| **Path A: Deterministic Corroboration** | Exact normalized numerical equality (within 0.01% tolerance), identical entity, period, and scope. | Direct comparison via Python `Decimal`. Bypasses LLM reasoning entirely. Emits `CORROBORATED`. | Low (< 10ms) |
| **Path B: Contextual Resolution** | Dimensional variance detected (differing accounting basis, differing reporting scope, or differing fiscal period). | Routes directly to Specialist Context Validators. If bridge context is verified, emits `RECONCILED`. | Moderate (~ 1-2s) |
| **Path C: Conflict Debate** | Disagreement in values under apparently identical context qualifiers. | Full epistemic tournament: Hypothesis Generator -> Validators -> Reconciliation Proposer -> Adversarial Skeptic -> Decision Policy. | Complete (~ 3-6s) |

### 5.2 Hypothesis Tournament

When facts in a group disagree, the system does not immediately declare a contradiction. It initiates a structured Hypothesis Tournament:

```
                                  Variance Detected
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                            Hypothesis Generator Agent                             |
|                                                                                   |
|  [H1] RESTATEMENT: Subsequent revision or restated filing                         |
|  [H2] ACCOUNTING_BASIS: GAAP vs Non-GAAP / Adjusted metric difference             |
|  [H3] SCOPE_MISMATCH: Consolidated group vs Standalone parent entity              |
|  [H4] TIMING_DIFFERENCE: Calendar quarter vs custom fiscal month-end              |
|  [H5] ERRONEOUS_CONTRADICTION: Genuine irreconcilable disagreement                |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                              Specialist Validators                                |
|                                                                                   |
|  * RestatementValidator: Checks filing dates, 10-K/A indicators, restatement notes |
|  * AccountingBasisValidator: Inspects GAAP-to-Non-GAAP reconciliation bridge tables |
|  * ScopeValidator: Checks legal entity hierarchy and segment disclosures          |
|  * ArithmeticValidator: Computes exact delta and tests reconciliation bridge math |
+-----------------------------------------------------------------------------------+
```

### 5.3 Reconciliation Agent vs. Adversarial Skeptic

To eliminate false reconciliations and model sycophancy, EVIDRA implements an adversarial debate protocol:

```
[ Validator Findings ]
          |
          v
+---------------------------------------------------+
|             Reconciliation Proposer               |
| Synthesizes supported validator findings into an  |
| explicit reconciliation bridge narrative.        |
+---------------------------------------------------+
          |
          | Proposed Reconciliation
          v
+---------------------------------------------------+
|               Adversarial Skeptic                 |
| Attacks proposed explanation using original       |
| source chunks.                                    |
|                                                   |
| Probes:                                           |
| 1. Is the bridge arithmetic explicitly confirmed? |
| 2. Does the text state the scope difference?      |
| 3. Does the explanation rely on assumptions?      |
+---------------------------------------------------+
          |
          +-----------------------+-----------------------+
          |                       |                       |
          v                       v                       v
     [SURVIVED]              [FALSIFIED]            [INSUFFICIENT]
          |                       |                       |
          v                       v                       v
     Reconciliation          Contradiction            Unresolved
        Confirmed               Declared               Assigned
```

### 5.4 Pure Python Deterministic Decision Policy

The final decision is never made by an LLM prompt. A deterministic Python rule engine evaluates validator and skeptic outcomes against strict conditions:

```python
# Pure Python Decision Policy Truth Table Logic
def evaluate_decision_policy(group: FactGroup, validators: list[ValidatorResult], skeptic: SkepticOutcome) -> Verdict:
    # Rule 1: Corroboration
    if group.is_numerically_equal(tolerance=Decimal("0.0001")) and group.has_matching_context():
        return Verdict.CORROBORATED
    
    # Rule 2: Reconciled
    if (
        skeptic.status == SkepticStatus.SURVIVED 
        and any(v.status == ValidationStatus.SUPPORTED for v in validators)
        and all(v.status != ValidationStatus.REFUTED for v in validators)
    ):
        return Verdict.RECONCILED
    
    # Rule 3: Contradiction
    if (
        group.has_matching_context() 
        and not group.is_numerically_equal()
        and (skeptic.status == SkepticStatus.FALSIFIED or all(v.status == ValidationStatus.REFUTED for v in validators))
    ):
        return Verdict.CONTRADICTION
    
    # Rule 4: Default Fallback
    return Verdict.UNRESOLVED
```

### 5.5 Categorical Decision Strength

Confidence is represented as an ordinal, transparent category rather than an uncalibrated float:

| Strength | Criteria |
|---|---|
| **HIGH** | Full dual-source provenance, zero unentailed claims, all validator rules passed, adversarial challenge survived or exact numerical match. |
| **MEDIUM** | Verified provenance, reconciliation supported by footnote text but lacking explicit arithmetic bridge table. |
| **LOW** | Minor contextual ambiguity remains unresolved, but direction of claims is compatible. |
| **INSUFFICIENT** | Missing source context, unentailed observations, or unresolved conflicting evidence. Automatically routes to `UNRESOLVED`. |

### 5.6 The Decision Card Specification

Every evaluated fact relationship produces a structured `DecisionCard`:

```
+---------------------------------------------------------------------------------+
| DECISION CARD: DEC-2024-0091                                                    |
+---------------------------------------------------------------------------------+
| Entity: Acme Corp                                                               |
| Attribute: Revenue (Q3 2024)                                                    |
| Scope: Consolidated                                                             |
|                                                                                 |
| Claim A: $8,500M (Press Release, Page 3, Chunk CHK-03-01)                       |
| Claim B: $8,485M (Form 10-Q, Page 12, Chunk CHK-12-04)                          |
|                                                                                 |
| VERDICT: RECONCILED                                                             |
| Decision Strength: HIGH                                                         |
+---------------------------------------------------------------------------------+
| PROVENANCE CITATIONS                                                            |
| Source A: DOC-PR-Q3 / Page 3 / BBox [72.0, 140.0, 520.0, 180.0]                 |
| Source B: DOC-10Q-Q3 / Page 12 / BBox [54.0, 220.0, 500.0, 260.0]               |
+---------------------------------------------------------------------------------+
| RECONCILIATION NARRATIVE                                                        |
| The $15M variance is explained by the subsequent reclassification of discontinued|
| operations in the European logistics unit, explicitly detailed in Note 4        |
| (Page 18 of Form 10-Q).                                                         |
+---------------------------------------------------------------------------------+
| ADVERSARIAL AUDIT                                                               |
| Challenge: Tested hypothesis H2 (Accounting Error) against restatement note.    |
| Outcome: SURVIVED. Reclassification table arithmetic matches $15M delta exactly.|
+---------------------------------------------------------------------------------+
```

---

## 6. Layer 4 -- Observability, Inspection, and Persistence

Layer 4 provides transparent inspection interfaces, relational storage, and human-readable reports.

### 6.1 Four-Level Inspection Hierarchy

```
[ Level 1: Run Overview ]     --> Total documents, throughput, verdict distribution
            |
            v
[ Level 2: Document Context ] --> Detected tables, context envelopes, manifest
            |
            v
[ Level 3: Decision Cards ]   --> Claim-by-claim comparison, verdicts, strength
            |
            v
[ Level 4: Raw Evidence ]     --> Exact PDF text chunk, bounding box, SHA-256 hash
```

### 6.2 Relational SQLite Schema (`ledger.db`)

The Evidence Ledger isolates persistence into 10 relational tables:

```sql
-- Relational System of Record
CREATE TABLE documents (
    document_id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    file_hash TEXT NOT NULL,
    page_count INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE evidence_chunks (
    chunk_id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL,
    page_number INTEGER NOT NULL,
    chunk_type TEXT CHECK(chunk_type IN ('text', 'table', 'figure')),
    bounding_box TEXT NOT NULL,
    content TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    FOREIGN KEY(document_id) REFERENCES documents(document_id)
);

CREATE TABLE observations (
    observation_id TEXT PRIMARY KEY,
    chunk_id TEXT NOT NULL,
    document_id TEXT NOT NULL,
    statement TEXT NOT NULL,
    entity TEXT NOT NULL,
    attribute TEXT NOT NULL,
    raw_value TEXT NOT NULL,
    observation_type TEXT CHECK(observation_type IN ('numerical', 'semantic', 'event')),
    temporal_scope TEXT NOT NULL,
    provenance_status TEXT CHECK(provenance_status IN ('ENTAILED', 'HALLUCINATED', 'AMBIGUOUS')),
    confidence REAL NOT NULL,
    FOREIGN KEY(chunk_id) REFERENCES evidence_chunks(chunk_id)
);

CREATE TABLE fact_candidates (
    fact_id TEXT PRIMARY KEY,
    observation_id TEXT NOT NULL,
    normalized_value TEXT NOT NULL,
    normalized_unit TEXT NOT NULL,
    normalized_currency TEXT NOT NULL,
    period_start TEXT NOT NULL,
    period_end TEXT NOT NULL,
    FOREIGN KEY(observation_id) REFERENCES observations(observation_id)
);

CREATE TABLE fact_groups (
    group_id TEXT PRIMARY KEY,
    entity TEXT NOT NULL,
    attribute TEXT NOT NULL,
    period_id TEXT NOT NULL,
    member_count INTEGER NOT NULL
);

CREATE TABLE group_members (
    group_id TEXT NOT NULL,
    fact_id TEXT NOT NULL,
    PRIMARY KEY(group_id, fact_id),
    FOREIGN KEY(group_id) REFERENCES fact_groups(group_id),
    FOREIGN KEY(fact_id) REFERENCES fact_candidates(fact_id)
);

CREATE TABLE hypotheses (
    hypothesis_id TEXT PRIMARY KEY,
    group_id TEXT NOT NULL,
    explanation_type TEXT NOT NULL,
    description TEXT NOT NULL,
    likelihood_score REAL NOT NULL,
    FOREIGN KEY(group_id) REFERENCES fact_groups(group_id)
);

CREATE TABLE validator_results (
    result_id TEXT PRIMARY KEY,
    hypothesis_id TEXT NOT NULL,
    validator_type TEXT NOT NULL,
    outcome TEXT NOT NULL,
    details_json TEXT NOT NULL,
    FOREIGN KEY(hypothesis_id) REFERENCES hypotheses(hypothesis_id)
);

CREATE TABLE decisions (
    decision_id TEXT PRIMARY KEY,
    group_id TEXT NOT NULL,
    verdict TEXT CHECK(verdict IN ('CORROBORATED', 'CONTRADICTION', 'RECONCILED', 'UNRESOLVED')),
    decision_strength TEXT CHECK(decision_strength IN ('HIGH', 'MEDIUM', 'LOW', 'INSUFFICIENT')),
    reasoning_summary TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(group_id) REFERENCES fact_groups(group_id)
);

CREATE TABLE decision_traces (
    trace_id TEXT PRIMARY KEY,
    decision_id TEXT NOT NULL,
    step_name TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    input_json TEXT NOT NULL,
    output_json TEXT NOT NULL,
    execution_time_ms REAL NOT NULL,
    FOREIGN KEY(decision_id) REFERENCES decisions(decision_id)
);
```

### 6.3 Automated Markdown Reporting Suite

Every execution automatically generates three human-readable reports in `runs/JOB-{id}/reports/`:

1. **Executive Summary (`summary.md`):** Complete job dashboard detailing total documents ingested, evidence chunks generated, fact groups formed, and verdict distribution.
2. **Contradiction Report (`contradictions.md`):** Focused audit of every genuine conflict detected, presenting side-by-side evidence chunks, bounding box references, and why reconciliation attempts failed.
3. **Unresolved Analysis Report (`unresolved.md`):** Comprehensive breakdown of all claims where evidence was incomplete, ambiguous, or unentailed, with specific analyst recommendations.

---

## 7. Execution Runtime and Orchestration

### 7.1 LangGraph State Machine Architecture

The reasoning engine is orchestrated as a directed acyclic state graph using LangGraph:

```python
# LangGraph Pipeline State Definition
class PipelineState(TypedDict):
    job_id: str
    documents: list[DocumentManifest]
    evidence_chunks: list[EvidenceChunk]
    observations: list[Observation]
    verified_facts: list[FactCandidate]
    fact_groups: list[FactGroup]
    current_group: Optional[FactGroup]
    hypotheses: list[Hypothesis]
    validator_results: list[ValidatorResult]
    reconciliation: Optional[ReconciliationProposal]
    skeptic_outcome: Optional[SkepticOutcome]
    decisions: list[DecisionCard]
    traces: list[DecisionTrace]
    errors: list[str]
```

### 7.2 LLM Provider Abstraction (`ReasoningService`)

All agent nodes interface with local models via an abstract protocol:

```python
class ReasoningService(ABC):
    @abstractmethod
    def generate_structured(
        self, 
        prompt: str, 
        schema: type[T], 
        temperature: float = 0.0
    ) -> T:
        """Forces the local model to emit validated Pydantic instances."""
        pass
```

* Concrete implementation `OllamaProvider` wraps `langchain-ollama`.
* Enforces temperature `0.0` for maximum reproducibility.
* Incorporates automated retry loops with JSON schema validation. If the local model returns unparseable JSON, the pipeline catches the error and marks the candidate `UNRESOLVED` rather than halting.

---

## 8. Benchmark Evaluation Mapping

The architecture directly satisfies the four mandatory evaluation scenarios defined in the project specification:

| Benchmark Case | Evaluator Scenario | Expected Architecture Path | Resulting Artifact |
|---|---|---|---|
| **Case 1: Corroboration** | Identical Q3 revenues reported in Press Release and Annual 10-K. | Path A: PyMuPDF/pdfplumber extract -> Decimal normalizer confirms exact equality -> Direct Python policy fires. | `DecisionCard` marked `CORROBORATED` (Strength: HIGH) with dual chunk bounding box citations. |
| **Case 2: Direct Contradiction** | Investor deck claims FY2024 Revenue was $120M; Audited 10-K reports $98M with no explanatory footnotes. | Path C: Fact Grouping matches entity and period -> Numerical variance exceeds 0.01% -> Hypothesis tournament tests restatement/scope -> All fail -> Adversarial skeptic confirms contradiction. | `DecisionCard` marked `CONTRADICTION` (Strength: HIGH); highlighted in `contradiction_report.md`. |
| **Case 3: Defensible Reconciliation** | Press Release reports Q3 Operating Income of $45M; 10-Q reports $38M. Footnote details $7M stock compensation exclusion in Non-GAAP figure. | Path B/C: Context Resolver detects GAAP vs Non-GAAP -> AccountingBasisValidator locates reconciliation table -> Proposer builds bridge -> Skeptic confirms bridge matches $7M delta exactly. | `DecisionCard` marked `RECONCILED` (Strength: HIGH) with explicit citation of Note 3 footnote bounding box. |
| **Case 4: Defensive Failure Handling** | Document contains missing footnote, truncated page, or ambiguous OCR scan. | Extract-Then-Verify flags claim as `AMBIGUOUS` or `UNENTAILED` -> Policy engine triggers fail-safe default. | `DecisionCard` marked `UNRESOLVED` (Strength: INSUFFICIENT); fully diagnosed in `unresolved_report.md`. |
