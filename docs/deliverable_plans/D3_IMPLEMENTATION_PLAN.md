# EVIDRA: Evidence-Driven Architecture for Fact Validation and Knowledge Reasoning

## Deliverable 3 (D3) Implementation Plan: Verification, Context, and Normalization Layer

---

## 1. Executive Overview and Epistemic Objective

Deliverable 3 (**D3**) implements the epistemic verification, semantic context resolution, and deterministic normalization tier of **EVIDRA** (Layer 2b). 

While Deliverable 2 harvested raw spatial evidence chunks and candidate observations, raw observations alone cannot be compared or reconciled due to four fundamental financial reporting hurdles:
1. **Hallucination Risk:** LLM extractors can occasionally introduce ungrounded claims or hallucinated figures. D3 implements an adversarial, isolated **Evidence Verifier Agent** that evaluates entailment strictly against the cited source chunk without broader conversational context.
2. **Contextual Asymmetry:** Two conflicting numbers for "Revenue" often describe different accounting scopes (e.g. *Consolidated* vs *Standalone*), distinct accounting bases (*GAAP* vs *Non-GAAP/Adjusted*), or different document versions (*Initial Filing* vs *Restated Prospectus*). D3 introduces a **Context Resolver Agent** that extracts these four essential dimensions.
3. **Representational Discrepancies:** Financial reports mix western scales (Millions, Billions) and Indian numbering systems (Crores, Lakhs), raw string formats (`(1,234.50)` vs `-1234.5`), and heterogeneous temporal expressions (`FY22`, `Twelve months ended March 31, 2022`, `Q3 FY21`). D3 implements **Pure Python Deterministic Normalizers** using exact `Decimal` arithmetic and ISO 8601 calendar intervals. Standard IEEE 754 floating-point arithmetic is strictly prohibited.
4. **Fact Grouping via Two-Tier Blocking:** To detect contradictions without quadratic $O(N^2)$ cross-comparisons, D3 implements a two-tier candidate blocking engine combining exact entity-temporal interval intersection (Hard Blocking) with semantic embedding similarity (Soft Matching via `BAAI/bge-small-en-v1.5` at cosine threshold $\ge 0.82$) to construct candidate `FactGroup` clusters.

---

## 2. Scope and Boundaries of Deliverable 3

### 2.1 In-Scope Deliverables
* **D3.1: Independent Evidence Verifier Agent:**
  * `src/verification/verifier.py`: Adversarial single-chunk verification assigning provenance status `ENTAILED`, `HALLUCINATED`, or `AMBIGUOUS`.
  * Automatic exclusion of `HALLUCINATED` claims from downstream reconciliation.
* **D3.2: Context Resolver Agent:**
  * `src/verification/context.py`: Multi-dimensional qualifier resolution tagging Accounting Basis (`GAAP`, `NON_GAAP`, `IFRS`), Organizational Scope (`CONSOLIDATED`, `STANDALONE`, `SEGMENT`), Filing Type (`ANNUAL_REPORT`, `PROSPECTUS`, `PRESS_RELEASE`), and Restatement Status (`INITIAL`, `RESTATED`, `AMENDED`).
* **D3.3: Pure Python Deterministic Normalizers:**
  * `src/verification/normalizers.py`:
    * `DecimalNormalizer`: String-to-Decimal conversion, bracketed negative handling, and magnitude scaling (`Crore` -> $10^7$, `Lakh` -> $10^5$, `Million` -> $10^6$, `Billion` -> $10^9$, `Thousand` -> $10^3$).
    * `CurrencyNormalizer`: ISO 4217 currency standardization (`INR`, `USD`, `EUR`, `GBP`). Currency conversion without explicit source exchange rates is prohibited.
    * `TemporalNormalizer`: Fiscal calendar parser mapping `FY22`, `Q3 FY21`, `Nine months ended Dec 31, 2021` to ISO 8601 date ranges `(period_start, period_end)`.
