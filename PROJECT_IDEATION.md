# Fact Knowledge Layer -- Project Ideation Document

---

## 1. Problem Statement

Important facts are often scattered across documents, stated in different ways, supported by other evidence, or contradicted elsewhere. The challenge is to build a **Fact Knowledge Layer** -- a system that:

- Extracts meaningful numerical or semantic facts from a collection of PDF documents.
- Links every extracted fact to its source evidence within the originating document.
- Identifies when facts across documents corroborate, contradict, or can be reconciled through context (time, scope, units, definitions).
- Provides a simple API or CLI through which PDFs can be uploaded and results inspected.
- Operates generically: no hard-coded facts, filenames, schemas, or document-specific rules.
- Treats the documents themselves as the guide for what counts as a fact and how it is represented.

The system must demonstrate at least one example of each of the following four cases:

| Case | Description |
|------|-------------|
| **Corroboration** | A fact corroborated across documents, even if expressed differently. |
| **Genuine Contradiction** | A genuine or likely contradiction between documents. |
| **Context-Explained Reconciliation** | An apparent contradiction explained by context such as time, scope, or units. |
| **Extraction/Reasoning Failure** | An extraction or reasoning failure found, and how it was handled or would be improved. |

Source evidence and the system's reasoning must be shown for the first three cases.

---

## 2. Core Design Philosophy

The system is **not** a document chatbot, a knowledge graph, or an LLM demo.

It is a **mechanism that decides what can be believed about facts extracted from a changing collection of documents, and can explain why**.

### Framing

Instead of:

```
PDF --> Extract Facts --> Compare Facts --> Label Contradiction
```

The system is framed as:

```
Documents produce Claims
    --> Claims produce Evidence-backed Fact Candidates
        --> Fact Candidates generate competing hypotheses
            --> Independent validators test those hypotheses
                --> A Decision Engine determines the current belief state
```

### Key Principle: The Fact is Not the Primitive

The system distinguishes three levels of epistemic status:

| Level | Definition |
|-------|------------|
| **Observation** | Something explicitly stated in a document. |
| **Fact Candidate** | A normalized interpretation of one or more observations. |
| **Decision** | The system's current assessment of the relationship between fact candidates. |

This separation ensures the architecture has a clean epistemic model. Raw document statements are never conflated with the system's conclusions about those statements.

### Five Non-Negotiable Principles

These collectively define the project's identity. Everything else can be scaled down, but these must be preserved:

| Principle | Description |
|-----------|-------------|
| **1. Evidence before fact** | No evidence means no observation. Nothing enters the knowledge layer without provenance. |
| **2. Observation is not fact is not decision** | Document statements, normalized interpretations, and relationship verdicts are kept as distinct objects. |
| **3. Context before contradiction** | `A != B` does not immediately mean `CONTRADICTION`. The system first investigates temporal, scope, unit, and definitional differences. |
| **4. Challenge your own reasoning** | Every proposed reconciliation is subjected to adversarial challenge before acceptance. |
| **5. Know when you don't know** | When evidence is insufficient, the system produces `UNRESOLVED` rather than forcing a verdict. |

---

## 3. Project Scope Boundaries

The project is organized into three concentric layers. The core innovations that make the project stand out are **implemented**, not merely designed.

```
+-------------------------------------------------------------+
|                      COMPLETE VISION                         |
|                                                              |
|  +-------------------------------------------------------+  |
|  |            IMPLEMENTED DIFFERENTIATOR                 |  |
|  |                                                        |  |
|  | Evidence-centric + multi-agent reasoning +            |  |
|  | context-aware reconciliation + adversarial checking   |  |
|  |                                                        |  |
|  |  +------------------------------------------------+   |  |
|  |  |            BASIC FOUNDATION                    |   |  |
|  |  | PDF --> evidence --> extraction --> storage --> API |  |
|  |  +------------------------------------------------+   |  |
|  +-------------------------------------------------------+  |
|                                                              |
|  Future: scale, sophistication, autonomy, persistence        |
+-------------------------------------------------------------+
```

### 3.1 Implementable Scope -- MUST BUILD

This is the minimum complete working system. It must take unseen PDFs and produce evidence-backed relationship decisions.

