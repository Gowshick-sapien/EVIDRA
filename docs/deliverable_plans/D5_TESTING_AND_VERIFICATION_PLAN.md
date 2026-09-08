# EVIDRA: Evidence-Driven Architecture for Fact Validation and Knowledge Reasoning

## Deliverable 5 (D5) Testing and Verification Plan: Observability, Reporting, and Evaluation Testing

---

## 1. Testing Philosophy and Observability Mandate

Deliverable 5 (**D5**) represents the operational auditability, reporting, and evaluation testing surface of **EVIDRA** (Layer 4).

Quality assurance for D5 enforces four strict mandates:
1. **100% Cryptographic Trace Replay:** Every state transformation, LLM prompt, raw completion, validator outcome, and policy rule fired during execution must be retrievable and replayable chronologically from `trace.jsonl` or the SQLite `decision_traces` table.
2. **Human-Readable Executive Reporting:** Reports (`summary.md`, `contradictions.md`, `unresolved.md`, `summary.json`) must be cleanly formatted in GitHub Flavored Markdown with side-by-side claim comparison tables, physical bounding box coordinates, verbatim source evidence snippets, and zero extraneous emojis.
3. **Quantitative Benchmark Evaluation:** All four mandatory assignment evaluation benchmarks must be programmatically verified against ground truth, achieving 100% accuracy, 100% precision, 100% recall, and 0.0% hallucination rate.
4. **Defensive Failure Resiliency:** Any corrupt text, missing document page, unstated assumption, or ambiguous observation must fail safe to `UNRESOLVED` with diagnostic warnings rather than causing system crashes or false reconciliations.

---

## 2. Automated Test Suites (57 Passing Tests)

The repository test suite contains 59 passing tests across 12 test modules:

```powershell
pytest tests/ -v
```

### 2.1 Test Suite Breakdown
```text
collected 59 items

tests\contracts\test_api.py .......                                      [ 11%]
tests\evaluation\test_scenarios.py .....                                 [ 20%]
tests\unit\test_cli.py ......                                            [ 30%]
tests\unit\test_decimal_units.py .....                                   [ 38%]
tests\unit\test_decision.py ...........                                  [ 57%]
tests\unit\test_extraction.py ...                                        [ 62%]
tests\unit\test_ledger.py .....                                          [ 71%]
tests\unit\test_llm.py ..                                                [ 74%]
tests\unit\test_pdf.py ...                                               [ 79%]
tests\unit\test_temporal_parsing.py .....                                [ 88%]
tests\unit\test_trace.py ..                                              [ 91%]
tests\unit\test_verification.py .....                                    [100%]

======================= 59 passed, 3 warnings in 33.79s =======================
```

### 2.2 Evaluation Scenario Tests (`tests/evaluation/test_scenarios.py`)
- `test_benchmark_scenario_1_dual_source_corroboration`: Verifies dual-source identical revenue matching within 0.01% tolerance -> `CORROBORATED` with `HIGH` decision strength.
- `test_benchmark_scenario_2_direct_contradiction`: Verifies conflicting operating profit figures under identical context -> `CONTRADICTION` with `HIGH` decision strength.
- `test_benchmark_scenario_3_defensible_reconciliation_accounting_basis`: Verifies Non-GAAP vs GAAP differences resolved via `ACCOUNTING_BASIS` hypothesis -> `RECONCILED` with `HIGH` decision strength.
- `test_benchmark_scenario_4_defensive_failure_handling`: Verifies single-source isolated observation fails safe to `UNRESOLVED` with `LOW` decision strength without pipeline errors.
- `test_evaluation_harness_metrics_computation`: Verifies `EvaluationHarness` metrics calculation and clean Markdown scorecard rendering.

### 2.3 Contract Tests for Trace and Report Endpoints (`tests/contracts/test_api.py`)
- `test_health_check`: Verifies system health probe, SQLite readiness, and Ollama status.
- `test_create_job_and_poll_status`: Verifies job creation and lifecycle status polling.
- `test_job_decisions_and_details`: Verifies decision listing and granular Decision Card retrieval.
- `test_job_reports`: Verifies downloading `summary.md` and 404 handling on missing reports.
- `test_job_traces`: Verifies `GET /jobs/{job_id}/traces` and `GET /jobs/{job_id}/traces/{decision_id}` endpoints.