* **D3.4: Candidate Fact Grouping & Blocking Engine:**
  * `src/matching/embeddings.py`:
    * Hard blocking on exact entity and temporal interval overlap.
    * Soft semantic matching using local SentenceTransformers (`BAAI/bge-small-en-v1.5`) with cosine similarity threshold $\ge 0.82$.
    * Population of `fact_candidates`, `fact_groups`, and `group_members` in the SQLite Evidence Ledger.
* **D3.5: Pipeline Integration & CLI/API Updates:**
  * Integration into `src/extraction/pipeline.py` (or `src/verification/pipeline.py`), CLI `process` command, and API background tasks.
* **D3.6: Automated & Manual Test Suites:**
  * Unit tests for decimal units across Indian/Western numbering (`tests/unit/test_decimal_units.py`).
  * Unit tests for temporal interval normalization (`tests/unit/test_temporal_parsing.py`).
  * Unit tests for adversarial hallucination rejection and embedding blocking (`tests/unit/test_verification.py`).

### 2.2 Out-of-Scope (Deferred to D4 & D5)
* LangGraph decision state machine and adversarial debate agents (Deferred to D4: `src/decision/`).
* Hypothesis formation, mathematical tolerance reconciliation, and final 4-verdict issuance (Deferred to D4: `src/decision/engine.py`).
* Multi-document synthesis reports and contradiction markdown export (Deferred to D5: `src/reporting/`).

---

## 3. Requirements Coverage (SRS & NFR Mapping)

### 3.1 Functional Requirements (FR)
| SRS ID | Requirement Statement | D3 Implementation Mechanism |
|---|---|---|
| **VER-ENT-01** | Adversarial verification: Evaluate observations against source chunk text; assign `ENTAILED`, `HALLUCINATED`, `AMBIGUOUS`. | `EvidenceVerifierAgent` in `src/verification/verifier.py`. |
| **VER-CTX-01** | Disambiguate multidimensional qualifiers: accounting basis, organizational scope, filing type, restatement status. | `ContextResolverAgent` in `src/verification/context.py`. |
| **NORM-NUM-01** | Convert raw numbers to exact Python `Decimal` objects with magnitude expansion (Crores, Lakhs, Millions, Billions). | `DecimalNormalizer` in `src/verification/normalizers.py`. |
| **NORM-NUM-02** | Prohibit floating-point representations; preserve exact precision without roundoff drift. | Direct instantiation of `decimal.Decimal` with string representations. |
| **NORM-CUR-01** | Normalize currency codes to ISO 4217; disallow unauthorized cross-currency conversions. | `CurrencyNormalizer` in `src/verification/normalizers.py`. |
| **NORM-DAT-01** | Map fiscal periods, quarters, and point-in-time dates to ISO 8601 calendar intervals `(period_start, period_end)`. | `TemporalNormalizer` in `src/verification/normalizers.py`. |
| **GRP-BLK-01** | Two-tier blocking: Filter by exact entity & temporal interval; cluster attributes with cosine similarity $\ge 0.82$. | `FactGroupEngine` in `src/matching/embeddings.py` using `BAAI/bge-small-en-v1.5`. |
| **OBS-REP-04** | Persist verified facts in `fact_candidates`, `fact_groups`, and `group_members` in SQLite ledger. | `EvidenceLedger.insert_fact_candidates()` and `EvidenceLedger.create_fact_group()`. |

### 3.2 Non-Functional Requirements (NFR)
| NFR ID | Requirement Statement | D3 Implementation Mechanism |
|---|---|---|
| **NFR-DET-01** | Mathematical and Arithmetic Determinism: Zero floating-point roundoff; 100% truth-table coverage for units. | `decimal.Decimal` arithmetic; exhaustive unit test suite for number formats. |
| **NFR-REL-01** | Local-First Zero Cloud Execution: Local sentence-transformer embeddings and Ollama verifiers. | Cached `BAAI/bge-small-en-v1.5` and local `qwen2.5:3b`. |
| **NFR-PERF-01** | Sub-quadratic Clustering: Prevent $O(N^2)$ candidate comparisons across thousands of facts. | Hard blocking on entity and temporal interval before executing embedding similarity. |
| **NFR-SEC-02** | SQL Parameterization: All candidate and group records inserted via parameterized queries. | Standardized `EvidenceLedger` transaction methods. |

