# EVIDRA: Evidence-Driven Architecture for Fact Validation and Knowledge Reasoning

## Deliverable 5 (D5) Implementation Plan: Observability, Reporting, and Evaluation Testing (Layer 4)

---

## 1. Executive Overview and Epistemic Objective

Deliverable 5 (**D5**) implements the observability, reporting, and evaluation testing layer of **EVIDRA** (Layer 4).

In Deliverables 1 through 4, EVIDRA established:
1. Deterministic evidence ledger storage, run directory management, CLI, and REST API (D1).
2. Layout-aware chunking, visual bounding boxes, and grounded observation extraction (D2).
3. Exact arithmetic normalization, context qualification, and soft dispute grouping (D3).
4. Epistemic reasoning, LangGraph adaptive paths, hypothesis tournaments, adversarial skepticism, and deterministic decision policy truth tables (D4).

Deliverable 5 delivers the operational, auditability, and verification surfaces of the architecture:
**"Can an auditor or human analyst independently verify, trace, and evaluate every decision from raw source coordinates to final verdict, and does the system pass the four mandatory assignment benchmark scenarios with quantitative rigor?"**

To satisfy rigorous financial and audit standards, D5 enforces four foundational principles:
1. **Cryptographic Step-by-Step Provenance Replay:** Every state transformation, LLM prompt, raw completion, validator outcome, and policy rule evaluation is recorded in `decision_traces` and streamed to `trace.jsonl`. A dedicated replay engine enables forensic reconstruction of any decision.
2. **Human-Readable Executive Reporting:** Generates clean, GitHub Flavored Markdown reports (`summary.md`, `contradictions.md`, `unresolved.md`) containing tabular side-by-side claim comparisons, exact source document citations, page numbers, and bounding box coordinates, without extraneous visual artifacts or emojis.
3. **Defensive Failure Handling:** Ambiguous claims, corrupted text, unstated assumptions, or single-source observations are systematically identified, categorized, and presented with actionable follow-up recommendations for financial analysts.
4. **Mandatory Assignment Benchmark Verification:** Implements an automated evaluation harness and executes tests across the four required assignment benchmark scenarios:
   - **Corroboration Benchmark:** Dual-source validation of identical metrics across distinct filings.
   - **Direct Contradiction Benchmark:** Detection and isolation of irreconcilable numerical discrepancies.
   - **Defensible Reconciliation Benchmark:** Resolution of reporting variances via accounting standard differences, restatements, or scope divergences.
   - **Defensive Failure Handling Benchmark:** Graceful fallback to `UNRESOLVED` when faced with corrupt text, missing disclosures, or ungrounded assertions.

---

## 2. Scope and Boundaries of Deliverable 5

### 2.1 In-Scope Deliverables

* **D5.1: Cryptographic Decision Trace Engine and Provenance Replay (`src/observability/trace.py`):**
  - Enhanced `TraceLogger` with structured step metadata, agent IDs, and execution latencies.
  - `TraceReplayer`: Standalone engine that reads `trace.jsonl` or queries `decision_traces` from SQLite to replay and inspect the decision graph chronologically.
  - Forensic CLI command: `evidra replay <job_id> [--decision-id <id>] [--step <idx>]`.
* **D5.2: Production Markdown Reporting Suite (`src/observability/reports.py`):**
  - `ExecutiveSummaryReporter` (`summary.md`): High-level dashboard showing documents ingested, chunks indexed, candidate facts normalized, fact groups formed, and categorical verdict distribution.
  - `ContradictionReporter` (`contradictions.md`): Detailed discrepancy audit featuring side-by-side comparative tables, percentage deltas, source document and page citations, evaluated hypotheses, and refutation logs.
  - `UnresolvedAnalysisReporter` (`unresolved.md`): Diagnostic inventory of single-source observations, ungrounded claims, and specific investigation guidance for analysts.
  - Support for multiple export formats (Markdown and structured JSON).
* **D5.3: Automated Evaluation Framework and Metrics Engine (`src/observability/evaluator.py`):**
  - Benchmark schemas: `BenchmarkCase`, `EvaluationDataset`, `EvaluationMetrics`.
  - Metrics calculation: Categorical Accuracy, Precision, Recall, F1-score across verdicts, Hallucination Rate, and Epistemic Soundness.
