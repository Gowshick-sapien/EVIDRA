# EVIDRA: Evidence-Driven Architecture for Fact Validation and Knowledge Reasoning

## Deliverable 2 (D2) Implementation Plan: Document Processing and Extraction Layer

---

## 1. Executive Overview and Epistemic Objective

Deliverable 2 (**D2**) implements the sensory and perceptual tier of **EVIDRA** (Layers 1 and 2a). It transforms raw, unstructured financial PDF documents into cryptographically bound evidence chunks and structured, typed factual observations.

In accordance with EVIDRA's foundational thesis:
1. **Unbroken Spatial Provenance:** Every statement extracted from a document must retain exact physical coordinates (page number and bounding box `[x0, y0, x1, y1]`) indicating its origin on the printed page.
2. **Dual-Engine Layout Disambiguation:** Free narrative text and structured financial tables present fundamentally different structural properties. D2 deploys **PyMuPDF (`fitz`)** for high-precision text block positioning and **`pdfplumber`** for table boundary and cell matrix extraction, using geometric masking to prevent duplicated extractions.
3. **Deterministic Chunk Identification:** Every text fragment and table snapshot is hashed into an immutable `chunk_id` derived from its document, page, coordinates, and content.
4. **Decoupled Local LLM Reasoning Protocol:** Prompts and extraction routines interact with a modular `ReasoningService` abstraction. The underlying implementation targets a local Ollama runtime (`qwen2.5:3b`) running at zero temperature with strict JSON schema enforcement, automatic retry mechanisms, and defensive error trapping.
5. **Epistemic Modesty in Extraction:** Extraction agents must record strictly what is explicitly stated in the source document without speculation, evaluation, or external extrapolation.

---

## 2. Scope and Boundaries of Deliverable 2

### 2.1 In-Scope Deliverables
* **D2.1: Dual-Engine PDF Ingestion:**
  * `src/pdf/tables.py`: Table detection, cell bounding box extraction, and Markdown/matrix serialization via `pdfplumber`.
  * `src/pdf/parser.py`: Text block harvesting, font-size hierarchy detection, coordinate extraction, and table-area masking via `PyMuPDF`.
* **D2.2: Cryptographic Evidence Chunk Generator:**
  * SHA-256 content hashing and deterministic `chunk_id` assignment (`CHK-{sha256[:8]}`).
  * Persistence of evidence chunks into the SQLite `evidence_chunks` table.
* **D2.3: ReasoningService Abstraction & Local LLM Provider:**
  * `src/llm/provider.py`: Protocol definition `ReasoningService` and implementation `OllamaProvider` wrapping local Qwen2.5 with schema enforcement, defensive JSON repair, and maximum 3 retries.
* **D2.4: Domain Extraction Agents:**
  * `src/extraction/agents.py`: Specialized agents for Numerical Metrics (revenue, EBITDA, margins, share counts), Qualitative Disclosures (commentary, risk factors, accounting policies), and Corporate Events (acquisitions, restructuring, board actions).
* **D2.5: End-to-End Extraction Pipeline:**
  * `src/extraction/pipeline.py`: Orchestrator driving PDF parsing, chunk persistence, agent dispatch, observation validation, and telemetry logging into `trace.jsonl`.
* **D2.6: CLI and API Integration:**
  * Integration with CLI `process` to run extraction end-to-end.
  * Integration with API `POST /jobs` to run extraction in asynchronous background workers.