---

## 4. Architecture and Pipeline Flow

### 4.1 Layer 2b Verification & Normalization Pipeline

```
+-------------------------------------------------------------------------------+
|                       RAW OBSERVATIONS (from Layer 2a)                        |
|        (Recorded in SQLite observations table with source chunk_id)           |
+-------------------------------------------------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|                STAGE 1: ADVERSARIAL EVIDENCE VERIFICATION                     |
|                                                                               |
|   EvidenceVerifierAgent:                                                      |
|   - Input: Observation.statement + raw cited EvidenceChunk.content            |
|   - Adversarial prompt: Does chunk strictly support statement?                |
|   - Provenance Verdict: ENTAILED | HALLUCINATED | AMBIGUOUS                   |
|   - If HALLUCINATED: Flag in ledger, emit telemetry, EXCLUDE from downstream   |
+-------------------------------------------------------------------------------+
                                        | (ENTAILED / AMBIGUOUS)
                                        v
+-------------------------------------------------------------------------------+
|                   STAGE 2: CONTEXT RESOLUTION QUALIFIERS                      |
|                                                                               |
|   ContextResolverAgent:                                                       |
|   - Accounting Basis:    GAAP | NON_GAAP | IFRS | UNKNOWN                     |
|   - Org Scope:           CONSOLIDATED | STANDALONE | SEGMENT                  |
|   - Filing Type:         ANNUAL_REPORT | PROSPECTUS | PRESS_RELEASE           |
|   - Version/Restatement: INITIAL | RESTATED | AMENDED                         |
+-------------------------------------------------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|                 STAGE 3: PURE PYTHON DETERMINISTIC NORMALIZERS                |
|                                                                               |
|   +--------------------------+  +-------------------+  +-------------------+  |
|   |    DecimalNormalizer     |  | CurrencyNormalizer|  | TemporalNormalizer|  |
|   | - Parse '(1,234.5)'      |  | - INR / Rs / ₹    |  | - FY22 ->         |  |
|   | - Lakh:  * 10^5          |  |   -> 'INR'        |  |   2021-04-01 to   |  |
|   | - Crore: * 10^7          |  | - USD / $ -> 'USD'|  |   2022-03-31      |  |
|   | - Exact decimal.Decimal  |  | - No FX conversion|  | - ISO 8601 bounds |  |
|   +--------------------------+  +-------------------+  +-------------------+  |
|                                       |                                       |
|                                       v                                       |
|                  +-----------------------------------------+                  |
|                  |       FactCandidate Construction        |                  |
|                  |   - fact_id: "FCT-{uuid[:8]}"           |                  |
|                  |   - normalized_value (Decimal string)   |                  |
|                  |   - normalized_unit / currency          |                  |
|                  |   - period_start / period_end (ISO)     |                  |
|                  |   - Insert into fact_candidates table   |                  |
|                  +-----------------------------------------+                  |
+-------------------------------------------------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|               STAGE 4: TWO-TIER CANDIDATE GROUPING & BLOCKING                 |
|                                                                               |
|   1. Hard Blocking Tier:                                                      |
|      - Group by: entity + temporal interval overlap (period_start, period_end)|
|                                                                               |
|   2. Soft Semantic Clustering Tier:                                           |
|      - Local Embedding: BAAI/bge-small-en-v1.5                                |
|      - Cosine similarity on attribute text >= 0.82                            |
|      - e.g., "Revenue from operations" <-> "Operating Revenue" (Sim: 0.93)    |
|                                                                               |
|   3. FactGroup Persistence:                                                   |
|      - group_id: "GRP-{entity_slug}-{attr_slug}-{period_slug}"                |
|      - Insert into fact_groups and group_members tables                       |
+-------------------------------------------------------------------------------+
```

---

## 5. Software Architecture of D3 Components

### 5.1 Evidence Verifier Agent (`src/verification/verifier.py`)