* **D5.4: Mandatory Assignment Evaluation Scenarios (`tests/evaluation/test_scenarios.py`):**
  - **Scenario 1 (Corroboration):** Press Release vs Annual Report identical revenue/EBITDA.
  - **Scenario 2 (Direct Contradiction):** Conflicting revenue figures with identical temporal and accounting context.
  - **Scenario 3 (Defensible Reconciliation):** Non-GAAP vs GAAP exclusions, prior-period restatement footnotes.
  - **Scenario 4 (Defensive Failure Handling):** Corrupt text, missing pages, and ungrounded claims.
* **D5.5: CLI and REST API Observability Endpoints (`src/cli/main.py`, `src/api/server.py`):**
  - CLI subcommands: `evidra report`, `evidra replay`, and `evidra benchmark`.
  - REST endpoints: `GET /jobs/{job_id}/traces`, `GET /jobs/{job_id}/traces/{decision_id}`, and `POST /evaluate`.

### 2.2 Out-of-Scope (Future Enhancements)
- External cloud monitoring integrations (e.g. Datadog, Prometheus) beyond local execution.
- Real-time WebSocket streaming UI (REST polling and CLI replay fully satisfy assignment scope).

---

## 3. Requirements Coverage (SRS and NFR Mapping)

### 3.1 Functional Requirements (SRS)
* **OBS-REP-01 (Relational Evidence Ledger):** Maintain SQLite `ledger.db` with complete foreign keys across documents, chunks, observations, fact candidates, fact groups, group members, hypotheses, validator results, decisions, and decision traces.
* **OBS-REP-02 (Isolated Run Directory):** Create structured run directories with dedicated subfolders (`documents/`, `evidence/`, `reports/`, `traces/`) and `run.json` manifests.
* **OBS-REP-03 (Executive Summary Report):** Generate `reports/summary.md` detailing corpus ingestion metrics, evidence volumes, and verdict distributions.
* **OBS-REP-04 (Contradiction Report):** Generate `reports/contradictions.md` detailing side-by-side claim comparisons, physical bounding boxes, and hypothesis evaluations.
* **OBS-REP-05 (Unresolved Report):** Generate `reports/unresolved.md` detailing ambiguous or single-source observations with analyst follow-up recommendations.
* **OBS-REP-06 (FastAPI REST Endpoints):** Expose endpoints for job creation, status monitoring, decision inspection, trace retrieval, and report downloading.
* **OBS-REP-07 (Command Line Interface):** Provide robust CLI subcommands (`process`, `inspect`, `report`, `replay`, `benchmark`) with clean ANSI formatting.

### 3.2 Non-Functional Requirements (NFR)
* **NFR-DET-02 (Provenance Replay):** Every decision must be 100% reconstructible and auditable from `trace.jsonl` and source PDF coordinates.
* **NFR-AUD-01 (Step-by-Step Auditability):** Millisecond-precision timestamps and input/output payloads recorded for every agent action and validator check.
* **NFR-REL-01 (Defensive Fallback):** Corrupt inputs or unexpected errors must gracefully route to `UNRESOLVED` with diagnostic warnings; the pipeline must never crash.
* **NFR-SEC-01 (Zero Credential Leakage):** Local-only execution without external network egress or API keys.

---

## 4. Architecture and Observability Pipeline Flow

### 4.1 Layer 4 Architecture Diagram

```
+-----------------------------------------------------------------------------+
|                                  LAYER 4                                    |
|                   OBSERVABILITY, REPORTING & EVALUATION                     |
+-----------------------------------------------------------------------------+
                                       |
          +----------------------------+----------------------------+
          |                            |                            |
          v                            v                            v
  [ Trace Engine ]            [ Reporting Suite ]          [ Evaluation Harness ]
  - TraceLogger               - summary.md                 - Benchmark Runner
  - trace.jsonl               - contradictions.md          - 4 Mandatory Scenarios
  - TraceReplayer             - unresolved.md              - Precision / Recall
          |                            |                            |
          +----------------------------+----------------------------+
                                       |
                                       v
         +-----------------------------------------------------------+
         |                     SURFACES & INTERFACES                 |
         |  - CLI: evidra report, inspect, replay, benchmark         |
         |  - REST API: /jobs, /decisions, /reports, /traces         |
         |  - SQLite: ledger.db (10 relational tables)               |
         +-----------------------------------------------------------+
```

### 4.2 Provenance Replay Flow