---

## 3. Turnkey Diagnostic Audit Script (`scripts/verify_d5.py`)

A dedicated verification audit script [scripts/verify_d5.py](file:///d:/projects/superjoin/EVIDRA/scripts/verify_d5.py) validates the entire D5 observability and evaluation stack independently:

```powershell
python scripts/verify_d5.py
```

### Audit Output
```text
============================================================
  EVIDRA Deliverable 5 (D5) Observability & Evaluation Audit
============================================================

[1/4] Auditing Cryptographic Trace Engine & TraceReplayer...
      PASS: TraceLogger and TraceReplayer validated.
[2/4] Auditing Production Reporting Suite (Markdown & JSON)...
      PASS: Reports generated with bounding boxes and structured JSON.
[3/4] Auditing Evaluation Framework & Metrics Calculation...
      PASS: Metric calculations and scorecard generation verified.
[4/4] Executing Mandatory Assignment Benchmark Scenarios...
      - BENCH-01: Dual-Source Corroboration Benchmark -> CORROBORATED (Latency: 92.1ms) [PASS]
      - BENCH-02: Direct Numerical Contradiction Benchmark -> CONTRADICTION (Latency: 141.8ms) [PASS]
      - BENCH-03: Defensible Reconciliation Benchmark -> RECONCILED (Latency: 156.0ms) [PASS]
      - BENCH-04: Defensive Failure Handling Benchmark -> UNRESOLVED (Latency: 82.5ms) [PASS]

============================================================
  ALL DELIVERABLE 5 (D5) QUALITY CHECKS PASSED
============================================================
```

---

## 4. Mandatory Assignment Benchmark Scenarios Execution

The automated benchmark harness was executed via the CLI:
```powershell
python -m src.cli.main benchmark
```

### Benchmark Scorecard
```text
Running EVIDRA mandatory assignment benchmark scenarios...

# EVIDRA Evaluation Benchmark Scorecard

- **Total Scenarios Evaluated:** 4
- **Passed Scenarios:** 4
- **Overall Accuracy:** 100.0%
- **Hallucination Rate:** 0.0%

## 1. Metric Breakdown by Epistemic Verdict

| Verdict Class | Precision | Recall | F1 Score |
| :--- | :--- | :--- | :--- |
| **CORROBORATED** | 100.0% | 100.0% | 100.0% |
| **CONTRADICTION** | 100.0% | 100.0% | 100.0% |
| **RECONCILED** | 100.0% | 100.0% | 100.0% |
| **UNRESOLVED** | 100.0% | 100.0% | 100.0% |

## 2. Individual Scenario Results

| Case ID | Scenario Name | Expected | Actual | Latency | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `BENCH-01` | Dual-Source Corroboration Benchmark | **CORROBORATED** | **CORROBORATED** | 135.73ms | **PASS** |
| `BENCH-02` | Direct Numerical Contradiction Benchmark | **CONTRADICTION** | **CONTRADICTION** | 173.49ms | **PASS** |
| `BENCH-03` | Defensible Reconciliation Benchmark | **RECONCILED** | **RECONCILED** | 196.65ms | **PASS** |
| `BENCH-04` | Defensive Failure Handling Benchmark | **UNRESOLVED** | **UNRESOLVED** | 113.88ms | **PASS** |
```

---

## 5. Forensic Replay & Production Reporting Verification

### 5.1 CLI Decision Replay Verification
Inspecting decision `DEC-57c1248a` from production run `JOB-20260908-034754-34f962`:
```powershell
python -m src.cli.main replay JOB-20260908-034754-34f962 --decision-id DEC-57c1248a
```
```text
================================================================================
  EVIDRA Cryptographic Audit Replay (Decision: DEC-57c1248a)
================================================================================
[01] Step: analyze_variance | Agent: VarianceAnalyzer | Decision: DEC-57c1248a | Latency: 0.05ms
     Timestamp: 2026-09-08 03:53:06
     Input:     {"candidates_count": 3}
     Output:    {"decision_path": "B", "arithmetic_equal": false, "matching_context": false}
--------------------------------------------------------------------------------
[02] Step: route_context | Agent: ContextRouter | Decision: DEC-57c1248a | Latency: 0.22ms
     Timestamp: 2026-09-08 03:53:06
     Input:     {"context_differences": true}
     Output:    {"hypotheses_count": 2, "validator_results_count": 1}
--------------------------------------------------------------------------------
[03] Step: propose_reconciliation | Agent: ReconciliationProposerAgent | Decision: DEC-57c1248a | Latency: 0.04ms
     Timestamp: 2026-09-08 03:53:06
     Input:     {"supported_validators": 1}
     Output:    {"proposal": {"supported_hypothesis_id": "HYP-BASIS-cfac76", "explanation_type": "ACCOUNTING_BASIS", "root_cause": "A...
--------------------------------------------------------------------------------
[04] Step: critique_reconciliation | Agent: AdversarialSkepticAgent | Decision: DEC-57c1248a | Latency: 0.03ms
     Timestamp: 2026-09-08 03:53:06
     Input:     {"proposal_root_cause": "Accounting Standard Discrepancy (GAAP vs Non-GAAP)"}
     Output:    {"skeptic_status": "SURVIVED", "critique": "Accounting standard variance explicitly verified: NON_GAAP vs UNKNOWN."}
--------------------------------------------------------------------------------
[05] Step: apply_policy | Agent: DecisionPolicy | Decision: DEC-57c1248a | Latency: 0.03ms
     Timestamp: 2026-09-08 03:53:06
     Input:     {"arithmetic_equal": false, "path": "B"}
     Output:    {"verdict": "RECONCILED", "decision_strength": "HIGH", "summary": "Reconciled: Reporting basis difference between NON...
--------------------------------------------------------------------------------
```

### 5.2 Production Reports Verification
- `summary.md`: Document manifest, pipeline counts, verdict distributions, and decision matrix.
- `contradictions.md`: Tabular side-by-side claim comparisons, spatial bounding box coordinates (`[x0, y0, x1, y1]`), verbatim source evidence snippets, evaluated hypotheses, and Adversarial Skeptic critique notes.
- `unresolved.md`: Itemized diagnostic report with specific follow-up recommendations for equity analysts.
- `summary.json`: Structured JSON export verified via `python -m src.cli.main report <job_id> --format json`.

---

## 6. Deliverable D5 Execution Verification Matrix

| Component | Target Artifact | Requirement Verified | Verification Method | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Trace Engine & Replayer** | `src/observability/trace.py` | JSONL and SQLite trace loading, timeline rendering, integrity audit | `scripts/verify_d5.py` & CLI replay | **PASSED** |
| **Forensic CLI Replay** | `src/cli/main.py` | `evidra replay <job_id>` with decision-level filtering | Live execution on Delhivery runs | **PASSED** |
| **Trace REST API Endpoints** | `src/api/server.py` | `GET /jobs/{id}/traces` and `GET /jobs/{id}/traces/{dec_id}` | `tests/contracts/test_api.py` | **PASSED** |
| **Production Reporting Suite** | `src/observability/reports.py` | Bounding boxes, verbatim evidence context, skeptic critiques | `scripts/verify_d5.py` & disk inspection | **PASSED** |
| **JSON Report Export** | `src/observability/reports.py`, `src/cli/main.py` | `summary.json` generation and `--format json` CLI export | Live CLI execution | **PASSED** |
| **Evaluation Framework** | `src/observability/evaluator.py` | Precision, Recall, F1, Accuracy, Hallucination Rate engine | `tests/evaluation/test_scenarios.py` | **PASSED** |
| **Benchmark Scenarios (1-4)** | `tests/evaluation/test_scenarios.py` | Corroboration, Contradiction, Reconciliation, Failure Handling | Automated pytest suite & `evidra benchmark` | **PASSED** |
| **Repository Regression Suite** | Entire Repository | 59 unit, contract, and evaluation tests | `pytest tests/ -v` (100% pass rate) | **PASSED** |
