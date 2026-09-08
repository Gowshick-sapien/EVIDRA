# EVIDRA 2.0: Deliverable Phase P0 Implementation Plan: Upstream Extraction Foundation

> **Parent Specification:** [docs/DELIVERABLES_DEFINITION_V2.md](file:///d:/projects/superjoin/EVIDRA/docs/DELIVERABLES_DEFINITION_V2.md)  
> **Architecture Reference:** [docs/ARCHITECTURE_V2.md](file:///d:/projects/superjoin/EVIDRA/docs/ARCHITECTURE_V2.md)  
> **SRS Reference:** [docs/SRS_V2.md](file:///d:/projects/superjoin/EVIDRA/docs/SRS_V2.md)  
> **Status:** Ready for Implementation (Development Branch: `dev_v2`)  
> **Deliverable Phase:** P0 (Make Extraction Trustworthy)  

---

## 1. Executive Overview and Epistemic Objective

Deliverable Phase P0 implements the **Upstream Extraction Foundation** of EVIDRA 2.0. Empirical analysis of the V1 pipeline proved that **reasoning cannot compensate for corrupted or context-starved facts**:

```text
V1 Bottleneck Flow:
  6,553 Parsed Chunks 
       | (Rigid global cap: max_llm_chunks = 2)
       v
  37 Observations (0.56% yield; isolated chunks stripped of headers and units)
       |
       v
  20 Fact Groups (Conflated distinct metrics into false-positive contradictions)
```

In accordance with EVIDRA 2.0's governing principle:
> **Never ask the reasoning model to reconstruct document structure that the parser already knows.**

Phase P0 moves intelligence upstream. It guarantees that raw PDF chunks are enriched into context-complete **Evidence Windows**, layout hierarchies are inferred with explicit confidence scores, financial schemas and metric families are dynamically induced from document text, and extraction budgets are allocated proportionally across all ingested documents.

---

## 2. Requirements Coverage (SRS V2 Mapping)

The following table maps the specific Software Requirements Specification (SRS V2) requirements satisfied by Deliverable Phase P0:

| Requirement ID | Requirement Statement | P0 Implementation Mechanism | Target Module |
| :--- | :--- | :--- | :--- |
| **REQ-DOC-EXT-01** | Multi-signal layout hierarchy classification with confidence scores ($C \in [0.0, 1.0]$). | `DocumentTopologyBuilder` evaluating Z-score font size, style flags, margins, repetition, and table proximity. | `src/pdf/topology.py` |
| **REQ-DOC-EXT-02** | Context-enriched Evidence Window construction with inherited units, currency, and headers. | `EvidenceWindowBuilder` binding table headers, section titles, stated units (`lakhs`, `crore`), and column dates. | `src/extraction/windows.py` |
| **REQ-DOC-EXT-03** | 3-tier budget-aware candidate discovery enforcing per-document quotas (budget=30). | Replace global `max_llm_chunks=2` with 3-tier discovery: structural table filter, relevance scoring, per-doc quota. | `src/extraction/pipeline.py` |
| **REQ-SCH-EXT-01** | Document-derived schema induction discovering metric families and subtypes dynamically. | `SchemaInductionEngine` discovering primary legal entities, Metric Families (`REVENUE`, `PROFITABILITY`), and Subtypes. | `src/extraction/schema_induction.py` |
| **REQ-EXT-EXT-01** | Structural prompt envelope ingestion formatting section, table, and unit headers. | `ExtractionAgent` prompt rewriting to present `EvidenceWindow` metadata headers. | `src/extraction/agents.py` |
| **REQ-VER-EXT-01** | Anti-generic entity filtering and verbatim raw value substring verification. | Post-extraction validation rejecting generic placeholders (`Reporting Entity`, `Company`) and unentailed values. | `src/extraction/agents.py` |
| **REQ-LEDG-EXT-01** | Additive schema migrations and ledger persistence for Evidence Windows. | Database table `evidence_windows` and dataclass `EvidenceWindowRecord`. | `src/db/schema.sql`<br>`src/db/ledger.py` |

---

## 3. Scope and Architectural Deliverables

Phase P0 delivers three core functional deliverables and one infrastructure migration:

### D-P0.0: Evidence Windows Schema and Ledger Migration
- Additive SQL migration in `src/db/schema.sql` creating the `evidence_windows` table.
- Extended dataclass `EvidenceWindowRecord` and CRUD query methods in `src/db/ledger.py`.
- Extended Pydantic schema `EvidenceWindow` in `src/extraction/schemas.py`.

### D-P0.1: Budget-Aware Evidence Candidate Discovery
- Elimination of the global `max_llm_chunks=2` choke point in `src/extraction/pipeline.py`.
- Implementation of 3-tier discovery:
  - **Tier 1 (Structural Filter):** 100% of detected tables preserved; boilerplate and fragments < 50 characters excluded.
  - **Tier 2 (Deterministic Relevance):** Surviving text chunks scored by keyword density, numerical tokens, and section relevance.
  - **Tier 3 (Per-Document Allocation):** Configurable quota (default: 30 chunks per document), prioritizing tables and filling remaining slots with top text blocks.

### D-P0.2: Multi-Signal Layout Hierarchy & Evidence Windows
- Implementation of `src/pdf/topology.py` generating in-memory `PageTopology` and `SectionNode` layout trees during single-pass PyMuPDF parsing.
- Multi-signal classification evaluating Z-score font size, style flags, margins, page repetition, whitespace, and table proximity with confidence scores ($C \in [0.0, 1.0]$).
- Implementation of `src/extraction/windows.py` constructing `EvidenceWindow` envelopes wrapping raw chunks:
  - Table grid binding (column headers from row 0, row labels from column 0).
  - Stated unit and currency extraction via deterministic regex (`Rs. in Lakhs`, `in Crore`, `USD Millions`).
  - Section title binding (applied when section confidence $C \ge 0.70$).
  - Temporal binding for column headers via `TemporalNormalizer`.

### D-P0.3: Lightweight Schema Induction Layer & Prompt Hardening
- Implementation of `src/extraction/schema_induction.py` discovering:
  - Legal corporate entities from cover pages, headers, and document manifests.
  - Discovered Metric Families (`REVENUE`, `PROFITABILITY`, `VOLUME`, `EXPENSES`).
  - Metric Subtypes (`OPERATING_REVENUE`, `SERVICE_REVENUE`), preserving verbatim surface strings.
- Refactoring `src/extraction/agents.py`:
  - `ExtractionAgent.extract_from_chunk()` updated to accept `EvidenceWindow`.
  - Prompt envelope formatting with document, section, table, and unit headers.
  - Post-extraction validation rejecting generic placeholders (`Reporting Entity`, `the Company`, `Management`, `Total`).
  - Verbatim raw value substring entailment check.

---

## 4. Detailed Component Specifications

### 4.1 Database Migration & Ledger Data Access

#### SQL Schema Extension (`src/db/schema.sql`)
```sql
-- Additive Table: Evidence Windows (Context Envelopes)
CREATE TABLE IF NOT EXISTS evidence_windows (
    window_id TEXT PRIMARY KEY,
    chunk_id TEXT NOT NULL UNIQUE,
    document_id TEXT NOT NULL,
    page_number INTEGER NOT NULL,
    section_title TEXT DEFAULT '',
    section_confidence REAL DEFAULT 0.0,
    table_caption TEXT DEFAULT '',
    stated_unit TEXT DEFAULT '',
    stated_currency TEXT DEFAULT '',
    column_headers TEXT DEFAULT '[]',   -- JSON array of column strings
    row_context TEXT DEFAULT '',
    page_header TEXT DEFAULT '',
    footnotes TEXT DEFAULT '[]',        -- JSON array of footnote strings
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(chunk_id) REFERENCES evidence_chunks(chunk_id),
    FOREIGN KEY(document_id) REFERENCES documents(document_id)
);

CREATE INDEX IF NOT EXISTS idx_evidence_windows_doc ON evidence_windows(document_id);
CREATE INDEX IF NOT EXISTS idx_evidence_windows_chunk ON evidence_windows(chunk_id);
```

#### Python Dataclass (`src/db/ledger.py`)
```python
@dataclass
class EvidenceWindowRecord:
    window_id: str
    chunk_id: str
    document_id: str
    page_number: int
    section_title: str = ""
    section_confidence: float = 0.0
    table_caption: str = ""
    stated_unit: str = ""
    stated_currency: str = ""
    column_headers: str = "[]"
    row_context: str = ""
    page_header: str = ""
    footnotes: str = "[]"
```

#### Ledger CRUD Methods to Implement in `EvidenceLedger`:
- `insert_evidence_windows(windows: list[EvidenceWindowRecord]) -> int`
- `get_evidence_window(chunk_id: str) -> Optional[EvidenceWindowRecord]`
- `get_windows_for_document(document_id: str) -> list[EvidenceWindowRecord]`

---

### 4.2 Multi-Signal Layout Hierarchy (`src/pdf/topology.py`)

Financial PDFs vary significantly in layout. To prevent brittle failures, layout hierarchy classification combines multiple independent layout signals:

```python
class StructuralRole(str, Enum):
    SECTION_TITLE = "SECTION_TITLE"
    TABLE_CAPTION = "TABLE_CAPTION"
    HEADER = "HEADER"
    FOOTER = "FOOTER"
    FOOTNOTE = "FOOTNOTE"
    BODY = "BODY"

class SectionNode(BaseModel):
    title: str
    title_bbox: list[float]
    font_size: float
    confidence: float
    children_chunk_ids: list[str] = Field(default_factory=list)

class PageTopology(BaseModel):
    page_number: int
    header_text: str = ""
    footer_text: str = ""
    sections: list[SectionNode] = Field(default_factory=list)
```

#### Multi-Signal Scoring Heuristics:
1. **Z-Score Font Size:** Compute mean mu and standard deviation sigma of font sizes across all blocks on the page. If Z = (size - mu) / sigma > 1.5, signal = SECTION_TITLE (+0.35).
2. **Font Style Flags:** Bold font flag (+0.25).
3. **Spatial Position:** Block in top 10% of page height (+0.20 for HEADER); block in bottom 10% (+0.20 for FOOTER).
4. **Repetition Frequency:** Identical or near-identical text appearing across >= 3 pages (+0.30 for HEADER/FOOTER).
5. **Table Caption Proximity:** Text block situated 0 to 25 vertical points directly above a table bounding box (+0.40 for TABLE_CAPTION).
6. **Lexical Patterns:** Regex matching `^(Section|Part|Table|Statement of|Notes to|Schedule)\b` (+0.20).

**Threshold:** Structural role is assigned if cumulative signal score >= 0.60. Confidence is normalized to [0.0, 1.0].

---

### 4.3 Context-Enriched Evidence Windows (`src/extraction/windows.py`)

#### Pydantic Schema (`src/extraction/schemas.py`)
```python
class EvidenceWindow(BaseModel):
    window_id: str
    chunk_id: str
    document_id: str
    page_number: int
    chunk_type: Literal["text", "table", "figure"]
    bounding_box: list[float]
    content: str
    content_hash: str

    section_title: str = ""
    section_confidence: float = 0.0
    table_caption: str = ""
    stated_unit: str = ""           # e.g., "crore", "lakhs", "millions"
    stated_currency: str = ""       # e.g., "INR", "USD"
    column_headers: list[str] = Field(default_factory=list)
    row_context: str = ""
    page_header: str = ""
    footnotes: list[str] = Field(default_factory=list)
```

#### Unit Extraction Regex Patterns:
```python
UNIT_PATTERNS = [
    (re.compile(r"(?:in\s+)?rs\.?\s*(?:in\s+)?crores?", re.IGNORECASE), "crore", "INR"),
    (re.compile(r"(?:in\s+)?rs\.?\s*(?:in\s+)?lakhs?", re.IGNORECASE), "lakh", "INR"),
    (re.compile(r"(?:in\s+)?rs\.?\s*(?:in\s+)?millions?", re.IGNORECASE), "million", "INR"),
    (re.compile(r"(?:in\s+)?(?:in\s+)?usd\s*(?:in\s+)?millions?", re.IGNORECASE), "million", "USD"),
    (re.compile(r"(?:in\s+)?(?:in\s+)?thousands?", re.IGNORECASE), "thousand", ""),
    (re.compile(r"(?:in\s+)?(?:in\s+)?billions?", re.IGNORECASE), "billion", ""),
]
```
The window builder scans table captions, column headers, and the 3 preceding text blocks for unit signatures.

---

### 4.4 3-Tier Budget-Aware Candidate Discovery (`src/extraction/pipeline.py`)

Modifies `ExtractionPipeline.process_document()` to replace the global `max_llm_chunks=2` cap:

```python
def discover_candidates(
    self,
    windows: list[EvidenceWindow],
    per_document_budget: int = 30
) -> list[EvidenceWindow]:
    # Tier 1: Structural Filter
    tables: list[EvidenceWindow] = []
    text_candidates: list[EvidenceWindow] = []
    
    for w in windows:
        if w.chunk_type == "table":
            tables.append(w)
        else:
            content = w.content.strip()
            if len(content) >= 50 and FINANCIAL_INDICATORS.search(content):
                text_candidates.append(w)
                
    # Tier 2: Relevance Scoring
    scored_texts = [(w, self._score_candidate_window(w)) for w in text_candidates]
    scored_texts.sort(key=lambda x: x[1], reverse=True)
    
    # Tier 3: Budget-Aware Allocation
    selected = list(tables)
    remaining_budget = max(0, per_document_budget - len(tables))
    selected.extend([w for w, score in scored_texts[:remaining_budget]])
    
    return selected
```

---

### 4.5 Lightweight Schema Induction Layer (`src/extraction/schema_induction.py`)

The Schema Induction Engine derives the structural vocabulary from the documents themselves:

```python
class MetricSubtype(BaseModel):
    subtype_name: str         # e.g., "OPERATING_REVENUE"
    surface_variants: list[str] # e.g., ["Revenue from Operations", "Revenue from operations"]

class MetricFamily(BaseModel):
    family_name: str          # e.g., "REVENUE"
    subtypes: list[MetricSubtype] = Field(default_factory=list)

class DocumentSchema(BaseModel):
    document_id: str
    primary_entity: str       # e.g., "Delhivery Limited"
    metric_families: list[MetricFamily] = Field(default_factory=list)

class SchemaInductionEngine:
    def induce_schema(
        self,
        document_id: str,
        windows: list[EvidenceWindow],
        manifest_entity: Optional[str] = None
    ) -> DocumentSchema:
        pass
```

#### Induction Protocol:
1. Extract candidate row labels from all table column 0 entries across the document.
2. Group candidate terms by lexical overlap and semantic proximity.
3. Map clusters into broad financial families (`REVENUE`, `PROFITABILITY`, `VOLUME`, `EXPENSES`).
4. Bind specific line item text as `MetricSubtype`, preserving the exact verbatim surface form.

---

### 4.6 ExtractionAgent Hardening (`src/extraction/agents.py`)

#### Envelope Ingestion Prompt:
```python
prompt = f"""DOCUMENT: {window.document_id}
PAGE: {window.page_number}
SECTION: {window.section_title if window.section_confidence >= 0.70 else "N/A"}
TABLE CAPTION: {window.table_caption or "N/A"}
STATED UNITS: {window.stated_unit or "N/A"} {window.stated_currency or ""}
COLUMN HEADERS: {window.column_headers or "N/A"}

CONTENT:
-----------------------------------------
{window.content}
-----------------------------------------

Extract factual numerical and semantic observations.
STRICT RULE: The entity must be the specific legal corporate entity described. Never output 'Reporting Entity', 'the Company', or 'Management'.
"""
```

#### Post-Extraction Quality Validator:
```python
GENERIC_ENTITIES = {
    "reporting entity", "the company", "company", "management",
    "total", "consolidated", "standalone", "group"
}

def validate_observation(obs: NumericalObservation, window: EvidenceWindow) -> bool:
    # 1. Reject generic placeholders
    if obs.entity.strip().lower() in GENERIC_ENTITIES:
        return False
    # 2. Raw value verbatim entailment
    if obs.raw_value not in window.content:
        return False
    # 3. Valid non-epoch temporal parsing
    start, end = TemporalNormalizer.normalize(obs.temporal_scope)
    if start == "1970-01-01" and end == "1970-01-01":
        return False
    return True
```

---

## 5. File Modification Inventory

| File Path | Action | Scope of Changes |
| :--- | :--- | :--- |
| `src/db/schema.sql` | **Modify** | Add `evidence_windows` table DDL and indices. |
| `src/db/ledger.py` | **Modify** | Add `EvidenceWindowRecord` dataclass; add `insert_evidence_windows()`, `get_evidence_window()`, `get_windows_for_document()`. |
| `src/extraction/schemas.py` | **Modify** | Add `EvidenceWindow` Pydantic model. |
| `src/pdf/topology.py` | **Create** | Implement `StructuralRole`, `SectionNode`, `PageTopology`, and `DocumentTopologyBuilder` multi-signal layout classifier. |
| `src/extraction/windows.py` | **Create** | Implement `EvidenceWindowBuilder` with unit regex extraction, table cell mapping, and temporal column binding. |
| `src/extraction/schema_induction.py` | **Create** | Implement `SchemaInductionEngine`, `MetricFamily`, `MetricSubtype`, and `DocumentSchema`. |
| `src/extraction/pipeline.py` | **Modify** | Integrate `DocumentTopologyBuilder`, `EvidenceWindowBuilder`, 3-tier budget candidate discovery, and `SchemaInductionEngine`. |
| `src/extraction/agents.py` | **Modify** | Update `ExtractionAgent` to ingest `EvidenceWindow`; implement post-extraction anti-generic validation. |
| `tests/unit/test_topology.py` | **Create** | Unit tests for multi-signal layout hierarchy classification and confidence scoring. |
| `tests/unit/test_windows.py` | **Create** | Unit tests for `EvidenceWindowBuilder`, unit regex patterns, and table context extraction. |
| `tests/unit/test_schema_induction.py` | **Create** | Unit tests for entity resolution and metric family discovery. |
| `tests/unit/test_p0_pipeline.py` | **Create** | Integration tests verifying 3-tier budget candidate discovery and post-extraction validation. |

---

## 6. Step-by-Step Implementation Sequence

The implementation proceeds in six sequential, test-driven steps:

```text
Step 1: Database & Ledger Extensions
  └── Modify src/db/schema.sql and src/db/ledger.py
  └── Verify with pytest tests/test_d0_d1.py

Step 2: Multi-Signal Layout Topology
  └── Implement src/pdf/topology.py
  └── Verify with tests/unit/test_topology.py

Step 3: Context-Enriched Evidence Windows
  └── Implement src/extraction/windows.py and src/extraction/schemas.py
  └── Verify with tests/unit/test_windows.py

Step 4: Schema Induction Engine
  └── Implement src/extraction/schema_induction.py
  └── Verify with tests/unit/test_schema_induction.py

Step 5: ExtractionAgent Prompt Envelope & Validation
  └── Modify src/extraction/agents.py
  └── Verify anti-generic entity filtering and verbatim entailment checks

Step 6: Pipeline Orchestration & End-to-End Test
  └── Modify src/extraction/pipeline.py with 3-tier budget discovery
  └── Execute end-to-end extraction on sample_docs/ Delhivery PDFs
  └── Verify against Phase P0 acceptance criteria
```

---

## 7. Testing & Verification Plan

### 7.1 Unit Tests
1. **Layout Topology Tests (`tests/unit/test_topology.py`):**
   - Test Z-score font size classification on mock pages.
   - Test header/footer repetitive block detection across 5 pages.
   - Test table caption spatial proximity (< 25 points).
   - Test confidence score outputs are bounded in [0.0, 1.0].
2. **Evidence Window Tests (`tests/unit/test_windows.py`):**
   - Test stated unit extraction across regex variants (`Rs. in Lakhs`, `in Crore`, `USD Millions`).
   - Test table column header extraction and date normalization.
   - Test section title inheritance when confidence >= 0.70.
3. **Schema Induction Tests (`tests/unit/test_schema_induction.py`):**
   - Test primary entity resolution from filing manifests.
   - Test concept discovery from table line items.
   - Test distinct subtype creation (`OPERATING_REVENUE` vs `SERVICE_REVENUE`).
4. **Extraction Validation Tests (`tests/unit/test_p0_pipeline.py`):**
   - Test rejection of `Reporting Entity` and `the Company`.
   - Test rejection of non-verbatim `raw_value`.
   - Test 3-tier candidate discovery preserves 100% of tables and honors per-document quotas.

### 7.2 Real Document Verification (Delhivery Dataset)
- Execute `ExtractionPipeline` across all 3 Delhivery PDF filings:
  - `01-delhivery-prospectus-2022-excerpt.pdf`
  - `02-delhivery-annual-report-2024-excerpt.pdf`
  - `03-delhivery-earnings-presentation-q4fy24.pdf`
- **Acceptance Thresholds:**
  - 100% of detected tables preserved in candidate discovery.
  - Per-document extraction quota strictly honored (<= 30 chunks per document).
  - Observation precision >= 90% on manual sample.
  - Zero observations extracted with entity = `Reporting Entity` or `Company`.
  - Stated units (`lakhs`, `crore`) preserved on all table observations.

---

## 8. Failure Modes, Edge Cases & Mitigations

| Failure Mode / Edge Case | Architectural Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **Multi-page financial tables spanning page breaks** | Headers present only on page 1; subsequent pages lose column titles. | `DocumentTopologyBuilder` carries forward previous page table headers if table continues at `y0 < 50` without title. |
| **Documents with inconsistent font sizes** | Z-score heading detection yields low confidence. | When `section_confidence < 0.70`, section title is suppressed; chunk falls back to page number and table caption. |
| **Missing stated units in table headers** | Table displays raw numbers without unit labels. | Scanner searches footnotes and the 3 preceding narrative text blocks; if none found, explicitly sets `stated_unit = "UNKNOWN"`. |
| **Ollama JSON parsing failure or timeout** | Agent call fails on complex table text. | Existing `OllamaProvider` retry logic (max 3 retries with exponential backoff and defensive JSON repair) catches failure and logs error to trace log without crashing pipeline. |
| **Extracted raw value slightly re-formatted by LLM** | Verbatim substring check fails due to space or comma differences. | Normalize whitespace and commas before substring check, while preserving numeric digits verbatim. |