```
[ runs/JOB-.../traces/trace.jsonl ] or [ ledger.db : decision_traces ]
                                  |
                                  v
                       [ TraceReplayer Engine ]
                                  |
         +------------------------+------------------------+
         |                                                 |
         v                                                 v
  [ Chronological Step Replay ]                 [ Forensic Decision Audit ]
  - Step Index & Timestamp                      - Candidate claims evaluated
  - Node Name & Agent ID                        - Variance metrics calculated
  - Input State snapshot                        - Hypotheses proposed
  - Output State / Decision                     - Skeptic critique outcome
                                                - Policy rule fired
```

---

## 5. Detailed Component Design

### 5.1 D5.1: Cryptographic Decision Trace Engine and Replayer (`src/observability/trace.py`)

#### Data Models & Classes
- `TraceEntry`:
  - `trace_id`: Unique identifier (`TRC-{uuid[:8]}`).
  - `decision_id`: Optional associated decision ID (`DEC-{hex[:8]}`).
  - `timestamp`: ISO-8601 UTC timestamp.
  - `step_name`: Pipeline or LangGraph node name (e.g. `analyze_variance`, `apply_policy`).
  - `agent_name`: Name of component emitting trace (e.g. `AdversarialSkeptic`, `DecisionPolicy`).
  - `latency_ms`: Execution latency in milliseconds.
  - `input`: Serialized input payload.
  - `output`: Serialized output payload.

- `TraceReplayer`:
  - `load_from_file(trace_path: Path)`: Reads and parses JSONL lines.
  - `load_from_db(db_path: Path, job_id: str)`: Queries SQLite `decision_traces`.
  - `get_steps(decision_id: Optional[str] = None) -> list[TraceEntry]`: Filters steps by decision.
  - `render_timeline(decision_id: Optional[str] = None) -> str`: Formats an ANSI or text timeline.
  - `verify_integrity() -> bool`: Verifies chronological sequence and structural integrity.

### 5.2 D5.2: Enhanced Production Markdown Reporting Suite (`src/observability/reports.py`)

The reporting suite produces three specialized documents upon job completion:

#### 1. Executive Summary Report (`reports/summary.md`)
- Document Manifest table: Document IDs, filenames, page counts, SHA-256 hashes.
- Pipeline Metrics table: Ingested documents, layout chunks, extracted observations, normalized candidates, fact groups, evaluated decisions.
- Verdict Breakdown: Corroborated, Contradiction, Reconciled, Unresolved counts and percentages.
- Decision Matrix table: Decision ID, Entity, Attribute, Period, Verdict, Confidence Strength.

#### 2. Contradiction and Reconciliation Report (`reports/contradictions.md`)
- Detailed breakdown for every decision with verdict `CONTRADICTION` or `RECONCILED`.
- Side-by-side claim comparison tables:
  - Source document and page number.
  - Verbatim stated value vs Normalized numerical value.
  - Stated unit and normalized currency.
  - Spatial bounding box coordinates.
- Hypothesis evaluation audit:
  - Hypothesis class (Restatement, Accounting Basis, Scope, Timing, Erroneous Contradiction).
  - Description, likelihood score, and validation status (`SUPPORTED`, `REFUTED`, `INSUFFICIENT_DATA`).
- Adversarial Skeptic critique outcome (`SURVIVED`, `FALSIFIED`, `UNGROUNDED`).
- Exact explanation bridge and policy rule justification.

#### 3. Unresolved Analysis Report (`reports/unresolved.md`)
- Detailed inventory of facts that did not reach a conclusive verdict.
- Categorization:
  - Single-source observations pending corroborating filings.
  - Ambiguous entity or attribute classifications.
  - Unentailed assertions flagged during provenance verification.
- Explicit, actionable next steps for equity research analysts.

### 5.3 D5.3: Automated Evaluation Framework and Benchmark Harness (`src/observability/evaluator.py`)

#### Evaluation Schemas
- `BenchmarkCase`:
  - `case_id`: Identifier (e.g. `BENCH-01-CORROBORATION`).
  - `name`: Human-readable test name.
  - `description`: Scenario explanation.
  - `documents`: List of PDF file paths or mock document contents.
  - `target_entity`: Entity to evaluate.
  - `target_attribute`: Metric to evaluate.
  - `target_period`: Temporal scope.
  - `expected_verdict`: Ground truth verdict (`CORROBORATED`, `CONTRADICTION`, `RECONCILED`, `UNRESOLVED`).
  - `expected_hypothesis`: Expected winning hypothesis class (if applicable).
  - `expected_strength`: Expected decision strength (`HIGH`, `MEDIUM`, `LOW`, `INSUFFICIENT`).