| Capability | Priority |
|------------|----------|
| PDF ingestion (arbitrary documents) | Must |
| Evidence-preserving document representation | Must |
| Numerical fact extraction | Must |
| Semantic fact extraction | Must |
| Evidence linking (document/page/section/table/cell) | Must |
| Evidence verification (independent second-pass) | Must |
| Context resolution (time, scope, unit, entity, definition) | Must |
| Dynamic fact schema (arbitrary attributes, no hard-coding) | Must |
| Fact grouping (entity + attribute + context) | Must |
| Corroboration detection | Must |
| Contradiction detection | Must |
| Context-based reconciliation | Must |
| Deterministic numerical validation (Python, not LLM) | Must |
| Hypothesis generation for apparent conflicts | Must |
| Specialist validators (numerical, temporal, semantic) | Must |
| Reconciliation agent | Must |
| Adversarial challenge agent | Must |
| Explicit decision policy (deterministic Python rules) | Must |
| `UNRESOLVED` as a first-class state | Must |
| Decision trace (full evidence-to-verdict audit trail) | Must |
| Evidence Ledger (system of record) | Must |
| Four required demo cases | Must |
| Simple API + CLI | Must |
| Local multi-agent reasoning (Ollama) | Must |

### 3.2 Innovation / Next Steps -- DESIGN, OPTIONALLY PROTOTYPE

These extend the implemented innovation. They show where the architecture evolves, but do not consume majority implementation time.

| Capability | Prototype Scope | Future Vision |
|------------|----------------|---------------|
| Dynamic ontology | Flexible attributes + semantic matching | Full ontology learning from accumulated observations |
| Workflow planning | Deterministic LangGraph workflow | Planner-driven adaptive tool selection |
| Visual/document understanding | Text + tables + basic layout | Charts, diagrams, scanned documents, complex layouts |
| Knowledge persistence | Per-run fact groups and decisions | Persistent incremental knowledge state |
| Incremental processing | Process all documents per run | Only re-evaluate affected fact groups on new document |
| Source reliability | Evidence strength characteristics | Learned claim-dependent reliability from historical outcomes |
| Confidence model | Categorical (HIGH/MEDIUM/LOW/INSUFFICIENT) | Probabilistic belief, confidence calibration, uncertainty propagation |
| Human review | Expose unresolved cases via API/CLI | Full review UI with feedback loop |
| Graph projection | Optional NetworkX visualization | Persistent knowledge graph with temporal/provenance edges |
| Multi-agent scaling | Logical roles, shared local model | Separate specialized models, distributed agents |

**Framing for evaluator**: "I deliberately kept these capabilities at the architectural level because they are orthogonal to demonstrating the core epistemic workflow."

### 3.3 Out of Scope

Capabilities explicitly excluded because they do not contribute to demonstrating the assignment's core problem:

- Production-grade distributed infrastructure (Kubernetes, Kafka, multi-node orchestration, cloud deployment)
- Enterprise authentication / authorization (OAuth, RBAC, SSO)
- Production database architecture (PostgreSQL cluster, sharding, replication, HA, backups)
- Universal document understanding (every PDF format, every language, arbitrary handwriting, heavily corrupted files)
- Absolute truth determination (the system determines evidence-supported relationships, not objective truth)
- Commercial LLM API dependency
- Polished enterprise frontend

---

## 4. System Architecture Overview

The system is organized into **four distinct layers**, each with a clear responsibility boundary.

```
+-----------------------------------------+
|   LAYER 1                               |
|   Document Evidence Preparation         |
|                                         |
|   PDF / Layout / Tables / Text          |
|   Provenance / Context / Evidence IDs   |
+-----------------------------------------+
                  |
                  v
+-----------------------------------------+
|   LAYER 2                               |
|   Fact Construction                     |
|                                         |
|   Extraction / Verification / Context   |
|   Normalization / Fact Groups           |
+-----------------------------------------+
                  |
                  v
+-----------------------------------------+
|   LAYER 3                               |
|   Fact Decision Engine                  |
|                                         |
|   Hypotheses / Validators / Reconcile   |
|   Challenge / Decision Policy / Trace   |
+-----------------------------------------+
                  |
                  v
+-----------------------------------------+
|   LAYER 4                               |
|   Observability and Inspection          |
|                                         |
|   CLI / API / Decision Cards / Reports  |
+-----------------------------------------+
```

---

## 5. Layer 1 -- Document Evidence Preparation

### 5.1 Purpose

This layer answers: **"What is physically and semantically present in this document?"**