* **D2.7: Comprehensive Test Suite:**
  * Automated unit tests for PDF parsing, table extraction, LLM client, and extraction agents (`tests/unit/test_pdf.py`, `tests/unit/test_llm.py`, `tests/unit/test_extraction.py`).
  * Real-world verification against [sample_docs/01-delhivery-prospectus-2022-excerpt.pdf](file:///d:/projects/superjoin/EVIDRA/sample_docs/01-delhivery-prospectus-2022-excerpt.pdf).

### 2.2 Out-of-Scope (Deferred to D3-D5)
* Numerical unit harmonization, currency conversions, and fiscal calendar alignments (Deferred to D3: `src/verification/normalizers.py`).
* Mathematical reconciliation and balance sheet equation cross-checks (Deferred to D3: `src/verification/rules.py`).
* NLI-based bidirectional claim entailment verification (Deferred to D3: `src/verification/entailment.py`).
* Adversarial debate, hypothesis generation, and LangGraph decision state machine (Deferred to D4: `src/decision/`).
* Multi-document contradiction reports and synthesis (Deferred to D5: `src/reporting/`).

---

## 3. Requirements Coverage (SRS & NFR Mapping)

### 3.1 Functional Requirements (FR)
| SRS ID | Requirement Statement | D2 Implementation Mechanism |
|---|---|---|
| **EXT-PDF-01** | Ingest heterogeneous financial PDFs and extract text blocks with font hierarchy and bounding boxes. | `src/pdf/parser.py` using `PyMuPDF` (`fitz`). |
| **EXT-PDF-02** | Detect multi-column financial tables, extract cell matrices, and maintain cell bounding boxes. | `src/pdf/tables.py` using `pdfplumber`. |
| **EXT-PDF-03** | Geometric disambiguation: Prevent double-extraction of table text by masking table bounding boxes during text block extraction. | `PDFParser._mask_table_regions()` in `src/pdf/parser.py`. |
| **EXT-CHK-01** | Assign deterministic, reproducible `chunk_id` via SHA-256 hash of `(document_id, page_number, bounding_box, content)`. | `EvidenceChunk.compute_chunk_id()` in `src/extraction/schemas.py`. |
| **EXT-LLM-01** | Decouple extraction prompts from LLM runtime via `ReasoningService` protocol supporting local Ollama. | `ReasoningService` protocol and `OllamaProvider` in `src/llm/provider.py`. |
| **EXT-LLM-02** | Enforce strict JSON output with schema validation, defensive repair, and maximum 3 retry attempts. | `OllamaProvider.generate_structured()` with regex repair and Pydantic validation. |
| **EXT-AGT-01** | Numerical Extractor: Harvest balance sheet, P&L, and cash flow metrics with explicit unit, currency, and period tags. | `NumericalExtractionAgent` in `src/extraction/agents.py`. |
| **EXT-AGT-02** | Semantic Extractor: Harvest management commentary, accounting policies, and qualitative guidance. | `SemanticExtractionAgent` in `src/extraction/agents.py`. |
| **EXT-AGT-03** | Event Extractor: Harvest dates, corporate actions, leadership changes, and restructuring events. | `EventExtractionAgent` in `src/extraction/agents.py`. |
| **OBS-REP-03** | Store extracted evidence chunks and observations in the Evidence Ledger with foreign key integrity. | `EvidenceLedger.insert_evidence_chunks()` and `EvidenceLedger.insert_observations()`. |

### 3.2 Non-Functional Requirements (NFR)
| NFR ID | Requirement Statement | D2 Implementation Mechanism |
|---|---|---|
| **NFR-DET-01** | Deterministic Reproducibility: Identical input PDFs must yield identical chunk IDs and extracted structures. | Cryptographic hashing of coordinates and content; LLM invocation with `temperature=0.0`. |
| **NFR-DET-02** | Full Provenance Replay: Every observation must reference an exact `chunk_id` and document coordinate. | `ObservationRecord.chunk_id` foreign key referencing `evidence_chunks.chunk_id`. |
| **NFR-REL-01** | Local-First Zero Cloud Dependency: Operates completely offline with local models. | Direct HTTP interface to local Ollama (`http://127.0.0.1:11434`) without external API keys. |
| **NFR-PERF-02** | Bounded Memory Footprint: Page-by-page streaming processing for large prospectuses (e.g. 50+ pages). | PyMuPDF document iterator releasing page objects sequentially; chunk batching for LLM dispatch. |

---

## 4. Architecture and Pipeline Flow

### 4.1 Ingestion and Extraction Workflow

```
+-------------------------------------------------------------------------------+
|                             RAW FINANCIAL PDF                                 |
|               (e.g., 01-delhivery-prospectus-2022-excerpt.pdf)                |
+-------------------------------------------------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|                       STAGE 1: DUAL-ENGINE PARSER                             |
|                                                                               |
|   +-----------------------------+         +-------------------------------+   |
|   |   pdfplumber Table Engine   |         |    PyMuPDF (fitz) Layout      |   |
|   | - Detect table boundaries   |         | - Extract text blocks         |   |
|   | - Extract row/col matrices  |         | - Extract font sizes/flags    |   |
|   | - Compute table bounding box|         | - Mask out table regions      |   |
|   +-----------------------------+         +-------------------------------+   |
|                  |                                        |                   |
|                  +--------------------+-------------------+                   |
|                                       v                                       |
|                  +-----------------------------------------+                  |
|                  |     Geometric Bounding Box Merger       |                  |
|                  |   - Spatial de-duplication              |                  |
|                  |   - Header/paragraph identification     |                  |
|                  +-----------------------------------------+                  |
+-------------------------------------------------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|                 STAGE 2: CRYPTOGRAPHIC CHUNK SYNTHESIS                        |
|                                                                               |
|   - Compute SHA-256(document_id, page, bounding_box, content)                 |
|   - Assign chunk_id: "CHK-{hex[:8]}"                                          |
|   - Batch insert into SQLite: evidence_chunks table                           |
+-------------------------------------------------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|                     STAGE 3: LOCAL LLM EXTRACTION TIER                        |
|                                                                               |
|   ReasoningService Protocol -> OllamaProvider (qwen2.5:3b @ temp=0.0)         |
|                                                                               |
|   +----------------------+  +----------------------+  +-------------------+   |
|   |  Numerical Extractor |  |  Semantic Extractor  |  |  Event Extractor  |   |
|   | - Metric, value, unit|  | - Commentary, policy |  | - Action, date    |   |
|   | - Currency, period   |  | - Risk disclosure    |  | - Entity involved |   |
|   +----------------------+  +----------------------+  +-------------------+   |
|                  |                     |                        |             |
|                  +---------------------+------------------------+             |
|                                        v                                      |
|                  +-----------------------------------------+                  |
|                  |      Pydantic Schema Validation         |                  |
|                  |    - Defensive JSON repair on parse err |                  |
|                  |    - Max 3 retries on validation fail   |                  |
|                  +-----------------------------------------+                  |
+-------------------------------------------------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|                  STAGE 4: EVIDENCE LEDGER PERSISTENCE                         |
|                                                                               |
|   - Map valid observations to ObservationRecord dataclass                     |
|   - Batch insert into SQLite: observations table                              |
|   - Append telemetry log to runs/JOB-.../traces/trace.jsonl                   |
+-------------------------------------------------------------------------------+
```

---

## 5. Software Architecture of D2 Components

### 5.1 Dual-Engine PDF Ingestion (`src/pdf/tables.py` & `src/pdf/parser.py`)

#### `src/pdf/tables.py`
Extracts tabular structures using `pdfplumber`:

```python
@dataclass(frozen=True)
class TableCell:
    row_index: int
    col_index: int
    text: str
    bounding_box: tuple[float, float, float, float]  # (x0, top, x1, bottom)

@dataclass
class ExtractedTable:
    page_number: int
    bounding_box: tuple[float, float, float, float]  # (x0, top, x1, bottom)
    headers: list[str]
    rows: list[list[str]]
    cells: list[TableCell]
    markdown_representation: str

class TableExtractor:
    def extract_tables_from_page(self, page: pdfplumber.page.Page, page_number: int) -> list[ExtractedTable]:
        """Detect tables, extract cell matrices, and format markdown summary."""
```

#### `src/pdf/parser.py`
Extracts layout text and coordinate geometry using `PyMuPDF (`fitz`)`, masking table regions to prevent duplicate text ingestion:

```python
@dataclass
class ExtractedBlock:
    page_number: int
    block_type: str  # 'text' | 'heading' | 'table'
    bounding_box: tuple[float, float, float, float]  # (x0, y0, x1, y1)
    content: str
    font_size: float = 0.0
    font_name: str = ""
    is_bold: bool = False

class PDFParser:
    def __init__(self, table_extractor: Optional[TableExtractor] = None):
        self.table_extractor = table_extractor or TableExtractor()

    def parse_document(self, pdf_path: Path | str) -> list[ExtractedBlock]:
        """Parse PDF into ordered layout blocks, isolating tables and body text."""
```

#### Table Area Masking Algorithm
When a table bounding box `(tx0, ty0, tx1, ty1)` is identified on page $P$, any raw text block with center point `((bx0 + bx1)/2, (by0 + by1)/2)` falling inside the table's spatial extent is excluded from the text stream, guaranteeing zero duplicate entries.

---

### 5.2 Pydantic Data Schemas (`src/extraction/schemas.py`)

Strict data contracts governing chunk representation and LLM output parsing:

```python
class BoundingBox(BaseModel):
    x0: float
    y0: float
    x1: float
    y1: float

class EvidenceChunk(BaseModel):
    chunk_id: str
    document_id: str
    page_number: int
    chunk_type: Literal["text", "table", "figure"]
    bounding_box: list[float]  # [x0, y0, x1, y1]
    content: str
    content_hash: str

    @classmethod
    def create(cls, document_id: str, page_number: int, chunk_type: str, bbox: list[float], content: str) -> EvidenceChunk:
        raw_key = f"{document_id}:{page_number}:{bbox}:{content}"
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        chunk_id = f"CHK-{hashlib.sha256(raw_key.encode('utf-8')).hexdigest()[:8]}"
        return cls(
            chunk_id=chunk_id,
            document_id=document_id,
            page_number=page_number,
            chunk_type=chunk_type,
            bounding_box=bbox,
            content=content,
            content_hash=content_hash,
        )

class NumericalObservation(BaseModel):
    statement: str = Field(description="Exact statement or claim from document")
    entity: str = Field(description="Company, subsidiary, segment, or reporting entity")
    attribute: str = Field(description="Financial metric (e.g., Revenue, EBITDA, PAT, EPS)")
    raw_value: str = Field(description="Exact numerical value as written (e.g. 5,000.50, (12.3)%)")
    unit: str = Field(default="", description="Stated unit (e.g. Millions, Crores, Thousands, Percent)")
    currency: str = Field(default="", description="Currency code (e.g. INR, USD, EUR) or empty if non-monetary")
    temporal_scope: str = Field(description="Fiscal period or point-in-time date (e.g. FY22, Q3 FY21, March 31, 2022)")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)

class SemanticObservation(BaseModel):
    statement: str
    entity: str
    attribute: str  # e.g., "Risk Factor", "Accounting Policy", "Management Commentary"
    raw_value: str
    temporal_scope: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)

class EventObservation(BaseModel):
    statement: str
    entity: str
    attribute: str  # e.g., "Acquisition", "Restructuring", "Dividend Declaration"
    raw_value: str
    temporal_scope: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)

class ObservationBundle(BaseModel):
    numerical_observations: list[NumericalObservation] = Field(default_factory=list)
    semantic_observations: list[SemanticObservation] = Field(default_factory=list)
    event_observations: list[EventObservation] = Field(default_factory=list)
```

---

### 5.3 ReasoningService Abstraction & Local LLM Provider (`src/llm/provider.py`)

Decouples agent logic from specific inference providers:

```python
class ReasoningService(Protocol):
    def generate_structured(
        self,
        prompt: str,
        response_model: type[T],
        system_prompt: Optional[str] = None,
        max_retries: int = 3,
    ) -> T:
        ...

class OllamaProvider:
    def __init__(self, base_url: str = "http://127.0.0.1:11434", model_name: str = "qwen2.5:3b", timeout_seconds: int = 60):
        self.base_url = base_url.rstrip("/")
        self.model_name = model_name
        self.timeout_seconds = timeout_seconds

    def generate_structured(
        self,
        prompt: str,
        response_model: type[T],
        system_prompt: Optional[str] = None,
        max_retries: int = 3,
    ) -> T:
        """Send request to Ollama with format='json', repair common JSON errors, and validate against response_model."""
```

#### JSON Defense & Repair Strategy
1. **Direct JSON Extraction:** Isolate JSON payloads inside markdown code fences (```` ```json ... ``` ````) or outermost `{ ... }`.
2. **Defensive Parsing:** Clean unescaped newlines and trailing commas.
3. **Pydantic Validation:** Instantiate `response_model.model_validate(json_data)`.
4. **Retry Loop with Feedback:** If Pydantic raises `ValidationError`, re-prompt Ollama feeding back the exact validation error message up to 3 times before raising a controlled exception.

---

### 5.4 Domain Extraction Agents (`src/extraction/agents.py`)

Specialized extractors driven by domain prompts:

```python
class ExtractionAgent:
    def __init__(self, reasoning_service: ReasoningService):
        self.llm = reasoning_service

    def extract_from_chunk(self, chunk: EvidenceChunk) -> ObservationBundle:
        """Analyze a text or table chunk and extract all valid factual observations."""
```

#### Extraction Prompt Architecture
* **System Prompt:** Instructs the LLM that it is a financial document reasoning engine. Strict instructions:
  - Do not calculate or derive unstated values.
  - Preserve exact numerical strings including brackets for negatives (e.g. `(45.2)`).
  - Extract exact stated units and currency denominators (e.g. `in millions`, `INR Lakhs`).
  - Output strictly conforming JSON according to the schema.
* **Input Context:** Injects chunk type (`text` vs `table`), page number, and chunk content.

---

### 5.5 End-to-End Extraction Pipeline (`src/extraction/pipeline.py`)

Coordinates ingestion, parsing, chunk generation, LLM extraction, and ledger persistence:

```python
class ExtractionPipeline:
    def __init__(self, ledger: EvidenceLedger, tracer: Optional[TraceLogger] = None, reasoning_service: Optional[ReasoningService] = None):
        self.ledger = ledger
        self.tracer = tracer
        self.llm = reasoning_service or OllamaProvider()
        self.parser = PDFParser()
        self.agent = ExtractionAgent(self.llm)

    def process_document(self, document_id: str, pdf_path: Path) -> dict[str, int]:
        """Execute full D2 processing pipeline for a single document."""
```

---

## 6. Detailed Implementation Steps

```
+--------------------------------------------------------------------+
|                      D2 IMPLEMENTATION ROADMAP                     |
+--------------------------------------------------------------------+
|  Phase 1: Schemas & Data Contracts                                 |
|  - Create src/extraction/schemas.py                                |
|  - Define BoundingBox, EvidenceChunk, Observation models           |
|                                                                    |
|  Phase 2: PDF Layout & Table Ingestion Engine                      |
|  - Implement src/pdf/tables.py (pdfplumber table & cell parser)    |
|  - Implement src/pdf/parser.py (PyMuPDF layout + table masking)    |
|  - Unit tests: tests/unit/test_pdf.py                              |
|                                                                    |
|  Phase 3: ReasoningService & Ollama Client                         |
|  - Implement src/llm/provider.py (ReasoningService + Ollama)       |
|  - Implement defensive JSON regex cleaning & validation retry loop |
|  - Unit tests: tests/unit/test_llm.py                              |
|                                                                    |
|  Phase 4: Extraction Agents & Prompt Engineering                   |
|  - Implement src/extraction/agents.py                              |
|  - Numerical, Semantic, and Event extraction prompts               |
|  - Unit tests: tests/unit/test_extraction.py                       |
|                                                                    |
|  Phase 5: Pipeline Integration & Ledger Persistence                |
|  - Implement src/extraction/pipeline.py                            |
|  - Update src/cli/main.py process command to trigger pipeline      |
|  - Update src/api/server.py POST /jobs background task worker      |
|                                                                    |
|  Phase 6: Real-World Document Validation & Sign-Off                |
|  - Run pipeline on sample_docs/01-delhivery-prospectus-2022.pdf    |
|  - Verify evidence_chunks and observations in ledger.db            |
|  - Document results in D2_TESTING_AND_VERIFICATION_PLAN.md        |
+--------------------------------------------------------------------+
```

---

## 7. Verification and Testing Strategy

### 7.1 Automated Unit and Contract Test Suites

1. **`tests/unit/test_pdf.py`**:
   - `test_pdf_text_block_extraction`: Verifies PyMuPDF extracts text blocks with coordinate bounding boxes.
   - `test_pdf_table_extraction`: Verifies `pdfplumber` detects multi-column tables and builds markdown matrices.
   - `test_table_masking`: Verifies text overlapping a detected table is masked out to prevent duplicate chunks.

2. **`tests/unit/test_llm.py`**:
   - `test_ollama_structured_generation`: Verifies `OllamaProvider` generates valid Pydantic models.
   - `test_json_repair_resilience`: Verifies provider handles markdown fences, unescaped newlines, and trailing commas.
   - `test_retry_on_validation_failure`: Verifies retry loop recovers from malformed payloads.

3. **`tests/unit/test_extraction.py`**:
   - `test_numerical_extraction_from_table`: Verifies extraction of revenues, margins, and period tags from a financial table chunk.
   - `test_semantic_extraction_from_text`: Verifies extraction of risk commentary and accounting notes.
   - `test_chunk_provenance_linkage`: Verifies every extracted observation references a valid `chunk_id`.

---

### 7.2 Real-World Document Verification

* **Test File:** [sample_docs/01-delhivery-prospectus-2022-excerpt.pdf](file:///d:/projects/superjoin/EVIDRA/sample_docs/01-delhivery-prospectus-2022-excerpt.pdf) (1.59 MB).
* **Execution Command:**
  ```powershell
  python -m src.cli.main process sample_docs/01-delhivery-prospectus-2022-excerpt.pdf
  ```
* **Pass Criteria:**
  - `evidence_chunks` count > 0 in `ledger.db`.
  - `observations` count > 0 in `ledger.db`.
  - All observations link to a valid `chunk_id` with non-empty bounding box `[x0, y0, x1, y1]`.
  - Job summary table renders with positive chunk and observation counts.

---

## 8. Acceptance Criteria and Sign-off Checklist

- [ ] `src/pdf/tables.py` accurately extracts tables and cell matrices with bounding boxes.
- [ ] `src/pdf/parser.py` extracts text blocks with coordinates and masks table regions.
- [ ] `src/extraction/schemas.py` defines deterministic `EvidenceChunk` and typed `Observation` models.
- [ ] `src/llm/provider.py` reliably forces Ollama to output valid Pydantic models with retry resilience.
- [ ] `src/extraction/agents.py` extracts numerical, semantic, and event claims from financial prose and tables.
- [ ] `src/extraction/pipeline.py` integrates all stages and persists records into SQLite `ledger.db`.
- [ ] All automated tests pass with 100% pass rate (`pytest tests/ -v`).
- [ ] Real-world filing `01-delhivery-prospectus-2022-excerpt.pdf` produces structured evidence chunks and observations.