- `EvaluationMetrics`:
  - `total_cases`: Integer count.
  - `passed_cases`: Integer count.
  - `accuracy`: Float percentage.
  - `verdict_confusion_matrix`: Dict mapping (expected, actual) pairs to counts.
  - `precision_by_verdict`: Dict of precision per verdict class.
  - `recall_by_verdict`: Dict of recall per verdict class.
  - `hallucination_rate`: Percentage of ungrounded reconciliations emitted (must be 0.0%).

- `BenchmarkRunner`:
  - Executes benchmark cases through the end-to-end pipeline in isolated temporary run directories.
  - Compares actual emitted decisions against expected ground truth.
  - Emits comprehensive evaluation scorecards.

### 5.4 D5.4: Mandatory Assignment Evaluation Scenarios (`tests/evaluation/test_scenarios.py`)

Implements the four assignment evaluation benchmarks:

1. **Benchmark Scenario 1: Dual-Source Corroboration**
   - **Scenario:** Entity reports identical Revenue and Operating Profit in an earnings press release and in the audited annual report.
   - **Expected Outcome:** Group formed across both documents; Path A deterministic arithmetic matches within 0.01%; verdict is `CORROBORATED` with dual document citations and `HIGH` confidence.
2. **Benchmark Scenario 2: Direct Numerical Contradiction**
   - **Scenario:** Two disclosures report conflicting Revenue figures for the exact same entity, temporal period, and accounting standard, with no restatement disclosure.
   - **Expected Outcome:** Variance > 0.01%; Path C hypothesis tournament evaluates all 5 variance classes; all reconciliation hypotheses refuted; verdict is `CONTRADICTION` with `HIGH` confidence.
3. **Benchmark Scenario 3: Defensible Reconciliation**
   - **Scenario:** Earnings presentation reports Adjusted EBITDA (Non-GAAP) while the statutory annual report reports Operating Profit (Ind AS / GAAP) with an explicit reconciliation footnote.
   - **Expected Outcome:** Path B / Path C evaluates `ACCOUNTING_BASIS`; reconciliation bridge survives Adversarial Skeptic critique; verdict is `RECONCILED` with citation of adjustments.
4. **Benchmark Scenario 4: Defensive Failure Handling**
   - **Scenario:** Input contains corrupted or truncated text, a single isolated claim without corroborating context, or an ungrounded candidate reconciliation.
   - **Expected Outcome:** System handles errors gracefully without crashing; fails safe to `UNRESOLVED` with `INSUFFICIENT` or `LOW` confidence and diagnostic trace.

---

## 6. Database Ledger Schema Extensions & Migrations

The existing SQLite schema in `src/db/ledger.py` contains the required 10 tables. For D5, performance and query optimization indexes are formalized:

```sql
-- Query acceleration for trace replay and decision inspection
CREATE INDEX IF NOT EXISTS idx_traces_decision ON decision_traces(decision_id);
CREATE INDEX IF NOT EXISTS idx_decisions_verdict ON decisions(verdict);
CREATE INDEX IF NOT EXISTS idx_decisions_group ON decisions(group_id);
CREATE INDEX IF NOT EXISTS idx_group_members_fact ON group_members(fact_id);
```

---

## 7. Integration Points with Previous Deliverables

- **Deliverable 1 Integration:**
  - `RunContext` manages `reports/` and `traces/` paths.
  - `FastAPI` server routes `GET /jobs/{id}/reports/{type}` and trace inspection endpoints.
  - CLI `main.py` dispatches `report`, `replay`, and `benchmark` subcommands.
- **Deliverable 2 Integration:**
  - Evidence chunk bounding boxes and spatial coordinates are projected into side-by-side contradiction tables.
- **Deliverable 3 Integration:**
  - Fact candidate normalized values, currencies, units, and dates populate report tables and ground truth comparisons.
- **Deliverable 4 Integration:**
  - Decision records, hypotheses, validator outcomes, and skeptic critiques populate the detailed contradiction audit trail.

---

## 8. Failure Modes, Defensive Fallbacks, and Edge Cases