It does **not** answer: "Is this fact true?"

Raw PDFs are never exposed directly to the fact-extraction agents. This layer creates a **provenance-preserving, reasoning-ready representation** of the document.

### 5.2 Implementable Scope

- Arbitrary PDF upload/ingestion
- PDF text extraction (PyMuPDF / pdfplumber)
- Page-level provenance
- Basic section/layout preservation
- Table extraction with context preservation (table title, row/column headers, units, footnotes)
- Evidence IDs assigned to every extractable span
- Canonical structured document representation (Markdown + JSON)
- Basic context cue detection ("this year", "previous year", "the company")

### 5.3 Output Format

The layer produces a **Document Representation Package**:

```
document/
|
+-- manifest.json
+-- document.md
+-- pages/
|   +-- page_001.md
|   +-- page_002.md
+-- tables/
|   +-- table_001.json
|   +-- table_002.json
+-- evidence_map.json
```

### 5.4 Document Manifest

Every document receives reasoning-relevant metadata:

```json
{
  "document_id": "DOC-001",
  "source_hash": "...",
  "title": "...",
  "page_count": 87,
  "language": "en",
  "document_characteristics": {
    "contains_tables": true,
    "contains_financial_statements": true,
    "contains_dates": true,
    "contains_named_entities": true
  },
  "detected_units": ["INR", "USD", "%"],
  "detected_entities": ["Company A", "John Smith"]
}
```

### 5.5 Context Envelope

Every piece of extracted content receives a **Context Envelope** -- the bridge between document understanding and fact reasoning:

```
Context Envelope
  Document, Page, Section, Entity, Time period, Geography,
  Reporting scope, Currency, Unit, Table title,
  Column header, Row header, Footnotes
```

### 5.6 Table Metadata (Domain-Oriented)

Tables receive semantic metadata, not just generic row/column counts:

```json
{
  "table_id": "T-014",
  "page": 47,
  "table_semantics": {
    "title": "Consolidated Statement of Profit",
    "reporting_scope": "consolidated",
    "currency": "INR",
    "unit": "crore",
    "period_columns": { "C2": "FY2024", "C3": "FY2023" }
  }
}
```

### 5.7 Evidence-Tagged Markdown Convention

```markdown
[DOCUMENT: DOC-001]
[PAGE: 12]

## SECTION: Financial Performance

[EVIDENCE:E-0012]
Revenue increased by 18% during FY2024.

[EVIDENCE:E-0013]
The company reported revenue of 120 crore INR.
```

Every downstream fact points to: `DOC-001 / PAGE-12 / EVIDENCE-E-0013`.

### 5.8 Critical Design Principles

- **Preserve uncertainty**: "approximately 100 crore" becomes `value=100, qualification=approximately`.
- **Preserve footnotes**: Footnotes become context evidence associated with the relevant table/cell/section.
- **Classify headers/footers**: Repeated structural content becomes metadata; page-specific headers may carry semantic context.
- **Do not destroy layout**: Tables must be preserved in structured form, never flattened.
- **No premature inference**: This layer documents what is present, not what is true.

### 5.9 Next Steps (Not Implemented)

- Sophisticated reading-order inference
- Complex figure/chart/diagram understanding
- Advanced scanned-document reconstruction
- Document-level semantic segmentation
- Multilingual document normalization

---

## 6. Layer 2 -- Fact Construction

### 6.1 Purpose

This layer answers: **"What facts can we derive from those observations, and how are they structured?"**

### 6.2 Fact Extraction (Dual Pipeline)

**Table-Native Extraction**: Treats `row header x column header x cell` as `(attribute, scope, value)` directly. Grounding is exact (page + cell coordinates).

**Prose Extraction via Constrained LLM Output**: For narrative claims, the model emits `(entity, attribute, value, qualifiers, supporting_evidence_ids)` against sentence-indexed text. Forces citation rather than paraphrasing.

### 6.3 Evidence Verification (Extract-Then-Verify)

An independent **Evidence Verifier** performs a second pass separate from extraction. Given only the evidence span and the claimed fact, it answers: "Does this text entail this fact?"

```
Extractor --> Observation --> Evidence Verifier
    --> SUPPORTED / PARTIALLY_SUPPORTED / NOT_SUPPORTED
```

This is the FEVER-style separation of claim generation from claim verification -- the single most important decoupling in the design. The system does not treat an LLM-generated extraction as automatically true.