Adversarial evaluation preventing hallucinated claims from polluting facts:

```python
class VerificationVerdict(BaseModel):
    status: Literal["ENTAILED", "HALLUCINATED", "AMBIGUOUS"]
    confidence: float = Field(ge=0.0, le=1.0)
    explanation: str

class EvidenceVerifierAgent:
    def __init__(self, reasoning_service: ReasoningService):
        self.llm = reasoning_service

    def verify_observation(
        self,
        statement: str,
        chunk_content: str,
    ) -> VerificationVerdict:
        """Evaluate whether statement is strictly entailed by source chunk."""
```

#### Adversarial Prompt Strategy
The verifier receives ONLY the observation's text statement and the exact evidence chunk content. The prompt explicitly instructs:
- If the statement asserts a figure, company name, or date not present in the chunk, return `HALLUCINATED`.
- If the statement is completely supported by the text, return `ENTAILED`.
- If the chunk is ambiguous, truncated, or lacks sufficient context, return `AMBIGUOUS`.

---

### 5.2 Context Resolver Agent (`src/verification/context.py`)

Captures the multidimensional qualifications of financial statements:

```python
class FinancialContext(BaseModel):
    accounting_basis: Literal["GAAP", "NON_GAAP", "IFRS", "UNKNOWN"] = "UNKNOWN"
    organizational_scope: Literal["CONSOLIDATED", "STANDALONE", "SEGMENT", "UNKNOWN"] = "UNKNOWN"
    filing_type: Literal["ANNUAL_REPORT", "PROSPECTUS", "QUARTERLY_REPORT", "PRESS_RELEASE", "UNKNOWN"] = "UNKNOWN"
    version_status: Literal["INITIAL", "RESTATED", "AMENDED", "UNKNOWN"] = "INITIAL"
    segment_name: Optional[str] = None
    notes: Optional[str] = None

class ContextResolverAgent:
    def __init__(self, reasoning_service: ReasoningService):
        self.llm = reasoning_service

    def resolve_context(
        self,
        statement: str,
        chunk_content: str,
        document_filename: str,
    ) -> FinancialContext:
        """Extract dimensional qualifiers from observation context and document metadata."""
```

---

### 5.3 Deterministic Normalizers (`src/verification/normalizers.py`)

Pure Python deterministic algorithms using `decimal.Decimal` and `python-dateutil`:

#### `DecimalNormalizer`
Converts heterogeneous raw string values into standardized `Decimal` magnitude values:
- Number systems supported:
  - **Indian:** Lakh ($10^5$), Crore ($10^7$), Arab ($10^9$).
  - **Western:** Thousand ($10^3$), Million ($10^6$), Billion ($10^9$), Trillion ($10^{12}$).
- Bracket parsing: `"(4,810.50)"` -> `Decimal("-4810.50")`.
- Percentage parsing: `"12.4%"` -> `Decimal("12.4")`, unit: `"PERCENT"`.
- Comma sanitization: `"6,882.29"` -> `Decimal("6882.29")`.
- Exact multiplication: e.g. `raw_value="4,810.50"`, `unit="Crores"` -> `Decimal("48105000000.00")`.

#### `CurrencyNormalizer`
- Standardizes: `₹`, `Rs`, `INR`, `Rs.` -> `"INR"`.
- Standardizes: `$`, `USD`, `US$` -> `"USD"`.
- Standardizes: `€`, `EUR` -> `"EUR"`.
- Standardizes: `£`, `GBP` -> `"GBP"`.
- Empty / non-monetary -> `""`.

#### `TemporalNormalizer`
Maps human financial reporting periods to ISO 8601 calendar bounds `(period_start, period_end)`:
- Indian Fiscal Year (April 1 - March 31):
  - `FY22` / `Fiscal 2022` / `FY 2021-22` -> `("2021-04-01", "2022-03-31")`.
  - `Q1 FY22` -> `("2021-04-01", "2021-06-30")`.
  - `Q2 FY22` -> `("2021-07-01", "2021-09-30")`.
  - `Q3 FY22` -> `("2021-10-01", "2021-12-31")`.
  - `Q4 FY22` -> `("2022-01-01", "2022-03-31")`.
  - `Nine months ended Dec 31, 2021` -> `("2021-04-01", "2021-12-31")`.