| Failure Mode | Root Cause | Defensive Handling | Resulting Verdict |
| :--- | :--- | :--- | :--- |
| Corrupted or unparseable trace log | Incomplete write or process abort | `TraceReplayer` logs warning, recovers valid JSONL lines up to corruption point | N/A (Diagnostic warning) |
| Missing bounding box data | Unstructured raw text chunk | Report gracefully renders page number with `Coordinates: N/A` | Maintained |
| Zero observations extracted | Empty document or non-financial PDF | Generates clean zero-count summary report and exits safely | `UNRESOLVED` |
| LLM timeout during benchmark | Local inference queue congestion | Auto-retry with temperature 0.0; if exhausted, falls back to deterministic rule | `UNRESOLVED` |
| Ungrounded reconciliation | LLM hallucinated explanation bridge | Adversarial Skeptic flags `UNGROUNDED`; truth table assigns `CONTRADICTION` or `UNRESOLVED` | Fail-safe enforced |

---

## 9. Implementation Step-by-Step Task Breakdown

### Phase 1: Cryptographic Trace Engine and Replay (D5.1)
- [ ] Task 1.1: Enhance `TraceLogger` in `src/observability/trace.py` to record step indexing, payload hashes, and agent identifiers.
- [ ] Task 1.2: Implement `TraceReplayer` in `src/observability/trace.py` to parse `trace.jsonl` and query `decision_traces` table.
- [ ] Task 1.3: Add `evidra replay` subcommand to `src/cli/main.py` for terminal inspection of step chronologies.
- [ ] Task 1.4: Implement API endpoints `GET /jobs/{job_id}/traces` and `GET /jobs/{job_id}/traces/{decision_id}` in `src/api/server.py`.

### Phase 2: Enhanced Production Markdown Reporting Suite (D5.2)
- [ ] Task 2.1: Refine `src/observability/reports.py` to include exact bounding box snippets and tabular side-by-side claim comparison matrices in `contradictions.md`.
- [ ] Task 2.2: Ensure `summary.md`, `contradictions.md`, and `unresolved.md` strictly adhere to GFM standards with zero emojis.
- [ ] Task 2.3: Support JSON summary export (`--format json`) in CLI `evidra report`.

### Phase 3: Automated Evaluation Framework (D5.3)
- [ ] Task 3.1: Create `src/observability/evaluator.py` defining `BenchmarkCase`, `EvaluationDataset`, and `EvaluationMetrics`.
- [ ] Task 3.2: Implement `BenchmarkRunner` with automated metric computation (Accuracy, Precision, Recall, Hallucination Rate).
- [ ] Task 3.3: Add `evidra benchmark` subcommand to `src/cli/main.py`.

### Phase 4: Mandatory Assignment Evaluation Scenarios (D5.4)
- [ ] Task 4.1: Implement `tests/evaluation/test_scenarios.py` with Scenario 1 (Corroboration Benchmark).
- [ ] Task 4.2: Implement Scenario 2 (Direct Contradiction Benchmark).
- [ ] Task 4.3: Implement Scenario 3 (Defensible Reconciliation Benchmark).
- [ ] Task 4.4: Implement Scenario 4 (Defensive Failure Handling Benchmark).

### Phase 5: Verification, Documentation, and Quality Gates
- [ ] Task 5.1: Create diagnostic audit script `scripts/verify_d5.py` testing replay, reporting, and evaluation harness.
- [ ] Task 5.2: Create `docs/deliverable_plans/D5_TESTING_AND_VERIFICATION_PLAN.md`.
- [ ] Task 5.3: Run full test suite across unit, contract, and evaluation suites to achieve 100% pass rate.

---

## 10. Verification Plan and Quality Gates

### 10.1 Automated Test Execution
```powershell
# 1. Run evaluation scenario suite
pytest tests/evaluation/ -v

# 2. Run API contract tests (including trace endpoints)
pytest tests/contracts/test_api.py -v

# 3. Run full repository regression suite
pytest tests/ -v
```

### 10.2 Turnkey Diagnostic Script
```powershell
python scripts/verify_d5.py
```

### 10.3 CLI Replay and Benchmark Execution
```powershell
# Replay recent multi-document job
python -m src.cli.main replay JOB-20260908-034754-34f962 --decision-id DEC-57c1248a

# Run benchmark evaluation
python -m src.cli.main benchmark
```