### 6.4 Context Resolution

The **Context Resolver** extracts the dimensions of meaning surrounding a fact:

For numerical facts: `value, unit, currency, period, period_type, scope, entity, geography, accounting_definition, aggregation`

For semantic facts: `entity, state, event, effective_date, role, scope, qualification, certainty`

### 6.5 Dynamic Fact Schema

Attribute names are not predefined. The extractor produces arbitrary attributes:

```json
{
  "entity": "Company X",
  "attribute": "operating_margin",
  "value": 14.2,
  "unit": "percent",
  "time_scope": "FY2025"
}
```

without a hard-coded `allowed_attributes` list. The system uses semantic matching (embeddings + LLM verification) to identify when two differently-named attributes refer to the same concept.

**Not implemented yet**: A sophisticated persistent ontology-learning system. That is the scaling of the innovation, not the innovation itself.

### 6.6 Fact Candidate Data Model

```
FactCandidate
  fact_id, entity, attribute, value, normalized_value,
  unit, currency, time_scope, geographic_scope,
  organizational_scope, source_documents, evidence_spans,
  extraction_method, extraction_confidence, context,
  supporting_observations, decision_status, decision_explanation
```

### 6.7 Evidence Bundle

Every candidate fact carries an Evidence Bundle:

```
EvidenceBundle
  source_document, page, bounding_box (where available),
  exact_text, table_reference, surrounding_context,
  evidence_type, evidence_strength
```

### 6.8 Fact Groups

Observations are organized into **Fact Groups** based on entity + attribute + context similarity. Relationships are evaluated between observations within the same group, not by blindly comparing every extracted fact.

```
FACT GROUP: Company X / Revenue
  +-- Observation A (Annual Report, FY2024)
  +-- Observation B (Investor Presentation, FY2024)
  +-- Observation C (News Report, FY2025)
```

---

## 7. Layer 3 -- Fact Decision Engine

### 7.1 Purpose

This layer answers: **"How do facts across documents relate -- do they corroborate, contradict, or can they be reconciled?"**

This is the core of the system and the primary differentiator.

### 7.2 Central Object: Evidence Ledger

The Evidence Ledger is the central object, not a graph. Every extracted proposition enters the ledger. The graph, if used, becomes a **projection of the ledger**, not the decision mechanism.

The ledger links: `Evidence --> Observation --> FactCandidate --> FactGroup --> Hypothesis --> Validation --> Decision --> DecisionTrace`

All linked through IDs, making every decision fully reproducible and inspectable.

### 7.3 Agent Decomposition -- Implemented Roles

Agents are split by **what kind of claim they are allowed to make**. The prototype implements ~4-5 logical roles using the same Ollama model with different prompts and access boundaries:

```
                 Orchestrator
                      |
          +-----------+-----------+
          v           v           v
    Extraction    Verification   Context
       Agent         Agent      Resolver
          |           |           |
          +-----------+-----------+
                      v
                Fact Grouping
                      v
             Relationship Detection
                      v
               Hypothesis Generator
                      v
          +-----------+-----------+
          v           v           v
     Numerical    Temporal    Semantic
     Validator    Validator   Validator
          +-----------+-----------+
                      v
               Reconciliation
                      v
            Adversarial Challenge
                      v
              Decision Policy
                      v
              Final Decision
```

These are **logical agents**, not separate deployed services. All use the same local model. The distinction is: **Agent A is allowed to make one kind of claim, while Agent B is allowed to make another.**

### 7.4 Agent Contracts

Every agent operates under a formal contract:

- **Input contract**: What it is allowed to see.
- **Output contract**: Strict JSON schema.
- **Responsibility contract**: What it is allowed to decide.
- **Prohibited decisions**: What it cannot decide.

Example -- Reconciliation Agent:

```
CAN:
  - Propose temporal explanation
  - Propose scope explanation
  - Cite evidence

CANNOT:
  - Declare final contradiction
  - Modify source evidence
  - Change extracted values
  - Override numerical validator
```

### 7.5 Structured Communication

Agents communicate through **structured objects**, not conversational text:

```json
{
  "hypothesis_id": "H-104",
  "type": "TEMPORAL_RECONCILIATION",
  "claims": ["F-21", "F-45"],
  "evidence": ["E-72", "E-91"],
  "reasoning": "...",
  "tests_required": ["period_overlap", "same_entity"]
}
```