- Calendar Fiscal Year (Jan 1 - Dec 31):
  - `FY2022` (calendar) -> `("2022-01-01", "2022-12-31")`.
- Exact Point-in-Time:
  - `March 31, 2022` / `As of March 31, 2022` -> `("2022-03-31", "2022-03-31")`.

---

### 5.4 Two-Tier Candidate Grouping & Blocking Engine (`src/matching/embeddings.py`)

Clusters normalized `FactCandidate` records into dispute clusters (`FactGroup`):

```python
class FactGroupEngine:
    def __init__(
        self,
        embedding_model_name: str = "BAAI/bge-small-en-v1.5",
        similarity_threshold: float = 0.82,
    ):
        self.model_name = embedding_model_name
        self.similarity_threshold = similarity_threshold
        self._model = None

    @property
    def model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def group_candidates(
        self,
        candidates: list[FactCandidateRecord],
    ) -> list[tuple[FactGroupRecord, list[str]]]:
        """Group candidates by hard temporal/entity match, then soft semantic cosine similarity."""
```

#### Grouping Logic
1. **Tier 1 (Hard Blocking Key):**
   Group key: `(entity.lower().strip(), period_start, period_end)`.
   Facts for different companies or completely non-overlapping periods can never be grouped into the same candidate fact dispute.
2. **Tier 2 (Soft Semantic Clustering):**
   Within each hard block, encode all candidate `attribute` strings into 384-dimensional embeddings using `BAAI/bge-small-en-v1.5`.
   Compute pairwise cosine similarity matrix.
   Attributes with similarity $\ge 0.82$ (e.g. `"Revenue from operations"` and `"Operating Revenue"`) are assigned to the same `FactGroup`.
3. **Database Insertion:**
   Inserts `fact_groups` and records mappings in `group_members`.

---

## 6. Detailed Implementation Steps

```
+--------------------------------------------------------------------+
|                      D3 IMPLEMENTATION ROADMAP                     |
+--------------------------------------------------------------------+
|  Phase 1: Deterministic Normalizers                                |
|  - Implement src/verification/normalizers.py                       |
|  - Exact Decimal scaling (Crores, Lakhs, Millions, Billions)       |
|  - ISO currency & temporal interval parsers (FY, Quarters)         |
|  - Unit tests: tests/unit/test_decimal_units.py                    |
|  - Unit tests: tests/unit/test_temporal_parsing.py                 |
|                                                                    |
|  Phase 2: Independent Evidence Verifier Agent                      |
|  - Implement src/verification/verifier.py                          |
|  - Adversarial single-chunk entailment prompt                      |
|  - Unit tests: tests/unit/test_verifier.py                         |
|                                                                    |
|  Phase 3: Context Resolver Agent                                   |
|  - Implement src/verification/context.py                           |
|  - Qualifier taxonomy (GAAP, Scope, Filing, Version)               |
|  - Unit tests: tests/unit/test_context.py                          |
|                                                                    |
|  Phase 4: Two-Tier Candidate Grouping Engine                       |
|  - Implement src/matching/embeddings.py                            |
|  - Hard blocking + BAAI/bge-small-en-v1.5 semantic clustering     |
|  - Unit tests: tests/unit/test_grouping.py                         |
|                                                                    |
|  Phase 5: Pipeline & Ledger Integration                            |
|  - Implement src/verification/pipeline.py                          |
|  - Wire verification, normalization, & grouping into CLI process   |
|  - Update src/db/ledger.py with batch methods for candidates/groups|
|                                                                    |
|  Phase 6: Real-World Prospectus Verification & Sign-Off            |
|  - Run full pipeline on sample_docs/01-delhivery-prospectus-2022   |
|  - Verify fact_candidates, fact_groups, and group_members populated|
|  - Create docs/deliverable_plans/D3_TESTING_AND_VERIFICATION_PLAN  |
+--------------------------------------------------------------------+
```