### 7.6 Hypothesis Tournament -- MUST IMPLEMENT

This is central to the project's identity. When two observations appear inconsistent, the system generates competing hypotheses rather than immediately labeling the relationship:

| Hypothesis | Description |
|------------|-------------|
| H1 | Genuine contradiction |
| H2 | Different time period |
| H3 | Different scope |
| H4 | Different metric definition |
| H5 | Unit/currency mismatch |
| H6 | Extraction error |
| H7 | Insufficient evidence |

Specialist validators independently test each hypothesis. A structured hypothesis list + evidence-based validation is sufficient. No mathematically sophisticated Bayesian model is required. But **the mechanism must actually run.**

### 7.7 Numerical Validation (Deterministic) -- MUST IMPLEMENT

Numerical comparison is done in **Python code**, not by the LLM:

1. Normalize units (5 crore INR = 50 million INR = 50,000,000 INR).
2. Normalize currency where applicable.
3. Compute difference and relative difference.
4. Classify: exact match / near match (rounding) / material difference.

The system first verifies the dimensional hierarchy before comparing values:

```
Same entity? --> Same metric? --> Same currency? --> Same unit?
    --> Same period? --> Same scope? --> Same definition?
        --> THEN compare values
```

### 7.8 Semantic Fact Comparison

Semantic facts use a state/event/time model:

| Classification | Example |
|---------------|---------|
| **Static fact** | Company headquarters is in Chennai. |
| **Temporal fact** | John Smith is a director. |
| **Event** | John Smith resigned on March 15. |

The prototype implements basic temporal fields: `period`, `period_type`, `effective_date`, `reported_date`. Full temporal knowledge representation is a Next Step.

### 7.9 Fact States

| State | Meaning |
|-------|---------|
| `CORROBORATED` | Multiple independent sources confirm the same fact. |
| `RECONCILED` | An apparent conflict is explained by context (with the specific mechanism named). |
| `CONTRADICTED` | The documents contain mutually inconsistent claims about the same fact. |
| `UNRESOLVED` | Insufficient textual evidence to decide. |
| `SUPERSEDED` | A later document updates or replaces an earlier observation. |

`UNRESOLVED` is a first-class design principle. Forcing a verdict when the documents do not support one is a worse failure than admitting uncertainty.

### 7.10 Three Decision Paths (Adaptive Reasoning Depth)

| Path | Trigger | Mechanism |
|------|---------|-----------|
| **Path A -- Deterministic** | Exact numeric equality, normalized unit equality, identical entity/attribute match | Evidence --> Normalization --> Deterministic comparison --> Decision. No debate. |
| **Path B -- Context Resolution** | Different periods, different scopes, different units | Route to specialist validators + reconciliation agent. |
| **Path C -- Genuine Ambiguity/Conflict** | Same context but materially different values | Full reasoning pipeline: validators --> reconciliation --> adversarial challenge --> decision policy --> verdict. |

The expensive reasoning layer activates only when necessary.

### 7.11 Reconciliation Agent -- MUST IMPLEMENT

The agent's job: **Find the strongest explanation under which both observations could be true.**

It must produce evidence for its reconciliation, not just assert it.

### 7.12 Adversarial Challenge -- MUST IMPLEMENT

This prevents the reconciliation mechanism from hallucinating explanations:

```
Candidate conflict --> Reconciliation --> "I found explanation X"
    --> Adversarial Validator --> Can evidence falsify X?
        --> SURVIVES / REJECTED / INSUFFICIENT_EVIDENCE
```

The skeptic has access to the **original evidence**, not the reconciliation agent's summary. This is a genuine implementation of the innovation, even if the underlying model is just Qwen running locally.

### 7.13 Decision Policy Layer -- MUST IMPLEMENT

Between agent outputs and the final verdict, an explicit **Decision Policy** defines what constitutes a valid verdict. Implemented as deterministic Python logic:

```
CONTRADICTION requires:
  1. Evidence verified
  2. Same entity
  3. Same attribute
  4. Compatible definition
  5. Comparable context
  6. Material disagreement
  7. No surviving reconciliation hypothesis

RECONCILIATION requires:
  1. Both observations independently supported
  2. Context difference identified
  3. Difference explains the discrepancy
  4. Evidence explicitly supports that context
  5. No surviving contradiction argument
```

This makes the architecture **auditable rather than prompt-dependent**. The LLM is not the final authority.

### 7.14 Decision Strength

Instead of a fake probabilistic confidence score, the system uses categorical/ordinal decision strength:

```
HIGH / MEDIUM / LOW / INSUFFICIENT
```

with exposed reasons:

```
Decision: RECONCILED
Strength: HIGH

Because:
  [pass] Both observations independently supported
  [pass] Periods explicitly differ
  [pass] Values are internally consistent
  [pass] Challenge failed to falsify temporal explanation
```

### 7.15 Decision Card (Core Output)

Every relationship produces a Decision Card:

```
+-------------------------------------------+
| FACT RELATIONSHIP                         |
+-------------------------------------------+
| Entity: Company X                          |
| Metric: Revenue                            |
| Document A: 100 Cr   Document B: 180 Cr   |
| VERDICT: CONTRADICTION                    |
| Decision Strength: HIGH                    |
+-------------------------------------------+
| WHY?                                      |
| [pass] Same entity                        |
| [pass] Same metric                        |
| [pass] Same period                        |
| [fail] Values materially differ           |
+-------------------------------------------+
| SUPPORTING EVIDENCE                       |
| A --> page 14 --> "...100 crore..."       |
| B --> page 22 --> "...180 crore..."       |
+-------------------------------------------+
| ALTERNATIVE EXPLANATIONS                  |
| No contextual reconciliation found.       |
+-------------------------------------------+
```

### 7.16 Decision Trace -- MUST IMPLEMENT

Every final decision has a complete audit trail:

```json
{
  "decision": "D-001",
  "relationship": "RECONCILED",
  "observations": ["O-12", "O-34"],
  "hypotheses": ["H-1", "H-2", "H-3"],
  "validation": {
    "temporal": "PASS",
    "scope": "PASS",
    "numerical": "PASS"
  },
  "reconciliation": "R-001",
  "challenge": "SURVIVED",
  "policy": "P-003",
  "strength": "HIGH"
}
```

Inspectable as JSON/JSONL/Markdown. This is part of the actual product, not debug output.

---

## 8. Layer 4 -- Observability and Inspection

### 8.1 Purpose

The interface is intentionally thin. The primary user experience is inspection of evidence-backed decisions rather than visualization of the underlying data.

### 8.2 Interface: API + CLI

**CLI** -- the primary human debugging interface:

```bash
python -m factlayer process ./documents/
```

**REST API** -- for programmatic access:

| Endpoint | Purpose |
|----------|---------|
| `POST /jobs` | Upload PDFs, create processing job (async). |
| `GET /jobs/{job_id}` | Check job status and progress. |
| `GET /documents/{document_id}` | Inspect document representation. |
| `GET /facts` | List all extracted fact candidates. |
| `GET /decisions/{decision_id}` | Inspect a specific decision with full trace. |

No full SaaS-style UI needed. Swagger interface is sufficient.

### 8.3 Output Artifacts

Every run produces a structured artifact directory:

```
runs/
+-- JOB-2026-001/
    +-- run.json
    +-- summary.md
    +-- documents/
    |   +-- DOC-001/
    |       +-- manifest.json
    |       +-- representation.md
    |       +-- evidence.json
    +-- observations/
    |   +-- observations.jsonl
    +-- facts/
    |   +-- facts.jsonl
    +-- decisions/
    |   +-- decisions.jsonl
    +-- reports/
    |   +-- fact_report.md
    |   +-- contradiction_report.md
    |   +-- unresolved_report.md
    +-- trace/
        +-- decision_trace.jsonl
        +-- events.jsonl
```

### 8.4 Four Inspection Levels

| Level | Question |
|-------|----------|
| **Run** | How did the whole job perform? |
| **Document** | What did we understand from this PDF? |
| **Fact** | What observations constitute this fact? |
| **Decision** | Why were these facts considered corroborated/contradicted/reconciled? |

### 8.5 Unresolved Report

A dedicated `unresolved_report.md` demonstrates the system knows when it does not know:

```
D-17
Facts: F-31 <-> F-54
Reason:
  Both observations are supported by their source evidence,
  but their reporting definitions could not be established.
Why not automatically classify:
  The documents do not provide sufficient context to determine
  whether "operating revenue" and "total revenue" represent
  the same metric.
Recommended action:
  Additional evidence required.
```

---