---

## 7. Verification and Testing Strategy

### 7.1 Automated Unit and Contract Test Suites

1. **`tests/unit/test_decimal_units.py`**:
   - `test_indian_system_crores_lakhs`: Verifies `INR 4,810.50 Crores` converts to `Decimal("48105000000.00")` and `25 Lakhs` converts to `Decimal("2500000")`.
   - `test_western_system_millions_billions`: Verifies `6,882.29 million` converts to `Decimal("6882290000.00")`.
   - `test_bracketed_negatives`: Verifies `(45.2)` parses to `Decimal("-45.2")`.
   - `test_zero_float_drift`: Confirms no floating point inaccuracies (`Decimal("0.1") + Decimal("0.2") == Decimal("0.3")`).

2. **`tests/unit/test_temporal_parsing.py`**:
   - `test_fiscal_year_interval`: Verifies `FY22` maps to `2021-04-01` to `2022-03-31`.
   - `test_quarterly_intervals`: Verifies `Q1 FY22`, `Q2 FY22`, `Q3 FY22`, `Q4 FY22`.
   - `test_nine_month_period`: Verifies `Nine months ended Dec 31, 2021`.
   - `test_point_in_time`: Verifies `As of March 31, 2022`.

3. **`tests/unit/test_verifier.py`**:
   - `test_verifier_entailed_claim`: Asserts truthful statement evaluates to `ENTAILED`.
   - `test_verifier_hallucinated_claim`: Asserts statement claiming false number (e.g. $99,000 when chunk says $500) evaluates to `HALLUCINATED`.
   - `test_verifier_ambiguous_claim`: Asserts statement without sufficient text context evaluates to `AMBIGUOUS`.

4. **`tests/unit/test_grouping.py`**:
   - `test_hard_blocking_filters_disjoint_periods`: Verifies facts with non-overlapping fiscal years are never grouped together.
   - `test_semantic_clustering_unifies_synonyms`: Verifies `"Revenue from operations"` and `"Operating Revenue"` for the same period cluster into the same `FactGroup`.

---

### 7.2 Real-World Document Verification

* **Test Document:** [sample_docs/01-delhivery-prospectus-2022-excerpt.pdf](file:///d:/projects/superjoin/EVIDRA/sample_docs/01-delhivery-prospectus-2022-excerpt.pdf).
* **Execution Command:**
  ```powershell
  python -m src.cli.main process sample_docs/01-delhivery-prospectus-2022-excerpt.pdf --max-chunks 5
  ```
* **Pass Criteria:**
  - `Evidence Chunks: > 0`
  - `Observations: > 0`
  - `Fact Candidates: > 0` (Normalized into exact `Decimal` strings and ISO periods in `fact_candidates`).
  - `Fact Groups: > 0` (Grouped into `fact_groups` and mapped in `group_members`).

---

## 8. Acceptance Criteria and Sign-off Checklist

- [ ] `DecimalNormalizer` accurately parses Indian (Crore/Lakh) and Western (Million/Billion) number strings with zero float roundoff.
- [ ] `TemporalNormalizer` reliably maps fiscal years and quarters to ISO 8601 calendar bounds.
- [ ] `CurrencyNormalizer` standardizes currency representations to ISO 4217.
- [ ] `EvidenceVerifierAgent` correctly detects and flags synthetic hallucinated figures.
- [ ] `ContextResolverAgent` categorizes accounting basis, organizational scope, and filing type.
- [ ] `FactGroupEngine` clusters synonymous attributes with similarity $\ge 0.82$ without grouping different periods or entities.
- [ ] `fact_candidates`, `fact_groups`, and `group_members` tables are populated in SQLite `ledger.db`.
- [ ] All automated tests pass with a 100% pass rate (`pytest tests/ -v`).
- [ ] Real-world filing `01-delhivery-prospectus-2022-excerpt.pdf` produces verified fact candidates and candidate fact groups.