## 9. Multi-Agent Architecture with Local LLM (Ollama)

### 9.1 Design Principle

> **Evidence-Centric Fact Decision Engine with Specialized Reasoning Agents.**

The system is **evidence-centric and decision-centric, with agents as specialized reasoning workers**. It is not an autonomous agent swarm.

### 9.2 Agent-to-Mechanism Mapping

| Problem | Best Mechanism |
|---------|---------------|
| PDF parsing | Deterministic/parser |
| Table extraction | Table parser |
| Sentence segmentation | Deterministic |
| Evidence coordinates | Parser |
| Unit normalization | Deterministic |
| Currency conversion | Deterministic/rules |
| Arithmetic | Deterministic |
| Date normalization | Deterministic |
| Entity candidate matching | Embeddings + retrieval |
| Attribute matching | Embeddings + LLM when ambiguous |
| Evidence entailment | LLM |
| Context interpretation | LLM |
| Hypothesis generation | LLM |
| Contradiction analysis | LLM + deterministic checks |
| Reconciliation reasoning | LLM |
| Adversarial challenge | LLM |
| Final decision | Explicit decision engine (Python) |
| Provenance | Database/ledger |

### 9.3 Workflow Orchestrator (Not Autonomous Agents)

Agents are **not** autonomous. A workflow orchestrator (LangGraph) controls execution flow deterministically:

```
DocumentState --> Parallel extraction --> Verification
    --> Fact normalization --> Candidate generation
    --> Conditional reasoning --> Decision --> Challenge --> Finalize
```

### 9.4 LLM Failure Recovery

```
LLM returns malformed output
    --> Schema validator
    --> Retry with constrained prompt
    --> Still invalid? --> Mark extraction failed --> Do NOT create fact
```

Uncertain judge decisions produce `UNRESOLVED`, not guesses.

### 9.5 Performance Optimization

- **Candidate filtering**: Only likely factual regions go to Ollama.
- **Batch processing**: Send candidate chunks in batches, not one at a time.
- **Conflict-triggered reasoning**: The expensive debate pipeline activates only when disagreement exists.

### 9.6 LLM Provider Abstraction

Agents call a `ReasoningService` abstraction, not Ollama directly. This allows future provider swaps without architectural changes.

---

## 10. Proposed Tech Stack

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Language | Python | Ecosystem for PDF processing, LLM integration, data manipulation. |
| LLM Runtime | Ollama (local) | No proprietary API dependency; reproducible and cost-controlled. |
| LLM Models | Qwen / Llama (via Ollama) | Interchangeable; model choice does not affect architecture. |
| API Framework | FastAPI | Lightweight, async-capable, structured output support. |
| Orchestration | LangGraph | Branching, parallel execution, state, conditional routing, checkpoints. |
| PDF Parsing | pdfplumber / PyMuPDF | Table extraction, text extraction, layout analysis. |
| Storage | SQLite + JSON artifacts | Simple, inspectable, no external database dependency. |
| Embeddings | Local embedding model | For entity/attribute canonicalization and matching. |
| CLI | Python click / argparse | Simple command-line interface. |
| Graph (optional) | NetworkX | Lightweight projection for visualization if time permits. |

---

## 11. Four Required Cases -- Architecture Mapping

| Case | System Behavior |
|------|----------------|
| **Corroboration** | Two independent sources support same fact (even if expressed differently) --> entity/attribute canonicalization --> context compatibility --> normalized comparison --> `CORROBORATED`. |
| **Contradiction** | Same context + materially different claims --> evidence verified --> reconciliation hypotheses generated and rejected --> adversarial challenge confirms --> `CONTRADICTED`. |
| **Context Reconciliation** | Apparent conflict explained by time/scope/definition --> specialist validation confirms --> reconciliation hypothesis survives adversarial challenge --> `RECONCILED` with specific mechanism named. |
| **Failure** | Extraction/reasoning cannot establish answer --> detection by verifier/context resolver --> `UNRESOLVED` with stated reason. Deliberately preserved, not hidden. |

For each case, the system produces: `Input --> Observations --> Evidence --> Reasoning --> Decision --> Trace`.

---

## 12. Innovation Already Implemented (What Makes This Stand Out)

| Innovation | Status |
|-----------|--------|
| Evidence-first architecture | Built |
| Observation / Fact / Decision separation | Built |
| Dynamic fact schema (no hard-coded attributes) | Built |
| Fact Groups (entity + attribute + context clustering) | Built |
| Evidence verification (independent second-pass) | Built |
| Context-aware comparison (time, scope, unit, entity, definition) | Built |
| Hypothesis tournament (competing explanations for conflict) | Built |
| Numerical validator (deterministic Python) | Built |
| Temporal validator | Built |
| Semantic validator | Built |
| Reconciliation agent | Built |
| Adversarial validator (challenge reconciliation with evidence) | Built |
| Explicit decision policy (deterministic, auditable) | Built |
| Unresolved as first-class state | Built |
| Decision trace (full evidence-to-verdict audit trail) | Built |
| Local multi-agent reasoning via Ollama | Built |

---

## 13. Next Steps (Documented Extensions)

These are **second-order innovations** that make the implemented system substantially more powerful. They demonstrate understanding of where the system would go, without consuming implementation time.

| Extension | Today | Future |
|-----------|-------|--------|
| **Persistent evolving knowledge** | Per-run fact groups and decisions | Knowledge state persists; new documents trigger incremental re-evaluation of affected groups only |
| **Autonomous workflow planning** | Fixed LangGraph workflow | Planner selects required specialists based on document characteristics |
| **Learned ontology evolution** | Dynamic attributes + semantic matching | Concept discovery --> ontology candidates --> validation --> persistent ontology |
| **Learned source reliability** | Evidence strength characteristics | Historical outcomes --> claim-specific reliability --> calibrated decision strength |
| **Advanced multimodal reasoning** | Text + tables | Charts, diagrams, scanned documents, images participating in the evidence/decision framework |
| **Large-scale incremental processing** | Few PDFs | Thousands of documents + parallel processing + caching + incremental recomputation |
| **Human knowledge adjudication** | UNRESOLVED state exposed via API | Human review --> feedback --> knowledge update --> future decisions improve |

---

## 14. Known Limitations and Acknowledged Risks

| Limitation | Mitigation |
|-----------|------------|
| Local LLMs are weaker at complex financial language, nuanced negation, and long table comprehension. | Architecture makes LLM failure recoverable; uncertain outputs become `UNRESOLVED`. |
| Attribute matching by embedding similarity may conflate lexically close but semantically different attributes. | Matching only proposes candidates; validation step checks "same definition" as precondition. When unconfirmable: "ambiguous -- insufficient definitional context". |
| Adversarial challenge shares the same model and blind spots as reconciliation. | Asymmetry is structural: the challenger has access only to raw evidence spans, not the reconciliation summary. |
| Complex PDF layouts may produce poor extraction. | Prototype targets reasonable-quality PDFs. Advanced layout reconstruction is documented as Next Steps. |

---

## 15. README Structure (Submission)

| Section | Content |
|---------|---------|
| **Setup and Run Instructions** | Ollama setup, Python environment, dependencies, run command, API command, CLI command. |
| **Video Demo (max 3 minutes)** | 0:00 Upload/process PDFs --> 0:30 Corroboration --> 1:00 Contradiction --> 1:30 Context reconciliation --> 2:00 Failure/uncertainty --> 2:30 Traceability + architecture. |
| **Approach** | Document Evidence Preparation, Fact Construction, Decision Engine, Multi-agent reasoning, Decision Policy, Observability. |
| **Limitations and Next Steps** | Local LLM limitations, complex PDF layouts, semantic ambiguity, scaling, ontology learning, incremental processing, multimodal expansion. |
| **Additional Notes** | Why local LLM, why agents, why deterministic validation, why graph is not central, why unresolved is a valid state. |

---

## 16. Guiding Statements

> "The system constructs evidence-backed fact candidates and determines the strongest relationship supported by the available documents."

> "When evidence is insufficient, the system explicitly preserves uncertainty rather than forcing a verdict."

> "The interface is intentionally thin. The primary user experience is inspection of evidence-backed decisions rather than visualization of the underlying data."

> "The knowledge graph is an optional representation of relationships; the decision procedure is evidence- and validation-driven."

> "Specialized agents are used only for tasks requiring semantic interpretation; deterministic validators govern numerical, temporal, and provenance-sensitive decisions."

> "You are not submitting an idea for an intelligent fact system. You are submitting a working miniature of the intelligent fact system, while explicitly showing how it could grow beyond the prototype."

---

*End of Project Ideation Document*
